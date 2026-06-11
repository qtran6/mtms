"""
order_service.py — business logic for the Order page.

Pure helpers stay at module level. UI glue lives in OrderController which
holds references to the widgets and wires up callbacks.
"""

from PySide6.QtCore import Qt, QTimer, QObject, QEvent
from PySide6.QtWidgets import QTableWidgetItem, QPushButton

from client.core.completer import combo_completer
from client.core.draft_service import save_draft, load_draft
from client.ui.custom_widgets import *
from client.core.printer import print_order
from client.core.config_service import load_config


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


# ── Controller ────────────────────────────────────────────────────────────────
class OrderController:
    """
    Owns multi-tab state and event handlers for the Order page.
    """

    def __init__(self, page):
        self.page = page
        self._select_all_filter = self._SelectAllFilter(page)
        self._enter_down_filter = EnterDownFilter(page)
        self._delete_filter = DeleteCellFilter(page)

        # Multi-tab state
        self._tabs: list[dict] = []     # list of saved tab states
        self._active_tab: int = 0
        self._tab_buttons: list = []    # list of TabButton widgets
        self._plus_btn: QPushButton | None = None

    # ── Bind ──────────────────────────────────────────────────────────────────
    def bind(self):
        page = self.page
        page._brand_input.currentTextChanged.connect(self.on_brand_changed)
        page._submit_btn.clicked.connect(self.on_submit)
        page._model_input.lineEdit().returnPressed.connect(self.on_submit)
        page._model_input.lineEdit().installEventFilter(self._select_all_filter)
        page._table_view.cellChanged.connect(self.on_cell_changed)
        page._clear_btn.clicked.connect(self.on_clear)
        page._print_btn.clicked.connect(self.on_print)
        page._table_view.installEventFilter(self._enter_down_filter)
        page._table_view.installEventFilter(self._delete_filter)
        page._duplicate_tab_btn.clicked.connect(self._duplicate_current_tab)

    # ── Brand changed ─────────────────────────────────────────────────────────
    def on_brand_changed(self, text: str):
        names = names_for_brand(self.page._products, text)
        m = self.page._model_input
        m.clear()
        m.addItems(names)
        m.setCurrentIndex(-1)
        m.lineEdit().setPlaceholderText("Nhập tên hàng hóa...")
        combo_completer(m)

    # ── Submit: add row ───────────────────────────────────────────────────────
    def on_submit(self):
        page = self.page
        brand = page._brand_input.currentText().strip()
        name  = page._model_input.currentText().strip()

        if not name:
            return  # name is required

        product = find_product(page._products, brand, name)

        # If not found in catalog, allow as custom item with empty price
        if not product:
            product = {"brand": brand, "name": name, "price": 0}

        if self._is_duplicate(product["name"]):
            QTimer.singleShot(100, self._reset_model_input)
            return

        table = page._table_view
        target_row = self._find_first_empty_row()
        if target_row is None:
            target_row = table.rowCount()
            table.insertRow(target_row)

        # If custom item (price is 0), leave price cell empty so user can fill in
        price_text = format_price(product["price"]) if product["price"] > 0 else ""

        table.blockSignals(True)
        table.setItem(target_row, 0, make_item(product["name"], ALIGN_LEFT))
        table.setItem(target_row, 1, make_item("", ALIGN_CENTER))
        table.setItem(target_row, 2, make_item(price_text, ALIGN_RIGHT))
        table.setItem(target_row, 3, make_item("", ALIGN_RIGHT))
        table.blockSignals(False)

        # Scroll the table to show the new row
        table.setCurrentCell(target_row, 0)

        self._update_grand_total()
        QTimer.singleShot(100, self._reset_model_input)

    # ── Clear ─────────────────────────────────────────────────────────────────
    def on_clear(self):
        page = self.page
        page._table_view.blockSignals(True)
        page._table_view.setRowCount(0)
        page._table_view.blockSignals(False)
        page._customer_text_box.clear()
        page._brand_input.setCurrentIndex(-1)
        page._model_input.clear()
        page._model_input.lineEdit().clear()
        page._customer_text_box.setFocus()
        self._update_grand_total()

    # ── Cell changed ──────────────────────────────────────────────────────────
    def on_cell_changed(self, row: int, col: int):
        if col not in (1, 2):
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
            self._update_grand_total()
            return

        try:
            qty = int(qty_text)
            price = float(price_text.replace(",", ""))
            if price < 5000:
                price = price * 1000
        except ValueError:
            table.blockSignals(True)
            table.setItem(row, 3, make_item("", ALIGN_RIGHT))
            table.blockSignals(False)
            self._update_grand_total()
            return

        total = calc_total(qty, price)
        table.blockSignals(True)
        table.setItem(row, 2, make_item(format_price(price), ALIGN_RIGHT))
        table.setItem(row, 3, make_item(format_price(total), ALIGN_RIGHT))
        table.blockSignals(False)
        self._update_grand_total()

    # ── Print ─────────────────────────────────────────────────────────────────
    def on_print(self):
        page = self.page
        try:
            pdf_path = print_order(
                parent=page,
                customer=page._customer_text_box.text(),
                table=page._table_view,
                products=page._products,
                border_thickness=load_config().get("border_thickness", 1),
            )
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(page, "Lỗi in", f"Không tạo được phiếu in:\n{e}")
            return
        if pdf_path:
            window = page.window()
            if hasattr(window, "show_print_preview"):
                window.show_print_preview(pdf_path)
                
    # ── Grand total ───────────────────────────────────────────────────────────
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

    # ── Row helpers ───────────────────────────────────────────────────────────
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

    # ── Tab management ────────────────────────────────────────────────────────
    def _capture_current_state(self) -> dict:
        """Collect the current widgets' values into a dict."""
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
        return {
            "customer": page._customer_text_box.text(),
            "rows": rows,
        }

    def _apply_state(self, state: dict):
        """Load a tab's state into the widgets."""
        page = self.page
        page._table_view.blockSignals(True)
        page._table_view.setRowCount(0)
        for row in state.get("rows", []):
            r = page._table_view.rowCount()
            page._table_view.insertRow(r)
            page._table_view.setItem(r, 0, make_item(row.get("name", ""),  ALIGN_LEFT))
            page._table_view.setItem(r, 1, make_item(row.get("qty", ""),   ALIGN_CENTER))
            page._table_view.setItem(r, 2, make_item(row.get("price", ""), ALIGN_RIGHT))
            page._table_view.setItem(r, 3, make_item(row.get("total", ""), ALIGN_RIGHT))
        page._table_view.blockSignals(False)
        page._customer_text_box.setText(state.get("customer", ""))
        self._update_grand_total()

    def _switch_to_tab(self, index: int):
        if index == self._active_tab or not (0 <= index < len(self._tabs)):
            return
        # Save current widget state into the active tab
        self._tabs[self._active_tab] = self._capture_current_state()
        # Switch
        self._active_tab = index
        self._apply_state(self._tabs[index])
        self._refresh_tab_bar()

    def _new_tab(self):
        # Save current widget state
        if self._tabs:
            self._tabs[self._active_tab] = self._capture_current_state()
        # Append a fresh empty tab
        self._tabs.append({"customer": "", "rows": []})
        self._active_tab = len(self._tabs) - 1
        self._apply_state(self._tabs[self._active_tab])
        self._refresh_tab_bar()

    def _close_tab(self, index: int):
        if not (0 <= index < len(self._tabs)):
            return

        # Capture current state if we're closing the active tab
        # (so we discard the right one)
        if index == self._active_tab:
            # Don't bother capturing — we're throwing it away
            pass
        else:
            self._tabs[self._active_tab] = self._capture_current_state()

        del self._tabs[index]

        # Ensure at least one tab exists
        if not self._tabs:
            self._tabs.append({"customer": "", "rows": []})
            self._active_tab = 0
        elif self._active_tab >= len(self._tabs):
            self._active_tab = len(self._tabs) - 1
        elif index < self._active_tab:
            self._active_tab -= 1

        self._apply_state(self._tabs[self._active_tab])
        self._refresh_tab_bar()

    def _refresh_tab_bar(self):
        page = self.page
        layout = page._tab_layout

        while layout.count() > 0:
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.setGraphicsEffect(None)
                w.deleteLater()

        self._tab_buttons = []

        for i in range(len(self._tabs)):
            custom_name = self._tabs[i].get("name", "")
            label = custom_name if custom_name else str(i + 1)
            btn = TabButton(label)
            btn.set_active(i == self._active_tab)
            btn.clicked.connect(lambda idx=i: self._switch_to_tab(idx))
            btn.closed.connect(lambda idx=i: self._close_tab(idx))
            btn.renamed.connect(lambda name, idx=i: self._on_tab_renamed(idx, name))
            layout.addWidget(btn)
            self._tab_buttons.append(btn)

        plus = QPushButton("+")
        plus.setObjectName("tab_plus_btn")
        plus.setFixedSize(28, 28)
        plus.setCursor(Qt.CursorShape.PointingHandCursor)
        plus.clicked.connect(self._new_tab)
        layout.addWidget(plus)
        self._plus_btn = plus

        layout.addStretch(1)
        page._tab_bar.update()
        page._left_column.update()

    def _on_tab_renamed(self, index: int, new_name: str):
        if 0 <= index < len(self._tabs):
            self._tabs[index]["name"] = new_name

    def _duplicate_current_tab(self):
        """Copy the current tab into a new tab (always uses default numbering)."""
        if self._tabs:
            self._tabs[self._active_tab] = self._capture_current_state()
        import copy
        copied = copy.deepcopy(self._tabs[self._active_tab])
        copied["name"] = ""   # force default numbering on the copy
        self._tabs.append(copied)
        self._active_tab = len(self._tabs) - 1
        self._apply_state(self._tabs[self._active_tab])
        self._refresh_tab_bar()

    # ── State save/restore (multi-tab) ────────────────────────────────────────
    def save_state(self):
        # Capture the visible widget state into the active tab
        if self._tabs:
            self._tabs[self._active_tab] = self._capture_current_state()
        save_draft({
            "active_tab": self._active_tab,
            "tabs": self._tabs,
        })

    def restore_state(self):
        data = load_draft()
        if data and isinstance(data.get("tabs"), list) and data["tabs"]:
            self._tabs = data["tabs"]
            self._active_tab = min(data.get("active_tab", 0), len(self._tabs) - 1)
        else:
            # Start with one empty tab
            self._tabs = [{"customer": "", "rows": []}]
            self._active_tab = 0
        self._apply_state(self._tabs[self._active_tab])
        self._refresh_tab_bar()

    # ── Nested filter ─────────────────────────────────────────────────────────
    class _SelectAllFilter(QObject):
        def eventFilter(self, obj, event):
            if event.type() == QEvent.Type.FocusIn:
                if hasattr(obj, "selectAll"):
                    QTimer.singleShot(0, obj.selectAll)
            return False