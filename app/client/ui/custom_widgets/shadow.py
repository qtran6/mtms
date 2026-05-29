"""
shadow.py — drop shadow helpers used by pages.
"""

from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtGui import QColor


def parse_color(rgba_str: str) -> QColor:
    """Parse 'rgba(r, g, b, a)' where a is 0.0-1.0 into QColor."""
    try:
        inner = rgba_str.strip().removeprefix("rgba(").removesuffix(")")
        r, g, b, a = [x.strip() for x in inner.split(",")]
        color = QColor(int(r), int(g), int(b))
        color.setAlphaF(float(a))
        return color
    except Exception:
        return QColor(0, 0, 0, 80)


def apply_shadow(widget, t: dict):
    """Subtle inner shadow (3px blur, 1px offset) using theme's 'shadow' color."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(3)
    shadow.setOffset(0, 1)
    shadow.setColor(parse_color(t.get("shadow", "rgba(0,0,0,0.2)")))
    widget.setGraphicsEffect(shadow)


def apply_cast_shadow(widget, t: dict):
    """Stronger cast shadow (12px blur, 3px offset) using theme's 'cast_shadow' color."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(12)
    shadow.setOffset(0, 3)
    shadow.setColor(parse_color(t.get("cast_shadow", "rgba(0,0,0,0.3)")))
    widget.setGraphicsEffect(shadow)
