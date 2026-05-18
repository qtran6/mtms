from PySide6.QtWidgets import QWidget

class OrderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def apply_theme(self, t: dict):
        self.setStyleSheet(f"background: {t['background']};")