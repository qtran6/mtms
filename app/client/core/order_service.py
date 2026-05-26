"""
order_service.py — business logic for the Order page.

Pure helpers stay at module level. UI glue lives in OrderController which
holds references to the widgets and wires up callbacks.
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QStandardItem


# ── Alignment constants ───────────────────────────────────────────────────────
ALIGN_LEFT   = Qt.AlignmentFlag.AlignLeft   | Qt.AlignmentFlag.AlignVCenter
ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter
ALIGN_RIGHT  = Qt.AlignmentFlag.AlignRight  | Qt.AlignmentFlag.AlignVCenter


# ── Pure data helpers ─────────────────────────────────────────────────────────
def find_product(products: list[dict], brand: str, name: str) -> dict | None:
    for p in products:
        if p["brand"] == brand and p["name"] == name:
            return p
    return None


def names_for_brand(products: list[dict], brand: str) -> list[str]:
    return [p["name"] for p in products if p["brand"] == brand]


def format_price(price: float) -> str:
    return f"{price:,.0f}"


def calc_total(quantity: int, price: float) -> float:
    return quantity * price


def make_item(text: str, alignment=ALIGN_LEFT) -> QStandardItem:
    item = QStandardItem(text)
    item.setTextAlignment(alignment)
    return item


# ── Controller — owns the widget references and event handlers ────────────────
class OrderController:
    """
    Wires up the Order page widgets. Holds references and handles user actions.
    Call `bind()` after the widgets are created and stored on the page.
    """

    def __init__(self, page):
        self.page = page  # reference to OrderPage instance

    # Public bind point — called from OrderPage after widgets exist
    def bind(self):
        page = self.page
        page._brand_input.currentTextChanged.connect(self.on_brand_changed)
        page._submit_btn.clicked.connect(self.on_submit)
        page._model_input.lineEdit().returnPressed.connect(self.on_submit)

    # ── Brand changed: refill name combo ──────────────────────────────────────
    def on_brand_changed(self, text: str):
        from client.core.completer import combo_completer
        names = names_for_brand(self.page._products, text)
        m = self.page._model_input
        m.clear()
        m.addItems(names)
        m.setCurrentIndex(-1)
        m.lineEdit().setPlaceholderText("Nhập tên hàng hóa...")
        combo_completer(m)

    # ── Submit: add row to table ──────────────────────────────────────────────
    def on_submit(self):
        page = self.page
        brand = page._brand_input.currentText().strip()
        name  = page._model_input.currentText().strip()

        if not brand or not name:
            return

        product = find_product(page._products, brand, name)
        if not product:
            return

        target_row = self._find_first_empty_row()
        if target_row is None:
            target_row = page._table_model.rowCount()
            page._table_model.insertRow(target_row)

        m = page._table_model
        m.setItem(target_row, 0, make_item(product["name"], ALIGN_LEFT))
        m.setItem(target_row, 1, make_item("",                 ALIGN_CENTER))
        m.setItem(target_row, 2, make_item(format_price(product["price"]), ALIGN_RIGHT))
        m.setItem(target_row, 3, make_item("",                 ALIGN_RIGHT))

        QTimer.singleShot(100, self._reset_model_input)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _find_first_empty_row(self) -> int | None:
        m = self.page._table_model
        for row in range(m.rowCount()):
            item = m.item(row, 0)
            if item is None or item.text().strip() == "":
                return row
        return None

    def _reset_model_input(self):
        m = self.page._model_input
        m.setCurrentIndex(-1)
        m.lineEdit().clear()
        m.setFocus()