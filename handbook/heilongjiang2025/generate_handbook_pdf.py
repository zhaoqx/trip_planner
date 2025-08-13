"""Enhanced PDF generation script with multi-page overview, landscape map page, colorful tables, icons, and improved line wrapping."""

import os
import re
from pathlib import Path
from typing import List, Dict

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph, Table, TableStyle, PageBreak, Spacer, Image, BaseDocTemplate,
    Frame, PageTemplate, NextPageTemplate, Flowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

BASE_DIR = Path(__file__).parent
TRIP_MD = BASE_DIR / 'trip_plan.md'
OUTPUT_PDF = BASE_DIR / '《2025黑龙江旅行手册》.pdf'

FONT_PATHS = [
    'C:/Windows/Fonts/msyh.ttc',  # 微软雅黑
    'C:/Windows/Fonts/simsun.ttc',
    'C:/Windows/Fonts/simhei.ttf'
]
FONT_NAME = 'HandbookFont'

SPOT_INTRO: Dict[str, str] = {
    '中央大街': '始建 1900 年前后欧式建筑群，被誉为“东方小巴黎”，晚间灯光层次好。',
    '黑龙江省博物馆': '自然与人文兼有，猛犸象化石/东北虎标本必看，周一闭馆。',
    '圣·索菲亚教堂': '拜占庭风格地标，外观拍摄 17:00 金色光，内部多媒体展示。',
    '太阳岛': '江心绿洲，骑行/步行清凉，午后暴晒需注意补水。',
    '东北虎林园': '乘笼车近距离观察东北虎，禁止敲打车窗与投喂。',
    '扎龙湿地': '丹顶鹤栖息地，放飞表演需提前抵达，长焦与望远镜增体验。',
    '黑龙山': '新期火山，环形火山口+熔岩台地清晰，碎石坡注意鞋底抓地力。',
    '北饮泉': '冷矿泉现场直饮，携洁净瓶取水不久置高温环境。',
    '瑷珲历史陈列馆': '了解中俄边界条约及边城历史背景，增强黑河人文深度。',
    '黑龙江公园': '界河江畔，日落斜光拍对岸城市剪影佳。',
    '茅兰沟': '峡谷溪流+瀑布复合景观，雨后路滑减速行走。',
    '汤旺河林海奇石': '花岗岩石林奇异造型+森林步道结合，适度删支线防疲劳。',
    '五营国家森林公园': '红松母树林生态完整，森林浴呼吸节奏放慢。',
    '九峰山养心谷': '梅花鹿互动与静心步道，早场光线柔和鹿更活跃。'
}

# ---------- Styles ----------
SECTION_TITLE = ParagraphStyle(
    'SectionTitle', fontName=FONT_NAME, fontSize=22, leading=28,
    textColor=colors.HexColor('#0B3954'), spaceAfter=10)
SUBTITLE = ParagraphStyle(
    'Subtitle', fontName=FONT_NAME, fontSize=14, leading=20,
    textColor=colors.HexColor('#1565C0'), spaceAfter=6)
BODY = ParagraphStyle(
    'Body', fontName=FONT_NAME, fontSize=10.5, leading=15.2, spaceAfter=3)
SMALL = ParagraphStyle(
    'Small', fontName=FONT_NAME, fontSize=9, leading=12, textColor=colors.HexColor('#455A64'))
QUOTE = ParagraphStyle(
    'Quote', parent=BODY, backColor=colors.HexColor('#E3F2FD'),
    borderColor=colors.HexColor('#64B5F6'), borderWidth=0.6, borderPadding=5,
    leftIndent=4, rightIndent=4, spaceBefore=4, spaceAfter=8)


def register_font():
    for p in FONT_PATHS:
        if os.path.exists(p):
            try:
                pdfmetrics.registerFont(TTFont(FONT_NAME, p))
                return
            except Exception:
                continue
    raise FileNotFoundError('未找到中文字体，请调整 FONT_PATHS。')


def parse_trip_markdown(md: str) -> List[Dict]:
    days = []
    current = None
    for line in md.splitlines():
        if line.startswith('### Day '):
            if current:
                days.append(current)
            current = {'title': line.replace('### ', '').strip(), 'lines': []}
        elif current is not None:
            current['lines'].append(line)
    if current:
        days.append(current)
    # enrich
    for d in days:
        block = '\n'.join(d['lines'])
        m = re.search(r'\*\*(\d{4}年[^*]+)\*\*', block)
        if m:
            d['date'] = m.group(1)
        m2 = re.search(r'当日总览:.*?\n\*\*(.*?)\*\*', block)
        # fallback simpler pattern
        if not m2:
            m2 = re.search(r'当日总览.*?\n', block)
        # timeline
        timeline = []
        capture = False
        for l in d['lines']:
            if '详细时间线' in l:
                capture = True
                continue
            if capture:
                if l.startswith('**优化') or l.startswith('---') or l.startswith('### Day'):
                    break
                if l.strip().startswith('- '):
                    timeline.append(l.strip()[2:])
        d['timeline'] = timeline
        # summary simpler
        ms = re.search(r'当日总览:\*\*? ?([^\n]+)', block)
        if ms:
            d['summary'] = ms.group(1).strip()
    return days


def split_overview_rows(rows: List[List[str]], max_rows: int = 15) -> List[List[List[str]]]:
    pages = []
    header, data = rows[0], rows[1:]
    for i in range(0, len(data), max_rows):
        pages.append([header] + data[i:i+max_rows])
    return pages


def build_overview_pages(days: List[Dict]) -> List:
    rows = [['日程', '日期', '亮点', '提要']]
    for d in days:
        summary = d.get('summary', '')
        tags = [k for k in ['火山', '湿地', '森林', '城市', '文化', '边境', '徒步', '自驾'] if k in summary]
        rows.append([d.get('title',''), d.get('date',''), ' / '.join(tags) if tags else '—', summary[:140] + ('...' if len(summary)>140 else '')])
    tablesets = split_overview_rows(rows, max_rows=11)
    flow = []
    for idx, tbl_rows in enumerate(tablesets):
        flow.append(Paragraph(f'行程概览表（第 {idx+1}/{len(tablesets)} 页）', SUBTITLE))
        table = Table(tbl_rows, colWidths=[38*mm, 32*mm, 18*mm, 87*mm])
        table.setStyle(TableStyle([
            ('FONTNAME',(0,0),(-1,-1),FONT_NAME),
            ('FONTSIZE',(0,0),(-1,0),10),
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#BBDEFB')),
            ('TEXTCOLOR',(0,0),(-1,0),colors.HexColor('#0D47A1')),
            ('GRID',(0,0),(-1,-1),0.3,colors.HexColor('#90CAF9')),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, colors.HexColor('#E3F2FD')]),
            ('ALIGN',(0,0),(-1,0),'CENTER'),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('FONTSIZE',(0,1),(-1,-1),9)
        ]))
        flow.append(table)
        flow.append(PageBreak())
    return flow


def build_timeline_table(timeline: List[str]):
    if not timeline:
        return Paragraph('（无时间线数据）', BODY)
    data = [['时间', '活动 / 说明']]
    pat = re.compile(r'^(\d{1,2}:\d{2})[\s\-—–]*(.*)')
    for row in timeline:
        m = pat.match(row)
        if m:
            t, desc = m.group(1), m.group(2).strip()
        else:
            t, desc = '—', row
        data.append([t, desc])
    table = Table(data, colWidths=[20*mm, 150*mm])
    table.setStyle(TableStyle([
        ('FONTNAME',(0,0),(-1,-1),FONT_NAME),
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#C8E6C9')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.HexColor('#1B5E20')),
        ('GRID',(0,0),(-1,-1),0.25,colors.HexColor('#A5D6A7')),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, colors.HexColor('#F1F8E9')]),
        ('FONTSIZE',(0,0),(-1,0),10),
        ('FONTSIZE',(0,1),(-1,-1),9.2),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE')
    ]))
    return table


def spot_reference(text: str):
    spots = [s for s in SPOT_INTRO if s in text]
    if not spots:
        return Paragraph('（未匹配到景点关键字）', QUOTE)
    lines = [f'📍 <b>{s}</b>：{SPOT_INTRO[s]}' for s in spots]
    return Paragraph('<br/>'.join(lines), QUOTE)


def footer(canvas, doc):
    canvas.setFont(FONT_NAME, 8)
    canvas.setFillColor(colors.HexColor('#607D8B'))
    canvas.drawRightString(doc.pagesize[0]-15*mm, 10*mm, f'Page {doc.page}')


def generate_pdf():
    register_font()
    md = TRIP_MD.read_text(encoding='utf-8')
    days = parse_trip_markdown(md)

    portrait = A4
    landscape_pg = landscape(A4)
    pw, ph = portrait
    lw, lh = landscape_pg
    frame_portrait = Frame(18*mm, 18*mm, pw-36*mm, ph-36*mm, id='F')
    frame_land = Frame(18*mm, 18*mm, lw-36*mm, lh-36*mm, id='L')
    doc = BaseDocTemplate(str(OUTPUT_PDF), pageTemplates=[
        PageTemplate(id='Portrait', frames=[frame_portrait], pagesize=portrait, onPage=footer),
        PageTemplate(id='Landscape', frames=[frame_land], pagesize=landscape_pg, onPage=footer)
    ], leftMargin=18*mm, rightMargin=18*mm, topMargin=18*mm, bottomMargin=18*mm)

    story: List = []
    # Cover
    story.append(Paragraph('2025 黑龙江旅行手册', SECTION_TITLE))
    story.append(Paragraph('打印彩色版 | 适用日期：2025/08/16 - 08/24', SUBTITLE))
    story.append(Paragraph('版本：V3（多页概览 + 城市地图横版）', SMALL))
    story.append(Spacer(1, 8))
    # 目录
    toc_lines = [f'• {d.get("title","")}  ——  {d.get("date","")}' for d in days]
    story.append(Paragraph('目录 / 快速索引', SUBTITLE))
    story.append(Paragraph('<br/>'.join(toc_lines), BODY))
    story.append(PageBreak())

    # Overview tables
    story.extend(build_overview_pages(days))

    # Overview image page (portrait)
    overview_img = BASE_DIR / 'materials' / '行程总览图.png'
    if overview_img.exists():
        story.append(Paragraph('行程总览图', SUBTITLE))
        story.append(Image(str(overview_img), width=pw-50*mm, height=ph/2))
        story.append(PageBreak())

    # Harbin map landscape
    city_map = BASE_DIR / 'materials' / '哈尔滨市旅游地图.jpg'
    if city_map.exists():
        story.append(NextPageTemplate('Landscape'))
        story.append(PageBreak())
        story.append(Paragraph('哈尔滨市旅游地图（示意）', SUBTITLE))
        story.append(Image(str(city_map), width=lw-40*mm, height=lh-60*mm))
        story.append(NextPageTemplate('Portrait'))
        story.append(PageBreak())

    # Daily sections
    detail_dir = BASE_DIR / 'materials' / 'details'
    for d in days:
        story.append(Paragraph(d['title'], SECTION_TITLE))
        if d.get('date'):
            story.append(Paragraph('📅 ' + d['date'], SUBTITLE))
        if d.get('summary'):
            story.append(Paragraph('🧭 ' + d['summary'], BODY))
        story.append(Paragraph('⏱ 详细时间线', SUBTITLE))
        story.append(build_timeline_table(d.get('timeline', [])))
        story.append(Paragraph('🗺 景点速览与导游提示', SUBTITLE))
        story.append(spot_reference('\n'.join(d['lines'])))
        # Images
        dm = re.match(r'Day (\d+):', d['title'])
        if dm:
            dn = dm.group(1)
            imgs = sorted(detail_dir.glob(f'{dn}-map-*.png'))
            for i, ip in enumerate(imgs):
                story.append(Image(str(ip), width=pw-60*mm, height=ph/3))
                if (i+1) % 2 == 0 and i+1 != len(imgs):
                    story.append(PageBreak())
        story.append(PageBreak())

    # Appendix
    story.append(Paragraph('附录：安全与装备要点', SECTION_TITLE))
    story.append(Paragraph('☑ 补水 / 防晒 / 防蚊 · ⛅ 雷阵雨远离高处 · 🚗 自驾 120 分钟休息 · 📸 每晚双备份照片 · 🥾 徒步前热身后拉伸。', BODY))

    doc.build(story)
    print(f'已生成 PDF: {OUTPUT_PDF}')


if __name__ == '__main__':
    generate_pdf()
