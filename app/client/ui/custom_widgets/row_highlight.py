"""
row_highlight.py — briefly flash a table row when added.
"""

from PySide6.QtCore import QVariantAnimation, QEasingCurve
from PySide6.QtGui import QColor, QBrush


def flash_row(table, row: int, highlight_color: str = "#fff4a3", duration_ms: int = 800):
    print(f"[flash] row={row}, cols={table.columnCount()}")
    print(f"[flash] item(row,0)={table.item(row, 0)}")

    start_color = QColor(highlight_color)
    end_color = QColor(0, 0, 0, 0)   # transparent

    anim = QVariantAnimation(table)
    anim.setStartValue(start_color)
    anim.setEndValue(end_color)
    anim.setDuration(duration_ms)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def on_value_changed(color: QColor):
        for col in range(table.columnCount()):
            item = table.item(row, col)
            if item:
                item.setBackground(QBrush(color))

    anim.valueChanged.connect(on_value_changed)
    anim.start(QVariantAnimation.DeletionPolicy.DeleteWhenStopped)
    print(f"[flash] animation started, state={anim.state()}")
