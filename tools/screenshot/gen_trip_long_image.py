import time
from playwright.sync_api import sync_playwright
from PIL import Image
import os

# 配置
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
# 修改为当前对比页面
HTML_PATH = os.path.join(BASE_DIR, "docs/v0.1/cases/2025_beijing_harbin_yichun_family_trip_v0.4.html")
IMG_PATH = os.path.join(BASE_DIR, "docs/v0.1/cases/2025_beijing_harbin_yichun_family_trip_v0.4_long.png")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    # 模拟手机尺寸
    context = browser.new_context(
        viewport={'width': 430, 'height': 932},
        device_scale_factor=2
    )
    page = context.new_page()
    page.goto('file://' + HTML_PATH)
    
    # 等待页面加载完成
    page.wait_for_load_state('networkidle')
    time.sleep(2) # 额外等待，确保所有动态内容加载

    # 截图
    page.screenshot(path=IMG_PATH, full_page=True)
    
    browser.close()

# 可选：裁剪白边
try:
    img = Image.open(IMG_PATH)
    bbox = img.getbbox()
    if bbox:
        img_cropped = img.crop(bbox)
        img_cropped.save(IMG_PATH)
    print(f"已生成长图：{IMG_PATH}")
except Exception as e:
    print(f"裁剪图片时出错: {e}")
    print(f"长图已生成，但可能未裁剪：{IMG_PATH}")
