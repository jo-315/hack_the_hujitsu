from calc_latlon import calc_moving

def get_map_url(lat, lon):
    """
    通常のグーグルマップのURLを取得する

    Args:
        lat (float): 北緯
        lon (float): 東経
    
    Returns:
        url (str): 入力された緯度経度のGoogle MapのURL
    """
    base_url = "https://maps.google.co.jp/maps?"

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


if __name__ == "__main__":
    current_lat = 21.292003771901275 
    current_lon = -157.85059440538518
    step = 10
    theta = 90
    print( get_map_url(current_lat, current_lon) )