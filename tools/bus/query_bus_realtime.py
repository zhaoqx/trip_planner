import requests
import sys

def query_bus_realtime(city, line_name, station_name, amap_key):
    # Step 1: 获取线路ID
    line_url = 'https://restapi.amap.com/v3/bus/linename'
    line_params = {
        'city': city,
        'keywords': line_name,
        'key': amap_key
    }
    line_resp = requests.get(line_url, params=line_params).json()
    print('线路查询接口返回:', line_resp)
    if not line_resp.get('buslines'):
        print('未找到线路')
        return
    line_id = line_resp['buslines'][0]['id']

    # Step 2: 查询实时公交到站信息
    realtime_url = 'https://restapi.amap.com/v4/bus/bus_realtime'
    realtime_params = {
        'city': city,
        'lineid': line_id,
        'key': amap_key
    }
    realtime_resp = requests.get(realtime_url, params=realtime_params).json()
    print('实时公交接口返回:', realtime_resp)
    if 'data' not in realtime_resp or 'stations' not in realtime_resp['data']:
        print('未找到实时公交信息')
        return

    # Step 3: 查找目标站点
    stations = realtime_resp['data']['stations']
    for station in stations:
        if station['name'] == station_name:
            buses = station.get('bus', [])
            if not buses:
                print('暂无车辆到达')
                return
            for i, bus in enumerate(buses[:2]):
                print(f"第{i+1}辆车预计{bus['time']}秒后到达{station_name}")
            return
    print('未找到指定站点')

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('用法: python query_bus_realtime.py 城市 线路名 站点名')
        print('示例: python query_bus_realtime.py 北京 909路 软件园西区')
        sys.exit(1)
    city = sys.argv[1]
    line_name = sys.argv[2]
    station_name = sys.argv[3]
    try:
        import sys
        import os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
        from local_config import amap_key
    except ImportError:
        print('请在 local_config.py 中配置 amap_key')
        sys.exit(1)
    query_bus_realtime(city, line_name, station_name, amap_key)
