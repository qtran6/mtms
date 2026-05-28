"""
printer.py — builds the order printout and sends it to the printer.
"""

import json
from datetime import datetime
from pathlib import Path

from PySide6.QtGui import QTextDocument, QPageSize, QPageLayout
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtCore import QMarginsF


_CONFIG_FILE = Path(__file__).parent.parent.parent / "data" / "company.json"
_QR_FILE     = Path(__file__).parent.parent.parent / "data" / "qr.png"


def _load_company_config() -> dict:
    try:
        return json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[printer] Could not load company.json: {e}")
        return {}


def _collect_rows(table, products_lookup: dict[str, str]) -> list[dict]:
    """
    Walk the table, keep only rows with a non-empty product name,
    and tag each with its brand for sorting.

    products_lookup: {product_name: brand} — built once for fast brand lookup.
    """
    rows = []
    for r in range(table.rowCount()):
        name_item = table.item(r, 0)
        if not name_item or not name_item.text().strip():
            continue
        name = name_item.text().strip()
        qty  = table.item(r, 1).text().strip() if table.item(r, 1) else ""
        price = table.item(r, 2).text().strip() if table.item(r, 2) else ""
        total = table.item(r, 3).text().strip() if table.item(r, 3) else ""
        brand = products_lookup.get(name, "")
        rows.append({
            "brand": brand,
            "name":  name,
            "qty":   qty,
            "price": price,
            "total": total,
        })

    # Sort by brand — items without brand info go last
    rows.sort(key=lambda x: (x["brand"] == "", x["brand"]))
    return rows


def _parse_total(text: str) -> int:
    """Parse '1,700,000' → 1700000."""
    try:
        return int(text.replace(",", ""))
    except (ValueError, AttributeError):
        return 0


def _build_html(customer: str, rows: list[dict], company: dict) -> str:
    today = datetime.now().strftime("%d/%m/%Y")
    grand_total = sum(_parse_total(r["total"]) for r in rows)

    rows_html = ""
    for i, r in enumerate(rows, start=1):
        price = r["price"] if r["price"].lower() not in ("nan", "inf") else ""
        total = r["total"] if r["total"].lower() not in ("nan", "inf") else ""
        rows_html += f"""
            <tr>
                <td align="center" style="padding-top: 6px; padding-bottom: 6px;">{i}</td>
                <td style="padding-top: 6px; padding-bottom: 6px;"><b>{r['name']}</b></td>
                <td align="center" style="padding-top: 6px; padding-bottom: 6px;"><b>{r['qty']}</b></td>
                <td align="right" style="padding-top: 6px; padding-bottom: 6px;"><b>{price}</b></td>
                <td align="right" style="padding-top: 6px; padding-bottom: 6px;"><b>{total}</b></td>
            </tr>
        """

    customer_html = ""
    if customer.strip():
        customer_html = f"""
            <table width="100%" cellpadding="1" cellspacing="0" style="margin: 0;">
                <tr>
                    <td width="15%" style="font-size: 7pt; vertical-align: middle;">TÊN KH</td>
                    <td align="center" style="font-size: 14pt; vertical-align: middle;"><b>{customer}</b></td>
                    <td width="15%"></td>
                </tr>
            </table>
        """

    return f"""
    <html><body style="font-family: 'Calibri'; font-size: 6pt; color: #000; margin: 0;">
        <table width="100%" cellpadding="0" cellspacing="0" style="margin: 0;">
            <tr>
                <td>
                    <div><b>{company.get('company_name', '')}</b></div>
                    <div>{company.get('tagline_1', '')}</div>
                    <div>{company.get('tagline_2', '')}</div>
                    <div>{company.get('address', '')}</div>
                    <div><b>{company.get('phone', '')}</b></div>
                    <div><b>{company.get('bank', '')}</b></div>
                </td>
            </tr>
        </table>

        <div align="center" style="font-size: 10pt; margin: 4px 0;"><b>ĐƠN HÀNG</b></div>

        {customer_html}

        <div align="right" style="margin: 4px 0;"><b>Ngày: {today}</b></div>

        <table width="100%" border="1" cellpadding="1" cellspacing="0" style="font-size: 9pt;">
             <thead style="font-size: 6pt;">
                <tr>
                    <th width="5%" align="center">TT</th>
                    <th>Tên HH</th>
                    <th width="7%" align="center">SL</th>
                    <th width="15%" align="center">ĐƠN GIÁ</th>
                    <th width="18%" align="center">Thành Tiền</th>
                </tr>
            </thead>
            {rows_html}
        </table>

        <table width="100%" cellpadding="4" cellspacing="0" style="margin-top: 4px; font-size: 10pt;">
            <tr>
                <td align="right"><b>TỔNG CỘNG</b></td>
                <td align="right" width="22%">
                    <b>{grand_total:,}</b>
                </td>
            </tr>
        </table>
    </body></html>
    """


def print_order(parent, customer, table, products):
    company = _load_company_config()
    lookup = {p["name"]: p["brand"] for p in products}

    rows = _collect_rows(table, lookup)
    if not rows:
        return

    html = _build_html(customer.strip(), rows, company)

    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setPageSize(QPageSize(QPageSize.PageSizeId.A5))
    printer.setPageMargins(QMarginsF(0, 0, 0, 0), QPageLayout.Unit.Millimeter)

    doc = QTextDocument()
    doc.setDocumentMargin(0)
    # Match document page size to printer — disables auto page number footer
    doc.setPageSize(printer.pageRect(QPrinter.Unit.Point).size())
    doc.setHtml(html)

    dialog = QPrintDialog(printer, parent)
    if dialog.exec() == QPrintDialog.DialogCode.Accepted:
        doc.print_(printer)