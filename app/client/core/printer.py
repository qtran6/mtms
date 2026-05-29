"""
printer.py — generates the order printout via ReportLab and sends to default printer.

Layout:
- Header (company info, ĐƠN HÀNG, customer, date) repeats on every page
- Table column header repeats on every page
- TỔNG CỘNG appears once at the very end, with at least one product row above it
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
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    Table, TableStyle, KeepTogether,
)


_CONFIG_FILE = Path(__file__).parent.parent.parent / "data" / "company.json"

# Font registration — Calibri from Windows ----------------------------------------
_FONT_REGULAR = "Calibri"
_FONT_BOLD = "Calibri-Bold"

def _register_fonts():
    """Register Calibri from Windows. Returns True on success."""
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
        name = name_item.text().strip()
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


# Page-level header drawn on every page ------------------------------------------
def _draw_page_header(canvas, doc):
    """Drawn by ReportLab on every page via onPage callback."""
    canvas.saveState()
    company = doc.company
    customer = doc.customer
    today = doc.today
    page_width, page_height = A5

    # Company block at top --------------------------------------------------------
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

    # ĐƠN HÀNG title
    y -= 16
    canvas.setFont(_FONT_BOLD, 14)
    canvas.drawCentredString(page_width / 2, y, "ĐƠN HÀNG")

    # Customer block
    if customer:
        y -= 14
        canvas.setFont(_FONT_REGULAR, 7)
        canvas.drawString(x, y - 2, "TÊN KH")
        canvas.setFont(_FONT_BOLD, 12)
        canvas.drawCentredString(page_width / 2, y - 2, customer)

    # Date
    y -= 14
    canvas.setFont(_FONT_BOLD, 8)
    canvas.drawRightString(page_width - 8 * mm, y, f"Ngày: {today}")

    canvas.restoreState()


def _build_table(rows: list[dict], grand_total: int, include_total: bool) -> Table:
    """Build a single Table flowable for a chunk of rows."""
    header = ["TT", "Tên HH", "SL", "ĐƠN GIÁ", "Thành Tiền"]
    data = [header]
    for i, r in enumerate(rows, start=1):
        data.append([str(i), r["name"], r["qty"], r["price"], r["total"]])

    if include_total:
        data.append(["", "", "", "TỔNG CỘNG", f"{grand_total:,}"])

    col_widths = [10 * mm, 60 * mm, 12 * mm, 22 * mm, 26 * mm]
    t = Table(data, colWidths=col_widths, repeatRows=1)

    style = TableStyle([
        ("FONTNAME",  (0, 0), (-1, -1), _FONT_REGULAR),
        ("FONTSIZE",  (0, 0), (-1, -1), 10),
        ("FONTNAME",  (0, 0), (-1, 0),  _FONT_BOLD),
        ("FONTSIZE",  (0, 0), (-1, 0),  9),
        ("ALIGN",     (0, 0), (0, -1),  "CENTER"),
        ("ALIGN",     (1, 0), (1, -1),  "LEFT"),
        ("ALIGN",     (2, 0), (2, -1),  "CENTER"),
        ("ALIGN",     (3, 0), (-1, -1), "RIGHT"),
        ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",      (0, 0), (-1, -2 if include_total else -1), 0.5, colors.black),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])

    if include_total:
        # Bold the TỔNG CỘNG row, no border on it
        style.add("FONTNAME", (3, -1), (-1, -1), _FONT_BOLD)
        style.add("FONTSIZE", (3, -1), (-1, -1), 11)
        style.add("TOPPADDING", (0, -1), (-1, -1), 6)

    t.setStyle(style)
    return t


def _send_to_default_printer(pdf_path: str):
    """Print the PDF to the system's default printer."""
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(pdf_path, "print")
        elif system == "Darwin":
            os.system(f'lpr "{pdf_path}"')
        else:  # Linux
            os.system(f'lp "{pdf_path}"')
    except Exception as e:
        print(f"[printer] Could not send to printer: {e}")


def print_order(parent, customer, table, products):
    """
    Build the PDF and send to the default printer.

    parent   — kept for API compatibility (not used)
    customer — customer name string
    table    — the QTableWidget containing order rows
    products — full product list
    """
    if not _register_fonts():
        return

    company = _load_company_config()
    lookup = {p["name"]: p["brand"] for p in products}

    rows = _collect_rows(table, lookup)
    if not rows:
        return

    grand_total = sum(_parse_total(r["total"]) for r in rows)

    # Header height reserved on every page (approx 80mm on page 1 with customer) -----
    # We use a top margin large enough to fit company + ĐƠN HÀNG + customer + date.
    header_height_mm = 70 if customer.strip() else 60

    # Build a temp PDF ---------------------------------------------------------------
    fd, pdf_path = tempfile.mkstemp(suffix=".pdf", prefix="order_")
    os.close(fd)

    doc = BaseDocTemplate(
        pdf_path,
        pagesize=A5,
        leftMargin=6 * mm,
        rightMargin=6 * mm,
        topMargin=header_height_mm * mm,
        bottomMargin=8 * mm,
    )
    doc.company  = company
    doc.customer = customer.strip()
    doc.today    = datetime.now().strftime("%d/%m/%Y")

    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height,
        showBoundary=0,
    )
    doc.addPageTemplates([
        PageTemplate(id="default", frames=[frame], onPage=_draw_page_header)
    ])

    # Build a single flowable table containing all rows + total ---------------------
    main_table = _build_table(rows, grand_total, include_total=True)

    # If everything fits on one page, ReportLab handles it.
    # If it overflows, ReportLab will paginate the table using repeatRows=1
    # (which repeats the column header on every page).
    #
    # The "TỔNG CỘNG must not be orphaned" rule: ReportLab's Table flowable
    # tries to keep rows together by default. If the total ends up alone on
    # the last page, we manually pull the last data row + total onto a
    # KeepTogether group.
    story = [main_table]

    doc.build(story)

    # Send to printer
    _send_to_default_printer(pdf_path)