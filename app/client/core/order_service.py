"""
order_service.py — business logic for the Order page.

Pure helpers stay at module level. UI glue lives in OrderController which
holds references to the widgets and wires up callbacks.
"""

from PySide6.QtCore import Qt, QTimer, QObject, QEvent
from PySide6.QtWidgets import QTableWidgetItem

from client.ui.custom_widgets.event_filters import *
from client.core.draft_service import save_draft, load_draft


# Alignment constants ---------------------------------------------------------------------
ALIGN_LEFT   = Qt.AlignmentFlag.AlignLeft   | Qt.AlignmentFlag.AlignVCenter
ALIGN_CENTER = Qt.AlignmentFlag.AlignCenter
ALIGN_RIGHT  = Qt.AlignmentFlag.AlignRight  | Qt.AlignmentFlag.AlignVCenter


# Pure data helpers -----------------------------------------------------------------------
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


# Controller - owns the widget references and event handlers -------------------------
class OrderController:
    """
    Wires up the Order page widgets. Holds references and handles user actions.
    Call `bind()` after the widgets are created and stored on the page.
    """

    def __init__(self, page):
        self.page = page  # reference to OrderPage instance
        self._select_all_filter = self._SelectAllFilter(page)

    # Public bind point — called from OrderPage after widgets exist ------------------
    def bind(self):
        page = self.page
        page._brand_input.currentTextChanged.connect(self.on_brand_changed)
        page._submit_btn.clicked.connect(self.on_submit)
        page._model_input.lineEdit().returnPressed.connect(self.on_submit)
        page._model_input.lineEdit().installEventFilter(self._select_all_filter)
        page._table_view.cellChanged.connect(self.on_cell_changed)
        page._clear_btn.clicked.connect(self.on_clear)
        page._print_btn.clicked.connect(self.on_print)
        self._enter_down_filter = EnterDownFilter(self.page)
        self.page._table_view.installEventFilter(self._enter_down_filter)
        self._delete_filter = DeleteCellFilter(self.page)
        self.page._table_view.installEventFilter(self._delete_filter)

    # Brand changed: refill name combo
    def on_brand_changed(self, text: str):
        from client.core.completer import combo_completer
        names = names_for_brand(self.page._products, text)
        m = self.page._model_input
        m.clear()
        m.addItems(names)
        m.setCurrentIndex(-1)
        m.lineEdit().setPlaceholderText("Nhập tên hàng hóa...")
        combo_completer(m)

    # Submit: add item to table --------------------------------------------------
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

        table.blockSignals(True)
        table.setItem(target_row, 0, make_item(product["name"], ALIGN_LEFT))
        table.setItem(target_row, 1, make_item("", ALIGN_CENTER))
        table.setItem(target_row, 2, make_item(format_price(product["price"]), ALIGN_RIGHT))
        table.setItem(target_row, 3, make_item("", ALIGN_RIGHT))
        table.blockSignals(False)

        QTimer.singleShot(100, self._reset_model_input)

        self._update_grand_total()

    # Clear table ----------------------------------------------------------------
    def on_clear(self):
        page = self.page

        # Clear table
        page._table_view.blockSignals(True)
        page._table_view.setRowCount(0)
        page._table_view.blockSignals(False)

        # Clear inputs
        page._customer_text_box.clear()
        page._brand_input.setCurrentIndex(-1)
        page._model_input.clear()
        page._model_input.lineEdit().clear()

        # Focus back to customer name
        page._customer_text_box.setFocus()

        self._update_grand_total()

    # Cell change events -----------------------------------------------------------
    def on_cell_changed(self, row: int, col: int):
        if col not in (1, 2):  # only quantity and price changes affect total
            return

        table = self.page._table_view
        qty_item = table.item(row, 1)
        price_item = table.item(row, 2)
        if not qty_item or not price_item:
            return
        
        qty_text = qty_item.text().strip()
        price_text = price_item.text().strip()
        if not qty_text or not price_text:
            table.blockSignals(True)
            table.setItem(row, 3, make_item("", ALIGN_RIGHT))
            table.blockSignals(False)
            return

        try:
            qty = int(qty_item.text().strip())
        except ValueError:
            table.blockSignals(True)
            table.setItem(row, 3, make_item("", ALIGN_RIGHT))
            table.blockSignals(False)
            return

        try:
            price = float(price_item.text().replace(",", ""))
        except ValueError:
            return

        total = calc_total(qty, price)

        table.blockSignals(True)
        table.setItem(row, 2, make_item(format_price(price), ALIGN_RIGHT))  # reformat price
        table.setItem(row, 3, make_item(format_price(total), ALIGN_RIGHT))
        table.blockSignals(False)

        self._update_grand_total()

    # Print order ----------------------------------------------------------------
    def on_print(self):
        from client.core.printer import print_order
        page = self.page
        print_order(
            parent=page,
            customer=page._customer_text_box.text(),
            table=page._table_view,
            products=page._products,
        )

    # Helpers ----------------------------------------------------------------------
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

    # Nested filter ----------------------------------------------------------------
    class _SelectAllFilter(QObject):
        def eventFilter(self, obj, event):
            if event.type() == QEvent.Type.FocusIn:
                if hasattr(obj, "selectAll"):
                    QTimer.singleShot(0, obj.selectAll)
            return False

    def save_state(self):
        page = self.page
        table = page._table_view

        rows = []
        for r in range(table.rowCount()):
            name_item = table.item(r, 0)
            if not name_item or not name_item.text().strip():
                continue
            rows.append({
                "name":  name_item.text().strip(),
                "qty":   table.item(r, 1).text().strip() if table.item(r, 1) else "",
                "price": table.item(r, 2).text().strip() if table.item(r, 2) else "",
                "total": table.item(r, 3).text().strip() if table.item(r, 3) else "",
            })

        save_draft({
            "customer": page._customer_text_box.text(),
            "rows": rows,
        })

    def restore_state(self):
        data = load_draft()
        if not data:
            return

        page = self.page
        page._customer_text_box.setText(data.get("customer", ""))

        table = page._table_view
        table.blockSignals(True)
        for row in data.get("rows", []):
            r = table.rowCount()
            table.insertRow(r)
            table.setItem(r, 0, make_item(row["name"],  ALIGN_LEFT))
            table.setItem(r, 1, make_item(row["qty"],   ALIGN_CENTER))
            table.setItem(r, 2, make_item(row["price"], ALIGN_RIGHT))
            table.setItem(r, 3, make_item(row["total"], ALIGN_RIGHT))
        table.blockSignals(False)

        self._update_grand_total()

    def _update_grand_total(self):
        table = self.page._table_view
        total = 0
        for r in range(table.rowCount()):
            item = table.item(r, 3)
            if not item:
                continue
            try:
                total += int(item.text().replace(",", ""))
            except (ValueError, AttributeError):
                pass
        self.page._grand_total_label.setText(f"Tổng cộng: {total:,}")