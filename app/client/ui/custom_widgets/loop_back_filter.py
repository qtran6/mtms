from PySide6.QtCore import QObject, QEvent, QTimer, Qt
from PySide6.QtWidgets import QComboBox

class LoopBackOnTab(QObject):
    def __init__(self, target, parent=None):
        super().__init__(parent)
        self._target = target

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress and event.key() == Qt.Key.Key_Tab:
            if not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                # Get the line edit if target is a combo
                target_widget = self._target
                if isinstance(target_widget, QComboBox) and target_widget.lineEdit():
                    target_widget = target_widget.lineEdit()
                
                target_widget.setFocus()
                # Defer selectAll so it runs after focus completes
                if hasattr(target_widget, "selectAll"):
                    QTimer.singleShot(0, target_widget.selectAll)
                return True
        return False