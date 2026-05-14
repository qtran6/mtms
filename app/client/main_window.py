import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QColor


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MTIM")
        self.setMinimumSize(960, 600)
        self.resize(1280, 720)

        # Central widget — carries the background color
        self._bg = QWidget()
        self.setCentralWidget(self._bg)

        # Apply theme immediately, then poll every 2 s for live switching
        self._apply_theme()
        self._timer = QTimer(self)
        self._timer.setInterval(2000)
        self._timer.timeout.connect(self._apply_theme)
        self._timer.start()

    # ------------------------------------------------------------------
    def _is_dark(self) -> bool:
        """Return True when the OS / Qt palette is dark."""
        palette = QApplication.palette()
        window_color: QColor = palette.color(QPalette.ColorRole.Window)
        # Luminance formula (perceived brightness)
        r, g, b = window_color.red(), window_color.green(), window_color.blue()
        luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
        return luminance < 128

    def _apply_theme(self):
        dark = self._is_dark()

        if dark:
            bg   = "#1a1a1f"   # deep neutral dark
            text = "#e8e8ec"
        else:
            bg   = "#f5f4f0"   # warm off-white
            text = "#1a1a1f"

        # Push colours into the widget palette so child widgets inherit correctly
        palette = self._bg.palette()
        palette.setColor(QPalette.ColorRole.Window,     QColor(bg))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(text))
        self._bg.setPalette(palette)
        self._bg.setAutoFillBackground(True)

        # Also update the window-level palette so title bar area matches
        self.setPalette(palette)


def main():
    app = QApplication(sys.argv)

    # On Windows let Qt detect and follow the system colour scheme
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()