"""
main_window_service.py — business logic and event handlers for the main window.

Holds the controller pattern just like OrderController. The MainWindow widget
constructs the UI and delegates behavior to MainWindowController.
"""

import subprocess

from PySide6.QtCore import QThread, Qt, QTimer, QEvent, QRect, Signal
from PySide6.QtGui import QColor, QPainter, QBrush, QPainterPath, QPen
from pathlib import Path
from PySide6.QtWidgets import QMessageBox


class MainWindowController:
    """
    Wires up the MainWindow behavior. Holds references to the window
    and handles state changes, print routing, and lifecycle events.
    """

    def __init__(self, window, *, radius: int, border: int, shadow: int, restore_size: tuple):
        self.window = window
        self.RADIUS = radius
        self.BORDER = border
        self.SHADOW = shadow
        self.RESTORE_SIZE = restore_size

        # State
        self._was_maximized_before_minimize = False
        
        self._autosave_timer = QTimer(window)
        self._autosave_timer.setInterval(30_000)   # 30s
        self._autosave_timer.timeout.connect(self.save_draft)
        self._autosave_timer.start()

    # ── Window state ──────────────────────────────────────────────────────────
    def set_margins(self, maximized: bool):
        m = 0 if maximized else self.SHADOW
        self.window.setContentsMargins(m, m, m, m)

    def handle_state_change(self, event: QEvent):
        """Called from MainWindow.changeEvent — handles maximize/minimize transitions."""
        if event.type() != QEvent.Type.WindowStateChange:
            return

        window = self.window
        old_state = event.oldState()

        # Detect minimizing — remember if we were maximized
        if window.windowState() & Qt.WindowState.WindowMinimized:
            self._was_maximized_before_minimize = bool(
                old_state & Qt.WindowState.WindowMaximized
            )
            return

        # Detect restoring from minimized
        if old_state & Qt.WindowState.WindowMinimized:
            if self._was_maximized_before_minimize:
                QTimer.singleShot(0, window.showMaximized)
            return

        # Normal maximize/restore handling
        maximized = window.isMaximized()
        if maximized != window._maximized:
            window._maximized = maximized
            if not maximized:
                QTimer.singleShot(0, lambda: window.resize(*self.RESTORE_SIZE))
            self.set_margins(maximized)
            window._apply_theme(force=True)
            window.update()

    # ── Painting ──────────────────────────────────────────────────────────────
    def paint_window(self, painter: QPainter):
        """Draw the rounded background + border. Called from paintEvent."""
        window = self.window
        if not window._theme:
            return

        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg_color     = QColor(window._theme["background"])
        border_color = QColor(window._theme["border"])

        if window._maximized:
            painter.fillRect(window.rect(), QBrush(bg_color))
        else:
            rect = QRect(
                self.SHADOW, self.SHADOW,
                window.width()  - self.SHADOW * 2,
                window.height() - self.SHADOW * 2
            )
            path = QPainterPath()
            path.addRoundedRect(rect, self.RADIUS, self.RADIUS)
            painter.fillPath(path, QBrush(bg_color))
            pen = QPen(border_color, self.BORDER)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(path)

    # ── Print routing ─────────────────────────────────────────────────────────
    def trigger_print(self):
        """Called by Ctrl+P shortcut. Delegates to the current page's controller."""
        current = self.window._content.currentWidget()
        if hasattr(current, "_controller") and hasattr(current._controller, "on_print"):
            current._controller.on_print()

    def show_print_preview(self, pdf_path: str):
        """Switch to the preview page and load a PDF."""
        self.window._print_preview_page.load_pdf(pdf_path)
        self.window._content.setCurrentWidget(self.window._print_preview_page)

    def handle_print_requested(self, pdf_path: str, printer_name: str, copies: int):
        try:
            sumatra = Path(__file__).parent.parent.parent / "data" / "SumatraPDF.exe"
            if not sumatra.exists():
                QMessageBox.warning(self.window, "Lỗi in",
                                    "Không tìm thấy SumatraPDF.exe — không thể in.")
                return
            result = subprocess.run([
                str(sumatra),
                "-print-to", printer_name,
                "-silent",
                "-print-settings", f"{copies}x",
                pdf_path,
            ], capture_output=True, text=True)
            if result.returncode != 0:
                QMessageBox.warning(self.window, "Lỗi in",
                                    f"In thất bại (máy in: {printer_name}).\n{result.stderr.strip()}")
        except Exception as e:
            QMessageBox.warning(self.window, "Lỗi in", f"In thất bại:\n{e}")
        finally:
            self.window._content.setCurrentWidget(self.window._order_page)

    def handle_preview_cancelled(self):
        self.window._content.setCurrentWidget(self.window._order_page)

    # ── Update button ───────────────────────────────────────────────────────
    def reposition_update_btn(self):
        btn = self.window._update_btn
        margin = 20
        btn.move(
            self.window.width()  - btn.width()  - margin,
            self.window.height() - btn.height() - margin,
        )

    def handle_resize(self, event):
        if hasattr(self.window, "_update_btn"):
            self.reposition_update_btn()

    def check_for_update(self):
        self._check_worker = _UpdateCheckWorker()
        self._check_worker.found.connect(
            lambda r: self.window._update_btn.notify(r["version"], r["download_url"])
        )
        self._check_worker.start()

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    def save_draft(self):
        page = self.window._order_page
        if hasattr(page, "_controller") and hasattr(page._controller, "save_state"):
            page._controller.save_state()
            
    def handle_close(self):
        """Called from MainWindow.closeEvent — save draft."""
        self.save_draft()

class _UpdateCheckWorker(QThread):
    """Runs the GitHub release check off the GUI thread."""
    found = Signal(dict)

    def run(self):
        from client.core.updater import check_for_update
        result = check_for_update()
        if result:
            self.found.emit(result)