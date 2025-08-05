
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
        "summary": "乘坐高铁从北京抵达哈尔滨，入住中央大街酒店后，品尝地道东北菜，下午参观黑龙江省博物馆，感受历史文化，傍晚漫步百年中央大街。<br/><b>住宿：</b> 哈尔滨中央大街美仑美奂酒店，江景家庭房，2224.77元/2晚。<br/><b>交通：</b> 高铁G901，北京朝阳-哈尔滨西，8:00-12:33，1500元。",
        "timeline": [
            "12:30 - 抵达哈尔滨西站，乘坐地铁或出租车前往中央大街附近酒店。",
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
        "day": "Day 2: 江北风光与清凉夏趣",
        "date": "2025年8月17日，星期日",
        "summary": "上午游览太阳岛，感受松花江畔的自然风光与清凉气息。下午近距离接触东北虎，傍晚可参与夏季啤酒节等特色活动，享受东北夏日的惬意与活力。<br/><b>住宿：</b> 哈尔滨中央大街美仑美奂酒店，江景家庭房，2224.77元/2晚。<br/><b>交通：</b> 市内交通自理。",
        "timeline": [
            "09:00 - 早餐后，通过松花江索道或轮渡前往太阳岛风景区，感受江风与绿荫。",
            "12:30 - 在太阳岛或返回江南午餐，推荐清爽东北菜。",
            "14:00 - 前往东北虎林园，乘坐观光车观察野生东北虎。",
            "16:30 - 游览结束，返回中央大街。",
            "18:00 - 晚餐，体验夏季特色美食。",
            "19:30 - 可前往夏季乐园或啤酒节，参与清凉活动，感受哈尔滨夏夜的活力。",
            "22:00 - 返回酒店休息。"
        ],
        "map_prompt": "地图区域：请在此处插入哈尔滨江北地图，标注中央大街、太阳岛、东北虎林园、夏季乐园的位置及交通方式。"
    },
    {
        "day": "Day 3: 前往鹤城，探秘扎龙湿地",
        "date": "2025年8月18日，星期一",
        "summary": "租车自驾前往齐齐哈尔，入住后下午前往扎龙国家级自然保护区，观赏丹顶鹤放飞，晚上品尝地道的齐市烤肉。<br/><b>住宿：</b> 全季齐齐哈尔卜奎大街解放门酒店，家庭房，379.70元。<br/><b>交通：</b> 租车自驾，哈尔滨-齐齐哈尔，费用约3800元（待定，含后续行程）。",
        "timeline": [
            "08:00 - 高铁站附近租车，出发前往齐齐哈尔（车程约3.5-4小时）。",
            "12:00 - 抵达齐齐哈尔市区，办理酒店入住。",
            "12:30 - 午餐。",
            "13:30 - 驱车前往扎龙自然保护区（车程约45分钟）。",
            "14:15 - 进入景区，观赏丹顶鹤放飞表演（下午场次）。",
            "17:00 - 游览结束，返回市区。",
            "18:00 - 晚餐：强烈推荐齐齐哈尔家庭式烤肉。",
            "20:00 - 返回酒店休息。"
        ],
        "map_prompt": "地图区域：请在此处插入哈尔滨至齐齐哈尔，以及齐齐哈尔市区至扎龙保护区的行车路线图。"
    },
    {
        "day": "Day 4: 火山奇景，五大连池地质之旅",
        "date": "2025年8月19日，星期二",
        "summary": "驱车前往世界地质公园——五大连池，探访新期火山群，感受震撼的火山地貌，品尝独特的矿泉水。<br/><b>住宿：</b> 汉庭五大连池市政府酒店，套房，483.65元。<br/><b>交通：</b> 租车自驾，齐齐哈尔-五大连池。",
        "timeline": [
            "08:00 - 早餐后，驱车前往五大连池风景区（车程约3.5-4小时）。",
            "11:30 - 抵达五大连池镇，午餐并办理入住。",
            "13:00 - 游览核心景区【黑龙山】，攀登火山，俯瞰火山熔岩台地。",
            "16:00 - 参观【北饮泉】，品尝世界三大冷矿泉之一。",
            "17:30 - 晚餐，品尝矿泉鱼、矿泉豆腐等特色菜。",
            "19:00 - 在小镇漫步，感受宁静的夜晚。"
        ],
        "map_prompt": "地图区域：请在此处插入齐齐哈尔至五大连池的行车路线图，以及五大连池主要景点（如黑龙山、北饮泉）的分布图。"
    },
    {
        "day": "Day 5: 边境风情，漫步黑河",
        "date": "2025年8月20日，星期三",
        "summary": "继续北上，抵达中俄边境城市黑河。漫步黑龙江畔，远眺对岸的俄罗斯城市，感受独特的边境文化。<br/><b>住宿：</b> 汉庭黑河中央步行街酒店，套房，350元。<br/><b>交通：</b> 租车自驾，五大连池-黑河。",
        "timeline": [
            "08:00 - 早餐后，驱车前往黑河（车程约3-3.5小时）。",
            "11:30 - 抵达黑河市，午餐并办理酒店入住。",
            "13:30 - 参观【瑷珲历史陈列馆】，了解边疆历史。",
            "15:30 - 前往【黑龙江公园】，沿江边漫步，远眺对岸的俄罗斯布拉戈维申斯克市。",
            "17:00 - 晚餐，可以尝试当地的俄式简餐或东北菜。",
            "18:30 - 逛一逛黑河的夜市或商业街，感受边城夜生活。"
        ],
        "map_prompt": "地图区域：请在此处插入五大连池至黑河的行车路线图，以及黑河市区地图，标注瑷珲、黑龙江公园的位置。"
    },
    {
        "day": "Day 6: 穿行林海，抵达汤旺河",
        "date": "2025年8月21日，星期四",
        "summary": "今天车程较长，途径逊克县，最终抵达伊春的汤旺河林海奇石风景区，入住林区，准备迎接森林的怀抱。<br/><b>住宿：</b> 伊春待定，待定，待定。<br/><b>交通：</b> 租车自驾，黑河-伊春。",
        "timeline": [
            "08:00 - 早餐后从黑河出发，途径逊克县（约2.5小时）。",
            "10:30 - 在逊克县或沿途乡镇午餐。",
            "11:30 - 继续驱车前往伊春汤旺河（约3.5小时）。",
            "15:00 - 抵达汤旺河镇，办理入住。",
            "16:00 - 在小镇或酒店晚餐，品尝林区特色山野菜。",
            "17:30 - 休息，适应林区宁静的环境，为第二天的游玩储备精力。"
        ],
        "map_prompt": "地图区域：请在此处插入黑河-逊克-汤旺河的行车路线图。"
    },
    {
        "day": "Day 7: 森呼吸，漫步林海奇石",
        "date": "2025年8月22日，星期五",
        "summary": "全天在汤旺河林海奇石风景区内游览，徒步穿行于花岗岩石林与原始红松林之间，享受高负氧离子的“森林浴”。<br/><b>住宿：</b> 伊春待定，待定，待定。<br/><b>交通：</b> 市内交通自理。",
        "timeline": [
            "08:30 - 进入汤旺河风景区，开始一天的探索。",
            "09:00 - 建议游览路线：一线天 -> 罗汉龟 -> 龙凤呈祥 -> 增喜龟 -> 南海观音...",
            "12:30 - 在景区内或返回镇上午餐。",
            "14:00 - 下午前往上甘岭溪水景区，体验溪水清凉与森林风光。",
            "16:30 - 返回汤旺河或继续游览未尽景点。",
            "18:30 - 晚餐，回味一天的森林与溪水之旅。",
        ],
        "map_prompt": "地图区域：请在此处插入汤旺河林海奇石风景区的游览路线图。"
    },
    {
        "day": "Day 8: 归途，返回哈尔滨，夜游美食",
        "date": "2025年8月23日，星期六",
        "summary": "在森林的晨光中醒来，上午探访可爱的梅花鹿，之后驱车返回哈尔滨，傍晚入住西站西广场漫心酒店。晚上可前往中央大街附近品尝特色餐饮（如老昌春饼、马迭尔冷饮、华梅西餐厅），或体验哈尔滨本地酒吧（推荐：果戈里大街的精酿酒吧、中央大街的俄式酒吧）。<br/><b>住宿：</b> 哈尔滨西站西广场漫心酒店，心享豪华家庭房，428.27元。<br/><b>交通：</b> 租车自驾，伊春-哈尔滨。",
        "timeline": [
            "08:00 - 早餐后，从汤旺河出发前往伊春市区方向（约1.5小时）。",
            "09:30 - 抵达九峰山养心谷景区（鹿苑）。",
            "11:00 - 游览结束，驱车返回哈尔滨（约4.5小时）。",
            "13:30 - 在途中的服务区或城市（如铁力市）午餐。",
            "17:00 - 抵达哈尔滨，入住西站西广场漫心酒店。",
            "18:30 - 前往中央大街或附近餐厅品尝特色美食。",
            "20:00 - 推荐体验果戈里大街精酿酒吧或俄式酒吧，感受哈尔滨夜生活。",
            "22:00 - 返回酒店休息。"
        ],
        "map_prompt": "地图区域：请在此处插入汤旺河-伊春市区（鹿苑）-哈尔滨的返程行车路线图，以及中央大街、果戈里大街酒吧推荐点。"
    },
    {
        "day": "Day 9: 返程，北京",
        "date": "2025年8月24日，星期日",
        "summary": "早餐后前往哈尔滨西站，乘坐高铁返回北京，结束本次黑龙江深度游。<br/><b>交通：</b> 高铁G906，哈尔滨西-北京朝阳，9:52-14:26，1500元。",
        "timeline": [
            "08:00 - 酒店早餐，收拾行李。",
            "09:00 - 前往哈尔滨西站。",
            "09:52 - 乘坐高铁G906返回北京。",
            "14:26 - 抵达北京，行程圆满结束。"
        ],
        "map_prompt": "地图区域：请在此处插入哈尔滨西站至北京的高铁路线图。"
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

    # --- 行程概览图表 ---
    overview_data = [
        ["日期", "城市/区域", "主要景点/活动", "住宿", "交通"],
        ["8.16", "哈尔滨", "中央大街、博物馆", "美仑美奂酒店", "高铁G901"],
        ["8.17", "哈尔滨", "太阳岛、虎林园、夏季乐园", "美仑美奂酒店", "市内交通"],
        ["8.18", "齐齐哈尔", "扎龙湿地", "全季酒店", "租车自驾"],
        ["8.19", "五大连池", "黑龙山、北饮泉", "汉庭酒店", "租车自驾"],
        ["8.20", "黑河", "瑷珲、黑龙江公园", "汉庭酒店", "租车自驾"],
        ["8.21", "伊春（汤旺河）", "汤旺河林海奇石", "待定", "租车自驾"],
        ["8.22", "伊春（汤旺河/上甘岭）", "林海奇石、上甘岭溪水", "待定", "市内交通"],
        ["8.23", "哈尔滨", "九峰山鹿苑、中央大街美食、果戈里酒吧", "漫心酒店", "租车自驾"],
        ["8.24", "哈尔滨-北京", "返程高铁G906", "无", "高铁G906"],
    ]
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    overview_table = Table(overview_data, colWidths=[1.1*inch, 1.5*inch, 2.2*inch, 1.5*inch, 1.5*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), font_to_register),
        ('FONTSIZE', (0,0), (-1,-1), 12),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    overview_frame = Frame(inch, height - 6.5 * inch, width - 2 * inch, 5 * inch, showBoundary=0)
    overview_frame.addFromList([overview_table], c)
    c.showPage()

    # --- 交通信息页 ---
    c.setFont(font_to_register, 20)
    c.drawCentredString(width / 2.0, height - 1 * inch, "交通安排一览")
    traffic_data = [
        ["日期/区间", "交通方式", "时间/车次", "费用"],
        ["8.16 北京-哈尔滨", "高铁 G901", "8:00-12:33", "1500元"],
        ["8.18-8.23", "租车", "齐齐哈尔-五大连池-黑河-伊春", "约3800元（待定）"],
        ["8.24 哈尔滨-北京", "高铁 G906", "9:52-14:26", "1500元"],
    ]
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    traffic_table = Table(traffic_data, colWidths=[2*inch, 1.5*inch, 2*inch, 1.2*inch])
    traffic_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), font_to_register),
        ('FONTSIZE', (0,0), (-1,-1), 13),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    traffic_frame = Frame(inch, height - 5.5 * inch, width - 2 * inch, 4 * inch, showBoundary=0)
    traffic_frame.addFromList([traffic_table], c)
    c.showPage()
    # --- 住宿信息页 ---
    c.setFont(font_to_register, 20)
    c.drawCentredString(width / 2.0, height - 1 * inch, "住宿安排一览")
    # 住宿信息表格内容
    lodging_data = [
        ["日期", "酒店名称", "房型", "价格"],
        ["8.16 - 8.18", "哈尔滨中央大街美仑美奂酒店", "江景家庭房", "2224.77元"],
        ["8.18 - 8.19", "全季齐齐哈尔卜奎大街解放门酒店", "家庭房", "379.70元"],
        ["8.19 - 8.20", "汉庭五大连池市政府酒店", "套房", "483.65元"],
        ["8.20 - 8.21", "汉庭黑河中央步行街酒店", "套房", "350元"],
        ["8.21 - 8.23", "伊春待定", "待定", "待定"],
        ["8.23 - 8.24", "哈尔滨西站西广场漫心酒店", "心享豪华家庭房", "428.27元"],
    ]
    from reportlab.platypus import Table, TableStyle
    from reportlab.lib import colors
    table = Table(lodging_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), font_to_register),
        ('FONTSIZE', (0,0), (-1,-1), 13),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    # 表格位置
    frame = Frame(inch, height - 5.5 * inch, width - 2 * inch, 4 * inch, showBoundary=0)
    frame.addFromList([table], c)
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
