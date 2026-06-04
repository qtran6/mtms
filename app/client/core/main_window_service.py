"""
main_window_service.py — business logic and event handlers for the main window.

Holds the controller pattern just like OrderController. The MainWindow widget
constructs the UI and delegates behavior to MainWindowController.
"""

import sys
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QEvent, QRect
from PySide6.QtGui import QColor, QPainter, QBrush, QPainterPath, QPen


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
        """Called when the preview page emits print_requested."""
        sumatra = Path(__file__).parent.parent.parent / "data" / "SumatraPDF.exe"

        if not sumatra.exists():
            print(f"[print] SumatraPDF not found at: {sumatra}")
            self.window._content.setCurrentWidget(self.window._order_page)
            return

        print(f"[print] Printing to '{printer_name}' x{copies}")
        result = subprocess.run([
            str(sumatra),
            "-print-to", printer_name,
            "-silent",
            "-print-settings", f"{copies}x",
            pdf_path,
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"[print] SumatraPDF failed: {result.stderr}")

        self.window._content.setCurrentWidget(self.window._order_page)

    def handle_preview_cancelled(self):
        self.window._content.setCurrentWidget(self.window._order_page)

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    def handle_close(self):
        """Called from MainWindow.closeEvent — save draft."""
        current = self.window._content.currentWidget()
        if hasattr(current, "_controller") and hasattr(current._controller, "save_state"):
            current._controller.save_state()