from PySide6.QtWidgets import QLabel, QGridLayout, QTableWidget, QWidget

class OrderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(10, 10, 10, 10)
        self._grid.setSpacing(10)
        self.createTable()
        self._grid.addWidget(self._customer_name_input, 0, 0)

    def createTable(self):
        self._customer_name_input = QLabel("Tên khách hàng:", self)

        self._table = QTableWidget(self)
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["TT", "Tên HH", "Số lượng", "Đơn giá", "Thành tiền"])
        self._table.setRowCount(10)
        self._grid.addWidget(self._table, 1, 0, 1, 2)

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