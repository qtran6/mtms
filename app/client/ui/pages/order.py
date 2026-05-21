from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTableView,
    QVBoxLayout,
    QWidget,
    QApplication,
    QHeaderView,
    QStyledItemDelegate
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont
from PySide6.QtCore import Qt


class OrderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFocusPolicy(Qt.ClickFocus)
        self._grid = QGridLayout(self)
        # self._grid.setContentsMargins(24, 24, 24, 24)
        self._grid.setHorizontalSpacing(24)
        self._grid.setColumnStretch(0, 4)
        self._grid.setColumnStretch(1, 2)

        self._customer_name_box = self._customer_name_text_box()
        self._table = self._createTable()
        self._item_input_box = self._addItemUI()

        left_column = QWidget()
        left_column.setObjectName("left_column")
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(18)
        left_layout.addWidget(self._customer_name_box)
        left_layout.addWidget(self._table)
        left_layout.setStretch(0, 0)
        left_layout.setStretch(1, 1)

        self._grid.addWidget(left_column, 0, 0)
        self._grid.addWidget(self._item_input_box, 0, 1)

    def _customer_name_text_box(self) -> QFrame:
        customer_name_box = QFrame()
        customer_name_box.setObjectName("customer_name_box")
        customer_name_layout = QHBoxLayout(customer_name_box)
        # customer_name_layout.setContentsMargins(20, 16, 20, 16)  # padding via margins
        customer_name_layout.setSpacing(20)

        text = QLabel("Tên khách hàng:")
        text.setObjectName("label_customer")
        self._customer_text_box = QLineEdit()
        self._customer_text_box.setPlaceholderText("Nhập tên khách hàng...")
        self._customer_text_box.setObjectName("input_customer")

        customer_name_layout.addWidget(text)
        customer_name_layout.addWidget(self._customer_text_box)

        return customer_name_box

    def _createTable(self) -> QFrame:
        table_box = QFrame()
        table_box.setObjectName("table_box")
        table_layout = QVBoxLayout(table_box)
        # table_layout.setContentsMargins(12, 12, 12, 12)

        table = QTableView()
        model = QStandardItemModel(10, 5)
        model.setHorizontalHeaderLabels(["TT", "Tên HH", "Số lượng", "Đơn giá", "Thành tiền"])

        table.setModel(model)
        table.setObjectName("table_view")

        h_header = table.horizontalHeader()
        h_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        h_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        table.setItemDelegateForColumn(0, AlignDelegate("center"))
        table.setItemDelegateForColumn(1, AlignDelegate("left"))
        table.setItemDelegateForColumn(2, AlignDelegate("center"))
        table.setItemDelegateForColumn(3, AlignDelegate("right"))
        table.setItemDelegateForColumn(4, AlignDelegate("right"))

        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(32)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)

        for row in range(10):
            item = QStandardItem(str(row + 1))
            model.setItem(row, 0, item)

        table_layout.addWidget(table)

        self._table_view = table
        self._table_model = model

        return table_box

    def _addItemToTable(self, item):
        ...

    def _addItemUI(self) -> QFrame:
        box = QFrame()
        box.setObjectName("item_box")
        layout = QVBoxLayout(box)
        # layout.setContentsMargins(20, 20, 20, 20)  # padding via margins
        layout.setSpacing(12)

        brand_input = QLineEdit()
        brand_input.setPlaceholderText("Nhập thương hiệu...")
        brand_input.setObjectName("item_input")

        model_input = QLineEdit()
        model_input.setPlaceholderText("Nhập tên hàng hóa...")
        model_input.setObjectName("item_input")

        layout.addWidget(brand_input)
        layout.addWidget(model_input)
        layout.addStretch(1)
        return box

    def mousePressEvent(self, event):
        focused = QApplication.focusWidget()
        if focused and focused is not self:
            try:
                focused.clearFocus()
            except Exception:
                pass
        self.setFocus()
        super().mousePressEvent(event)

    def apply_theme(self, t: dict):
        r = t.get("radius", 12)

        self.setStyleSheet("background: transparent;")

        # ── Shared card style ─────────────────────────────────────────────────
        card_style = f"""
            background: {t['card_bg']};
            border: 1px solid {t['card_border']};
            border-radius: {r}px;
        """

        # ── Shared input style ────────────────────────────────────────────────
        input_style = f"""
            QLineEdit {{
                background: {t['input_bg']};
                color: {t['text']};
                border: 1px solid {t['input_border']};
                border-radius: {r}px;
                padding: 20px;
                selection-background-color: {t['border']};
            }}
            QLineEdit:focus {{
                border: 1px solid {t['input_border_focus']};
            }}
            QLineEdit::placeholder {{
                color: {t['placeholder']};
            }}
        """

        # ── Customer name card ────────────────────────────────────────────────
        self._customer_name_box.setStyleSheet(f"""
            QFrame#customer_name_box {{
                {card_style}
            }}
            QLabel {{
                color: {t['text']};
                background: transparent;
                border: none;
            }}
            {input_style}
            QLineEdit {{
                border: none;
            }}
            QLineEdit:focus {{
                border: none;
            }}
        """)

        # ── Table card ────────────────────────────────────────────────────────
        self._table.setStyleSheet(f"""
            QFrame#table_box {{
                {card_style}
            }}
        """)

        if hasattr(self, '_table_view'):
            self._table_view.setStyleSheet(f"""
                QTableView {{
                    background: transparent;
                    alternate-background-color: {t['card_bg']};
                    color: {t['text']};
                    gridline-color: transparent;
                    border: none;
                }}
                QTableView::item {{
                }}
                QTableView::item:selected {{
                    background: {t['btn_hover_bg']};
                    color: {t['text']};
                }}
                QHeaderView {{
                    background: transparent;
                    border: none;
                }}
                QHeaderView::section {{
                    background: transparent;
                    color: {t['text']};
                    font-family: '{t['header_font']}';
                    font-size: {t['header_size']}pt;
                }}
                QHeaderView::section:last {{
                    border-right: none;
                }}
            """)

        # ── Item input card ───────────────────────────────────────────────────
        self._item_input_box.setStyleSheet(f"""
            QFrame#item_box {{
                {card_style}
            }}
            QLabel {{
                color: {t['text']};
                background: transparent;
                border: none;
            }}
            {input_style}
        """)


class AlignDelegate(QStyledItemDelegate):
    def __init__(self, alignment_name, parent=None):
        super().__init__(parent)
        alignment_map = {
            "left":   Qt.AlignmentFlag.AlignLeft  | Qt.AlignmentFlag.AlignVCenter,
            "center": Qt.AlignmentFlag.AlignCenter,
            "right":  Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        }
        self._alignment = alignment_map.get(
            alignment_name, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = self._alignment