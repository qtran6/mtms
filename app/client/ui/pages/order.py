from PySide6.QtWidgets import QTableWidget, QWidget

class OrderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.createTable()

    def createTable(self):
        self._table = QTableWidget(self)
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["ID", "Name", "Quantity", "Price", "Total"])
        self._table.setRowCount(10)  # Example row count
        self._table.setGeometry(10, 10, 780, 580)  # Example geometry

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