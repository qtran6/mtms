"""
draft_service.py — saves/loads the current order draft to disk.

Used to restore the in-progress order when the app restarts.
"""

import json
from pathlib import Path

_DRAFT_FILE = Path(__file__).parent.parent.parent / "data" / "draft.json"


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