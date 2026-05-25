"""
theme.py — loads and exposes the active theme from theme.json.

Usage:
    from theme import theme
    bg = theme["background"]
"""

import json
from pathlib import Path

_THEME_FILE = Path(__file__).parent / "theme.json"


def load_theme(mode: str) -> dict:
    """
    Load the theme dict for the given mode ('dark' or 'light').
    Falls back to light if the file is missing or malformed.
    """
    try:
        data = json.loads(_THEME_FILE.read_text(encoding="utf-8"))
        return {**data["base"], **data[mode]}  # Merge base with mode-specific overrides
    except Exception as e:
        print(f"[theme] Failed to load theme.json: {e} — using built-in fallback")
        return {**_FALLBACK["base"], **_FALLBACK[mode]}


# Built-in fallback so the app never crashes if theme.json is missing
_FALLBACK = {
    "base": {
        "close_hover":      "#c0392b",
        "close_hover_text": "#ffffff",
        "radius":           12,
        "border_width":     2,
        "shadow":           10,
        "font":             "Segoe UI",
        "header_font":      "Segoe UI Semibold",
        "header_size":      35,
        "font_size":        5
    },
    "dark": {
        "background":   "#1a1a1f",
        "text":         "#e8e8ec",
        "border":       "#555560",
        "titlebar_bg":  "#1a1a1f",
        "btn_hover_bg": "#2e2e35"
    },
    "light": {
        "background":   "#f5f4f0",
        "text":         "#1a1a1f",
        "border":       "#aaaaaa",
        "titlebar_bg":  "#f5f4f0",
        "btn_hover_bg": "#e0deda"
    }
}
