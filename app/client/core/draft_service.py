"""
draft_service.py — saves/loads the current order draft to disk.

Used to restore the in-progress order when the app restarts.
"""

import json
from pathlib import Path
import os

def _draft_file() -> Path:
    """Return the draft file path. Uses %APPDATA%\\MTMS\\draft.json."""
    appdata = os.environ.get("APPDATA")
    if appdata:
        folder = Path(appdata) / "MTMS"
    else:
        # Fallback to user home
        folder = Path.home() / ".mtms"
        print(folder)
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "draft.json"

_DRAFT_FILE = _draft_file()

def save_draft(data: dict):
    """Write the current order draft to disk."""
    try:
        _DRAFT_FILE.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        print(f"[draft] Could not save draft: {e}")


def load_draft() -> dict | None:
    """Load the saved draft, or None if missing/invalid."""
    if not _DRAFT_FILE.exists():
        return None
    try:
        return json.loads(_DRAFT_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[draft] Could not load draft: {e}")
        return None