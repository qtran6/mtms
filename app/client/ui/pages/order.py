from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QGridLayout, QTableWidget, QWidget

class OrderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(10, 10, 10, 10)
        # self._grid.setColumnStretch()

        self._customer_name_layout = self._input_customer_name()
        self._table = self._createTable()

        self._grid.addLayout(self._customer_name_layout, 0, 0)
        self._grid.addWidget(self._table, 1, 0)


    def _input_customer_name(self) -> QHBoxLayout:
        customer_name_layout = QHBoxLayout()

        text = QLabel("Tên khách hàng:")
        text_box = QLineEdit()
        text_box.setPlaceholderText("Nhập tên khách hàng...")

        customer_name_layout.addWidget(text)
        customer_name_layout.addWidget(text_box)
        
        return customer_name_layout

    def _createTable(self) -> QTableWidget:
        table = QTableWidget(self)

        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["TT", "Tên HH", "Số lượng", "Đơn giá", "Thành tiền"])
        table.setRowCount(10)

        return table


    def _addItemUI(self):
        ...


    def apply_theme(self, t: dict): 
        self.setStyleSheet(f"background: {t['background']};")
        self._table.setStyleSheet(f"""
            QTableWidget {{
                background: {t['background']};
                color: {t['text']};
                gridline-color: {t['border']};
                border: none;
            }}
            QHeaderView::section {{
                background: {t['background']};
                color: {t['text']};
                border: 1px solid {t['border']};
            }}
        """)