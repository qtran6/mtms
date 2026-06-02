from PySide6.QtWidgets import (
    QScrollArea,
    QWidget,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QVBoxLayout,
    QApplication,
    QHeaderView,
    QComboBox,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, Signal

from client.core.completer import combo_completer
from client.core.data_loader import load_products
from client.core.order_service import OrderController
from client.ui.custom_widgets import *


class OrderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load data 
        self._products = load_products()
        self._brands = list(dict.fromkeys(p["brand"] for p in self._products))

        self._build_ui()

    # Build UI
    def _build_ui(self):
        # ── Page layout ───────────────────────────────────────────────────────
        self.setFocusPolicy(Qt.ClickFocus)
        self._grid = QGridLayout(self)
        self._grid.setHorizontalSpacing(24)
        self._grid.setColumnStretch(0, 4)
        self._grid.setColumnStretch(1, 2)

        self._customer_name_box = self._customer_name_text_box()
        self._table = self._createTable()
        self._tab_bar = self._create_tab_bar()
        self._item_input_box = self._addItemUI()

        self._left_column = QWidget()
        self._left_column.setObjectName("left_column")
        left_layout = QVBoxLayout(self._left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(18)
        left_layout.addWidget(self._customer_name_box)
        left_layout.addWidget(self._table)
        left_layout.addWidget(self._tab_bar)
        left_layout.setStretch(0, 0)
        left_layout.setStretch(1, 1)

        self._grid.addWidget(self._left_column, 0, 0)
        self._grid.addWidget(self._item_input_box, 0, 1)

        # ── Tab order ─────────────────────────────────────────────────────────
        QWidget.setTabOrder(self._customer_text_box, self._brand_input)
        QWidget.setTabOrder(self._brand_input, self._model_input)

        self._loop_filter = LoopBackOnTab(self._brand_input, self)
        self._model_input.installEventFilter(self._loop_filter)

        # ── Wire up business logic ────────────────────────────────────────────
        self._controller = OrderController(self)
        self._controller.bind()
        self._controller.restore_state()

    # ── Sub-widget builders ───────────────────────────────────────────────────
    def _customer_name_text_box(self) -> QFrame:
        customer_name_box = QFrame()
        customer_name_box.setObjectName("customer_name_box")
        customer_name_layout = QHBoxLayout(customer_name_box)
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

        table = QTableWidget(0, 4)
        table.setObjectName("table_view")
        table.setHorizontalHeaderLabels(["Tên HH", "SL", "Đơn giá", "Thành tiền"])

        table.horizontalHeader().setObjectName("horizontal_header")
        h_header = table.horizontalHeader()
        h_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        h_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        table.verticalHeader().setObjectName("vertical_header")
        table.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        table.verticalHeader().setMinimumWidth(40)
        table.verticalHeader().setDefaultSectionSize(70)

        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        table.setShowGrid(True)

        table_layout.addWidget(table)

        # Duplicate tab button — bottom-right of the table card
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self._duplicate_tab_btn = QPushButton("+")
        self._duplicate_tab_btn.setObjectName("duplicate_tab_btn")
        self._duplicate_tab_btn.setFixedSize(32, 32)
        self._duplicate_tab_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(self._duplicate_tab_btn)
        table_layout.addLayout(btn_row)

        self._table_view = table
        return table_box

    def _create_tab_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName("tab_bar")
        self._tab_layout = QHBoxLayout(bar)
        self._tab_layout.setContentsMargins(0, 4, 0, 0)
        self._tab_layout.setSpacing(4)
        self._tab_layout.addStretch(1)

        scroll_area = HorizontalScrollArea()
        scroll_area.setWidget(bar)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setFixedHeight(48)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        return scroll_area

    def _addItemUI(self) -> QFrame:
        box = QFrame()
        box.setObjectName("item_box")
        layout = QVBoxLayout(box)
        layout.setSpacing(12)

        # Brand combo
        brand_input = QComboBox()
        brand_input.setObjectName("item_input")
        brand_input.setEditable(True)
        brand_input.addItems(self._brands)
        brand_input.setCurrentIndex(-1)
        brand_input.setPlaceholderText("Nhập thương hiệu...")
        brand_input.lineEdit().setPlaceholderText("Nhập thương hiệu...")

        # Model combo
        model_input = QComboBox()
        model_input.setObjectName("item_input")
        model_input.setEditable(True)
        model_input.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        model_input.lineEdit().setPlaceholderText("Nhập tên hàng hóa...")
        combo_completer(model_input)

        # Buttons
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
        btn_layout.addWidget(print_btn,  0, 1)
        btn_layout.addWidget(clear_btn,  1, 1)

        self._grand_total_label = QLabel("Tổng cộng:")
        self._grand_total_label.setObjectName("grand_total_label")
        self._grand_total_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        for b in (submit_btn, print_btn, clear_btn):
            b.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.addWidget(brand_input)
        layout.addWidget(model_input)
        layout.addWidget(btn_box)
        layout.addWidget(self._grand_total_label)
        layout.addStretch(1)

        # Store references for OrderController
        self._brand_input = brand_input
        self._model_input = model_input
        self._submit_btn  = submit_btn
        self._print_btn   = print_btn
        self._clear_btn   = clear_btn

        return box

    # ── Focus handling ────────────────────────────────────────────────────────
    def mousePressEvent(self, event):
        focused = QApplication.focusWidget()
        if focused and focused is not self:
            try:
                focused.clearFocus()
            except Exception:
                pass
        self.setFocus()
        super().mousePressEvent(event)

    # ── Theme ─────────────────────────────────────────────────────────────────
    def apply_theme(self, t: dict):
        r = t.get("radius", 12)

        self.setStyleSheet("background: transparent;")

        # Shadows
        apply_shadow(self, t)
        apply_cast_shadow(self._customer_name_box, t)
        apply_cast_shadow(self._left_column, t)
        apply_cast_shadow(self._item_input_box, t)

        card_style = f"""
            background: {t['card_bg']};
            border: none;
            border-radius: {r}px;
            padding: 10px;
        """

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

        button_style = f"""
            color: {t['text']};
            border: none;
            border-radius: {r-20}px;
            background: {t['btn_bg']};
        """

        # Customer card
        self._customer_name_box.setStyleSheet(f"""
            QFrame#customer_name_box {{ {card_style} }}
            QLabel {{ color: {t['text']}; background: transparent; border: none; }}
            {input_style}
            QLineEdit {{ border: none; }}
            QLineEdit:focus {{ border: none; }}
        """)

        # Table card
        self._table.setStyleSheet(f"""
            QFrame#table_box {{ {card_style} }}
            QPushButton#duplicate_tab_btn {{
                background: {t['btn_bg']};
                color: {t['text']};
                border: none;
                border-radius: 16px;
                font-size: 14pt;
                font-weight: bold;
                text-align: center;
                padding-bottom: 3;
            }}
            QPushButton#duplicate_tab_btn:hover {{
                background: {t['btn_hover_bg']};
            }}
        """)

        if hasattr(self, '_table_view'):
            self._table_view.setStyleSheet(f"""
                QTableWidget {{
                    background: transparent;
                    color: {t['text']};
                    gridline-color: {t['border']};
                    border: 2px solid {t['border']};
                    border-radius: {r-10}px;
                    padding: 20px 9px 20px 20px;
                }}
                QTableWidget::item {{ 
                    border: none; 
                }}
                QTableWidget::item:selected {{ 
                    background: {t['btn_bg']};
                    color: {t['text']};
                }}
                QTableWidget::item:selected:!active {{ 
                    background: {t['card_bg']};
                    color: {t['text']}; 
                }}
                QTableWidget QLineEdit {{
                    background: {t['card_bg']};
                    color: {t['text']};
                    border: none;
                }}
                QHeaderView {{ 
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
                QTableWidget QTableCornerButton::section {{
                    background: transparent;
                    color: {t['text']};
                    border: 1px solid {t['border']};
                }}
            """)

        # Tab bar
        self._tab_bar.setStyleSheet(f"""
            QWidget#tab_btn {{
                background: {t['card_bg']};
                border-radius: 6px;
            }}
            QWidget#tab_btn[active="true"] {{
                background: {t['btn_bg']};
            }}
            QWidget#tab_btn QLabel {{
                color: {t['text']};
                background: transparent;
                padding: 2px 4px;
            }}
            QPushButton#tab_close_btn {{
                background: transparent;
                color: {t['text']};
                border: none;
                font-size: 11pt;
            }}
            QPushButton#tab_close_btn:hover {{
                color: {t['placeholder']};
            }}
            QPushButton#tab_plus_btn {{
                background: {t['btn_bg']};
                color: {t['text']};
                border: none;
                border-radius: 14px;
                font-size: 14pt;
            }}
            QPushButton#tab_plus_btn:hover {{
                background: {t['btn_hover_bg']};
            }}
        """)

        # Item input card
        self._item_input_box.setStyleSheet(f"""
            QFrame#item_box {{ {card_style} }}
            QLabel {{ color: {t['text']}; background: transparent; border: none; }}
            {input_style}
            QComboBox {{
                background: {t['input_bg']};
                color: {t['text']};
                border: 1px solid {t['input_border']};
                border-radius: {r-20}px;
                padding: 20px;
                placeholder-text-color: {t['placeholder']};
            }}
            QComboBox:focus {{ border: 1px solid {t['input_border_focus']}; }}
            QComboBox QLineEdit {{
                background: transparent;
                color: {t['text']};
                border: none;
                placeholder-text-color: {t['placeholder']};
            }}
            QComboBox QAbstractItemView {{
                background: {t['card_bg']};
                color: {t['text']};
                selection-background-color: {t['btn_hover_bg']};
                border: 1px solid {t['border']};
            }}
            QPushButton#submit_btn {{ {button_style} }}
            QPushButton#submit_btn:hover {{ background: {t['btn_hover_bg']}; color: {t['text']}; }}
            QPushButton#print_btn {{ {button_style} }}
            QPushButton#print_btn:hover {{ background: {t['btn_hover_bg']}; color: {t['text']}; }}
            QPushButton#clear_btn {{
                {button_style}
                color: {t['close_hover_text']};
                background: {t['clear_btn_bg']};
            }}
            QPushButton#clear_btn:hover {{
                background: {t['clear_btn_hover_bg']};
                color: {t['close_hover_text']};
            }}
            QLabel#grand_total_label {{
                color: {t['text']};
                font-size: 16pt;
                font-weight: bold;
                background: transparent;
                border: none;
                padding: 8px;
            }}
        """)
        
class TabButton(QWidget):
    """A tab with a numeric label and a small ✕ close button."""
    clicked = Signal()
    closed  = Signal()

    def __init__(self, number: int, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 4, 4)
        layout.setSpacing(6)

        self._label = QLabel(str(number))
        self._close = QPushButton("✕")
        self._close.setFixedSize(16, 16)
        self._close.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close.setObjectName("tab_close_btn")

        layout.addWidget(self._label)
        layout.addWidget(self._close)

        self._close.clicked.connect(self.closed.emit)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("tab_btn")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def set_active(self, active: bool):
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)