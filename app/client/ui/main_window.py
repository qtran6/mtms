import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QStackedLayout, QStackedWidget,
    QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QPoint, QRect, QEvent
from PySide6.QtGui import QFontDatabase, QPalette, QColor, QPainter, QBrush, QPainterPath, QPen

from ..core.theme import load_theme
from .title_bar import TitleBar
from .pages import *


RADIUS = 12
BORDER = 2
SHADOW = 10
RESTORE_SIZE = (1280, 720)

# ── Main window ───────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Manager")
        self.setMinimumSize(960, 600)
        self.resize(*RESTORE_SIZE)

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._last_dark = None
        self._maximized = False
        self._theme     = {}

        # Root
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        self._title_bar = TitleBar(self)
        root_layout.addWidget(self._title_bar)

        self._content = QStackedWidget()
        self._order_page = OrderPage()
        self._content.addWidget(self._order_page)
        self._content.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        root_layout.addWidget(self._content)

        self._set_margins(maximized=False)
        self._apply_theme()

        self._timer = QTimer(self)
        self._timer.setInterval(2000)
        self._timer.timeout.connect(self._apply_theme)
        self._timer.start()


    def _set_margins(self, maximized: bool):
        m = 0 if maximized else SHADOW
        self.setContentsMargins(m, m, m, m)


    def changeEvent(self, event):
        super().changeEvent(event)
        if event.type() == QEvent.Type.WindowStateChange:
            maximized = self.isMaximized()
            if maximized != self._maximized:
                self._maximized = maximized
                if not maximized:
                    # Defer resize so Qt finishes the state change first
                    QTimer.singleShot(0, lambda: self.resize(*RESTORE_SIZE))
                self._set_margins(maximized)
                self._apply_theme(force=True)
                self.update()


    # ── Paint background + border ─────────────────────────────────────────────
    def paintEvent(self, event):
        if not self._theme:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        bg_color     = QColor(self._theme["background"])
        border_color = QColor(self._theme["border"])

        if self._maximized:
            painter.fillRect(self.rect(), QBrush(bg_color))
        else:
            rect = QRect(SHADOW, SHADOW,
                         self.width()  - SHADOW * 2,
                         self.height() - SHADOW * 2)
            path = QPainterPath()
            path.addRoundedRect(rect, RADIUS, RADIUS)
            painter.fillPath(path, QBrush(bg_color))
            pen = QPen(border_color, BORDER)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(path)

    # ── Theme ─────────────────────────────────────────────────────────────────
    def _is_dark(self) -> bool:
        c = QApplication.palette().color(QPalette.ColorRole.Window)
        return (0.2126 * c.red() + 0.7152 * c.green() + 0.0722 * c.blue()) < 128
    

    def _apply_theme(self, force: bool = False):
        dark = self._is_dark()
        if dark == self._last_dark and not force:
            return
        self._last_dark = dark

        self._theme = load_theme("dark" if dark else "light")
        t = self._theme

        # Apply font globally to the entire app
        from PySide6.QtGui import QFont
        app_font = QFont(t['font'], t['font_size'])
        QApplication.setFont(app_font)

        self._title_bar.apply_theme(t)
        self._order_page.apply_theme(t)
        self._content.setStyleSheet("background: transparent;")
        self.centralWidget().setStyleSheet("#root { background: transparent; }")

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window,     QColor(t["background"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(t["text"]))
        self.setPalette(palette)
        self.update()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()

    def _start_maximized():
        window.showMaximized()

    QTimer.singleShot(0, _start_maximized)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()