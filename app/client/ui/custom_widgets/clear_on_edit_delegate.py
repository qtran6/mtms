from PySide6.QtWidgets import QStyle, QStyledItemDelegate


class ClearOnEditDelegate(QStyledItemDelegate):
    def setEditorData(self, editor, index):
        # Open editor blank
        pass

    def paint(self, painter, option, index):
        # If this cell is being edited, don't draw its text
        if option.state & QStyle.StateFlag.State_Editing:
            return
        super().paint(painter, option, index)