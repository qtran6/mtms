from PySide6.QtCore import QObject, QEvent, Qt
from PySide6.QtWidgets import QComboBox

class LoopBackOnTab(QObject):
    def __init__(self, target, parent=None):
        super().__init__(parent)
        self._target = target

    def eventFilter(self, obj, event):
        if (event.type() == QEvent.Type.KeyPress and
            event.key() == Qt.Key.Key_Tab and
            not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier)):
            if hasattr(self._target, "lineEdit") and self._target.lineEdit():
                self._target.lineEdit().setFocus()
            else:
                self._target.setFocus()
            return True
        return False