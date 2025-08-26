import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont

# Simple, robust Chinese font loader for Windows/Linux/Mac

WINDOWS_FONTS = [
    ("Microsoft YaHei", r"C:\\Windows\\Fonts\\msyh.ttc"),
    ("SimHei", r"C:\\Windows\\Fonts\\simhei.ttf"),
    ("SimSun", r"C:\\Windows\\Fonts\\simsun.ttc"),
]
MAC_FONTS = [
    ("PingFangSC", "/System/Library/Fonts/PingFang.ttc"),
    ("SongtiSC", "/System/Library/Fonts/Songti.ttc"),
]
LINUX_FONTS = [
    ("WenQuanYiZenHei", "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"),
    ("NotoSansCJKsc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
]


def register_cn_font():
    tested = []
    for name, path in (WINDOWS_FONTS + MAC_FONTS + LINUX_FONTS):
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                return name
            except Exception:
                tested.append((name, path))
                continue
    # Fallback: built-in CID font (limited weight)
    try:
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        return "STSong-Light"
    except Exception:
        return "Helvetica"


def draw_wrapped_text(c, text, x, y, max_width, font_name, font_size, leading=None):
    c.setFont(font_name, font_size)
    leading = leading or (font_size * 1.35)
    # naive wrapping based on stringWidth
    words = []
    for line in str(text).split("\n"):
        if not line:
            words.append([""])
        else:
            words.append([ch for ch in line])  # char-based for CJK
    for line in words:
        buf = ""
        for ch in line:
            w = c.stringWidth(buf + ch, font_name, font_size)
            if w > max_width and buf:
                c.drawString(x, y, buf)
                y -= leading
                buf = ch
            else:
                buf += ch
        c.drawString(x, y, buf)
        y -= leading
    return y


def render_pdf(itinerary_path: str, out_pdf: str):
    with open(itinerary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    title = data.get("title", "行程单")
    date = data.get("date")
    notes = data.get("notes", [])
    items = data.get("items", [])
    tips = data.get("tips", [])

    font_name = register_cn_font()

    c = canvas.Canvas(out_pdf, pagesize=A4)
    width, height = A4
    margin = 18 * mm

    # Page 1: 标题 + 主行程（按时间顺序）
    c.setTitle(title)
    c.setAuthor("AccountOps Trip")

    y = height - margin
    c.setFont(font_name, 18)
    c.drawString(margin, y, title)
    if date:
        c.setFont(font_name, 12)
        c.drawString(margin + 140, y, f"日期：{date}")
    y -= 14 * mm

    c.setFont(font_name, 12)
    c.drawString(margin, y, "行程安排：")
    y -= 8 * mm

    c.setFont(font_name, 11)
    bullet = "• "
    line_h = 6.2 * mm
    max_width = width - margin * 2

    for it in items:
        txt = f"{it.get('time','')}  {it.get('title','')}"
        detail = it.get("detail")
        y = draw_wrapped_text(c, bullet + txt, margin, y, max_width, font_name, 11, leading=line_h)
        if detail:
            y = draw_wrapped_text(c, "    " + detail, margin, y, max_width, font_name, 10, leading=5.6 * mm)
        y -= 2.5 * mm
        if y < margin + 30 * mm:
            # 留出空间放页脚
            break

    # 页脚
    c.setFont(font_name, 9)
    c.drawRightString(width - margin, margin, "第 1 / 2 页")
    c.showPage()

    # Page 2: 注意事项/清单
    y = height - margin
    c.setFont(font_name, 16)
    c.drawString(margin, y, "出行提示与清单")
    y -= 12 * mm

    c.setFont(font_name, 12)
    c.drawString(margin, y, "重要提示：")
    y -= 8 * mm
    for n in notes:
        y = draw_wrapped_text(c, bullet + n, margin, y, max_width, font_name, 11, leading=6.2 * mm)
        y -= 2 * mm

    y -= 4 * mm
    c.setFont(font_name, 12)
    c.drawString(margin, y, "当季气候与穿着：")
    y -= 8 * mm
    for t in tips:
        y = draw_wrapped_text(c, bullet + t, margin, y, max_width, font_name, 11, leading=6.2 * mm)
        y -= 2 * mm

    y -= 6 * mm
    extras = [
        "导航关键词：黄花沟游客中心；察右后旗（餐饮集中区）；乌兰哈达五号/三号火山停车场；乌兰察布站",
        "安全与健康：避开未开放区域；防晒与防风并重；老人量力而行，随时补水",
        "备选方案：缩短草原或仅五号火山打卡，确保19:00前返站"
    ]
    c.setFont(font_name, 12)
    c.drawString(margin, y, "实用补充：")
    y -= 8 * mm
    for e in extras:
        y = draw_wrapped_text(c, bullet + e, margin, y, max_width, font_name, 11, leading=6.2 * mm)
        y -= 2 * mm

    c.setFont(font_name, 9)
    c.drawRightString(width - margin, margin, "第 2 / 2 页")

    c.save()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", required=True, help="itinerary.json path")
    parser.add_argument("--outfile", required=True, help="output pdf path")
    args = parser.parse_args()

    render_pdf(args.infile, args.outfile)
