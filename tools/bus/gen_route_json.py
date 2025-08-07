import requests
import sys
import os
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from local_config import amap_key

def get_route_data_json(city, origin, destination_coord, amap_key, output_json):
    def geocode(address):
        url = 'https://restapi.amap.com/v3/geocode/geo'
        params = {
            'address': address,
            'city': city,
            'key': amap_key
        }
        resp = requests.get(url, params=params).json()
        if resp.get('status') == '1' and resp.get('geocodes'):
            return resp['geocodes'][0]['location']
        else:
            return None
    origin_loc = geocode(origin)
    if not origin_loc:
        print('地理编码失败')
        return None
    destination_loc = destination_coord
    route_url = 'https://restapi.amap.com/v3/direction/transit/integrated'
    route_params = {
        'origin': origin_loc,
        'destination': destination_loc,
        'city': city,
        'strategy': 5,
        'key': amap_key
    }
    route_resp = requests.get(route_url, params=route_params).json()
    if route_resp.get('status') != '1' or not route_resp.get('route'):
        print('未找到公交路线')
        return None
    transits = route_resp['route'].get('transits', [])
    if not transits:
        print('未找到公交路线')
        return None
    transit = transits[0]
    # 组装为 plotly 脚本可用的 json
    route_data = {'segments': []}
    for segment in transit.get('segments', []):
        seg_type = 'walk' if segment.get('walking') else 'bus' if segment.get('bus') else 'other'
        stops = []
        # 步行段
        if segment.get('walking'):
            for step in segment['walking'].get('steps', []):
                for p in step.get('polyline', '').split(';'):
                    if p:
                        lat, lng = map(float, p.split(','))
                        stops.append({'lat': lat, 'lng': lng, 'name': '步行'})
        # 公交段
        if segment.get('bus'):
            for busline in segment['bus'].get('buslines', []):
                for stop in [busline.get('departure_stop')] + busline.get('via_stops', []) + [busline.get('arrival_stop')]:
                    if stop and 'location' in stop:
                        lat, lng = map(float, stop['location'].split(','))
                        stops.append({'lat': lat, 'lng': lng, 'name': stop.get('name', '公交站')})
        route_data['segments'].append({'type': seg_type, 'stops': stops})
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(route_data, f, ensure_ascii=False, indent=2)
    print(f'公交路线数据已保存为 {output_json}')

if __name__ == '__main__':
    city = '北京'
    origin = '亚信大厦'
    destination_coord = '116.311560,40.035227'
    output_json = 'route.json'
    get_route_data_json(city, origin, destination_coord, amap_key, output_json)
