"""
printer.py — generates the order printout via ReportLab and opens it
              in the default PDF viewer where the user can print.

Layout:
- Page 1: full company info + ĐƠN HÀNG title + customer + date
- Later pages: ĐƠN HÀNG title + customer + date only (no company info)
- Table column header repeats on every page
- TỔNG CỘNG appears once at the very end
- Rows are sorted by brand
"""

import json
import os
import tempfile
import platform
from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Table, TableStyle, NextPageTemplate
)


_CONFIG_FILE = Path(__file__).parent.parent.parent / "data" / "company.json"

_FONT_REGULAR = "Calibri"
_FONT_BOLD = "Calibri-Bold"


def _register_fonts() -> bool:
    try:
        pdfmetrics.registerFont(TTFont(_FONT_REGULAR, r"C:\Windows\Fonts\calibri.ttf"))
        pdfmetrics.registerFont(TTFont(_FONT_BOLD,    r"C:\Windows\Fonts\calibrib.ttf"))
        return True
    except Exception as e:
        print(f"[printer] Could not register Calibri: {e}")
        return False


def _load_company_config() -> dict:
    try:
        return json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[printer] Could not load company.json: {e}")
        return {}


def _collect_rows(table, products_lookup: dict[str, str]) -> list[dict]:
    rows = []
    for r in range(table.rowCount()):
        name_item = table.item(r, 0)
        if not name_item or not name_item.text().strip():
            continue
        name  = name_item.text().strip()
        qty   = table.item(r, 1).text().strip() if table.item(r, 1) else ""
        price = table.item(r, 2).text().strip() if table.item(r, 2) else ""
        total = table.item(r, 3).text().strip() if table.item(r, 3) else ""
        if price.lower() in ("nan", "inf"): price = ""
        if total.lower() in ("nan", "inf"): total = ""
        brand = products_lookup.get(name, "")
        rows.append({"brand": brand, "name": name, "qty": qty, "price": price, "total": total})
    rows.sort(key=lambda x: (x["brand"] == "", x["brand"]))
    return rows


def _parse_total(text: str) -> int:
    try:
        return int(text.replace(",", ""))
    except (ValueError, AttributeError):
        return 0


# ── Page header drawing ──────────────────────────────────────────────────────────
def _draw_title_and_meta(canvas, y, customer, today, page_width):
    """Draw ĐƠN HÀNG title + (customer) + date starting at y, going downward."""
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
    customer = doc.customer
    today = doc.today
    page_width, page_height = A5

    # Company block
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

    # Title + customer + date below the company block
    y -= 16
    _draw_title_and_meta(canvas, y, customer, today, page_width)
    canvas.restoreState()


def _draw_later_page_header(canvas, doc):
    canvas.saveState()
    customer = doc.customer
    today = doc.today
    page_width, page_height = A5

    y = page_height - 12 * mm
    _draw_title_and_meta(canvas, y, customer, today, page_width)
    canvas.restoreState()


# ── Table ────────────────────────────────────────────────────────────────────────
def _build_table(rows: list[dict], grand_total: int) -> Table:
    header = ["TT", "Tên HH", "SL", "Đơn Giá", "Thành Tiền"]
    data = [header]
    for i, r in enumerate(rows, start=1):
        data.append([str(i), r["name"], r["qty"], r["price"], r["total"]])
    data.append(["", "", "", "TỔNG CỘNG", f"{grand_total:,}"])

    col_widths = [7 * mm, 70 * mm, 10 * mm, 24 * mm, 24 * mm]
    t = Table(data, colWidths=col_widths, repeatRows=1)

    style = TableStyle([
        # Data rows (applied first, overridden by header rules below)
        ("FONTNAME",  (0, 0), (-1, -1), _FONT_BOLD),
        ("FONTSIZE",  (0, 0), (-1, -1), 13),
        ("ALIGN",     (0, 0), (0, -1),  "CENTER"),
        ("ALIGN",     (1, 0), (1, -1),  "LEFT"),
        ("ALIGN",     (2, 0), (2, -1),  "CENTER"),
        ("ALIGN",     (3, 0), (-1, -1), "RIGHT"),
        ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",      (0, 0), (-1, -2), 0.5, colors.darkgray),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 2),
        ("LEFTPADDING",   (0, 0), (-1, -1), 2),

        # Header row — applied AFTER so it wins ----------------------------
        ("FONTNAME",      (0, 0), (-1, 0), _FONT_BOLD),
        ("FONTSIZE",      (0, 0), (-1, 0), 8),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        ("VALIGN",        (0, 0), (-1, 0), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, 0), 2),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 2),

        # TỔNG CỘNG row ----------------------------------------------------
        ("FONTNAME",   (3, -1), (-1, -1), _FONT_BOLD),
        ("FONTSIZE",   (3, -1), (-1, -1), 14),
        ("TOPPADDING", (0, -1), (-1, -1), 6),
    ])
    t.setStyle(style)
    return t


# ── Output ───────────────────────────────────────────────────────────────────────
def _open_pdf(pdf_path: str):
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(pdf_path)
        elif system == "Darwin":
            os.system(f'open "{pdf_path}"')
        else:
            os.system(f'xdg-open "{pdf_path}"')
    except Exception as e:
        print(f"[printer] Could not open PDF: {e}")


def print_order(parent, customer, table, products):
    """Generate the PDF and open it in the default PDF viewer."""
    if not _register_fonts():
        return

    company = _load_company_config()
    lookup = {p["name"]: p["brand"] for p in products}

    rows = _collect_rows(table, lookup)
    if not rows:
        return

    grand_total = sum(_parse_total(r["total"]) for r in rows)

    fd, pdf_path = tempfile.mkstemp(suffix=".pdf", prefix="order_")
    os.close(fd)

    doc = BaseDocTemplate(
        pdf_path,
        pagesize=A5,
        leftMargin=0,
        rightMargin=0,
        topMargin=0,
        bottomMargin=10 * mm,
    )
    doc.company  = company
    doc.customer = customer.strip()
    doc.today    = datetime.now().strftime("%d/%m/%Y")

    # First page reserves more vertical space at the top for company info
    first_frame_height = A5[1] - 40 * mm - doc.bottomMargin
    later_frame_height = A5[1] - 25 * mm - doc.bottomMargin

    first_frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, first_frame_height,
        showBoundary=0,
    )
    later_frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, later_frame_height,
        showBoundary=0,
    )

    doc.addPageTemplates([
        PageTemplate(id="first", frames=[first_frame], onPage=_draw_first_page_header),
        PageTemplate(id="later", frames=[later_frame], onPage=_draw_later_page_header),
    ])

    story = [
        NextPageTemplate("later"),  # any subsequent page uses 'later'
        _build_table(rows, grand_total),
    ]
    doc.build(story)

    _open_pdf(pdf_path)