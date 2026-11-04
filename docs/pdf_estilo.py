"""Estilos y utilidades compartidas por los generadores de resúmenes en PDF."""
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", FONT_DIR + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DV-B", FONT_DIR + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-M", FONT_DIR + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV", boldItalic="DV-B")

NAVY = colors.HexColor("#1F3A5F")
BLUE = colors.HexColor("#3D6A9E")
LIGHT = colors.HexColor("#EAF0F7")
AMBER = colors.HexColor("#B7791F")
AMBER_BG = colors.HexColor("#FDF3E1")
RED = colors.HexColor("#A33A3A")
RED_BG = colors.HexColor("#FBEAEA")
GREEN = colors.HexColor("#2F6B45")
GREEN_BG = colors.HexColor("#E8F3EC")
GREY = colors.HexColor("#5A6270")
LINE = colors.HexColor("#C9D3DF")

S = {
    "title": ParagraphStyle("title", fontName="DV-B", fontSize=24, leading=30, textColor=NAVY, alignment=TA_CENTER),
    "subtitle": ParagraphStyle("subtitle", fontName="DV", fontSize=12, leading=17, textColor=GREY, alignment=TA_CENTER),
    "h1": ParagraphStyle("h1", fontName="DV-B", fontSize=16, leading=21, textColor=NAVY, spaceBefore=4, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="DV-B", fontSize=12, leading=16, textColor=BLUE, spaceBefore=8, spaceAfter=4),
    "body": ParagraphStyle("body", fontName="DV", fontSize=9.5, leading=13.5, spaceAfter=4),
    "small": ParagraphStyle("small", fontName="DV", fontSize=8.5, leading=11.5),
    "mono": ParagraphStyle("mono", fontName="DV-M", fontSize=8.5, leading=11.5),
    "cell": ParagraphStyle("cell", fontName="DV", fontSize=8.8, leading=12),
    "cellc": ParagraphStyle("cellc", fontName="DV", fontSize=8.8, leading=12, alignment=TA_CENTER),
    "cellb": ParagraphStyle("cellb", fontName="DV-B", fontSize=8.8, leading=12),
    "cellw": ParagraphStyle("cellw", fontName="DV-B", fontSize=8.8, leading=12, textColor=colors.white),
    "tag": ParagraphStyle("tag", fontName="DV-B", fontSize=10, leading=13, textColor=colors.white, alignment=TA_CENTER),
    "tagsm": ParagraphStyle("tagsm", fontName="DV", fontSize=7.5, leading=10, textColor=colors.white, alignment=TA_CENTER),
    "q": ParagraphStyle("q", fontName="DV-B", fontSize=9.5, leading=13, textColor=NAVY),
    "bullet": ParagraphStyle("bullet", fontName="DV", fontSize=9.5, leading=13.5, leftIndent=12, bulletIndent=2, spaceAfter=2),
}

CONTENT_WIDTH = 174 * mm


def P(text, style="body"):
    return Paragraph(text, S[style])


def bullets(items, style="bullet"):
    return [Paragraph(t, S[style], bulletText="•") for t in items]


def box(flowables, bg, border, width=None):
    t = Table([[flowables]], colWidths=[width or CONTENT_WIDTH])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBEFORE", (0, 0), (0, -1), 3, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def grid(rows, widths, header=True, zebra=True, head_bg=NAVY, center=False):
    body_style = "cellc" if center else "cell"
    data = []
    for i, r in enumerate(rows):
        st = "cellw" if (header and i == 0) else body_style
        data.append([c if not isinstance(c, str) else Paragraph(c, S[st]) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        style.append(("BACKGROUND", (0, 0), (-1, 0), head_bg))
    if zebra:
        for i in range(1 if header else 0, len(rows)):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(style))
    return t


def make_on_page(footer):
    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("DV", 7.5)
        canvas.setFillColor(GREY)
        canvas.drawString(18 * mm, 10 * mm, footer)
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Pág. {doc.page}")
        canvas.setStrokeColor(LINE)
        canvas.line(18 * mm, 13 * mm, A4[0] - 18 * mm, 13 * mm)
        canvas.restoreState()
    return on_page
