"""Harbor screens are Components; chrome is Session; act uses callables."""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

from app import store
from app.carousel import hero_at
from app.catalog import PRODUCTS
from app.chrome import Chrome
from app.host import (
    PAGES,
    account,
    cart,
    checkout,
    chrome,
    confirm,
    home,
    host,
    order,
    orders,
    product,
    shop,
    wish,
)
from app.screens import Home, Shop
from app.wiring import action_name

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

APP_ROOT = Path(__file__).resolve().parents[1] / "app"


def _submit(fn, **args):
    name = action_name(fn)
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


def test_carousel_next_prev_keeps_image_and_title_keyed_together():
    first = hero_at(0)
    second = hero_at(1)
    assert first["hero"]["id"] != second["hero"]["id"]
    assert first["card_id"] == f"hero-card-{first['hero']['id']}"
    assert first["photo_id"] == f"hero-photo-{first['hero']['id']}"
    _submit(home.next)
    slot = hero_at(home.slide)
    assert slot["hero"]["id"] == second["hero"]["id"]
    assert slot["card_id"].endswith(slot["hero"]["id"])
    assert slot["photo_id"].endswith(slot["hero"]["id"])
    _submit(home.prev)
    back = hero_at(home.slide)
    assert back["hero"]["id"] == first["hero"]["id"]
    assert (back["hero"]["img"], back["hero"]["name"]) == (
        first["hero"]["img"],
        first["hero"]["name"],
    )


def test_control_uses_callables():
    attrs = host.control(home.next)
    assert attrs["data_action"] == "home.next"
    assert host.control(cart.add, id="x")["data_action"] == "cart.add"
    assert host.control(chrome.toggle)["data_action"] == "chrome.toggle"
    assert action_name(shop.browse) == "shop.browse"


def test_renders_are_not_empty_action_bags():
    assert home.render is not None
    assert chrome.render is not None
    for path in (APP_ROOT / "screens").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert 'return ""' not in text
        assert "return ''" not in text


def test_menu_and_notice_are_chrome_session():
    chrome.menu_open = False
    _submit(chrome.toggle)
    assert chrome.menu_open is True
    _submit(chrome.dismiss)
    assert chrome.notice is None
    _submit(chrome.close_menu)
    assert chrome.menu_open is False


def test_cart_stays_in_product_store():
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


def test_checkout_happy_path_keeps_money_in_store():
    sku = PRODUCTS[0]["id"]
    store.add_cart(sku, qty=1)
    _submit(
        checkout.place,
        name="Ada",
        address="1 Dock",
        email="ada@harbor.test",
        city="Gorakhpur",
        pin="273001",
    )
    assert store.HOST["orders"]
    assert store.HOST["cart"] == []
    assert store.HOST["orders"][0]["total"] > 0
    assert store.HOST["orders"][0]["id"] == "HC-24001"
    assert chrome.page == "confirm"
    assert "cart" not in chrome.field_specs


def test_components_registered():
    assert isinstance(home, Home)
    assert isinstance(chrome, Chrome)
    assert isinstance(shop, Shop)
    assert set(PAGES) == {
        "home",
        "shop",
        "pdp",
        "cart",
        "checkout",
        "confirm",
        "orders",
        "order",
        "wish",
        "account",
    }
    for key, fn in PAGES.items():
        assert inspect.ismethod(fn)
        assert fn.__name__ == "render"
    assert confirm is not None
    assert order is not None
    assert account is not None
    assert wish is not None


def _markup_files():
    files = [
        APP_ROOT / "chrome.py",
        APP_ROOT / "ui.py",
        APP_ROOT / "shell.py",
        *sorted((APP_ROOT / "screens").glob("*.py")),
    ]
    return [p for p in files if p.exists()]


def test_no_stringly_act_in_product_markup():
    hits: list[str] = []
    for path in _markup_files():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = ""
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            if name not in {"act", "wire"}:
                continue
            if not node.args:
                continue
            arg = node.args[0] if name == "wire" else (node.args[1] if len(node.args) > 1 else None)
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and "." in arg.value:
                hits.append(f"{path.name}:{node.lineno}:{arg.value}")
    assert hits == []


def test_no_ux_channel_import_in_product():
    hits: list[str] = []
    for path in sorted(APP_ROOT.rglob("*.py")):
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
