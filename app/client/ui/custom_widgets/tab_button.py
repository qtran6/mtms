"""
tab_button.py — a tab with a label, a ✕ close button, and rename on double-click.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtCore import Qt, Signal


class TabButton(QWidget):
    """A tab with a label, a small ✕ close button, and rename on double-click."""
    clicked = Signal()
    closed = Signal()
    renamed = Signal(str)

    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 4, 4)
        layout.setSpacing(6)

        self._label = QLabel(str(label))

        self._editor = QLineEdit()
        self._editor.setObjectName("tab_edit")
        self._editor.setFixedSize(80, 24)
        self._editor.hide()
        self._editor.editingFinished.connect(self._finish_rename)

        self._close = QPushButton("✕")
        self._close.setFixedSize(28, 28)
        self._close.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close.setObjectName("tab_close_btn")

        layout.addWidget(self._label)
        layout.addWidget(self._editor)
        layout.addWidget(self._close)

        self._close.clicked.connect(self.closed.emit)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("tab_btn")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._start_rename()
        super().mouseDoubleClickEvent(event)

    def _start_rename(self):
        self._editor.setText(self._label.text())
        self._label.hide()
        self._editor.show()
        self._editor.setFocus()
        self._editor.selectAll()

    def _finish_rename(self):
        new_name = self._editor.text().strip()
        if new_name:
            self._label.setText(new_name)
            self.renamed.emit(new_name)
        self._editor.hide()
        self._label.show()

    def set_active(self, active: bool):
        self.setProperty("active", "true" if active else "false")
        self.style().unpolish(self)
        self.style().polish(self)