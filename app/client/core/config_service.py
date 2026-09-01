import json, os
from pathlib import Path

def _config_file() -> Path:
    appdata = os.environ.get("APPDATA")
    folder = Path(appdata) / "MTMS" if appdata else Path.home() / ".mtms"
    folder.mkdir(parents=True, exist_ok=True)
    return folder / "config.json"

def load_config() -> dict:
    path = _config_file()
    server_url = "http://Desktop-01:6161"
    if not path.exists():
        return {"server_url": server_url}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_config(data: dict):
    try:
        _config_file().write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
    except Exception as e:
        print(f"[config] Could not save: {e}")