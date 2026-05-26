from PySide6.QtCore import QObject, QEvent, QTimer, Qt


class EnterDownFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and event.key() in (
            Qt.Key.Key_Return, Qt.Key.Key_Enter
        ):
            QTimer.singleShot(0, lambda: self._move_down(obj))
            return False  # let Qt also process the Enter (commit edit)
        return False

    def _move_down(self, table):
        current = table.currentIndex()
        next_row = current.row() + 1
        if next_row < table.rowCount():
            table.setCurrentCell(next_row, current.column())