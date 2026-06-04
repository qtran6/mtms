import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QStackedWidget, QSizePolicy
)
from PySide6.QtCore import QTimer
from PySide6.QtGui import (
    QKeySequence, QPalette, QColor, QPainter, QShortcut, QIcon, QFont
)

from client.core.theme import load_theme
from client.core.main_window_service import MainWindowController
from client.ui.pages import *
from client.ui.custom_widgets.title_bar import TitleBar


RADIUS = 12
BORDER = 2
SHADOW = 10
RESTORE_SIZE = (1280, 720)
ICON_PATH = Path(__file__).parent.parent / "assets" / "MT.ico"

if not ICON_PATH.exists():
    print(f"[icon] Not found: {ICON_PATH}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Toa Hang")
        self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.setMinimumSize(960, 600)
        self.resize(*RESTORE_SIZE)

        from PySide6.QtCore import Qt
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # State
        self._last_dark = None
        self._maximized = False
        self._theme     = {}

        # Build root UI
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Custom title bar
        self._title_bar = TitleBar(self)
        root_layout.addWidget(self._title_bar)

        # Content area with stacked pages
        self._content = QStackedWidget()
        self._order_page = OrderPage()
        self._print_preview_page = PrintPreviewPage()

        self._content.addWidget(self._order_page)
        self._content.addWidget(self._print_preview_page)
        self._content.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        root_layout.addWidget(self._content)

        # Controller — owns all logic
        self._controller = MainWindowController(
            self,

            radius=RADIUS, border=BORDER, shadow=SHADOW,
            restore_size=RESTORE_SIZE,
        )

        # Wire signals
        self._print_preview_page.print_requested.connect(self._controller.handle_print_requested)
        self._print_preview_page.cancelled.connect(self._controller.handle_preview_cancelled)

        self._controller.set_margins(maximized=False)
        self._apply_theme()

        QShortcut(QKeySequence.StandardKey.Print, self,
                  activated=self._controller.trigger_print)

        # Theme polling
        self._timer = QTimer(self)
        self._timer.setInterval(2000)
        self._timer.timeout.connect(self._apply_theme)
        self._timer.start()

    # Qt event hooks, delegate to controller
    def changeEvent(self, event):
        super().changeEvent(event)
        if hasattr(self, "_controller"):
            self._controller.handle_state_change(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        if hasattr(self, "_controller"):
            self._controller.paint_window(painter)

    def closeEvent(self, event):
        self._controller.handle_close()
        super().closeEvent(event)

    # Public API used by other pages/controllers
    def show_print_preview(self, pdf_path: str):
        self._controller.show_print_preview(pdf_path)

    # Theme
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
        app_font = QFont(t['font'], t['font_size'])
        QApplication.setFont(app_font)

        # Global scrollbar style
        r = t.get("radius", 12)
        QApplication.instance().setStyleSheet(f"""
            QScrollBar:vertical {{
                background: transparent;
                width: 11px;
                margin: {r}px 0px {r}px 3px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {t['placeholder']};
                min-height: 20px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {t['text_secondary']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
            QScrollBar:horizontal {{
                background: transparent;
                height: 6px;
                margin: 0px;
                border-radius: 3px;
            }}
            QScrollBar::handle:horizontal {{
                background: {t['placeholder']};
                min-width: 30px;
                border-radius: 3px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {t['text_secondary']};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: transparent;
            }}
        """)

        self._title_bar.apply_theme(t)
        self._order_page.apply_theme(t)
        self._print_preview_page.apply_theme(t)
        self._content.setStyleSheet("background: transparent;")
        self.centralWidget().setStyleSheet("#root { background: transparent; }")

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window,     QColor(t["background"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(t["text"]))
        self.setPalette(palette)
        self.update()


def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(ICON_PATH)))
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    QTimer.singleShot(0, window.showMaximized)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()