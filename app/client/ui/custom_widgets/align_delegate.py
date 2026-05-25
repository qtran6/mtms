from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtCore import Qt

class AlignDelegate(QStyledItemDelegate):
    def __init__(self, alignment_name, parent=None):
        super().__init__(parent)
        alignment_map = {
            "left":   Qt.AlignmentFlag.AlignLeft  | Qt.AlignmentFlag.AlignVCenter,
            "center": Qt.AlignmentFlag.AlignCenter,
            "right":  Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        }
        self._alignment = alignment_map.get(
            alignment_name, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.displayAlignment = self._alignment