"""
order_service.py — business logic for the Order page.

Pure helpers stay at module level. UI glue lives in OrderController which
holds references to the widgets and wires up callbacks.
"""

from PySide6.QtCore import Qt, QTimer, QObject, QEvent
from PySide6.QtWidgets import QTableWidgetItem


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


def make_item(text: str, alignment=ALIGN_LEFT) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
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
        self._select_all_filter = self._SelectAllFilter(page)

    # ── Public bind point — called from OrderPage after widgets exist ─────────
    def bind(self):
        page = self.page
        page._brand_input.currentTextChanged.connect(self.on_brand_changed)
        page._submit_btn.clicked.connect(self.on_submit)
        page._model_input.lineEdit().returnPressed.connect(self.on_submit)
        page._model_input.lineEdit().installEventFilter(self._select_all_filter)

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

        # Skip if already in the table
        if self._is_duplicate(product["name"]):
            QTimer.singleShot(100, self._reset_model_input)
            return

        table = page._table_view

        target_row = self._find_first_empty_row()
        if target_row is None:
            target_row = table.rowCount()
            table.insertRow(target_row)

        table.setItem(target_row, 0, make_item(product["name"],          ALIGN_LEFT))
        table.setItem(target_row, 1, make_item("",                       ALIGN_CENTER))
        table.setItem(target_row, 2, make_item(format_price(product["price"]), ALIGN_RIGHT))
        table.setItem(target_row, 3, make_item("",                       ALIGN_RIGHT))

        QTimer.singleShot(100, self._reset_model_input)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _find_first_empty_row(self) -> int | None:
        table = self.page._table_view
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item is None or item.text().strip() == "":
                return row
        return None

    def _reset_model_input(self):
        m = self.page._model_input
        m.setCurrentIndex(-1)
        m.lineEdit().clear()
        m.setFocus()

    def _is_duplicate(self, name: str) -> bool:
        table = self.page._table_view
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item and item.text().strip() == name:
                return True
        return False

    # ── Nested filter ─────────────────────────────────────────────────────────
    class _SelectAllFilter(QObject):
        def eventFilter(self, obj, event):
            if event.type() == QEvent.Type.FocusIn:
                if hasattr(obj, "selectAll"):
                    QTimer.singleShot(0, obj.selectAll)
            return False