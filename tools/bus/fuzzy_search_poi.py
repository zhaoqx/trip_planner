import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from local_config import amap_key

def fuzzy_search_poi(city, keywords, amap_key):
    url = 'https://restapi.amap.com/v3/place/text'
    params = {
        'city': city,
        'keywords': keywords,
        'key': amap_key,
        'offset': 5
    }
    resp = requests.get(url, params=params).json()
    print(f"POI模糊搜索接口返回({keywords}):", resp)
    pois = resp.get('pois', [])
    if not pois:
        print('未找到相关POI')
        return
    for i, poi in enumerate(pois):
        print(f"{i+1}. 名称: {poi.get('name')}, 地址: {poi.get('address')}, 坐标: {poi.get('location')}")

if __name__ == '__main__':
    city = '北京'
    keywords = '管氏翅吧(上地店)'
    fuzzy_search_poi(city, keywords, amap_key)
