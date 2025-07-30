
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, Frame, PageBreak
from reportlab.lib.units import inch

# --- Configuration ---
PDF_FILENAME = "黑龙江全景深度游手册.pdf"
FONT_NAME = "SimSun"
FONT_PATH = "C:/Windows/Fonts/simsun.ttc"  # Common path for SimSun font on Windows

# --- Itinerary Data ---
itinerary = [
    {
        "day": "Day 1: 抵达冰城，初探魅力哈尔滨",
        "date": "2025年8月16日，星期六",
        "summary": "乘坐高铁从北京抵达哈尔滨，入住中央大街酒店后，品尝地道东北菜，下午参观黑龙江省博物馆，感受历史文化，傍晚漫步百年中央大街。",
        "timeline": [
            "12:00 - 抵达哈尔滨西站，乘坐地铁或出租车前往中央大街附近酒店。",
            "13:30 - 酒店办理入住，稍作休整。",
            "14:00 - 午餐：推荐酒店附近的本地菜馆，品尝锅包肉、地三鲜。",
            "15:30 - 前往黑龙江省博物馆（请提前确认开放时间）。",
            "17:30 - 游览结束，返回中央大街。",
            "18:30 - 漫步中央大街，欣赏欧式建筑，品尝马迭尔冰棍。",
            "19:30 - 晚餐：在中央大街解决，或选择俄式西餐体验。",
            "21:00 - 返回酒店休息。"
        ],
        "map_prompt": "地图区域：请在此处插入哈尔滨市区地图，标注出哈尔滨西站、中央大街酒店、省博物馆的位置及交通路线。"
    },
    {
        "day": "Day 2: 江北风光与冰雪奇缘",
        "date": "2025年8月17日，星期日",
        "summary": "上午游览太阳岛，感受自然风光。下午近距离接触东北虎，晚上在冰雪大世界（夏季啤酒节）感受夏日里的冰雪激情。",
        "timeline": [
            "09:00 - 早餐后，通过松花江索道或轮渡前往太阳岛风景区。",
            "12:30 - 在太阳岛或返回江南午餐。",
            "14:00 - 前往东北虎林园，乘坐观光车观察野生东北虎。",
            "16:30 - 游览结束，返回中央大街。",
            "18:00 - 晚餐。",
            "19:30 - 前往冰雪大世界夏季乐园，参与啤酒节等活动。",
            "22:00 - 返回酒店休息。"
        ],
        "map_prompt": "地图区域：请在此处插入哈尔滨江北地图，标注中央大街、太阳岛、东北虎林园、冰雪大世界的位置及交通方式。"
    },
    {
        "day": "Day 3: 前往鹤城，探秘扎龙湿地",
        "date": "2025年8月18日，星期一",
        "summary": "租车自驾前往齐齐哈尔，入住后下午前往扎龙国家级自然保护区，观赏丹顶鹤放飞，晚上品尝地道的齐市烤肉。",
        "timeline": [
            "08:30 - 在哈尔滨办理租车手续，出发前往齐齐哈尔（车程约3.5-4小时）。",
            "12:30 - 抵达齐齐哈尔市区，办理酒店入住。",
            "13:30 - 午餐。",
            "15:00 - 驱车前往扎龙自然保护区（车程约45分钟）。",
            "15:45 - 进入景区，注意丹顶鹤放飞表演时间（通常下午有场次）。",
            "18:00 - 游览结束，返回市区。",
            "19:00 - 晚餐：强烈推荐齐齐哈尔家庭式烤肉。",
            "21:00 - 返回酒店休息。"
        ],
        "map_prompt": "地图区域：请在此处插入哈尔滨至齐齐哈尔，以及齐齐哈尔市区至扎龙保护区的行车路线图。"
    },
    {
        "day": "Day 4: 火山奇景，五大连池地质之旅",
        "date": "2025年8月19日，星期二",
        "summary": "驱车前往世界地质公园——五大连池，探访新期火山群，感受震撼的火山地貌，品尝独特的矿泉水。",
        "timeline": [
            "08:30 - 早餐后，从齐齐哈尔出发，驱车前往五大连池风景区（车程约3.5-4小时）。",
            "12:30 - 抵达五大连池镇，午餐并办理入住。",
            "14:00 - 游览核心景区【黑龙山】，攀登火山，俯瞰火山熔岩台地。",
            "17:00 - 参观【北饮泉】，品尝世界三大冷矿泉之一。",
            "18:30 - 晚餐，品尝矿泉鱼、矿泉豆腐等特色菜。",
            "20:00 - 在小镇漫步，感受宁静的夜晚。"
        ],
        "map_prompt": "地图区域：请在此处插入齐齐哈尔至五大连池的行车路线图，以及五大连池主要景点（如黑龙山、北饮泉）的分布图。"
    },
    {
        "day": "Day 5: 边境风情，漫步黑河",
        "date": "2025年8月20日，星期三",
        "summary": "继续北上，抵达中俄边境城市黑河。漫步黑龙江畔，远眺对岸的俄罗斯城市，感受独特的边境文化。",
        "timeline": [
            "09:00 - 出发前往黑河（车程约3-3.5小时）。",
            "12:30 - 抵达黑河市，午餐并办理酒店入住。",
            "14:30 - 参观【瑷珲历史陈列馆】，了解边疆历史。",
            "16:30 - 前往【黑龙江公园】，沿江边漫步，远眺对岸的俄罗斯布拉戈维申斯克市。",
            "18:00 - 晚餐，可以尝试当地的俄式简餐或东北菜。",
            "19:30 - 逛一逛黑河的夜市或商业街，感受边城夜生活。"
        ],
        "map_prompt": "地图区域：请在此处插入五大连池至黑河的行车路线图，以及黑河市区地图，标注瑷珲、黑龙江公园的位置。"
    },
    {
        "day": "Day 6: 穿行林海，抵达汤旺河",
        "date": "2025年8月21日，星期四",
        "summary": "今天车程较长，途径逊克县，最终抵达伊春的汤旺河林海奇石风景区，入住林区，准备迎接森林的怀抱。",
        "timeline": [
            "08:00 - 早餐后从黑河出发，途径逊克县。",
            "11:30 - 在逊克县或沿途乡镇午餐。",
            "12:30 - 继续驱车前往伊春汤旺河（黑河-逊克约2.5小时，逊克-汤旺河约3.5小时）。",
            "16:30 - 抵达汤旺河镇，办理入住。",
            "17:30 - 在小镇或酒店晚餐，品尝林区特色山野菜。",
            "19:00 - 休息，适应林区宁静的环境，为第二天的游玩储备精力。"
        ],
        "map_prompt": "地图区域：请在此处插入黑河-逊克-汤旺河的行车路线图。"
    },
    {
        "day": "Day 7: 森呼吸，漫步林海奇石",
        "date": "2025年8月22日，星期五",
        "summary": "全天在汤旺河林海奇石风景区内游览，徒步穿行于花岗岩石林与原始红松林之间，享受高负氧离子的“森林浴”。",
        "timeline": [
            "08:30 - 进入汤旺河风景区，开始一天的探索。",
            "09:00 - 建议游览路线：一线天 -> 罗汉龟 -> 龙凤呈祥 -> 增喜龟 -> 南海观音...",
            "12:30 - 在景区内或返回镇上午餐。",
            "14:00 - 下午继续游览未尽的景点，或者选择一条舒适的步道进行徒步。",
            "17:00 - 游览结束，返回酒店。",
            "18:30 - 晚餐，回味一天的森林之旅。",
        ],
        "map_prompt": "地图区域：请在此处插入汤旺河林海奇石风景区的游览路线图。"
    },
    {
        "day": "Day 8: 归途，返回哈尔滨",
        "date": "2025年8月23日，星期六",
        "summary": "在森林的晨光中醒来，上午探访可爱的梅花鹿，之后驱车返回哈尔滨，结束愉快的黑龙江全景深度游。",
        "timeline": [
            "08:30 - 早餐后，从汤旺河出发前往伊春市区方向。",
            "09:30 - 抵达九峰山养心谷景区（鹿苑）。",
            "11:00 - 游览结束，出发返回哈尔滨（车程约4.5-5小时）。",
            "13:00 - 在途中的服务区或城市（如铁力市）午餐。",
            "17:00 - 抵达哈尔滨，根据后续安排（返程火车/飞机或继续停留）前往相应地点。",
            "18:00 - 行程结束。"
        ],
        "map_prompt": "地图区域：请在此处插入汤旺河-伊春市区（鹿苑）-哈尔滨的返程行车路线图。"
    }
]

# --- PDF Generation ---
def create_travel_handbook():
    """Generates the travel handbook PDF."""
    
    # Check if font file exists
    if not os.path.exists(FONT_PATH):
        print(f"错误：找不到字体文件 {FONT_PATH}。请检查路径是否正确。")
        print("将使用默认字体，中文可能无法显示。")
        # Fallback to a default font if SimSun is not found
        font_to_register = "Helvetica"
    else:
        pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
        font_to_register = FONT_NAME

    # Create canvas
    output_path = os.path.join("materials", PDF_FILENAME)
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # Styles
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleN.fontName = font_to_register
    styleN.fontSize = 13 # Increased base font size
    styleN.leading = 20 # Increased line spacing

    # --- Title Page ---
    c.setFont(font_to_register, 26)
    c.drawCentredString(width / 2.0, height - 2 * inch, "黑龙江全景深度游")
    c.setFont(font_to_register, 20)
    c.drawCentredString(width / 2.0, height - 2.5 * inch, "一家三口的夏日冒险")
    c.setFont(font_to_register, 14)
    c.drawCentredString(width / 2.0, 1.5 * inch, "旅行时间：2025年8月16日 - 2025年8月23日")
    c.drawCentredString(width / 2.0, 1.2 * inch, "旅行手册 | V1.0")
    c.showPage()

    # --- Itinerary Pages ---
    for i, item in enumerate(itinerary):
        # Add background image with transparency if it exists
        bg_image_path = os.path.join("materials", "background.jpg")
        if os.path.exists(bg_image_path):
            try:
                # Draw the background image first
                c.drawImage(bg_image_path, 0, 0, width=width, height=height, preserveAspectRatio=False)
                # Then, draw a semi-transparent white rectangle over it to fade it out
                # The 'alpha' parameter controls transparency (0=transparent, 1=opaque)
                c.setFillColorRGB(1, 1, 1, alpha=0.8) # 80% opaque white, making the image look faded
                c.rect(0, 0, width, height, fill=1, stroke=0)
                # Reset fill color to black for the text
                c.setFillColorRGB(0, 0, 0)
            except Exception as e:
                print(f"无法加载背景图片: {e}")

        # Title
        c.setFont(font_to_register, 20)
        c.drawString(inch, height - 1 * inch, item["day"])
        
        # Date
        c.setFont(font_to_register, 14)
        c.drawString(inch, height - 1.3 * inch, item["date"])
        
        # Summary
        summary_p = Paragraph(f"<b>当日总览:</b> {item['summary']}", styleN)
        summary_frame = Frame(inch, height - 2.5 * inch, width - 2 * inch, 1.2 * inch, showBoundary=0)
        summary_frame.addFromList([summary_p], c)

        # Timeline
        c.setFont(font_to_register, 16)
        c.drawString(inch, height - 2.8 * inch, "详细时间线:")
        
        timeline_text = "<br/>".join(item["timeline"])
        timeline_p = Paragraph(timeline_text, styleN)
        timeline_frame = Frame(inch, height - 5.5 * inch, width - 2 * inch, 2.5 * inch, showBoundary=0)
        timeline_frame.addFromList([timeline_p], c)

        # Map Placeholder
        map_image_path = os.path.join("materials", f"map_day{i+1}.jpg")
        if os.path.exists(map_image_path):
            try:
                # Use a helper function to draw the image centered and scaled in a wider box
                draw_image_in_box(c, map_image_path, 0.5 * inch, 1 * inch, width - 1 * inch, 3 * inch)
            except Exception as e:
                print(f"无法加载地图图片 {map_image_path}: {e}")
        else:
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.rect(0.5 * inch, 1 * inch, width - 1 * inch, 3 * inch, stroke=1, fill=0)
            c.setFont(font_to_register, 12)
            c.setFillColorRGB(0.5, 0.5, 0.5)
            map_prompt_p = Paragraph(item["map_prompt"], styleN)
            map_prompt_frame = Frame(0.7 * inch, 1 * inch, width - 1.4 * inch, 3 * inch, showBoundary=0)
            map_prompt_frame.addFromList([map_prompt_p], c)
            c.setFillColorRGB(0, 0, 0) # Reset color
        
        c.showPage()

    # Save the PDF
    c.save()
    print(f"成功！旅行手册已生成：{output_path}")
    print("请注意：手册中的地图和背景图片是预留的占位符。")
    print("请将您自己的图片替换掉 materials 文件夹中的 background.jpg 和 map_dayX.jpg 文件，然后重新运行此脚本。")

def draw_image_in_box(canvas, img_path, x, y, box_w, box_h):
    """
    Draws an image, scaling it to fit within a bounding box while preserving aspect ratio,
    and centering it within that box.
    """
    from reportlab.lib.utils import ImageReader
    
    img = ImageReader(img_path)
    img_w, img_h = img.getSize()
    
    # Calculate the scaling factor to fit the image in the box
    scale_w = box_w / img_w
    scale_h = box_h / img_h
    scale = min(scale_w, scale_h)
    
    # New dimensions of the image
    new_w = img_w * scale
    new_h = img_h * scale
    
    # Calculate position to center the image in the box
    new_x = x + (box_w - new_w) / 2
    new_y = y + (box_h - new_h) / 2
    
    canvas.drawImage(img_path, new_x, new_y, width=new_w, height=new_h)

if __name__ == "__main__":
    create_travel_handbook()
