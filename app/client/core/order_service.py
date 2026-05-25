def find_product(products: list[dict], brand: str, name: str) -> dict | None:
    for p in products:
        if p["brand"] == brand and p["name"] == name:
            return p
    return None


def format_price(price: float) -> str:
    """Format price as Vietnamese style with thousand separators."""
    return f"{price:,.0f}" 


def calc_total(quantity: int, price: float) -> float:
    """Calculate the total for a row."""
    return quantity * price