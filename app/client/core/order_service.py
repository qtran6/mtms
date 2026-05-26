from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem


# ── Alignment constants ───────────────────────────────────────────────────────
ALIGN_LEFT   = Qt.AlignmentFlag.AlignLeft   | Qt.AlignmentFlag.AlignVCenter
ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter
ALIGN_RIGHT  = Qt.AlignmentFlag.AlignRight  | Qt.AlignmentFlag.AlignVCenter


# ── Data lookups ──────────────────────────────────────────────────────────────
def find_product(products: list[dict], brand: str, name: str) -> dict | None:
    for p in products:
        if p["brand"] == brand and p["name"] == name:
            return p
    return None


# ── Formatting ────────────────────────────────────────────────────────────────
def format_price(price: float) -> str:
    """Format price with thousand separators."""
    return f"{price:,.0f}"


def calc_total(quantity: int, price: float) -> float:
    """Calculate the total for a row."""
    return quantity * price


# ── Item factory ──────────────────────────────────────────────────────────────
def make_item(text: str, alignment=ALIGN_LEFT) -> QStandardItem:
    """Create a QStandardItem with the given text and alignment."""
    item = QStandardItem(text)
    item.setTextAlignment(alignment)
    return item