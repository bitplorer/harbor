"""App.boot, attach, region, Component registry. Actions live on screens."""
from __future__ import annotations

from typing import Any

from ux_app import App
from ux_app.overlay import form_result

from app import store
from app.screens import (
    Account,
    Cart,
    Checkout,
    Chrome,
    Confirm,
    Home,
    Order,
    Orders,
    Product,
    Shop,
    Wish,
)

host = App.boot(title="Harbor & Co.", strict=False)
host.require_composite("dialog", "sheet", "command")

home = host.add(Home)
chrome = host.add(Chrome)
shop = host.add(Shop)
product = host.add(Product)
cart = host.add(Cart)
checkout = host.add(Checkout)
confirm = host.add(Confirm)
orders = host.add(Orders)
order = host.add(Order)
wish = host.add(Wish)
account = host.add(Account)

checkout._reset_draft()

PAGES = {
    "home": home.render,
    "shop": shop.render,
    "pdp": product.render,
    "cart": cart.render,
    "checkout": checkout.render,
    "confirm": confirm.render,
    "orders": orders.render,
    "order": order.render,
    "wish": wish.render,
    "account": account.render,
}


def _storefront():
    from app.views import storefront

    return storefront()


host.region(_storefront)


def kv() -> dict[str, Any]:
    return host.world.kv


def finish(ops, *, message: str | None = None, level: str = "success", keep_menu: bool = False):
    if not keep_menu:
        chrome.menu_open = False
    if message:
        chrome.notice = {"text": message, "level": level}
        extra = form_result(ok=level != "error", message=message, target="shop")
        ops = [*list(ops or []), *extra]
    return ops
