"""
data_loader.py — Reads BangGia.xlsx and returns a flat list of products.

Place this file in the same directory as BangGia.xlsx (above client/).

Usage:
    from data_loader import load_products
    products = load_products()
    # Each product: {"brand": str, "name": str, "price": float}
"""

import sys

import pandas as pd
from pathlib import Path

def _xlsx_path() -> Path:
    """Find BangGia.xlsx — checks dev location and bundled location."""
    # When bundled with PyInstaller, sys.frozen is True
    if getattr(sys, "frozen", False):
        # Executable directory
        return Path(sys.executable).parent.parent / "BangGia.xlsx"
    else:
        # Dev — file is at app/data/BangGia.xlsx
        return Path(__file__).parent.parent.parent / "data" / "BangGia.xlsx"

_FILE = _xlsx_path()

def load_products(file_path: Path = _FILE) -> list[dict]:
    """
    Parse BangGia.xlsx and return a flat list of products.
    Each entry: {"brand": str, "name": str, "price": float}
    """
    file_path = Path(file_path)
    if file_path.is_dir():
        file_path = file_path / "BangGia.xlsx"

    df = pd.read_excel(file_path, sheet_name="Tổng Quát", header=None)

    # Row 0 = brand names in even columns (0, 2, 4 ...)
    # Rows 1+ = product name in even col, price in odd col
    brand_row = df.iloc[0]
    products = []

    for col in range(0, df.shape[1] - 1, 2):
        brand = brand_row[col]
        if pd.isna(brand) or str(brand).strip() == "":
            continue
        brand = str(brand).strip()

        for row in range(1, df.shape[0]):
            name  = df.iloc[row, col]
            price = df.iloc[row, col + 1]

            # Skip empty or separator rows
            if pd.isna(name) or str(name).strip() in ("", "."):
                continue

            # Skip rows where price is not numeric
            try:
                price = float(price)
            except (ValueError, TypeError):
                continue

            products.append({
                "brand": brand,
                "name":  str(name).strip(),
                "price": price,
            })

    return products

def _gia_dac_biet_path() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent.parent / "GiaDacBiet.xlsx"
    else:
        return Path(__file__).parent.parent.parent / "data" / "GiaDacBiet.xlsx"


def load_price_groups() -> list[dict]:
    """
    Parse GiaDacBiet.xlsx into brand blocks:
        [
            {"brand": "Chengshin", "tiers": [{"label": None, "prices": {name: price, ...}}]},
            {"brand": "OTO GS",    "tiers": [{"label": "9", "prices": {...}}, ...]},
            ...
        ]
    Column type is inferred from data rows: text→name, numeric→price.
    Returns [] if the file is missing or has no data rows yet.
    """
    path = _gia_dac_biet_path()
    if not path.exists():
        return []

    try:
        df = pd.read_excel(path, sheet_name="Tổng Quát", header=None)
    except Exception as e:
        print(f"[price_groups] load failed: {e}")
        return []

    if df.shape[0] < 2:
        return []  # header only, no products

    # Classify each column from data rows
    def classify(col: int) -> str:
        text, num = 0, 0
        for r in range(1, df.shape[0]):
            v = df.iloc[r, col]
            if pd.isna(v):
                continue
            try:
                float(v)
                num += 1
            except (ValueError, TypeError):
                text += 1
        if text == 0 and num == 0:
            return "empty"
        return "name" if text > num else "price"
    
    # Format header labels
    def _fmt_label(v) -> str:
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v).strip()

    kinds = [classify(c) for c in range(df.shape[1])]

    blocks = []
    current = None
    for c, kind in enumerate(kinds):
        header = df.iloc[0, c]
        if kind == "name":
            if current:
                blocks.append(current)
            current = {
                "brand": str(header).strip() if not pd.isna(header) else "",
                "_name_col": c,
                "tiers": [],
            }
        elif kind == "price" and current is not None:
            label = None if pd.isna(header) else _fmt_label(header)
            prices = {}
            for r in range(1, df.shape[0]):
                name = df.iloc[r, current["_name_col"]]
                price = df.iloc[r, c]
                if pd.isna(name) or str(name).strip() in ("", "."):
                    continue
                try:
                    prices[str(name).strip()] = float(price)
                except (ValueError, TypeError):
                    continue
            current["tiers"].append({"label": label, "prices": prices})
    if current:
        blocks.append(current)

    for b in blocks:
        b.pop("_name_col", None)
    return blocks

if __name__ == "__main__":
    products = load_products()
    print(f"Loaded {len(products)} products")
    for p in products[:100]:
        print(p)