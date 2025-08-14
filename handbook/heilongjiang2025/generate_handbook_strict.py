"""
Strict, spec-driven renderer for the Heilongjiang Teen Handbook.
- Does NOT reuse prior generator logic; built to follow the approved design brief.
- Two-phase workflow (validate -> render) and a single final output PDF.
- Pulls daily content from materials/details and trip_plan.md.

Output: 《2025黑龙江旅行手册_严格版》.pdf
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph, Table, TableStyle, PageBreak, Spacer, Image,
    BaseDocTemplate, Frame, PageTemplate, NextPageTemplate, Flowable, KeepTogether
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.platypus.flowables import KeepInFrame

BASE_DIR = Path(__file__).parent
MATERIALS = BASE_DIR / 'materials'
DETAILS = MATERIALS / 'details'
TRIP_MD = MATERIALS / 'trip_plan.md'

# 单一输出文件（原先的 v2 作为最终版本）
OUTPUT = BASE_DIR / '《2025黑龙江旅行手册_严格版》.pdf'

# 是否在每日笔记中保留“打卡清单/小任务”等任务段落
# True = 保留（包含“任务清单/任务单/挑战/打卡”等内容）
# False = 移除这些段落并自动重排后续编号
INCLUDE_TASKS: bool = True

FONT_PATHS = [
    'C:/Windows/Fonts/SourceHanSerifSC-Regular.otf',
    'C:/Windows/Fonts/msyh.ttc',
    'C:/Windows/Fonts/simsun.ttc',
    'C:/Windows/Fonts/simhei.ttf',
]
FONT_NAME = 'HLJTeen'
MARGIN = 12 * mm  # tighter margins to reduce outer whitespace

# ---------- Styles tuned for teen edition ----------
TITLE = ParagraphStyle('Title', fontName=FONT_NAME, fontSize=24, leading=30, textColor=colors.HexColor('#0B3954'), spaceAfter=10)
H1 = ParagraphStyle('H1', fontName=FONT_NAME, fontSize=18, leading=24, textColor=colors.HexColor('#0B3954'), spaceAfter=8)
H2 = ParagraphStyle('H2', fontName=FONT_NAME, fontSize=14, leading=20, textColor=colors.HexColor('#1565C0'), spaceAfter=6)
BODY = ParagraphStyle('Body', fontName=FONT_NAME, fontSize=10.8, leading=15.5, spaceAfter=4)
BODY_WRAP = ParagraphStyle('BodyWrap', fontName=FONT_NAME, fontSize=10.2, leading=15.2, spaceAfter=3, wordWrap='CJK')
SMALL = ParagraphStyle('Small', fontName=FONT_NAME, fontSize=9, leading=12, textColor=colors.HexColor('#546E7A'))
QUOTE = ParagraphStyle('Quote', parent=BODY, backColor=colors.HexColor('#E3F2FD'), borderColor=colors.HexColor('#64B5F6'), borderWidth=0.6, borderPadding=5, leftIndent=4, rightIndent=4, spaceBefore=4, spaceAfter=8)

# Slightly larger styles for the notes area to better fill remaining space
NOTES_TITLE = ParagraphStyle('NotesTitle', parent=H2, fontSize=16.5, leading=22.5)
NOTES_BODY = ParagraphStyle('NotesBody', parent=BODY_WRAP, fontSize=12.8, leading=18.2)


@dataclass
class DayPlan:
    day_no: int
    title: str
    date: str = ''
    summary: str = ''
    timeline: List[str] = field(default_factory=list)
    detail_text: str = ''
    images: List[Path] = field(default_factory=list)


@dataclass
class RenderState:
    issues: List[str] = field(default_factory=list)
    fixed: List[str] = field(default_factory=list)


def register_font():
    for p in FONT_PATHS:
        if os.path.exists(p):
            try:
                pdfmetrics.registerFont(TTFont(FONT_NAME, p))
                return
            except Exception:
                continue
    raise FileNotFoundError('未找到中文字体，请调整 FONT_PATHS。')


def parse_trip_markdown(md_text: str) -> List[DayPlan]:
    days: List[DayPlan] = []
    current: Optional[DayPlan] = None
    buf: List[str] = []

    for line in md_text.splitlines():
        if line.startswith('### Day '):
            if current:
                current.detail_text = '\n'.join(buf)
                days.append(current)
                buf = []
            m = re.match(r'### Day (\d+):\s*(.*)', line.strip())
            dn = int(m.group(1)) if m else len(days) + 1
            title = f'Day {dn}: ' + (m.group(2) if m else '')
            current = DayPlan(day_no=dn, title=title)
        else:
            buf.append(line)
    if current:
        current.detail_text = '\n'.join(buf)
        days.append(current)

    # enrich per day
    for d in days:
        block = d.detail_text
        m_date = re.search(r'\*\*(\d{4}年[^*]+)\*\*', block)
        if m_date:
            d.date = m_date.group(1)
        m_summary = re.search(r'当日总览[:：]\*\*?\s*([^\n]+)', block)
        if m_summary:
            d.summary = m_summary.group(1).strip()
        # timeline
        timeline: List[str] = []
        capture = False
        for l in block.splitlines():
            if '详细时间线' in l:
                capture = True
                continue
            if capture:
                if l.strip().startswith('- '):
                    timeline.append(l.strip()[2:])
                elif l.strip().startswith('**') or l.strip().startswith('---') or l.startswith('### Day'):
                    break
        d.timeline = timeline
        # images
        d.images = sorted((DETAILS).glob(f'{d.day_no}-map-*.png'))
        # detail .md
        md_file = next(DETAILS.glob(f'{d.day_no}*.md'), None)
        if md_file:
            try:
                d.detail_text = md_file.read_text(encoding='utf-8')
            except Exception:
                pass
    return days


# ---------- Page builders ----------

def footer(canvas, doc):
    canvas.setFont(FONT_NAME, 8)
    canvas.setFillColor(colors.HexColor('#607D8B'))
    canvas.drawRightString(doc.pagesize[0] - 15 * mm, 10 * mm, f'Page {doc.page}')


def paragraph(text: str, style=BODY) -> Paragraph:
    # basic sanitization
    safe = text.replace('**', '')
    return Paragraph(safe, style)


def fitted_image(img_path: Path, max_w: float, max_h: float) -> Flowable:
    """Return an Image scaled to fit within max_w x max_h (keeping aspect).
    Falls back to a text placeholder on error.
    """
    try:
        ir = ImageReader(str(img_path))
        iw, ih = ir.getSize()
        if iw <= 0 or ih <= 0:
            return Paragraph(img_path.name, SMALL)
        scale = min(max_w / iw, max_h / ih, 1.0)
        w, h = iw * scale, ih * scale
        return Image(str(img_path), width=w, height=h)
    except Exception:
        return Paragraph(img_path.name, SMALL)


def make_notes_panel(width: float, height: float, title_text: str, body_html: str, max_font: float = 13.5, min_font: float = 10.0) -> Flowable:
    """Create an artistic bordered notes panel that auto-fits font size to the box.
    It tries from max_font down to min_font; uses a subtle background and border.
    """
    pad = 8  # points; panel inner padding
    avail_w = max(10, width - 2 * pad)
    avail_h = max(10, height - 2 * pad)

    chosen_body_fs = min_font
    chosen_title_fs = min_font + 2.0
    # Try decreasing sizes to fit
    step = 0.5
    sz = max_font
    while sz >= min_font:
        t_style = ParagraphStyle('NotesTitleTmp', parent=NOTES_TITLE, fontSize=sz + 2.0, leading=(sz + 2.0) * 1.35)
        b_style = ParagraphStyle('NotesBodyTmp', parent=NOTES_BODY, fontSize=sz, leading=sz * 1.45)
        t_para = Paragraph(title_text, t_style)
        b_para = Paragraph(body_html, b_style)
        _, th = t_para.wrap(avail_w, 0)
        _, bh = b_para.wrap(avail_w, 0)
        if th + 6 + bh <= avail_h:
            chosen_body_fs = sz
            chosen_title_fs = sz + 2.0
            break
        sz -= step

    # Build content with chosen sizes; KeepInFrame as final guard
    t_style = ParagraphStyle('NotesTitleChosen', parent=NOTES_TITLE, fontSize=chosen_title_fs, leading=chosen_title_fs * 1.35)
    b_style = ParagraphStyle('NotesBodyChosen', parent=NOTES_BODY, fontSize=chosen_body_fs, leading=chosen_body_fs * 1.45)
    content = [Paragraph(title_text, t_style), Spacer(1, 4), Paragraph(body_html, b_style)]
    inner = KeepInFrame(maxWidth=avail_w, maxHeight=avail_h, content=content, mergeSpace=True, mode='shrink')

    panel = Table([[inner]], colWidths=[width])
    panel.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F9FBFE')),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#90CAF9')),
        ('LEFTPADDING', (0, 0), (-1, -1), pad),
        ('RIGHTPADDING', (0, 0), (-1, -1), pad),
        ('TOPPADDING', (0, 0), (-1, -1), pad),
        ('BOTTOMPADDING', (0, 0), (-1, -1), pad),
    ]))
    return panel


def build_cover(story: List, state: RenderState):
    # Summer-themed cover: emphasize forests, rivers, sunshine
    story.append(paragraph('黑龙江：森林与河流的暑期探索之旅', TITLE))
    story.append(paragraph('一本给未来探险家的地理与人文观察手册（Summer 2025）', H2))
    cover_img = MATERIALS / '行程总览图封面2.png'
    if not cover_img.exists():
        cover_img = MATERIALS / '行程总览图封面.png'
    if cover_img.exists():
        pw, ph = A4
        story.append(Image(str(cover_img), width=pw - 50 * mm, height=ph / 2))
    else:
        state.issues.append('缺少封面图片')
    # 底部补充风光图，填充封面下方留白
    summer_img = MATERIALS / '黑龙江夏日风光图.png'
    if summer_img.exists():
        pw, ph = A4
        frame_w = pw - 2 * MARGIN
        max_w = frame_w - 8 * mm
        max_h = 80 * mm
        story.append(Spacer(1, 10))
        story.append(fitted_image(summer_img, max_w=max_w, max_h=max_h))
    else:
        state.issues.append('缺少黑龙江夏日风光图.png')
    # 按要求：封面不展示签名与版本信息
    story.append(PageBreak())


def build_overview(story: List, days: List[DayPlan], state: RenderState):
    story.append(paragraph('远征序章 / 行程总览', H1))
    # table（增大行高，开启换行）
    rows = [[Paragraph('日程', BODY), Paragraph('日期', BODY), Paragraph('提要', BODY)]]
    for d in days:
        day_cell = Paragraph(f'Day {d.day_no}', BODY)
        date_cell = Paragraph(d.date or '—', BODY_WRAP)
        # 略缩摘要，压缩总体高度以与下方总览图同页显示
        summary_txt = (d.summary[:140] + '...') if len(d.summary) > 140 else (d.summary or '—')
        sum_cell = Paragraph(summary_txt, BODY_WRAP)
        rows.append([day_cell, date_cell, sum_cell])
    pw, ph = A4
    frame_w = pw - 2 * MARGIN
    # 列宽严格适配版心宽度，避免溢出
    cw0 = 24 * mm
    cw1 = 32 * mm
    cw2 = frame_w - (cw0 + cw1)
    tbl = Table(rows, colWidths=[cw0, cw1, cw2])
    tbl.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#BBDEFB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#90CAF9')),
        ('TOPPADDING', (0, 1), (-1, -1), 3.2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3.2),
        ('WORDWRAP', (0, 0), (-1, -1), 'CJK'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, -1), 8.2)
    ]))
    story.append(tbl)
    # map
    overview = MATERIALS / '行程总览图封面.png'
    if overview.exists():
        # 控制高度，确保与表格同页
        story.append(Spacer(1, 6))
        max_w = frame_w - 8 * mm
        max_h = 110 * mm
        story.append(fitted_image(overview, max_w=max_w, max_h=max_h))
    else:
        state.issues.append('缺少行程总览图封面.png')
    story.append(PageBreak())


def build_intro(story: List, state: RenderState):
    story.append(paragraph('时空坐标：东北与黑龙江', H1))
    story.append(paragraph('我们站在哪里？——从中国北疆到界江森林的广袤土地', H2))
    # 扩展型文字介绍（约半页）
    intro_paras = [
        '地理格局：黑龙江位于中国最东北，东与俄罗斯隔黑龙江（阿穆尔河）相望，西北连小兴安岭与松嫩平原，北部接近北纬50°。这里冬长夏短、昼夜温差大，形成独特的寒温带森林生态系统与黑土地农业区。',
        '历史脉络：这片土地是满—通古斯诸民族的重要活动区域，也是近代交通与工业化的关键舞台。中东铁路的修建，使哈尔滨迅速崛起为近代都市；抗联精神、边疆开发与林业建设，塑造了今天的城市肌理与人文记忆。',
        '国家意义：黑土粮仓与北方生态屏障在此叠加。上游跨境河流与广袤林海，对维护生物多样性与水土保持具有战略价值；边境城市的对外开放，则承载着跨境贸易与文明交流。',
        '经典景观线索：哈尔滨的欧式街区与松花江、齐齐哈尔扎龙湿地的丹顶鹤、五大连池的新生代火山群、黑河的界江风貌、嘉荫的恐龙化石、伊春的红松母树林与奇石地貌，共同构成“城市—湿地—火山—边城—化石—森林”的主题串联。',
    ]
    for p in intro_paras:
        story.append(paragraph(p, BODY))
    # 大图：东北位置图，保持原比例，限制宽高以适配版心
    img1 = MATERIALS / '东北位置图.png'
    if img1.exists():
        pw, ph = A4
        frame_w = pw - 2 * MARGIN
        # 防止与 Frame 精确宽度冲突，留出边界余量，并限制高度避免溢出
        max_w = frame_w - 8 * mm
        max_h = 120 * mm
        story.append(Spacer(1, 6))
        story.append(fitted_image(img1, max_w=max_w, max_h=max_h))
    else:
        state.issues.append('缺少东北位置图.png')
    story.append(PageBreak())


def parse_detail_snippet(md_text: str) -> str:
    # Keep first 200-400 chars as contextual intro
    text = re.sub(r'^#.*$', '', md_text, flags=re.M)
    text = re.sub(r'```.*?```', '', text, flags=re.S)
    text = text.strip()
    return text[:600]


def load_day_notes(d: DayPlan) -> str:
    """Prefer a curated guide file like 'N_guide.md'; fallback to snippet of detail text.
    Convert newlines to <br/> for Paragraph rendering.
    """
    guide_md = DETAILS / f'{d.day_no}_guide.md'
    text = ''
    if guide_md.exists():
        try:
            text = guide_md.read_text(encoding='utf-8')
        except Exception:
            text = ''
    if not text:
        text = parse_detail_snippet(d.detail_text)
    # simple markdown hygiene: strip leading '#' and keep line breaks
    text = re.sub(r'^#+\s*', '', text, flags=re.M).strip()
    # remove task/checklist/challenge blocks to keep notes concise
    text = sanitize_notes(text)
    text = text.replace('\n', '<br/>')
    return text


def sanitize_notes(text: str) -> str:
    """Drop lines/blocks related to 任务/挑战/打卡/checklists and then renumber headings.
    - Remove any standalone heading like "4. 任务清单" / "任务单" / "今日任务单".
    - Skip subsequent task list bullets until a blank line.
    - Remove GitHub style checkboxes.
    - Finally, renumber leading numeric headings (1. / 2. / 3.) to keep sequence.
    """
    if INCLUDE_TASKS:
        # Keep tasks as-is; only normalize heading numbers for consistency
        return _renumber_headings(text)
    lines = text.splitlines()
    keep: list[str] = []
    skip = False
    # patterns
    heading_pat = re.compile(r"^\s*(?:\d{1,2}[\.、)]\s*)?(?:今日)?任务(?:清单|单)?(?:\s*[:：])?\s*$")
    for ln in lines:
        s = ln.strip()
        # remove a pure heading that mentions 任务/任务清单
        if heading_pat.match(s):
            # drop the heading itself, and start skipping following block until blank line
            skip = True
            continue
        # start skipping on lines mentioning tasks/challenges if they look like section starters
        if not skip and (("任务" in s) or ("挑战" in s) or ("打卡" in s)):
            if s.startswith('-') or s.startswith('*') or '：' in s or s.endswith(':'):
                skip = True
                continue
        if skip:
            # continue skipping list-like lines; stop at empty line
            if s == '':
                skip = False
            continue
        # drop GitHub-style checklists regardless
        if s.startswith('- [') or s.startswith('[ ]'):
            continue
        keep.append(ln)

    cleaned = '\n'.join(keep)
    return _renumber_headings(cleaned)


def _renumber_headings(text: str) -> str:
    """Renumber top-level numeric headings after removals.
    Convert lines like "5. 安全与礼仪" -> "4. 安全与礼仪".
    Matches patterns: "N. ", "N) ", "N、" (with a space optional after punct).
    """
    out_lines: list[str] = []
    n = 0
    pat = re.compile(r"^(\s*)(\d{1,2})([\.、)])(\s+)(.+)$")
    for ln in text.splitlines():
        m = pat.match(ln)
        if m:
            n += 1
            indent, _oldn, punct, sp, rest = m.groups()
            out_lines.append(f"{indent}{n}{punct}{sp}{rest}")
        else:
            out_lines.append(ln)
    return '\n'.join(out_lines)


def build_day_page(story: List, d: DayPlan, state: RenderState):
    story.append(paragraph(d.title, H1))
    if d.date:
        story.append(paragraph('📅 ' + d.date, H2))
    if d.summary:
        story.append(paragraph('🧭 ' + d.summary))
    # timeline table
    rows = [['时间', '活动 / 说明']]
    pat = re.compile(r'^(\d{1,2}:\d{2})[\s\-—–]*(.*)')
    if not d.timeline:
        state.issues.append(f'Day {d.day_no} 缺少时间线')
    for item in (d.timeline or ['— 无时间线 —']):
        m = pat.match(item)
        t, desc = (m.group(1), m.group(2).strip()) if m else ('—', item)
        rows.append([t, desc])
    tbl = Table(rows, colWidths=[22 * mm, 125 * mm])
    tbl.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#C8E6C9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1B5E20')),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#A5D6A7')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F1F8E9')]),
        ('FONTSIZE', (0, 0), (-1, -1), 9.2),
    ]))
    story.append(tbl)
    # 下半部分：左右两栏布局（左：观察要点/导游词，右：竖排最多3张地图）
    pw, ph = A4
    avail_w = pw - 2 * MARGIN
    left_w = avail_w * 0.72
    right_w = avail_w - left_w
    # 根据表格实际高度估算剩余可用高度，尽量填满页面
    _w, tbl_h = tbl.wrap(avail_w, 0)
    content_h = ph - 2 * MARGIN
    header_est = 58 * mm  # 题头/日期/摘要等的估计高度
    section_h = max(86 * mm, content_h - tbl_h - header_est)

    # 左侧：优先使用自定义导游词（N_guide.md），次选详情摘要（控制长度，避免溢出）
    # 左栏标题移除“任务单/清单”等措辞，只保留观察与导游词
    notes_title_txt = '观察要点 · 导游词摘录'
    notes_body_txt = load_day_notes(d)[:4000]

    # Day 9：替换为结语与寒假建议
    if d.day_no == 9:
        summary_txt = (
            '这一周，我们从城市到森林、从湿地到火山，认识了黑龙江的地理线索与人文故事。<br/><br/>'
            '回到北京之后，可以把本次行程中最难忘的三个地点画在一张手绘地图上，写下你想要继续研究的问题。'
        )
        winter_opts = (
            '寒假去哪儿 · 南方候选路线：<br/>'
            '1) 广西北部湾—涠洲岛：火山岛海蚀地貌与珊瑚礁生态。<br/>'
            '2) 海南东线—陵水/万宁：海岸地貌、热带雨林与海盐文化。<br/>'
            '3) 湛江·雷州半岛（含硇洲岛）：玄武岩台地、古火山口与海岸渔村文化。<br/>'
            '4) 潮汕（汕头/潮州/南澳岛）：海岛风光、广式-潮汕饮食与海丝港口史。'
        )
        notes_title_txt = '结语 · 我们的黑龙江之旅'
        notes_body_txt = summary_txt + '<br/><br/>' + winter_opts

    # （Day 9 的内容已在 notes_title_txt/notes_body_txt 上方替换为结语+寒假建议，不再单独构建 left_flows）

    # 生成艺术化笔记面板（自动调字号以适配高度）
    left_panel = make_notes_panel(left_w, section_h, notes_title_txt, notes_body_txt, max_font=13.6, min_font=10.4)

    # 始终采用左右两栏布局（无论文本长度），确保右侧地图始终显示

    # 右侧：最多3张地图竖排
    right_items: List[Flowable] = []
    imgs = (d.images or [])[:3]
    if imgs:
        # 动态分配单图高度以吃满右侧栏
        gaps = 3 * (len(imgs) - 1)
        img_max_h = max(24 * mm, (section_h - gaps) / len(imgs))
        for p in imgs:
            right_items.append(fitted_image(p, max_w=right_w - 4 * mm, max_h=img_max_h))
            right_items.append(Spacer(1, 3))
        if right_items:
            right_items = right_items[:-1]
    else:
        right_items = [paragraph('（暂无地图）', SMALL)]

    # 右侧同样用 KeepInFrame 限高
    right_box = KeepInFrame(maxWidth=right_w, maxHeight=section_h, content=right_items, mergeSpace=True, mode='truncate')

    two_col = Table([[left_panel, right_box]], colWidths=[left_w, right_w])
    two_col.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBEFORE', (1, 0), (1, 0), 0.3, colors.HexColor('#CFD8DC')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    story.append(Spacer(1, 6))
    story.append(two_col)
    story.append(PageBreak())


def build_city_overview(story: List, title: str, text: str, img: Path, state: RenderState):
    # Portrait layout; scale image by aspect ratio to fit content box
    story.append(paragraph(title, H1))
    if text:
        story.append(paragraph(text))
    pw, ph = A4
    # 稍微小于版心宽度，避免潜在的边界误差
    max_w = pw - 48 * mm
    max_h = ph - 90 * mm  # leave space for title/text
    if img.exists():
        try:
            ir = ImageReader(str(img))
            iw, ih = ir.getSize()
            scale = min(max_w / iw, max_h / ih)
            w, h = iw * scale, ih * scale
            story.append(Spacer(1, 8))
            story.append(Image(str(img), width=w, height=h))
        except Exception:
            story.append(Image(str(img), width=max_w))
    else:
        state.issues.append(f'缺少城市图：{img.name}')
    story.append(PageBreak())


def build_topic(story: List, title: str, text: str, img: Optional[Path], state: RenderState):
    story.append(paragraph(title, H1))
    if text:
        story.append(paragraph(text))
    if img and img.exists():
        pw, ph = A4
        story.append(Image(str(img), width=pw - 50 * mm, height=ph / 2))
    elif img:
        state.issues.append(f'专题缺图：{img.name}')
    story.append(PageBreak())

def validate_and_fix(days: List[DayPlan], state: RenderState):
    # Basic checks and small auto-fixes
    for d in days:
        if len(d.summary) > 220:
            d.summary = d.summary[:220] + '...'
            state.fixed.append(f'Day {d.day_no} 摘要过长，已截断')
        if not d.timeline:
            # try to parse again from detail_text (fallback bullet times)
            tl = []
            for l in d.detail_text.splitlines():
                ml = re.match(r'-\s*(\d{1,2}:\d{2})\s*(.*)', l)
                if ml:
                    tl.append(f'{ml.group(1)} {ml.group(2)}')
            if tl:
                d.timeline = tl
                state.fixed.append(f'Day {d.day_no} 从详情中补全时间线')
        # ensure at least one image placeholder
        if not d.images:
            # try generic city map if day 1-3 哈尔滨/齐齐哈尔
            if d.day_no in (1, 2):
                p = MATERIALS / '哈尔滨旅游图.jpg'
                if p.exists():
                    d.images = [p]
                    state.fixed.append('Day 1/2 使用哈尔滨旅游图作为占位')
            elif d.day_no == 3:
                p = MATERIALS / '齐齐哈尔旅游图.jpg'
                if p.exists():
                    d.images = [p]
                    state.fixed.append('Day 3 使用齐齐哈尔旅游图作为占位')


def build_document(days: List[DayPlan], output_path: Path, state: RenderState):
    register_font()

    portrait = A4
    landscape_pg = landscape(A4)
    pw, ph = portrait
    lw, lh = landscape_pg
    frame_portrait = Frame(MARGIN, MARGIN, pw-2*MARGIN, ph-2*MARGIN, id='F')
    frame_land = Frame(MARGIN, MARGIN, lw-2*MARGIN, lh-2*MARGIN, id='L')
    doc = BaseDocTemplate(str(output_path), pageTemplates=[
        PageTemplate(id='Portrait', frames=[frame_portrait], pagesize=portrait, onPage=footer),
        PageTemplate(id='Landscape', frames=[frame_land], pagesize=landscape_pg, onPage=footer)
    ], leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN)

    story: List = []

    # Cover / Overview / Intro
    build_cover(story, state)
    build_overview(story, days, state)
    build_intro(story, state)

    # Day pages + required interleaved pages per spec
    for d in days:
        build_day_page(story, d, state)
        # Inserts after specific days（保留城市全览与专题页）
        if d.day_no == 2:
            build_city_overview(
                story,
                '再会·冰城哈尔滨',
                '两天的城市观察：从“远东小巴黎”的历史建筑到松花江畔的现代活力。下图为全市旅游图，便于回顾足迹与规划再访。',
                MATERIALS / '哈尔滨市旅游地图.jpg',
                state,
            )
        if d.day_no == 3:
            build_city_overview(
                story,
                '鹤城齐齐哈尔全览',
                '齐齐哈尔不仅有扎龙湿地的丹顶鹤，更有工业底蕴与嫩江平原的开阔风光。',
                MATERIALS / '齐齐哈尔旅游图.jpg',
                state,
            )
        if d.day_no == 4:
            build_city_overview(
                story,
                '黑河城市鸟瞰',
                '口岸城市黑河与对岸布拉戈维申斯克隔江相望，边境文化与中俄交流在此叠加。',
                MATERIALS / '黑河旅游图.jpg',
                state,
            )
        if d.day_no == 5:
            build_topic(
                story,
                '专题·胡焕庸线详解',
                '胡焕庸线是理解中国人口与经济空间格局的钥匙。本次行程主要位于线的西北侧，请结合沿途观察思考地理对聚落与产业的影响。',
                MATERIALS / '胡焕庸线.png',
                state,
            )
        if d.day_no == 6:
            build_city_overview(
                story,
                '林都伊春全景',
                '林海、奇石与红松母树林共同构成伊春独特的自然名片。',
                MATERIALS / '伊春旅游图.jpg',
                state,
            )
    # 不再单独插入“思考与总结”，已合并到 Day 9 左栏

    # 不再追加单独“附录”页，已合并到 Day 9 左栏

    doc.build(story)


def main():
    # Data load
    md_text = TRIP_MD.read_text(encoding='utf-8')
    days = parse_trip_markdown(md_text)

    # Pass 1: Validate (不输出文件)
    state = RenderState()
    validate_and_fix(days, state)

    # Pass 2: Adjustments based on recorded issues
    # Heuristics: if any city map missing -> degrade to portrait and add text placeholder; too many issues -> reduce images per day
    if any('缺少城市图' in s for s in state.issues):
        # nothing to change in spec; recorded for awareness
        state.fixed.append('城市图缺失：保持占位文本')
    # If many day pages missing maps, avoid grid clutter by removing images beyond first
    if sum(1 for s in state.issues if '缺少地图图片' in s) >= 2:
        for d in days:
            if len(d.images) > 1:
                d.images = d.images[:1]
                state.fixed.append(f'Day {d.day_no} 仅保留首张地图以保持整洁')

    # Shorten very long detail snippets
    for d in days:
        if len(d.detail_text) > 1500:
            d.detail_text = d.detail_text[:1500] + '...'
            state.fixed.append(f'Day {d.day_no} 详情截断以避免排版溢出')

    # Render final
    build_document(days, OUTPUT, state)

    # Report
    print('严格版手册已生成:')
    print('  输出文件:', OUTPUT)
    if state.issues:
        print('\n检查发现的问题:')
        for s in state.issues:
            print(' -', s)
    if state.fixed:
        print('\n自动修复/优化:')
        for s in state.fixed:
            print(' -', s)


if __name__ == '__main__':
    register_font()
    main()
