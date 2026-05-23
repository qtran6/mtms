from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
    QApplication,
    QHeaderView,
    QStyledItemDelegate,
    QGraphicsDropShadowEffect,
    QAbstractButton,
)
from PySide6.QtGui import QColor, QPainter, QRegion, QRgba64, QStandardItemModel, QStandardItem, QFont
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

        self._left_column = QWidget()
        self._left_column.setObjectName("left_column")
        left_layout = QVBoxLayout(self._left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(18)
        left_layout.addWidget(self._customer_name_box)
        left_layout.addWidget(self._table)
        left_layout.setStretch(0, 0)
        left_layout.setStretch(1, 1)

        self._grid.addWidget(self._left_column, 0, 0)
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
        model = QStandardItemModel(300, 4)
        model.setHorizontalHeaderLabels(["Tên HH", "Số lượng", "Đơn giá", "Thành tiền"])

        table.setModel(model)
        table.setObjectName("table_view")

        table.horizontalHeader().setObjectName("horizontal_header")
        h_header = table.horizontalHeader()
        h_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        table.setItemDelegateForColumn(0, AlignDelegate("left"))
        table.setItemDelegateForColumn(1, AlignDelegate("center"))
        table.setItemDelegateForColumn(2, AlignDelegate("right"))
        table.setItemDelegateForColumn(3, AlignDelegate("right"))

        # table.verticalHeader().setVisible(False)
        table.verticalHeader().setObjectName("vertical_header")
        table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setShowGrid(True)

        # for row in range(300):
        #     item = QStandardItem(str(row + 1))
        #     model.setItem(row, 0, item)

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

        submit_btn = QPushButton("Thêm")
        submit_btn.setObjectName("submit_btn")
        submit_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        print_btn = QPushButton("In")
        print_btn.setObjectName("print_btn")
        print_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        clear_btn = QPushButton("Xóa")
        clear_btn.setObjectName("clear_btn")
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        btn_box = QWidget()
        btn_layout = QGridLayout(btn_box)
        btn_layout.addWidget(submit_btn, 0, 0, 2, 1)
        btn_layout.addWidget(print_btn, 0, 1)
        btn_layout.addWidget(clear_btn, 1, 1)
        
        layout.addWidget(brand_input)
        layout.addWidget(model_input)
        layout.addWidget(btn_box)
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

        # ── Apply shadow  ─────────────────────────────────────────────────────
        self.set_shadow(self, t)
        self.set_cast_shadow(self._customer_name_box, t)
        self.set_cast_shadow(self._left_column, t)
        self.set_cast_shadow(self._item_input_box, t)

        # ── Shared card style ─────────────────────────────────────────────────
        card_style = f"""
            background: {t['card_bg']};
            border: none;
            border-radius: {r}px;
            padding: 10px;
        """

        # ── Shared input style ────────────────────────────────────────────────
        input_style = f"""
            QLineEdit {{
                background: {t['input_bg']};
                color: {t['text']};
                border: 1px solid {t['input_border']};
                border-radius: {r-20}px;
                padding: 20px;
                selection-background-color: {t['border']};
                placeholder-text-color: {t['placeholder']};
            }}
            QLineEdit:focus {{
                border: 1px solid {t['input_border_focus']};
            }}
        """

        # ── Shared button style ───────────────────────────────────────────────
        button_style = f"""
            color: {t['text']};
            border: none;
            border-radius: {r-20}px;
            color: {t['text']};
            background: {t['btn_bg']};
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
                    color: {t['text']};
                    gridline-color: {t['border']};
                    border: 2px solid {t['border']};
                    border-radius: {r-10}px;
                    padding: 20px 9px 20px 20px;
                }}
                QTableView::item {{
                    border: none;
                }}
                QTableView::item:selected {{
                    background: {t['btn_bg']};
                    color: {t['text']};
                }}
                QTableView::item:selected:!active {{
                    background: {t['card_bg']};
                    color: {t['text']};
                }}
                QHeaderView{{
                    background: transparent;
                    border: none;
                    color: {t['text']};
                }}
                QHeaderView#horizontal_header::section {{
                    border-right: 1px solid {t['border']};
                    border-top: 1px solid {t['border']};
                    border-bottom: 1px solid {t['border']};
                }}
                QHeaderView#vertical_header::section {{
                    border-left: 1px solid {t['border']};
                    border-top: none;
                    border-bottom: 1px solid {t['border']};
                    border-right: 1px solid {t['border']};
                }}
                QTableView QTableCornerButton::section {{
                    background: transparent;
                    color: {t['text']};
                    border: 1px solid {t['border']};
                }}
                QScrollBar:vertical {{
                    background: transparent;
                    width: 11px;
                    margin: {r}px 0px {r}px 3px;
                    border-radius: 3px;
                }}
                QScrollBar::handle:vertical {{
                    background: {t['border']};
                    min-height: 20px;
                    border-radius: 3px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background: {t['text_secondary']};
                }}
                QScrollBar::add-line:vertical,
                QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
                QScrollBar::add-page:vertical,
                QScrollBar::sub-page:vertical {{
                    background: transparent;
                }}
                QScrollBar:horizontal {{
                    background: transparent;
                    height: 6px;
                    margin: 0px;
                    border-radius: 3px;
                }}
                QScrollBar::handle:horizontal {{
                    background: {t['border']};
                    min-width: 30px;
                    border-radius: 3px;
                }}
                QScrollBar::handle:horizontal:hover {{
                    background: {t['text_secondary']};
                }}
                QScrollBar::add-line:horizontal,
                QScrollBar::sub-line:horizontal {{
                    width: 0px;
                }}
                QScrollBar::add-page:horizontal,
                QScrollBar::sub-page:horizontal {{
                    background: transparent;
                }}
            """)

        btn = self._table_view.findChild(QAbstractButton)
        if btn:
            btn.setToolTip("TT")
            print(btn.toolTip())

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
            QPushButton#submit_btn {{
                {button_style}
            }}
            QPushButton#submit_btn:hover {{
                background: {t['btn_hover_bg']};
                color: {t['text']};
            }}
            QPushButton#print_btn {{
                {button_style}
            }}
            QPushButton#print_btn:hover {{
                background: {t['btn_hover_bg']};
                color: {t['text']};
            }}
            QPushButton#clear_btn {{
                {button_style}
                color: {t['close_hover_text']};
                background: {t['clear_btn_bg']};
            }}
            QPushButton#clear_btn:hover {{
                background: {t['clear_btn_hover_bg']};
                color: {t['close_hover_text']};
            }}
        """)

    def set_shadow(self, widget, t: dict):
        # Core shadow
        widget.shadow = QGraphicsDropShadowEffect(widget)
        widget.shadow.setBlurRadius(3)
        widget.shadow.setOffset(0, 1)
        widget.shadow.setColor(self._parse_color(t["shadow"]))

        widget.setGraphicsEffect(widget.shadow)

    def set_cast_shadow(self, widget, t: dict):
        # Core shadow
        widget.shadow = QGraphicsDropShadowEffect(widget)
        widget.shadow.setBlurRadius(12)
        widget.shadow.setOffset(0, 3)
        widget.shadow.setColor(self._parse_color(t["cast_shadow"]))

        widget.setGraphicsEffect(widget.shadow)

    def _parse_color(self, rgba_str: str) -> QColor:
        """Parse 'rgba(r, g, b, a)' where a is 0.0-1.0 into QColor."""
        try:
            inner = rgba_str.strip().removeprefix("rgba(").removesuffix(")")
            r, g, b, a = [x.strip() for x in inner.split(",")]
            color = QColor(int(r), int(g), int(b))
            color.setAlphaF(float(a))
            return color
        except Exception:
            return QColor(0, 0, 0, 80)

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