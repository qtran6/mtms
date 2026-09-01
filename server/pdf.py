"""
pdf.py — Server-side aggregated-order PDF generator.

Same layout as the desktop app's printer.py, but takes pre-computed rows
(with brand already attached) and returns raw PDF bytes for HTTP delivery.
"""

import json
from io import BytesIO
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Table, TableStyle,
    NextPageTemplate, Spacer,
)

def _resource(name: str) -> Path:
    import sys
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base / name

_HERE = Path(__file__).parent
_FONTS_DIR = _resource("fonts")
_CONFIG_FILE = _resource("company.json")

_FONT_REGULAR = "Calibri"
_FONT_BOLD = "Calibri-Bold"

_fonts_registered = False

def _register_fonts() -> bool:
    global _fonts_registered
    if _fonts_registered:
        return True
    try:
        pdfmetrics.registerFont(TTFont(_FONT_REGULAR, str(_FONTS_DIR / "calibri.ttf")))
        pdfmetrics.registerFont(TTFont(_FONT_BOLD,    str(_FONTS_DIR / "calibrib.ttf")))
        _fonts_registered = True
        return True
    except Exception as e:
        print(f"[pdf] Could not register Calibri: {e}")
        return False


def _load_company_config() -> dict:
    try:
        return json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[pdf] Could not load company.json: {e}")
        return {}


# ── Page header drawing (unchanged from desktop) ─────────────────────────────────
def _draw_title_and_meta(canvas, y, customer, today, page_width):
    x = 8 * mm
    canvas.setFont(_FONT_BOLD, 10)
    canvas.drawCentredString(page_width / 2, y, "ĐƠN HÀNG")

    if customer:
        y -= 16
        canvas.setFont(_FONT_REGULAR, 8)
        canvas.drawString(x, y - 2, "TÊN KH")
        canvas.setFont(_FONT_BOLD, 20)
        canvas.drawCentredString(page_width / 2, y - 2, customer)

    y -= 14
    canvas.setFont(_FONT_BOLD, 8)
    canvas.drawRightString(page_width - 8 * mm, y, f"Ngày: {today}")


def _draw_first_page_header(canvas, doc):
    canvas.saveState()
    company = doc.company
    page_width, page_height = A5

    x = 8 * mm
    y = page_height - 8 * mm
    canvas.setFont(_FONT_BOLD, 8)
    canvas.drawString(x, y, company.get("company_name", ""))
    canvas.setFont(_FONT_REGULAR, 7)
    for line in [
        company.get("tagline_1", ""),
        company.get("tagline_2", ""),
        company.get("address", ""),
    ]:
        y -= 9
        canvas.drawString(x, y, line)
    canvas.setFont(_FONT_BOLD, 7)
    for line in [
        company.get("phone", ""),
        company.get("bank", ""),
    ]:
        y -= 9
        canvas.drawString(x, y, line)

    y -= 16
    _draw_title_and_meta(canvas, y, doc.customer, doc.today, page_width)
    canvas.restoreState()


def _draw_later_page_header(canvas, doc):
    canvas.saveState()
    page_width, page_height = A5
    y = page_height - 12 * mm
    _draw_title_and_meta(canvas, y, doc.customer, doc.today, page_width)
    canvas.restoreState()


# ── Table (unchanged from desktop) ───────────────────────────────────────────────
def _build_table(rows: list[dict], grand_total: int, border_thickness: int = 1) -> Table:
    header = ["TT", "Tên HH", "SL", "Đơn Giá", "Thành Tiền"]
    data = [header]
    for i, r in enumerate(rows, start=1):
        qty = str(r["qty"])
        price = f"{r['price']:,.0f}"
        total = f"{r['total']:,.0f}"
        data.append([str(i), r["name"], qty, price, total])
    data.append(["", "", "", "TỔNG CỘNG", f"{grand_total:,.0f}"])

    col_widths = [7 * mm, 70 * mm, 10 * mm, 24 * mm, 24 * mm]
    t = Table(data, colWidths=col_widths, repeatRows=1)

    style = TableStyle([
        ("FONTNAME",  (0, 0), (-1, -1), _FONT_BOLD),
        ("FONTSIZE",  (0, 0), (-1, -1), 13),
        ("ALIGN",     (0, 0), (0, -1),  "CENTER"),
        ("ALIGN",     (1, 0), (1, -1),  "LEFT"),
        ("ALIGN",     (2, 0), (2, -1),  "CENTER"),
        ("ALIGN",     (3, 0), (-1, -1), "RIGHT"),
        ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",      (0, 0), (-1, -2), border_thickness, colors.darkgray),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 2),

        ("FONTNAME",      (0, 0), (-1, 0), _FONT_BOLD),
        ("FONTSIZE",      (0, 0), (-1, 0), 8),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        ("VALIGN",        (0, 0), (-1, 0), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, 0), 2),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 2),

        ("FONTNAME",     (3, -1), (-1, -1), _FONT_BOLD),
        ("FONTSIZE",     (3, -1), (-1, -1), 14),
        ("TOPPADDING",   (0, -1), (-1, -1), 6),
        ("RIGHTPADDING", (3, -1), (3, -1),  12),
    ])
    t.setStyle(style)
    return t


def _estimate_orphan(row_count: int) -> bool:
    rows_per_first_page = 15
    rows_per_later_page = 16
    if row_count == rows_per_first_page:
        return True
    if row_count <= rows_per_first_page:
        return False
    remaining = row_count - rows_per_first_page
    return remaining % rows_per_later_page == 0


# ── Public entry point ───────────────────────────────────────────────────────────
def build_pdf(customer: str, rows: list[dict], border_thickness: int = 1) -> bytes:
    """
    Build the PDF from pre-aggregated rows.

    Args:
        customer: text for the "TÊN KH" line (can be empty).
        rows: list of {"brand", "name", "qty", "price", "total"}.
              qty/price/total are numeric. brand is used for sort only.
        border_thickness: passed through to the table style.

    Returns:
        The PDF as bytes. Raises RuntimeError if fonts are missing.
    """
    if not _register_fonts():
        raise RuntimeError("Không thể tải font Calibri từ server/fonts/")

    rows = sorted(rows, key=lambda x: (x.get("brand", "") == "", x.get("brand", "")))
    grand_total = sum(int(r["total"]) for r in rows)

    buf = BytesIO()
    doc = BaseDocTemplate(
        buf,
        pagesize=A5,
        leftMargin=0,
        rightMargin=0,
        topMargin=0,
        bottomMargin=10 * mm,
    )
    doc.company  = _load_company_config()
    doc.customer = (customer or "").strip()
    doc.today    = datetime.now().strftime("%d/%m/%Y")

    first_frame_height = A5[1] - (40 * mm) - doc.bottomMargin
    later_frame_height = A5[1] - (23 * mm) - doc.bottomMargin

    first_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, first_frame_height, showBoundary=0)
    later_frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, later_frame_height, showBoundary=0)

    doc.addPageTemplates([
        PageTemplate(id="first", frames=[first_frame], onPage=_draw_first_page_header),
        PageTemplate(id="later", frames=[later_frame], onPage=_draw_later_page_header),
    ])

    story = [NextPageTemplate("later")]
    if _estimate_orphan(len(rows)):
        story.append(Spacer(1, 8 * mm))
    story.append(_build_table(rows, grand_total, border_thickness))

    doc.build(story)
    return buf.getvalue()