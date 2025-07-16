import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from PIL import Image
import os

# 配置
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
HTML_PATH = os.path.join(BASE_DIR, "docs/v0.1/cases/2025_beijing_harbin_yichun_family_trip_v0.3.html")
IMG_PATH = os.path.join(BASE_DIR, "docs/v0.1/cases/2025_beijing_harbin_yichun_family_trip_v0.3_long.png")
EDGE_DRIVER_PATH = os.path.join(os.path.dirname(__file__), "msedgedriver.exe")

edge_options = Options()
edge_options.add_argument('--headless')
edge_options.add_argument('--disable-gpu')
edge_options.add_argument('--window-size=430,2000')
edge_options.add_argument('--force-device-scale-factor=2')

service = Service(EDGE_DRIVER_PATH)
browser = webdriver.Edge(service=service, options=edge_options)
browser.get('file://' + HTML_PATH)
time.sleep(2)

# 获取页面高度，调整窗口高度以截全图
scroll_height = browser.execute_script('return document.body.scrollHeight')
browser.set_window_size(430, scroll_height)
time.sleep(1)

# 截图
browser.save_screenshot(IMG_PATH)
browser.quit()

# 可选：裁剪白边
img = Image.open(IMG_PATH)
bbox = img.getbbox()
img_cropped = img.crop(bbox)
img_cropped.save(IMG_PATH)

print(f"已生成长图：{IMG_PATH}")
