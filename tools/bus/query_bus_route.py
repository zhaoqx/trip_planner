import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from local_config import amap_key


def query_bus_route(city, origin, destination_coord, amap_key):
    # Step 1: 地点转经纬度（仅起点）
    def geocode(address):
        url = 'https://restapi.amap.com/v3/geocode/geo'
        params = {
            'address': address,
            'city': city,
            'key': amap_key
        }
        resp = requests.get(url, params=params).json()
        print(f"地理编码接口返回({address}):", resp)
        if resp.get('status') == '1' and resp.get('geocodes'):
            return resp['geocodes'][0]['location']
        else:
            return None

    origin_loc = geocode(origin)
    if not origin_loc:
        print('地理编码失败')
        return
    destination_loc = destination_coord

    # Step 2: 路线规划（公交模式）
    route_url = 'https://restapi.amap.com/v3/direction/transit/integrated'
    route_params = {
        'origin': origin_loc,
        'destination': destination_loc,
        'city': city,
        'strategy': 5,  # 公交优先
        'key': amap_key
    }
    route_resp = requests.get(route_url, params=route_params).json()
    print('公交路线规划接口返回:', route_resp)
    # 分析是否有预计到站时间
    if route_resp.get('status') == '1' and route_resp.get('route'):
        transits = route_resp['route'].get('transits', [])
        if not transits:
            print('未找到公交路线')
            return
        for i, transit in enumerate(transits[:1]):
            print(f"方案{i+1}: 总时长{transit['duration']}秒, 预计步行{transit['walking_distance']}米")
            for segment in transit.get('segments', []):
                for bus in segment.get('bus', {}).get('buslines', []):
                    print(f"公交线路: {bus['name']}, 预计发车时间: {bus.get('start_time', '未知')}, 预计到达时间: {bus.get('end_time', '未知')}")
    else:
        print('未找到公交路线')

if __name__ == '__main__':
    city = '北京'
    origin = '亚信大厦'
    # 管氏翅吧(上地店)坐标
    destination_coord = '116.311560,40.035227'
    query_bus_route(city, origin, destination_coord, amap_key)
