from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import QLabel, QStyle, QToolButton, QWidget, QHBoxLayout, QPushButton, QSizePolicy, QMainWindow

# ── Title bar ─────────────────────────────────────────────────────────────────
class TitleBar(QWidget):
    HEIGHT = 42

    def __init__(self, window: QMainWindow):
        super().__init__()
        self._mouse_pos = None
        self._window = window
        self.setFixedHeight(self.HEIGHT)

        self._icon = QLabel()
        icon = self.style().standardIcon(QStyle.SP_ComputerIcon)
        self._icon.setPixmap(icon.pixmap(16, 16))

        self._drag_pos = QPoint()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(0)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._btn_close = QPushButton("✕")
        self._btn_close.setFixedSize(36, 28)
        # self._btn_close.setFlat(True)
        self._btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_close.clicked.connect(self._window.close)

        # layout.addWidget(self._icon)
        layout.addWidget(spacer)
        layout.addWidget(self._btn_close)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - self._window.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_pos.isNull():
            if self._window.isMaximized():
                self._window.showNormal()
                self._drag_pos = QPoint(
                    self._window.width() // 2,
                    self._drag_pos.y()
                )
            self._window.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = QPoint()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self._window.isMaximized():
                self._window.showNormal()
            else:
                self._window.showMaximized()

    def apply_theme(self, t: dict):
        self.setStyleSheet("background: transparent;")
        self._btn_close.setStyleSheet(f"""
            QPushButton {{
                color: {t['text']};
                background: transparent;
                border: none;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {t['close_hover']};
                color: {t['close_hover_text']};
                border-radius: 4px;
            }}
        """)
