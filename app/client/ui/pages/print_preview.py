"""
print_preview.py — print preview page styled like Excel's print pane.

Layout:
- Left column: Print button, Copies, Printer dropdown
- Right column: rendered preview of the PDF
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QGridLayout,
    QPushButton, QLabel, QComboBox, QSpinBox, QScrollArea,
    QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPrintSupport import QPrinterInfo

from client.ui.custom_widgets import *


class PrintPreviewPage(QWidget):
    """
    A print preview page. Call `load_pdf(path)` to display a PDF
    and let the user pick printer + copies and click Print.
    """

    # Signal emitted when print is requested
    # Args: pdf_path, printer_name, copies
    print_requested = Signal(str, str, int)
    cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pdf_path: str | None = None
        self._pdf_doc = QPdfDocument(self)
        self._page_pixmaps: list[QPixmap] = []

        self._build_ui()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        # Left settings panel
        self._settings_panel = self._build_settings_panel()
        self._settings_panel.setFixedWidth(280)

        # Right preview panel
        self._preview_panel = self._build_preview_panel()

        layout.addWidget(self._settings_panel)
        layout.addWidget(self._preview_panel, 1)

    def _build_settings_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("settings_panel")
        v = QVBoxLayout(panel)
        v.setSpacing(16)
        v.setContentsMargins(20, 20, 20, 20)

        # Print button — large, focused by default
        self._print_btn = QPushButton("In")
        self._print_btn.setObjectName("preview_print_btn")
        self._print_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._print_btn.setMinimumHeight(100)
        self._print_btn.clicked.connect(self._on_print)
        # This is the default button — Enter triggers it
        self._print_btn.setDefault(True)
        self._print_btn.setAutoDefault(True)

        # Cancel button
        self._cancel_btn = QPushButton("Hủy")
        self._cancel_btn.setObjectName("preview_cancel_btn")
        self._cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._cancel_btn.clicked.connect(self.cancelled.emit)

        # Copies
        copies_label = QLabel("Số bản:")
        copies_label.setObjectName("preview_label")
        self._copies_spin = QSpinBox()
        self._copies_spin.setMinimum(1)
        self._copies_spin.setMaximum(99)
        self._copies_spin.setValue(1)

        # Printer dropdown
        printer_label = QLabel("Máy in:")
        printer_label.setObjectName("preview_label")
        self._printer_combo = QComboBox()
        self._populate_printers()

        v.addWidget(self._print_btn)
        v.addSpacing(8)
        v.addWidget(copies_label)
        v.addWidget(self._copies_spin)
        v.addWidget(printer_label)
        v.addWidget(self._printer_combo)
        v.addStretch(1)
        v.addWidget(self._cancel_btn)

        return panel

    def _build_preview_panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("preview_panel")
        v = QVBoxLayout(panel)
        v.setContentsMargins(0, 0, 0, 0)

        # Scroll area holding the rendered PDF pages
        self._scroll = QScrollArea()
        self._scroll.setObjectName("preview_scroll")
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Inner container — holds page QLabels stacked vertically
        self._pages_container = QWidget()
        self._pages_layout = QVBoxLayout(self._pages_container)
        self._pages_layout.setSpacing(12)
        self._pages_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._scroll.setWidget(self._pages_container)
        v.addWidget(self._scroll)

        return panel

    def _populate_printers(self):
        self._printer_combo.clear()
        printers = QPrinterInfo.availablePrinterNames()
        default = QPrinterInfo.defaultPrinterName()

        if not printers:
            self._printer_combo.addItem("(không có máy in)")
            self._printer_combo.setEnabled(False)
            return

        self._printer_combo.addItems(printers)
        if default in printers:
            self._printer_combo.setCurrentText(default)

    # ── Public API ────────────────────────────────────────────────────────────
    def load_pdf(self, pdf_path: str):
        """Load a PDF and render its pages into the preview area."""
        self._pdf_path = pdf_path
        result = self._pdf_doc.load(pdf_path)
        if result != QPdfDocument.Error.None_:
            print(f"[preview] PDF load failed: {result}")
            return

        self._clear_pages()
        self._render_pages()
        # Move focus to the Print button so Enter works
        self._print_btn.setFocus()

    def _clear_pages(self):
        while self._pages_layout.count():
            item = self._pages_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        self._page_pixmaps = []

    def _render_pages(self):
        # Render each page at ~150 DPI for smooth preview
        # PDF page size is in points; 1 inch = 72 points; 150 DPI → 150/72 = ~2.08x
        scale = 2.0
        for i in range(self._pdf_doc.pageCount()):
            point_size = self._pdf_doc.pagePointSize(i)
            target_w = int(point_size.width()  * scale)
            target_h = int(point_size.height() * scale)
            from PySide6.QtCore import QSize
            image = self._pdf_doc.render(i, QSize(target_w, target_h))

            pix = QPixmap.fromImage(image)
            self._page_pixmaps.append(pix)

            label = QLabel()
            label.setPixmap(pix)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setObjectName("preview_page")
            self._pages_layout.addWidget(label)

    # ── Slot ──────────────────────────────────────────────────────────────────
    def _on_print(self):
        if not self._pdf_path:
            return
        printer = self._printer_combo.currentText()
        copies = self._copies_spin.value()
        self.print_requested.emit(self._pdf_path, printer, copies)

    # ── Theme ─────────────────────────────────────────────────────────────────
    def apply_theme(self, t: dict):
        r = t.get("radius", 12)

        # Shadows
        apply_shadow(self._settings_panel, t)
        apply_cast_shadow(self._settings_panel, t)
        apply_shadow(self._preview_panel, t)
        apply_cast_shadow(self._preview_panel, t)

        card_style = f"""
            background: {t['card_bg']};
            border: none;
            border-radius: {r}px;
            padding: 10px;
        """

        self.setStyleSheet(f"""
            QFrame#settings_panel {{ {card_style} }}
            QFrame#preview_panel {{ {card_style} }}

            QLabel#preview_label {{
                color: {t['text']};
                background: transparent;
                font-weight: bold;
                padding: 0;
            }}

            QPushButton#preview_print_btn {{
                background: {t['btn_bg']};
                color: {t['text']};
                border: none;
                border-radius: 6px;
                font-size: 26pt;
                font-weight: bold;
            }}
            QPushButton#preview_print_btn:hover {{
                background: {t['btn_hover_bg']};
            }}
            QPushButton#preview_print_btn:focus {{
                border: 2px solid {t['input_border_focus']};
            }}

            QPushButton#preview_cancel_btn {{
                background: {t['clear_btn_bg']};
                color: {t['close_hover_text']};
                border: none;
                border-radius: 6px;
                padding: 10px;
            }}
            QPushButton#preview_cancel_btn:hover {{
                background: {t['clear_btn_hover_bg']};
            }}

            QComboBox, QSpinBox {{
                background: {t['input_bg']};
                color: {t['text']};
                border: 1px solid {t['input_border']};
                border-radius: 4px;
                padding: 8px;
            }}
            QComboBox QAbstractItemView {{
                background: {t['card_bg']};
                color: {t['text']};
                selection-background-color: {t['btn_hover_bg']};
            }}

            QScrollArea#preview_scroll {{
                background: transparent;
                border: none;
            }}
            QLabel#preview_page {{
                background: white;
                border: 1px solid {t['border']};
            }}
        """)
