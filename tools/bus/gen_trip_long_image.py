import requests
import sys
import os
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from local_config import amap_key

def get_route_data(city, origin, destination_coord, amap_key):
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
        return None, None, None
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
    return origin_loc, destination_loc, route_resp

def plot_route_image(city, origin, destination_coord, amap_key, output_file='route_map.png'):
    origin_loc, destination_loc, route_resp = get_route_data(city, origin, destination_coord, amap_key)
    if not origin_loc or not destination_loc:
        print('地理编码失败，无法生成图片')
        return
    if not route_resp or route_resp.get('status') != '1' or not route_resp.get('route'):
        print('未找到公交路线')
        return
    transits = route_resp['route'].get('transits', [])
    if not transits:
        print('未找到公交路线')
        return
    transit = transits[0]
    # 起点和终点坐标
    origin_lat, origin_lng = map(float, origin_loc.split(','))
    dest_lat, dest_lng = map(float, destination_loc.split(','))
    plt.figure(figsize=(10, 8))
    plt.scatter(origin_lat, origin_lng, c='green', s=100, label='起点: '+origin)
    plt.scatter(dest_lat, dest_lng, c='red', s=100, label='终点: 管氏翅吧(上地店)')
    # 绘制公交和步行段
    for segment in transit.get('segments', []):
        # 步行段
        walking = segment.get('walking', {})
        if 'steps' in walking:
            for step in walking['steps']:
                polyline = step.get('polyline', '')
                points = [list(map(float, p.split(','))) for p in polyline.split(';') if p]
                if points:
                    x, y = zip(*points)
                    plt.plot(x, y, color='blue', linewidth=2, label='步行')
        # 公交段
        bus = segment.get('bus', {})
        for busline in bus.get('buslines', []):
            polyline = busline.get('polyline', '')
            points = [list(map(float, p.split(','))) for p in polyline.split(';') if p]
            if points:
                x, y = zip(*points)
                plt.plot(x, y, color='orange', linewidth=3, label=busline.get('name'))
            # 标注公交站点
            for stop in [busline.get('departure_stop')] + busline.get('via_stops', []) + [busline.get('arrival_stop')]:
                if stop and 'location' in stop:
                    lat, lng = map(float, stop['location'].split(','))
                    plt.scatter(lat, lng, c='blue', s=50)
                    plt.text(lat, lng, stop.get('name', '公交站'), fontsize=8, color='blue')
    plt.xlabel('经度')
    plt.ylabel('纬度')
    plt.title('公交路线图')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()
    print(f'路线图片已保存为 {output_file}')

if __name__ == '__main__':
    city = '北京'
    origin = '亚信大厦'
    destination_coord = '116.311560,40.035227'
    from local_config import amap_key
    plot_route_image(city, origin, destination_coord, amap_key)
