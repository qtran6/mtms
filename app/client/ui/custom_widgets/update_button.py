"""
update_button.py — floating download button with circular progress ring.
"""

from PySide6.QtWidgets import QWidget, QPushButton
from PySide6.QtCore import Qt, QRect, QThread, Signal, QSize
from PySide6.QtGui import QPainter, QColor, QPen, QIcon


class _DownloadWorker(QThread):
    progress = Signal(int)
    finished = Signal()
    failed = Signal(str)

    def __init__(self, url: str):
        super().__init__()
        self._url = url

    def run(self):
        from client.core.updater import download_and_install
        try:
            download_and_install(self._url, self.progress.emit)
            self.finished.emit()
        except Exception as e:
            self.failed.emit(str(e))


class UpdateButton(QWidget):
    """
    Floating circular button with a progress arc drawn outside it.
    Parent must call `notify(version, download_url)` when update is found.
    """

    SIZE = 52        # button diameter
    RING = 5         # progress ring thickness
    PADDING = 6      # gap between button edge and ring

    def __init__(self, parent=None):
        super().__init__(parent)
        total = self.SIZE + (self.RING + self.PADDING) * 2
        self.setFixedSize(total, total)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setVisible(False)

        self._progress = 0          # 0–100
        self._download_url = ""
        self._worker: _DownloadWorker | None = None
        self._failed = False
        self._theme: dict = {}

        # Inner arrow button
        self._btn = QPushButton("↓", self)
        self._btn.setFixedSize(self.SIZE, self.SIZE)
        self._btn.move(self.RING + self.PADDING, self.RING + self.PADDING)
        self._btn.setObjectName("update_fab")
        self._btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn.clicked.connect(self._on_clicked)
        self._btn.setToolTip("Tải bản cập nhật")

    def notify(self, version: str, download_url: str):
        self._download_url = download_url
        self._btn.setToolTip(f"Cập nhật v{version} — nhấn để tải")
        self._progress = 0
        self._failed = False
        self.setVisible(True)
        self.update()

    def apply_theme(self, t: dict):
        self._theme = t
        r = self.SIZE // 2
        self._btn.setStyleSheet(f"""
            QPushButton#update_fab {{
                background: {t['btn_bg']};
                color: {t['text']};
                border: none;
                border-radius: {r}px;
                font-size: 22pt;
                font-weight: bold;
            }}
            QPushButton#update_fab:hover {{
                background: {t['btn_hover_bg']};
            }}
            QPushButton#update_fab:disabled {{
                background: {t['input_bg']};
                color: {t['placeholder']};
            }}
        """)
        self.update()

    # ── Paint the progress arc ────────────────────────────────────────────
    def paintEvent(self, event):
        if self._progress <= 0:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        offset = self.RING // 2 + 1
        rect = QRect(offset, offset,
                     self.width() - offset * 2,
                     self.height() - offset * 2)

        # Background track
        track_color = QColor(self._theme.get("input_border", "#cccccc"))
        pen = QPen(track_color, self.RING, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(rect, 0, 360 * 16)

        # Progress arc (starts at 12 o'clock, goes clockwise)
        if self._failed:
            arc_color = QColor("#e53935")
        else:
            arc_color = QColor(self._theme.get("btn_bg", "#1976d2"))
        pen.setColor(arc_color)
        painter.setPen(pen)
        span = int(self._progress / 100 * 360 * 16)
        painter.drawArc(rect, 90 * 16, -span)

    # ── Download logic ────────────────────────────────────────────────────
    def _on_clicked(self):
        if self._worker and self._worker.isRunning():
            return
        if self._failed:
            # Reset and retry
            self._failed = False
            self._progress = 0
            self.update()

        self._btn.setEnabled(False)
        self._btn.setText("↓")
        self._progress = 1
        self.update()

        self._worker = _DownloadWorker(self._download_url)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)
        self._worker.start()

    def _on_progress(self, value: int):
        self._progress = value
        self.update()

    def _on_finished(self):
        self._progress = 100
        self.update()

    def _on_failed(self, msg: str):
        self._failed = True
        self._btn.setEnabled(True)
        self._btn.setText("↻")
        self._btn.setToolTip(f"Tải thất bại — nhấn để thử lại")
        self.update()