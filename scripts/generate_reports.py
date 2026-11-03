from pathlib import Path
import html
import os
import re

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
    PageBreak, Preformatted, KeepTogether
)

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "docs" / "reports"
REGULAR = os.environ.get("DAIMON_CJK_FONT_REGULAR")
BOLD = os.environ.get("DAIMON_CJK_FONT_BOLD")
if not REGULAR or not BOLD:
    raise RuntimeError("Не найдены управляемые шрифты с поддержкой русского языка")
pdfmetrics.registerFont(TTFont("DaimonCJK", REGULAR))
pdfmetrics.registerFont(TTFont("DaimonCJK-Bold", BOLD))
pdfmetrics.registerFontFamily("DaimonCJK", normal="DaimonCJK", bold="DaimonCJK-Bold", italic="DaimonCJK", boldItalic="DaimonCJK-Bold")

NAVY = HexColor("#17324D")
GRAY = HexColor("#5D6B78")
BLACK = HexColor("#27333D")
LIGHT = HexColor("#D7E0E7")

TITLES = {
    1: "Анализ предметной области и требования",
    2: "Создание и ведение Git-репозитория",
    3: "Проектирование архитектуры программного продукта",
    4: "Проектирование пользовательского интерфейса",
    5: "Проектирование и создание базы данных",
}


def styles():
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle("BodyRU", parent=base["BodyText"], fontName="DaimonCJK", fontSize=10.2, leading=14.5, textColor=BLACK, spaceAfter=7, alignment=TA_LEFT),
        "h2": ParagraphStyle("H2RU", parent=base["Heading2"], fontName="DaimonCJK-Bold", fontSize=16, leading=20, textColor=NAVY, spaceBefore=2, spaceAfter=10, keepWithNext=True),
        "h3": ParagraphStyle("H3RU", parent=base["Heading3"], fontName="DaimonCJK-Bold", fontSize=12.5, leading=16, textColor=NAVY, spaceBefore=8, spaceAfter=6, keepWithNext=True),
        "bullet": ParagraphStyle("BulletRU", parent=base["BodyText"], fontName="DaimonCJK", fontSize=10, leading=14, leftIndent=16, firstLineIndent=-9, bulletIndent=3, textColor=BLACK, spaceAfter=4),
        "cell": ParagraphStyle("CellRU", parent=base["BodyText"], fontName="DaimonCJK", fontSize=8.2, leading=10.5, textColor=BLACK),
        "cell_head": ParagraphStyle("CellHeadRU", parent=base["BodyText"], fontName="DaimonCJK-Bold", fontSize=8.3, leading=10.5, textColor=NAVY),
        "caption": ParagraphStyle("CaptionRU", parent=base["BodyText"], fontName="DaimonCJK", fontSize=8.5, leading=11, textColor=GRAY, alignment=TA_CENTER, spaceBefore=4, spaceAfter=8),
        "code": ParagraphStyle("CodeRU", parent=base["Code"], fontName="DaimonCJK", fontSize=8.5, leading=12, leftIndent=10, rightIndent=10, backColor=HexColor("#F3F5F7"), borderPadding=7, spaceAfter=8),
        "cover_top": ParagraphStyle("CoverTop", parent=base["BodyText"], fontName="DaimonCJK", fontSize=12, leading=17, alignment=TA_CENTER, textColor=GRAY),
        "cover_title": ParagraphStyle("CoverTitle", parent=base["Title"], fontName="DaimonCJK-Bold", fontSize=22, leading=29, alignment=TA_CENTER, textColor=NAVY, spaceAfter=18),
        "cover_sub": ParagraphStyle("CoverSub", parent=base["Title"], fontName="DaimonCJK-Bold", fontSize=17, leading=23, alignment=TA_CENTER, textColor=BLACK),
        "cover_meta": ParagraphStyle("CoverMeta", parent=base["BodyText"], fontName="DaimonCJK", fontSize=12, leading=19, textColor=BLACK, leftIndent=8*cm, firstLineIndent=0),
    }


def inline(value):
    value = html.escape(value.strip())
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"`(.+?)`", r'<font color="#17324D">\1</font>', value)
    value = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", value)
    return value


def table_widths(rows, available):
    n = len(rows[0])
    header = [re.sub(r"[*`]", "", x).strip().lower() for x in rows[0]]
    if n == 2:
        first = 1.65*cm if header[0] in {"id", "pk"} else 4.1*cm
        return [first, available-first]
    if n == 3:
        return [3.1*cm, (available-3.1*cm)*0.53, (available-3.1*cm)*0.47]
    if n == 4:
        return [available*0.18, available*0.28, available*0.27, available*0.27]
    return [available/n]*n


def make_table(rows, available, st):
    data = []
    for ridx, row in enumerate(rows):
        data.append([Paragraph(inline(cell), st["cell_head"] if ridx == 0 else st["cell"]) for cell in row])
    table = Table(data, colWidths=table_widths(rows, available), repeatRows=1, hAlign="LEFT", splitByRow=1)
    table.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, 0), 1.2, NAVY),
        ("LINEBELOW", (0, 0), (-1, 0), 0.7, NAVY),
        ("LINEBELOW", (0, -1), (-1, -1), 1.2, NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return [table, Spacer(1, 8)]


def make_image(caption, target, md_path, available, st):
    path = (md_path.parent / target).resolve()
    with PILImage.open(path) as source:
        width, height = source.size
    max_height = 15.2*cm
    ratio = min(available/width, max_height/height)
    image = Image(str(path), width=width*ratio, height=height*ratio)
    image.hAlign = "CENTER"
    return [Spacer(1, 3), image, Paragraph(inline(caption), st["caption"])]


def parse_markdown(md_path, available, st):
    lines = md_path.read_text(encoding="utf-8").splitlines()
    story = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line == "<!-- pagebreak -->":
            story.append(PageBreak())
            i += 1
            continue
        if line.startswith("```"):
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            story.append(Preformatted("\n".join(code), st["code"]))
            continue
        image_match = re.match(r"!\[(.*?)\]\((.*?)\)$", line)
        if image_match:
            story.extend(make_image(image_match.group(1), image_match.group(2), md_path, available, st))
            i += 1
            continue
        if line.startswith("|"):
            raw_rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                raw_rows.append(lines[i].strip())
                i += 1
            rows = []
            for ridx, raw in enumerate(raw_rows):
                cells = [cell.strip() for cell in raw.strip("|").split("|")]
                if ridx == 1 and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                    continue
                rows.append(cells)
            story.extend(make_table(rows, available, st))
            continue
        if line.startswith("### "):
            story.append(Paragraph(inline(line[4:]), st["h3"]))
            i += 1
            continue
        if line.startswith("## "):
            story.append(Paragraph(inline(line[3:]), st["h2"]))
            i += 1
            continue
        if line.startswith("- "):
            story.append(Paragraph(inline(line[2:]), st["bullet"], bulletText="•"))
            i += 1
            continue
        paragraph = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i].strip()
            if not nxt or nxt == "<!-- pagebreak -->" or nxt.startswith(("## ", "### ", "|", "- ", "```", "![")):
                break
            paragraph.append(nxt)
            i += 1
        story.append(Paragraph(inline(" ".join(paragraph)), st["body"]))
    return story


def header_footer(canvas, doc, lab):
    canvas.saveState()
    width, height = A4
    canvas.setFont("DaimonCJK", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(2.2*cm, height-1.25*cm, f"Лабораторная работа №{lab}. {TITLES[lab]}")
    canvas.setStrokeColor(LIGHT)
    canvas.line(2.2*cm, height-1.45*cm, width-2*cm, height-1.45*cm)
    canvas.drawString(2.2*cm, 1.15*cm, "Гатин Тимофей, еозИСИП-308")
    canvas.drawRightString(width-2*cm, 1.15*cm, f"Страница {doc.page}")
    canvas.restoreState()


def build_report(lab):
    md_path = REPORTS / f"lab{lab}.md"
    pdf_path = REPORTS / f"Лабораторная_{lab}_Гатин_Тимофей.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path), pagesize=A4, leftMargin=2.2*cm, rightMargin=2*cm,
        topMargin=1.9*cm, bottomMargin=1.8*cm,
        title=f"Лабораторная работа №{lab}. {TITLES[lab]}",
        author="Гатин Тимофей", subject="Технологии разработки программного обеспечения",
    )
    st = styles()
    story = [
        Spacer(1, 1.2*cm),
        Paragraph("Дисциплина «Технологии разработки программного обеспечения»", st["cover_top"]),
        Spacer(1, 3.2*cm),
        Paragraph(f"ОТЧЁТ<br/>ПО ЛАБОРАТОРНОЙ РАБОТЕ №{lab}", st["cover_title"]),
        Paragraph(TITLES[lab], st["cover_sub"]),
        Spacer(1, 1.2*cm),
        Paragraph("Сквозной проект «Система учёта заявок»", st["cover_top"]),
        Spacer(1, 4.2*cm),
        Paragraph("Выполнил: Гатин Тимофей<br/>Группа: еозИСИП-308<br/>Форма обучения: заочная", st["cover_meta"]),
        Spacer(1, 2.2*cm),
        Paragraph("03.11.2026", st["cover_top"]),
        PageBreak(),
    ]
    story.extend(parse_markdown(md_path, doc.width, st))
    doc.build(
        story,
        onFirstPage=lambda canvas, d: None,
        onLaterPages=lambda canvas, d: header_footer(canvas, d, lab),
    )
    return pdf_path


if __name__ == "__main__":
    for number in range(1, 6):
        print(build_report(number).relative_to(ROOT))
