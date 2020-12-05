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


if __name__ == "__main__":

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