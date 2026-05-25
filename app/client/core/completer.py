from PySide6.QtWidgets import QComboBox, QCompleter
from PySide6.QtCore import Qt


def combo_completer(combo: QComboBox):
    """
    Configure a QComboBox's built-in completer for contains-match filtering.
    Call this once after setEditable(True), and again after clear()/addItems()
    since clear() resets the completer.
    """
    completer = combo.completer()
    if completer is None:
        return
    completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
    completer.setFilterMode(Qt.MatchFlag.MatchContains)
    completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)