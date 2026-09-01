"""MTMS logging server — runs on the main PC. Localhost UI + LAN client POSTs."""
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime, date
import sqlite3, json

DB = Path(__file__).parent / "orders.db"

class RowIn(BaseModel):
    brand: str
    name: str
    qty: int
    price: float
    total: float

class OrderIn(BaseModel):
    client_name: str
    printed_at: str
    customer: str
    rows: list[RowIn]

# Database connection helper
def __conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with __conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            printed_at TEXT NOT NULL,
            printed_date TEXT NOT NULL,
            received_at TEXT NOT NULL,
            customer TEXT,
            rows_json TEXT NOT NULL
        )""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_date ON orders(printed_date)")

app = FastAPI()
init_db()

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")

@app.get("/", response_class=HTMLResponse)
def index():
    return (Path(__file__).parent / "index.html").read_text(encoding="utf-8")

@app.get("/aggregate", response_class=HTMLResponse)
def aggregate_page():
    return (Path(__file__).parent / "aggregate.html").read_text(encoding="utf-8")

@app.get("/orders")
def list_orders(date: str,
                brand: str | None = None,
                client: str | None = None,
                customer: str | None = None):
    with __conn() as c:
        raw = c.execute(
            "SELECT * FROM orders WHERE printed_date = ? ORDER BY id DESC",
            (date,)
        ).fetchall()

    result = []
    for row in raw:
        if client and row["client_name"] != client:
            continue
        if customer and customer.lower() not in (row["customer"] or "").lower():
            continue

        all_rows = json.loads(row["rows_json"])
        filtered = [r for r in all_rows if not brand or r.get("brand") == brand]
        if brand and not filtered:
            continue

        result.append({
            "id": row["id"],
            "client_name": row["client_name"],
            "printed_at": row["printed_at"],
            "customer": row["customer"],
            "rows": filtered,
        })
    return result

@app.get("/brands")
def list_brands():
    with __conn() as c:
        seen = set()
        for row in c.execute("SELECT rows_json FROM orders"):
            for r in json.loads(row["rows_json"]):
                if r.get("brand"):
                    seen.add(r["brand"])
    return sorted(seen)

@app.get("/clients")
def list_clients():
    with __conn() as c:
        return sorted(r["client_name"] for r in c.execute(
            "SELECT DISTINCT client_name FROM orders"
        ))

@app.post("/orders")
def post_order(order: OrderIn):
    with __conn() as c:
        c.execute(
            "INSERT INTO orders (client_name, printed_at, printed_date, received_at, customer, rows_json)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                order.client_name,
                order.printed_at,
                order.printed_at[:10],
                datetime.now().isoformat(),
                order.customer,
                json.dumps([row.model_dump() for row in order.rows], ensure_ascii=False)
            )
        )
    return {"ok": True}

@app.delete("/orders/{order_id}")
def delete_order(order_id: int):
    with __conn() as c:
        cur = c.execute("DELETE FROM orders WHERE id = ?", (order_id,))
        if cur.rowcount == 0:
            raise HTTPException(404, "not found")
    return {"ok": True}

@app.get("/api/aggregate")
def aggregate(date_from: str, date_to: str):
    with __conn() as c:
        raw = c.execute(
            "SELECT rows_json FROM orders WHERE printed_date BETWEEN ? AND ?",
            (date_from, date_to)
        ).fetchall()

    grouped: dict[tuple[str, str], dict] = {}
    for row in raw:
        for r in json.loads(row["rows_json"]):
            key = (r.get("brand", ""), r["name"])
            if key not in grouped:
                grouped[key] = {
                    "brand": key[0],
                    "name":  key[1],
                    "qty":   r["qty"],
                    "price": r["price"],
                }
            else:
                grouped[key]["qty"] += r["qty"]
                grouped[key]["price"] = min(grouped[key]["price"], r["price"])

    items = sorted(grouped.values(), key=lambda x: (x["brand"], x["name"]))
    for it in items:
        it["total"] = it["qty"] * it["price"]

    return {
        "items": items,
        "grand_total": sum(it["total"] for it in items),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6034)