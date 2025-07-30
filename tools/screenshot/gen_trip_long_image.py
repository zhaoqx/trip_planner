import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from PIL import Image
import os

# 配置
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
# 修改为当前对比页面
HTML_PATH = os.path.join(BASE_DIR, "docs/v0.1/cases/2025_harbin_yichun_wudalianchi_compare.html")
IMG_PATH = os.path.join(BASE_DIR, "docs/v0.1/cases/2025_harbin_yichun_wudalianchi_compare_long.png")
EDGE_DRIVER_PATH = os.path.join(os.path.dirname(__file__), "msedgedriver.exe")

edge_options = Options()
edge_options.add_argument('--headless')
edge_options.add_argument('--disable-gpu')
# 适配更长页面
edge_options.add_argument('--window-size=430,4000')
edge_options.add_argument('--force-device-scale-factor=2')

service = Service(EDGE_DRIVER_PATH)
browser = webdriver.Edge(service=service, options=edge_options)
browser.get('file://' + HTML_PATH)
time.sleep(3)

# 获取页面高度，调整窗口高度以截全图
scroll_height = browser.execute_script('return document.body.scrollHeight')
browser.set_window_size(430, scroll_height)
time.sleep(2)

# 截图

browser.save_screenshot(IMG_PATH)
browser.quit()

# 可选：裁剪白边
bbox = img.getbbox()

img = Image.open(IMG_PATH)
bbox = img.getbbox()
img_cropped = img.crop(bbox)
img_cropped.save(IMG_PATH)

print(f"已生成长图：{IMG_PATH}")
