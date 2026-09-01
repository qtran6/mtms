"""Fire-and-forget order logging with local queue for offline resilience."""
import json
import socket
import threading
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

from client.core.config_service import load_config

QUEUE_FILE = Path.home() / "AppData" / "Roaming" / "MTMS" / "pending.jsonl"


def log_order(customer: str, rows: list[dict]):
    """Called after a successful print. Never raises."""
    cfg = load_config()
    payload = {
        "client_name": cfg.get("client_name", socket.gethostname()),
        "printed_at": datetime.now().isoformat(),
        "customer": customer,
        "rows": rows,
    }
    threading.Thread(target=_send, args=(payload,), daemon=True).start()


def _send(payload: dict):
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    server_url = load_config().get("server_url", "http://desktop-01:6161").rstrip("/")

    # Drain any pending orders first, then add this one at the end
    pending = _read_queue() + [payload]
    remaining = []
    for item in pending:
        if _post(server_url, item):
            continue
        remaining.append(item)
    _write_queue(remaining)

def _post(server_url: str, payload: dict) -> bool:
    """POST one order. Return True on success, False on any failure."""
    try:
        req = Request(
            f"{server_url}/orders",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urlopen(req, timeout=3) as r:
            return r.status == 200
    except (URLError, TimeoutError, OSError):
        return False


def _read_queue() -> list[dict]:
    if not QUEUE_FILE.exists():
        return []
    with open(QUEUE_FILE, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _write_queue(items: list[dict]):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")