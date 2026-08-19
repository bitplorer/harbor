"""App.boot, attach, region, Component registry. Composition root only."""
from __future__ import annotations

from typing import Any

from ux_app import App

from app.chrome import Chrome
from app.screens import (
    Account,
    Cart,
    Checkout,
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

# Optional parallel ux-behavior root (does not replace host).
behavior_host = None
try:
    from app.pilot import register_pilot

    behavior_host = register_pilot(host)
except Exception:
    behavior_host = None

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


def _storefront(page: str | None = None):
    from app.shell import storefront

    return storefront(page)


host.region(_storefront)


def kv() -> dict[str, Any]:
    return host.world.kv
