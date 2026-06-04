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
        return Path(sys.executable).parent / "BangGia.xlsx"
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

if __name__ == "__main__":
    products = load_products()
    print(f"Loaded {len(products)} products")
    for p in products[:100]:
        print(p)