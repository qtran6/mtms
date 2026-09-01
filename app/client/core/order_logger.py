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
    server_url = load_config().get("server_url", "http://localhost:6034").rstrip("/")
    if not server_url:
        _enqueue(payload)
        return

    try:
        req = Request(
            f"{server_url}/orders",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urlopen(req, timeout=3) as r:
            if r.status != 200:
                _enqueue(payload)
    except (URLError, TimeoutError, OSError):
        _enqueue(payload)


def _enqueue(payload: dict):
    with open(QUEUE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")