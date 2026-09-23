import html
import re
import uuid
from pathlib import Path

from langchain_core.tools import tool
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer


OUTPUT_DIRECTORY = Path(__file__).resolve().parent.parent / "output" / "pdf"
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def markdown_to_pdf(markdown_text: str) -> str:
    """Render the supported travel-plan Markdown subset to a local PDF file."""
    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TravelTitle",
        parent=styles["Title"],
        fontName="STSong-Light",
        fontSize=20,
        leading=28,
        alignment=TA_CENTER,
        spaceAfter=14,
    )
    heading_style = ParagraphStyle(
        "TravelHeading",
        parent=styles["Heading2"],
        fontName="STSong-Light",
        fontSize=14,
        leading=20,
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "TravelBody",
        parent=styles["BodyText"],
        fontName="STSong-Light",
        fontSize=10.5,
        leading=18,
        spaceAfter=5,
    )

    story = []
    for raw_line in markdown_text.splitlines():
        line = raw_line.strip()
        if not line:
            story.append(Spacer(1, 0.15 * cm))
            continue

        image_match = IMAGE_PATTERN.fullmatch(line)
        if image_match:
            image_path = Path(image_match.group(1))
            if image_path.is_file():
                image = Image(str(image_path))
                image._restrictSize(16 * cm, 11 * cm)
                story.extend([image, Spacer(1, 0.25 * cm)])
            continue

        if line.startswith("# "):
            story.append(Paragraph(format_inline(line[2:]), title_style))
        elif line.startswith("## "):
            story.append(Paragraph(format_inline(line[3:]), heading_style))
        elif line.startswith("- "):
            story.append(Paragraph(f"• {format_inline(line[2:])}", body_style))
        else:
            story.append(Paragraph(format_inline(line), body_style))

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    pdf_path = OUTPUT_DIRECTORY / f"travel-plan-{uuid.uuid4()}.pdf"
    document = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
    )
    document.build(story)
    return str(pdf_path)


def format_inline(text: str) -> str:
    escaped = html.escape(text)
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)


@tool("create_travel_pdf")
def create_travel_pdf(markdown_text: str) -> str:
    """将旅行方案 Markdown 生成 PDF，并返回本地 PDF 文件路径。"""
    return markdown_to_pdf(markdown_text)
