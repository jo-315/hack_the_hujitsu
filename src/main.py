from flask import render_template, request
from src import app
import os
import json
import httplib2
import requests
import time
from datetime import datetime, timedelta
from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow, flow_from_clientsecrets
from oauth2client.file import Storage

OAUTH_SCOPE = 'https://www.googleapis.com/auth/fitness.activity.read'
DATA_SOURCE = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
CREDENTIALS_FILE = "./credentials"

START = {'latitude': -157.85059440538518, 'longitude': 21.292003771901275}
GOAL = {'latitude': -157.84389066977633, 'longitude': 21.289743961838436}

# 最初の検索画面
@app.route('/', methods=['GET'])
def index():
    msg = "歩数を記録"
    point={"ロンドン":"https://www.google.com/maps/embed?pb=!4v1607025863243!6m8!1m7!1sierMTh4ePdwoKu6_7IiCvA!2m2!1d51.50897647482117!2d-0.08739389902462565!3f180!4f0!5f0.7820865974627469","ラスベガス":"https://www.google.com/maps/embed?pb=!4v1607026447718!6m8!1m7!1s2OlsjeKFZu4GQN0EOi4lHA!2m2!1d36.11234006692544!2d-115.1749467008171!3f90!4f0!5f0.7820865974627469"  }
    return render_template("index.html", msg = msg,point =  point)


#  javascriptからのAPIを受け取って歩数を返す
@app.route('/fetch', methods=['GET'])
def fetch():
    # 現在の緯度経度を取得
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')

    # TODO: 歩数をAPIで取得（google fit api）
    # steps = fetch_steps()
    steps = 10

    # TODO: 移動後の緯度経度を計算

    # TODO: Google MAP の URL を取得

    return {'hogehoge': ''}


def auth_data():

    credentials = ""

    if os.path.exists(CREDENTIALS_FILE):
        credentials = Storage(CREDENTIALS_FILE).get()
    else:
        #flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)
        flow = flow_from_clientsecrets(
            # API有効化時に取得したOAuth用のJSONファイルを指定
            './secret/oauth2.json',
            # スコープを指定
            scope=OAUTH_SCOPE,
            # ユーザーの認証後の、トークン受け取り方法を指定（後述）
            redirect_uri=REDIRECT_URI)

        authorize_url = flow.step1_get_authorize_url()
        print('下記URLをブラウザで起動してください。')
        print(authorize_url)

        code = input('Codeを入力してください: ').strip()
        credentials = flow.step2_exchange(code)

        if not os.path.exists(CREDENTIALS_FILE):
            Storage(CREDENTIALS_FILE).put(credentials)

    # Create an httplib2.Http object and authorize it with our credentials
    http = httplib2.Http()
    http = credentials.authorize(http)

    fitness_service = build('fitness', 'v1', http=http)

    return fitness_service


def retrieve_data(fitness_service, dataset):

    return fitness_service.users().dataSources(). \
        datasets(). \
        get(userId='me', dataSourceId=DATA_SOURCE, datasetId=dataset). \
        execute()


def nanoseconds(nanotime):
    """
    ナノ秒に変換する
    """
    dt = datetime.fromtimestamp(nanotime // 1000000000)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def logwrite(date, step):
    with open('./data/step.log', 'a') as outfile:
        outfile.write(str(date) + "," + str(step) + "\n")


def fetch_steps():
    authdata = auth_data()

    # 前日分のデータを取得
    TODAY = datetime.today() - timedelta(days=1)
    STARTDAY = datetime(TODAY.year, TODAY.month, TODAY.day, 0, 0, 0)
    NEXTDAY = datetime(TODAY.year, TODAY.month, TODAY.day, 23, 59, 59)
    NOW = datetime.today()

    START = int(time.mktime(STARTDAY.timetuple())*1000000000)
    NEXT = int(time.mktime(NEXTDAY.timetuple())*1000000000)
    END = int(time.mktime(NOW.timetuple())*1000000000)
    data_set = "%s-%s" % (START, NEXT)

    while True:

        if END < NEXT:
            break

        dataset = retrieve_data(authdata, data_set)

        starts = []
        ends = []
        values = []
        for point in dataset["point"]:
            if int(point["startTimeNanos"]) > START:
                starts.append(int(point["startTimeNanos"]))
                ends.append(int(point["endTimeNanos"]))
                values.append(point['value'][0]['intVal'])

        print("From: {}".format(nanoseconds(min(starts))))
        print("To: {}".format(nanoseconds(max(ends))))
        print("Steps:{}".format(sum(values)))

        step = sum(values)

        startdate = STARTDAY.date()
        logwrite(startdate, step)

        STARTDAY = STARTDAY + timedelta(days=1)
        NEXTDAY = NEXTDAY + timedelta(days=1)
        START = int(time.mktime(STARTDAY.timetuple())*1000000000)
        NEXT = int(time.mktime(NEXTDAY.timetuple())*1000000000)
        data_set = "%s-%s" % (START, NEXT)

        time.sleep(5)

    # TODO: stepsをreturnさせる
    # return steps

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
