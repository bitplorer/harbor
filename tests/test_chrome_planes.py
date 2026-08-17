"""Harbor chrome lives on Component Session fields, not store.HOST."""

from __future__ import annotations

import ast
from pathlib import Path

from app import store
from app.catalog import PRODUCTS
from app.host import chrome, home, host
from app.planes import Chrome, Home


CHROME_KEYS = {
    "page",
    "slide",
    "menu_open",
    "notice",
    "pdp_tab",
    "command_q",
    "category",
    "query",
    "sort",
    "page_n",
    "price_max",
    "product_id",
    "size",
    "ship",
    "gift",
    "deliver",
    "promo",
    "order_id",
    "checkout",
}


def _submit(name: str, **args):
    cap = host.mint(name, args)
    return host.submit(name, args, cap=cap)


def test_slide_is_plain_int_not_session_var():
    home.slide = 0
    assert home.slide == 0
    assert type(home.slide) is int
    home.slide = 2
    assert home.slide == 2
    assert type(home.slide) is int
    assert not hasattr(home.slide, "get")


def test_nav_slide_keeps_image_and_title_keyed_together():
    featured = [p for p in PRODUCTS if p.get("featured")]
    assert len(featured) >= 2
    _submit("nav.slide", index="1")
    idx = int(home.slide or 0) % len(featured)
    assert idx == 1
    hero = featured[idx]
    assert hero["img"] and hero["name"]
    _submit("nav.slide", index="0")
    other = featured[int(home.slide or 0) % len(featured)]
    assert (other["img"], other["name"]) != (hero["img"], hero["name"])
    assert other["id"] == featured[0]["id"]


def test_menu_and_notice_are_chrome_session():
    chrome.menu_open = False
    _submit("menu.toggle")
    assert chrome.menu_open is True
    _submit("notice.dismiss")
    assert chrome.notice is None
    _submit("menu.close")
    assert chrome.menu_open is False


def test_cart_stays_in_product_store():
    store.reset()
    sku = PRODUCTS[0]["id"]
    msg = store.add_cart(sku, qty=1)
    assert "Added" in msg or "Updated" in msg
    assert store.HOST["cart"]
    assert "cart" not in chrome.field_specs
    assert "wish" not in chrome.field_specs
    assert "orders" not in chrome.field_specs


def test_host_bag_has_no_chrome_keys():
    for key in CHROME_KEYS:
        assert key not in store.HOST, key
    assert "cart" in store.HOST
    assert "wish" in store.HOST
    assert "orders" in store.HOST
    assert "account" in store.HOST


def test_components_registered():
    assert isinstance(home, Home)
    assert isinstance(chrome, Chrome)
    assert home.id == "home"
    assert chrome.id == "chrome"
    assert "home" in host.runtime.components
    assert "chrome" in host.runtime.components


def test_no_ux_channel_import_in_product():
    root = Path(__file__).resolve().parents[1] / "app"
    hits: list[str] = []
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".", 1)[0] in {"ux_channel", "cek_host", "cek_surface"}:
                        hits.append(f"{path.name}:{node.lineno} import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                root_mod = node.module.split(".", 1)[0]
                if root_mod in {"ux_channel", "cek_host", "cek_surface"} or root_mod.startswith("cek_"):
                    hits.append(f"{path.name}:{node.lineno} from {node.module}")
    assert hits == []
