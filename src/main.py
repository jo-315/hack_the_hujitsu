from flask import render_template, request
from src import app
import numpy as np
import json
import collections as cl

OAUTH_SCOPE = 'https://www.googleapis.com/auth/fitness.activity.read'
DATA_SOURCE = "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
CREDENTIALS_FILE = "./credentials"

START = {'latitude': -157.85059440538518, 'longitude': 21.292003771901275}
GOAL = {'latitude': -157.84389066977633, 'longitude': 21.289743961838436}
start = {'latitude':0, 'longitude':0}
theta = 0
mobile_bool = 0
total_step = 0
step = 0

# 最初の検索画面
@app.route('/', methods=['GET'])
def index():
    start = START
    # print('request.form.getlist("mobile-check")',request.form.getlist("mobile-check"))
    # total_step = total_step + step


    with open("./step_data.json", "r") as f:
        data = json.load(f)
        print(data)
        total_step = data['step']
        latitude = data['latitude']
        longitude = data['longitude']

    if total_step == 0:
        start = START
    else:
        start = {'latitude':latitude, 'longitude':longitude}


    return render_template("index.html", start=start)

@app.route('/', methods=['POST'])
def reload_steps():
    step = request.form.getlist("steps")
    step = int(step[0])
    # print("steps:",step)

    with open("./step_data.json", "r") as f:
        data = json.load(f)
        print(data)
        total_step = data['step']
        latitude = data['latitude']
        longitude = data['longitude']

    theta = calc_theta(START, GOAL)
    if total_step == 0:
        # start = START
        latitude,longitude = calc_moving(latitude, longitude, theta, step)
        start = {'latitude':latitude, 'longitude':longitude}

        print("total_step == 0")
        with open("./step_data.json", "w") as f:
            data = cl.OrderedDict()
            data['step'] = step
            data['latitude'] = start['latitude']
            data['longitude'] = start['longitude']
            json.dump(data,f,indent=4)
        

    else:
        print("total_step > 0")
        # start['latitude'],start['longitude'] = calc_moving(latitude, longitude, theta, step)
        longitude,latitude = calc_moving(latitude, longitude, theta, step)
        start = {'latitude':latitude, 'longitude':longitude}
        total_step += step
        with open("./step_data.json", "w") as f:
            data = cl.OrderedDict()
            data['step'] = total_step
            data['latitude'] = start['latitude']
            data['longitude'] = start['longitude']
            json.dump(data,f,indent=4)

    return render_template("index.html", start=start)


#  javascriptからのAPIを受け取って歩数を返す
@app.route('/fetch', methods=['GET'])
def fetch():
    # 現在の緯度経度及び歩数を取得
    latitude = float(request.args.get('latitude'))
    longitude = float(request.args.get('longitude'))

    # TODO 歩数データをファイルより取得
    steps = 0

    # 移動後の緯度経度を計算
    n_latitude, n_longitude = calc_moving(latitude, longitude, theta, steps)

    # Google MAP の URL を取得
    map_url = get_map_url(n_latitude, n_longitude)
    # theta = 0
    # map_url = get_view_url(n_latitude, n_longitude, theta)

    return {
        'map_url': map_url,
        'n_latitude': n_latitude,
        'n_longitude': n_longitude
        }

# スマホから歩数データを受け取る
@app.route('/mobiledata', methods=['POST'])
def mobiledata():
    # 歩数データを記録したファイルを作成
    return

def get_map_url(lat, lon):
    """
    通常のグーグルマップのURLを取得する

    Args:
        lat (float): 北緯
        lon (float): 東経

    Returns:
        url (str): 入力された緯度経度のGoogle MapのURL
    """
    base_url = "https://maps.google.co.jp/maps?key=AIzaSyDBvtAzU-u_hQeSR5TvMGY3Lj8XgC8yDao"

    # 緯度経度オプション
    opt_location = "ll=" + str(lat) + "," + str(lon)

    # ズーム倍率オプション
    zoom = 20
    opt_zoom = "&z=" + str(zoom)

    # ピン止めオプション
    pin = True
    opt_pin = "&q=" + str(lat) + "," + str(lon) if pin else ""

    url = base_url + opt_location + opt_zoom + opt_pin

    return url

def get_view_url(lat, lon, theta):
    """
    グーグルストリートビューのURLを取得する
​
    Args:
        lat (float): 北緯
        lon (float): 東経
​
    Returns:
        url (str): 入力された緯度経度のGoogle MapのURL
    """
    base_url = "https://www.google.com/maps/@?api=1&map_action=pano&parameters"
    # 緯度経度オプション
    opt_location = "&viewpoint=" + str(lon) + "," + str(lat)
    head = theta + 90
    opt_head = "&heading=" + str(head)
    url = base_url + opt_location + opt_head
    return url

def calc_moving(current_lat, current_lon, theta, step):
    """
    Args:
        current_lat (float): 現在地の北緯
        current_lon (float): 現在地の東経
        theta (float): 向いている角度 (進む方向)
        step (int): 歩数

    Returns:
        next_lat (float): 移動後の北緯
        next_lon (float): 移動後の東経
    """

    stride = 1.0 # 歩幅 (1歩を1mとする)
    moving = stride * float(step) # 移動距離[m]
    moving_east = np.cos(np.radians(theta)) * moving # 東西方向の移動距離[m], 東が正方向
    moving_north = np.sin(np.radians(theta)) * moving # 南北方向の移動距離[m], 北が正方向

    next_lon, next_lat = trans_lat_lon(moving_east, moving_north, current_lat, current_lon)

    return next_lat, next_lon


def calc_theta(start, goal):
    """
    出発地, 到着地から向かうべき方角を決める

    Args:
        start: 出発地点
            ( start = {'latitude': -157.85059440538518, 'longitude': 21.292003771901275} )
        goal: 到着地点
            ( goal = {'latitude': -157.84389066977633, 'longitude': 21.289743961838436} )

    Returns:
        theta (float): 方向(0 ~ 360)
    """
    start_plot = trans_xy(start["latitude"], start["longitude"], 0, 0)
    goal_plot = trans_xy(goal["latitude"], goal["longitude"], 0, 0)
    x_dist = (goal_plot[0] - start_plot[0])
    y_dist = goal_plot[1] - start_plot[1]
    tan = y_dist / x_dist
    theta = np.rad2deg(np.arctan(tan))

    # 東経, 北緯による条件分岐
    theta += 360 # 今回のスタート, ゴールの場合
    return theta

def trans_lat_lon(x, y, phi0_deg, lambda0_deg):
    """
    平面直角座標を緯度経度に変換する

    Args:
        (x, y): 変換したいx, y座標[m]
        (phi0_deg, lambda0_deg): 平面直角座標系原点の緯度・経度[度]（分・秒でなく小数であることに注意）

    Returns:
        latitude:  緯度[度]
        longitude: 経度[度]
        * 小数点以下は分・秒ではないことに注意
    """
    # 平面直角座標系原点をラジアンに直す
    phi0_rad = np.deg2rad(phi0_deg)
    lambda0_rad = np.deg2rad(lambda0_deg)

    # 補助関数
    def A_array(n):
        A0 = 1 + (n**2)/4. + (n**4)/64.
        A1 = -     (3./2)*( n - (n**3)/8. - (n**5)/64. )
        A2 =     (15./16)*( n**2 - (n**4)/4. )
        A3 = -   (35./48)*( n**3 - (5./16)*(n**5) )
        A4 =   (315./512)*( n**4 )
        A5 = -(693./1280)*( n**5 )
        return np.array([A0, A1, A2, A3, A4, A5])

    def beta_array(n):
        b0 = np.nan # dummy
        b1 = (1./2)*n - (2./3)*(n**2) + (37./96)*(n**3) - (1./360)*(n**4) - (81./512)*(n**5)
        b2 = (1./48)*(n**2) + (1./15)*(n**3) - (437./1440)*(n**4) + (46./105)*(n**5)
        b3 = (17./480)*(n**3) - (37./840)*(n**4) - (209./4480)*(n**5)
        b4 = (4397./161280)*(n**4) - (11./504)*(n**5)
        b5 = (4583./161280)*(n**5)
        return np.array([b0, b1, b2, b3, b4, b5])

    def delta_array(n):
        d0 = np.nan # dummy
        d1 = 2.*n - (2./3)*(n**2) - 2.*(n**3) + (116./45)*(n**4) + (26./45)*(n**5) - (2854./675)*(n**6)
        d2 = (7./3)*(n**2) - (8./5)*(n**3) - (227./45)*(n**4) + (2704./315)*(n**5) + (2323./945)*(n**6)
        d3 = (56./15)*(n**3) - (136./35)*(n**4) - (1262./105)*(n**5) + (73814./2835)*(n**6)
        d4 = (4279./630)*(n**4) - (332./35)*(n**5) - (399572./14175)*(n**6)
        d5 = (4174./315)*(n**5) - (144838./6237)*(n**6)
        d6 = (601676./22275)*(n**6)
        return np.array([d0, d1, d2, d3, d4, d5, d6])

    # 定数 (a, F: 世界測地系-測地基準系1980（GRS80）楕円体)
    m0 = 0.9999
    a = 6378137.
    F = 298.257222101

    # (1) n, A_i, beta_i, delta_iの計算
    n = 1. / (2*F - 1)
    A_array = A_array(n)
    beta_array = beta_array(n)
    delta_array = delta_array(n)

    # (2), S, Aの計算
    A_ = ( (m0*a)/(1.+n) )*A_array[0]
    S_ = ( (m0*a)/(1.+n) )*( A_array[0]*phi0_rad + np.dot(A_array[1:], np.sin(2*phi0_rad*np.arange(1,6))) )

    # (3) xi, etaの計算
    xi = (x + S_) / A_
    eta = y / A_

    # (4) xi', eta'の計算
    xi2 = xi - np.sum(np.multiply(beta_array[1:],
                                  np.multiply(np.sin(2*xi*np.arange(1,6)),
                                              np.cosh(2*eta*np.arange(1,6)))))
    eta2 = eta - np.sum(np.multiply(beta_array[1:],
                                   np.multiply(np.cos(2*xi*np.arange(1,6)),
                                               np.sinh(2*eta*np.arange(1,6)))))

    # (5) chiの計算
    chi = np.arcsin( np.sin(xi2)/np.cosh(eta2) ) # [rad]
    latitude = chi + np.dot(delta_array[1:], np.sin(2*chi*np.arange(1, 7))) # [rad]

    # (6) 緯度(latitude), 経度(longitude)の計算
    longitude = lambda0_rad + np.arctan( np.sinh(eta2)/np.cos(xi2) ) # [rad]

    # ラジアンを度になおしてreturn
    return np.rad2deg(latitude), np.rad2deg(longitude) # [deg]

def trans_xy(phi_deg, lambda_deg, phi0_deg, lambda0_deg):
    """ 緯度経度を平面直角座標に変換する
    - input:
        (phi_deg, lambda_deg): 変換したい緯度・経度[度]（分・秒でなく小数であることに注意）
        (phi0_deg, lambda0_deg): 平面直角座標系原点の緯度・経度[度]（分・秒でなく小数であることに注意）
    - output:
        x: 変換後の平面直角座標[m]
        y: 変換後の平面直角座標[m]
    """
    # 緯度経度・平面直角座標系原点をラジアンに直す
    phi_rad = np.deg2rad(phi_deg)
    lambda_rad = np.deg2rad(lambda_deg)
    phi0_rad = np.deg2rad(phi0_deg)
    lambda0_rad = np.deg2rad(lambda0_deg)

    # 補助関数
    def A_array(n):
        A0 = 1 + (n**2)/4. + (n**4)/64.
        A1 = -     (3./2)*( n - (n**3)/8. - (n**5)/64. ) 
        A2 =     (15./16)*( n**2 - (n**4)/4. )
        A3 = -   (35./48)*( n**3 - (5./16)*(n**5) )
        A4 =   (315./512)*( n**4 )
        A5 = -(693./1280)*( n**5 )
        return np.array([A0, A1, A2, A3, A4, A5])

    def alpha_array(n):
        a0 = np.nan # dummy
        a1 = (1./2)*n - (2./3)*(n**2) + (5./16)*(n**3) + (41./180)*(n**4) - (127./288)*(n**5)
        a2 = (13./48)*(n**2) - (3./5)*(n**3) + (557./1440)*(n**4) + (281./630)*(n**5)
        a3 = (61./240)*(n**3) - (103./140)*(n**4) + (15061./26880)*(n**5)
        a4 = (49561./161280)*(n**4) - (179./168)*(n**5)
        a5 = (34729./80640)*(n**5)
        return np.array([a0, a1, a2, a3, a4, a5])

    # 定数 (a, F: 世界測地系-測地基準系1980（GRS80）楕円体)
    m0 = 0.9999
    a = 6378137.
    F = 298.257222101

    # (1) n, A_i, alpha_iの計算
    n = 1. / (2*F - 1)
    A_array = A_array(n)
    alpha_array = alpha_array(n)

    # (2), S, Aの計算
    A_ = ( (m0*a)/(1.+n) )*A_array[0] # [m]
    S_ = ( (m0*a)/(1.+n) )*( A_array[0]*phi0_rad + np.dot(A_array[1:], np.sin(2*phi0_rad*np.arange(1,6))) ) # [m]

    # (3) lambda_c, lambda_sの計算
    lambda_c = np.cos(lambda_rad - lambda0_rad)
    lambda_s = np.sin(lambda_rad - lambda0_rad)

    # (4) t, t_の計算
    t = np.sinh( np.arctanh(np.sin(phi_rad)) - ((2*np.sqrt(n)) / (1+n))*np.arctanh(((2*np.sqrt(n)) / (1+n)) * np.sin(phi_rad)) )
    t_ = np.sqrt(1 + t*t)

    # (5) xi', eta'の計算
    xi2  = np.arctan(t / lambda_c) # [rad]
    eta2 = np.arctanh(lambda_s / t_)

    # (6) x, yの計算
    x = A_ * (xi2 + np.sum(np.multiply(alpha_array[1:],
                                       np.multiply(np.sin(2*xi2*np.arange(1,6)),
                                                   np.cosh(2*eta2*np.arange(1,6)))))) - S_ # [m]
    y = A_ * (eta2 + np.sum(np.multiply(alpha_array[1:],
                                        np.multiply(np.cos(2*xi2*np.arange(1,6)),
                                                    np.sinh(2*eta2*np.arange(1,6)))))) # [m]
    # return
    return x, y # [m]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
