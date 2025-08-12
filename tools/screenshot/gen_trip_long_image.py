"""生成移动端长图截图（支持 v0.5 H5 页面时间轴与卡片展开）

用法示例：
  python tools/screenshot/gen_trip_long_image.py \
    --html docs/v0.1/cases/2025_beijing_harbin_yichun_family_trip_v0.5.html \
    --out docs/v0.1/cases/2025_beijing_harbin_yichun_family_trip_v0.5_long.png \
    --width 430 --scale 2 --wait 3 --expand --theme light

特点：
1. 自动等待页面动态渲染（md -> DOM -> timeline/callouts 注入）。
2. 可选展开所有 <details>（便于长图完整呈现）。
3. 支持切换暗色 / 亮色主题截图。
4. 基础裁剪去除透明或纯色边缘。
"""

import time
import argparse
from playwright.sync_api import sync_playwright
from PIL import Image
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

def parse_args():
    parser = argparse.ArgumentParser(description="生成行程 H5 页面长图")
    parser.add_argument('--html', default='docs/v0.1/cases/2025_beijing_harbin_yichun_family_trip_v0.5.html', help='HTML 文件相对或绝对路径')
    parser.add_argument('--out', default='docs/v0.1/cases/2025_beijing_harbin_yichun_family_trip_v0.5_long.png', help='输出 PNG 路径')
    parser.add_argument('--width', type=int, default=430, help='视口宽度(px)')
    parser.add_argument('--height', type=int, default=932, help='视口高度(px)')
    parser.add_argument('--scale', type=float, default=2, help='设备像素比(device_scale_factor)')
    parser.add_argument('--wait', type=float, default=2.5, help='初始加载额外等待秒数')
    parser.add_argument('--expand', action='store_true', help='展开所有 details')
    parser.add_argument('--theme', choices=['light','dark'], default='light', help='主题模式')
    parser.add_argument('--no-crop', action='store_true', help='不执行裁剪')
    return parser.parse_args()

def ensure_path(path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.join(BASE_DIR, path)

def crop_image(path: str):
    try:
        img = Image.open(path)
        bbox = img.getbbox()
        if bbox:
            img_cropped = img.crop(bbox)
            img_cropped.save(path)
        print(f"已生成长图：{path}")
    except Exception as e:
        print(f"裁剪图片时出错: {e}\n长图已生成但未裁剪：{path}")

def main():
    args = parse_args()
    html_path = ensure_path(args.html)
    out_path = ensure_path(args.out)
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"HTML 不存在: {html_path}")

    with sync_playwright() as p:
        # 优先尝试使用系统已安装 Edge / Chrome，避免下载内置浏览器
        browser = None
        for channel in ('msedge','chrome'):
            try:
                browser = p.chromium.launch(channel=channel, headless=True)
                print(f"使用系统浏览器 channel: {channel}")
                break
            except Exception as e:
                print(f"尝试 channel={channel} 失败：{e}")
        if not browser:
            print("回退到内置 chromium (需已安装 playwright 浏览器内核)")
            browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': args.width, 'height': args.height},
            device_scale_factor=args.scale,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
        )
        page = context.new_page()
        page.goto('file://' + html_path)

        # 等待网络静止
        page.wait_for_load_state('networkidle')
        time.sleep(args.wait)

        # 主题设置
        if args.theme == 'dark':
            page.evaluate("document.documentElement.classList.add('dark');")

        # 等待自定义渲染（timeline / callouts）出现
        try:
            page.wait_for_selector('.timeline .tl-item', timeout=4000)
        except Exception:
            print('警告：未检测到 .timeline，尝试手动触发 render() 或继续...')
            try:
                page.evaluate("if(window.render) render();")
                page.wait_for_selector('.timeline .tl-item', timeout=3000)
            except Exception:
                print('仍未检测到时间轴，可能页面为旧版本。')

        # 展开全部 details 以完整呈现
        if args.expand:
            page.evaluate("document.querySelectorAll('details').forEach(d=>d.open=true)")
            # 展开后等待布局稳定
            time.sleep(0.5)

        # 滚动到底部一次，确保懒加载（若有）触发
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(0.3)
        page.evaluate("window.scrollTo(0,0)")

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        page.screenshot(path=out_path, full_page=True)
        browser.close()

    if not args.no_crop:
        crop_image(out_path)
    else:
        print(f"已生成长图（未裁剪）：{out_path}")

if __name__ == '__main__':
    main()
