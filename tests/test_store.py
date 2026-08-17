"""Pure store — money, listing, first order. No Component imports in store."""

from __future__ import annotations

import ast
from pathlib import Path

from app import store
from app.catalog import PRODUCTS
from app.store import ShopQuery


def test_listing_takes_query_not_host():
    rows = store.listing(ShopQuery(category="wear", sort="price_desc"))
    assert rows
    assert all(p["category"] == "wear" for p in rows)
    assert rows[0]["price"] >= rows[-1]["price"]


def test_price_cap_and_search():
    cheap = store.listing(ShopQuery(price_max=2000))
    assert all(p["price"] <= 2000 for p in cheap)
    flax = store.listing(ShopQuery(query="flax"))
    assert any(p["id"] == "linen-throw" for p in flax)


def test_promo_and_shipping_are_arguments():
    sku = PRODUCTS[0]["id"]
    store.add_cart(sku, qty=1)
    sub = store.subtotal()
    assert store.discount("HARBOR10") == int(sub * 0.1)
    assert store.discount("COAST20") == int(sub * 0.2)
    assert store.discount("NOPE") == 0
    assert store.shipping("", "standard") in {0, 80}
    assert store.gift_fee(True) == 180
    assert store.gift_fee(False) == 0
    store.add_cart("wool-overshirt", qty=1)
    assert store.subtotal() >= 8000
    assert store.shipping("", "standard") == 0


def test_first_order_is_hc_24001():
    store.add_cart("linen-throw", qty=1)
    order = store.place_order(
        checkout={"name": "Ada", "address": "1 Dock", "city": "Gorakhpur", "pin": "273001", "pay": "upi"},
        ship="express",
        gift=True,
        promo="HARBOR10",
    )
    assert order is not None
    assert order["id"] == "HC-24001"
    assert order["status"] == "Packed"
    assert order["gift"] is True
    assert order["ship"] == "express"
    assert store.HOST["cart"] == []
    assert store.HOST["last_order"] == "HC-24001"


def test_store_does_not_import_components():
    src = Path(__file__).resolve().parents[1] / "app" / "store.py"
    tree = ast.parse(src.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert not node.module.startswith("app.host")
            assert not node.module.startswith("app.screens")
            assert not node.module.startswith("app.chrome")
            assert "ux_app" not in node.module
            assert "ux_channel" not in node.module
