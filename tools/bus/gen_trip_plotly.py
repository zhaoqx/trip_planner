import plotly.graph_objects as go
import plotly.io as pio
import os
import sys
import json

# 用法：python gen_trip_plotly.py route.json output.html
# route.json 格式参考 generate_route_map.py 的数据结构

def load_route_data(route_json_path):
    with open(route_json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def plot_route(route_data, output_html):
    # 解析数据
    points = []
    names = []
    colors = []
    for seg in route_data.get('segments', []):
        for idx, stop in enumerate(seg.get('stops', [])):
            points.append((stop['lat'], stop['lng']))
            names.append(stop['name'])
            if seg['type'] == 'bus':
                colors.append('blue')
            elif seg['type'] == 'walk':
                colors.append('green')
            else:
                colors.append('gray')
    lats = [p[0] for p in points]
    lngs = [p[1] for p in points]

    # 创建图形
    fig = go.Figure()
    fig.add_trace(go.Scattermapbox(
        lat=lats,
        lon=lngs,
        mode='markers+lines',
        marker=dict(size=12, color=colors),
        text=names,
        hoverinfo='text',
        line=dict(width=4, color='blue'),
    ))
    # 标注起点终点
    if points:
        fig.add_trace(go.Scattermapbox(
            lat=[points[0][0]],
            lon=[points[0][1]],
            mode='markers',
            marker=dict(size=16, color='red'),
            text=['起点'],
            hoverinfo='text',
        ))
        fig.add_trace(go.Scattermapbox(
            lat=[points[-1][0]],
            lon=[points[-1][1]],
            mode='markers',
            marker=dict(size=16, color='orange'),
            text=['终点'],
            hoverinfo='text',
        ))
    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_zoom=12,
        mapbox_center={"lat": points[0][0] if points else 39.9, "lon": points[0][1] if points else 116.4},
        margin={"r":0,"t":0,"l":0,"b":0},
        font=dict(family="Microsoft YaHei, SimHei, Arial", size=16),
    )
    # 输出为html
    pio.write_html(fig, output_html, auto_open=False)
    print(f"已生成可视化地图: {output_html}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python gen_trip_plotly.py route.json output.html")
        sys.exit(1)
    route_json_path = sys.argv[1]
    output_html = sys.argv[2]
    route_data = load_route_data(route_json_path)
    plot_route(route_data, output_html)
