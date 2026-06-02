"""
filters.py — event filters used by the Order page.
"""

from PySide6.QtCore import QObject, QEvent, Qt, QTimer
from PySide6.QtWidgets import QComboBox, QAbstractItemView, QScrollArea


class LoopBackOnTab(QObject):
    """Tab in `obj` jumps focus back to `_target`."""

    def __init__(self, target, parent=None):
        super().__init__(parent)
        self._target = target

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Tab:
            if not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                target = self._target
                if isinstance(target, QComboBox) and target.lineEdit():
                    target = target.lineEdit()
                target.setFocus()
                if hasattr(target, "selectAll"):
                    QTimer.singleShot(0, target.selectAll)
                return True
        return False


class EnterDownFilter(QObject):
    """Pressing Enter in a QTableWidget moves selection one row down."""

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and event.key() in (
            Qt.Key.Key_Return, Qt.Key.Key_Enter
        ):
            QTimer.singleShot(0, lambda: self._move_down(obj))
            return False
        return False

    def _move_down(self, table):
        current = table.currentIndex()
        next_row = current.row() + 1
        if next_row < table.rowCount():
            table.setCurrentCell(next_row, current.column())


class DeleteCellFilter(QObject):
    """Pressing Delete on selected cells clears their contents."""

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Delete:
            if obj.state() == QAbstractItemView.State.EditingState:
                return False
            for index in obj.selectedIndexes():
                item = obj.item(index.row(), index.column())
                if item:
                    item.setText("")
            return True
        return False
    
class HorizontalScrollArea(QScrollArea):
    """QScrollArea where mouse wheel scrolls horizontally instead of vertically."""
    
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta:
            bar = self.horizontalScrollBar()
            bar.setValue(bar.value() - delta)
            event.accept()
        else:
            super().wheelEvent(event)