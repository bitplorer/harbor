"""ux-app actions — App.boot / attach / mint / submit. Overlay macros emit Ops."""
from __future__ import annotations

from typing import Any

from ux_app import App, action
from ux_app.overlay import close_overlay, form_result, open_overlay, select_region

from app import store
from app.catalog import get
from app.planes import Chrome, Home

host = App.boot(title="Harbor & Co.", strict=False)
host.require_composite("dialog", "sheet", "command")

home = host.add(Home)
chrome = host.add(Chrome)


def _seed_checkout() -> None:
    acc = store.HOST["account"]
    chrome.checkout = {
        "name": acc.get("name") or "",
        "email": acc.get("email") or "",
        "address": acc.get("address") or "",
        "city": acc.get("city") or "",
        "pin": acc.get("pin") or "",
        "pay": "upi",
    }


if chrome.checkout is None:
    _seed_checkout()


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


def go(page: str, **extra):
    chrome.page = page
    for key, value in extra.items():
        if key in chrome.field_specs:
            setattr(chrome, key, value)
    return finish([*close_overlay(), *select_region("page:shop", page)])


@action("nav.go", caps=())
def nav_go(ctx, page: str = "home"):
    return go(page)


@action("nav.shop", caps=())
def nav_shop(ctx, category: str = "all"):
    chrome.category = category or "all"
    chrome.page = "shop"
    chrome.page_n = 1
    return finish([*close_overlay(), *select_region("page:shop", "shop")])


@action("nav.slide", caps=())
def nav_slide(ctx, index: str = "0"):
    try:
        home.slide = int(index)
    except ValueError:
        home.slide = 0
    return finish(select_region("carousel:hero", str(int(home.slide or 0))))


@action("nav.page", caps=())
def nav_page(ctx, page: str = "1"):
    try:
        chrome.page_n = max(1, int(page))
    except ValueError:
        chrome.page_n = 1
    return finish(select_region("page:board", str(int(chrome.page_n or 1))))


@action("shop.search", caps=())
def shop_search(ctx, q: str = ""):
    chrome.query = q
    chrome.page = "shop"
    chrome.page_n = 1
    return finish(select_region("page:shop", "shop"))


@action("shop.sort", caps=())
def shop_sort(ctx, sort: str = "featured"):
    chrome.sort = sort
    chrome.page = "shop"
    chrome.page_n = 1
    return finish([])


@action("shop.price", caps=())
def shop_price(ctx, price: str = "10000"):
    try:
        chrome.price_max = int(float(price))
    except ValueError:
        chrome.price_max = 10000
    chrome.page = "shop"
    chrome.page_n = 1
    return finish([])


@action("product.open", caps=())
def product_open(ctx, id: str = ""):
    p = get(id)
    if not p:
        return finish([], message="That piece left the floor", level="error")
    chrome.product_id = id
    chrome.size = (p.get("sizes") or ("",))[0] if p.get("sizes") else ""
    chrome.pdp_tab = "story"
    chrome.page = "pdp"
    return finish([*close_overlay(), *select_region("page:shop", "pdp")])


@action("product.size", caps=())
def product_size(ctx, opt: str = ""):
    chrome.size = opt
    return finish([])


@action("pdp.tab", caps=())
def pdp_tab(ctx, tab: str = "story"):
    chrome.pdp_tab = tab or "story"
    return finish(select_region("tabs:pdp", chrome.pdp_tab))


@action("guide.open", caps=())
def guide_open(ctx, id: str = ""):
    return finish(open_overlay("dialog", key="guide", id=id))


@action("cart.add", caps=())
def cart_add(ctx, id: str = "", qty: str = "1"):
    try:
        n = int(qty)
    except ValueError:
        n = 1
    msg = store.add_cart(id, qty=n, size=chrome.size or "")
    p = get(id)
    if p and p["stock"] <= 0:
        return finish([], message=msg, level="error")
    return finish(open_overlay("sheet", key="cart"), message=msg)


@action("cart.open", caps=())
def cart_open(ctx):
    chrome.menu_open = False
    return finish(open_overlay("sheet", key="cart"))


@action("cart.qty", caps=())
def cart_qty(ctx, id: str = "", qty: str = "1", opt: str = ""):
    try:
        n = int(qty)
    except ValueError:
        n = 1
    store.set_qty(id, n, opt)
    return finish(open_overlay("sheet", key="cart"))


@action("cart.remove", caps=())
def cart_remove(ctx, id: str = "", opt: str = ""):
    store.remove_cart(id, opt)
    return finish(open_overlay("sheet", key="cart"), message="Removed")


@action("cart.page", caps=())
def cart_page(ctx):
    return go("cart")


@action("wish.toggle", caps=())
def wish_toggle(ctx, id: str = ""):
    on = store.toggle_wish(id)
    p = get(id)
    name = p["name"] if p else "Piece"
    return finish([], message=f"Saved {name}" if on else f"Dropped {name}")


@action("wish.open", caps=())
def wish_open(ctx):
    return go("wish")


@action("promo.apply", caps=())
def promo_apply(ctx, code: str = ""):
    key = (code or "").strip().upper()
    if key in store.PROMO:
        chrome.promo = key
        return finish(open_overlay("sheet", key="cart"), message=f"{key} · {store.PROMO[key]}% off")
    chrome.promo = ""
    return finish(open_overlay("sheet", key="cart"), message="Code not recognised", level="error")


@action("ship.set", caps=())
def ship_set(ctx, ship: str = "standard"):
    chrome.ship = ship if ship in {"standard", "express"} else "standard"
    return finish([])


@action("gift.set", caps=())
def gift_set(ctx, gift: str = ""):
    chrome.gift = gift in {"true", "1", "on", "gift"}
    return finish([])


@action("checkout.start", caps=())
def checkout_start(ctx):
    if not store.cart_lines():
        return finish(open_overlay("sheet", key="cart"), message="Bag is empty", level="error")
    return go("checkout")


@action("checkout.place", caps=())
def checkout_place(
    ctx,
    name: str = "",
    email: str = "",
    address: str = "",
    city: str = "",
    pin: str = "",
    pay: str = "upi",
    ship: str = "",
    deliver: str = "",
    gift: str = "",
):
    if not store.cart_lines():
        return finish([], message="Bag is empty", level="error")
    if not (name or "").strip() or not (address or "").strip():
        return finish([], message="Name and address are required", level="error")
    draft = {
        "name": name.strip(),
        "email": (email or "").strip(),
        "address": address.strip(),
        "city": (city or "").strip(),
        "pin": (pin or "").strip(),
        "pay": pay or "upi",
    }
    chrome.checkout = draft
    if ship:
        chrome.ship = ship
    if deliver:
        chrome.deliver = deliver
    if gift:
        chrome.gift = gift in {"true", "1", "on", "gift"}
    order = store.place_order(
        checkout=draft,
        ship=chrome.ship or "standard",
        gift=bool(chrome.gift),
        deliver=chrome.deliver or "",
    )
    if not order:
        return finish([], message="Could not place", level="error")
    chrome.promo = ""
    chrome.gift = False
    chrome.order_id = order["id"]
    chrome.page = "confirm"
    return finish(close_overlay(), message=f"Order {order['id']} placed")


@action("orders.open", caps=())
def orders_open(ctx):
    return go("orders")


@action("order.show", caps=())
def order_show(ctx, id: str = ""):
    chrome.order_id = id
    chrome.page = "order"
    return finish(select_region("page:shop", "order"))


@action("account.open", caps=())
def account_open(ctx):
    chrome.menu_open = False
    return go("account")


@action("account.signin", caps=())
def account_signin(ctx, email: str = "", name: str = ""):
    acc = dict(store.HOST["account"])
    acc["signed_in"] = True
    if email:
        acc["email"] = email
    if name:
        acc["name"] = name
    store.HOST["account"] = acc
    return finish([], message=f"Signed in as {acc['name']}")


@action("account.signout", caps=())
def account_signout(ctx):
    acc = dict(store.HOST["account"])
    acc["signed_in"] = False
    store.HOST["account"] = acc
    chrome.menu_open = False
    return finish([], message="Signed out")


@action("menu.toggle", caps=())
def menu_toggle(ctx):
    chrome.menu_open = not bool(chrome.menu_open)
    return finish([], keep_menu=True)


@action("menu.close", caps=())
def menu_close(ctx):
    chrome.menu_open = False
    return finish([])


@action("command.open", caps=())
def command_open(ctx):
    chrome.menu_open = False
    chrome.command_q = chrome.query or ""
    return finish(open_overlay("command", key="find"))


@action("command.query", caps=())
def command_query(ctx, q: str = ""):
    chrome.command_q = q
    return finish(open_overlay("command", key="find", q=q))


@action("ui.close", caps=())
def ui_close(ctx):
    chrome.menu_open = False
    return finish(close_overlay())


@action("notice.dismiss", caps=())
def notice_dismiss(ctx):
    chrome.notice = None
    return finish([])


@action("desk.reset", caps=())
def desk_reset(ctx):
    store.reset()
    home.slide = 0
    chrome.reset_chrome()
    _seed_checkout()
    host.world.kv.clear()
    host.world.log.clear()
    return finish(close_overlay(), message="Store reset")
