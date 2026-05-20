from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

class OrderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(24, 24, 24, 24)
        self._grid.setHorizontalSpacing(24)
        self._grid.setVerticalSpacing(18)
        self._grid.setColumnStretch(0, 3)
        self._grid.setColumnStretch(1, 2)

        self._customer_name_box = self._customer_name_text_box()
        self._table = self._createTable()
        self._item_input_box = self._addItemUI()

        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(18)
        left_layout.addWidget(self._customer_name_box)
        left_layout.addWidget(self._table)
        left_layout.setStretch(0, 0)
        left_layout.setStretch(1, 1)

        self._grid.addWidget(left_column, 0, 0)
        self._grid.addWidget(self._item_input_box, 0, 1, 2, 1)


    def _customer_name_text_box(self) -> QHBoxLayout:
        customer_name_box = QFrame()
        customer_name_box.setObjectName("customer_name_box")
        customer_name_layout = QHBoxLayout(customer_name_box)
        customer_name_layout.setContentsMargins(20, 16, 20, 16)
        customer_name_layout.setSpacing(12)

        text = QLabel("Tên khách hàng:")
        text_box = QLineEdit()
        text_box.setPlaceholderText("Nhập tên khách hàng...")

        customer_name_layout.addWidget(text)
        customer_name_layout.addWidget(text_box)
        
        return customer_name_box
    

    def _createTable(self) -> QWidget:
        table_box = QFrame()
        table_box.setObjectName("table_box")
        table_layout = QVBoxLayout(table_box)
        table_layout.setContentsMargins(12, 12, 12, 12)

        table = QTableWidget()

        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["TT", "Tên HH", "Số lượng", "Đơn giá", "Thành tiền"])
        table.setRowCount(10)

        table_layout.addWidget(table)
        return table_box


    def _addItemUI(self) -> QWidget:
        box = QFrame()
        box.setObjectName("item_box")
        layout = QVBoxLayout(box)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        brand_label = QLabel("Thương hiệu:")
        brand_input = QLineEdit()
        model_label = QLabel("Tên hàng hóa:")
        model_input = QLineEdit()

        layout.addWidget(brand_label)
        layout.addWidget(brand_input)
        layout.addWidget(model_label)
        layout.addWidget(model_input)
        layout.addStretch(1)
        return box


    def apply_theme(self, t: dict): 
        self.setStyleSheet(f"background: {t['background']};")
        self._customer_name_box.setStyleSheet(f"""
            QFrame#customer_name_box {{
                border: 1px solid {t['border']};
                background: {t['background']};
            }}
        """)
        self._item_input_box.setStyleSheet(f"""
            QFrame#item_box {{
                border: 1px solid {t['border']};
                background: {t['background']};
            }}
        """)
        self._table.setStyleSheet(f"""
            QTableWidget {{
                background: {t['background']};
                color: {t['text']};
                gridline-color: {t['border']};
                border: 1px solid {t['border']};
            }}
            QHeaderView::section {{
                background: {t['background']};
                color: {t['text']};
                border: 1px solid {t['border']};
            }}
        """)