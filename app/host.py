"""ux-app actions — App.boot / attach / mint / submit. Overlay macros emit Ops."""
from __future__ import annotations

from typing import Any

from ux_app import App, action
from ux_app.overlay import close_overlay, form_result, open_overlay, select_region

from app import store
from app.catalog import get

host = App.boot(title="Harbor & Co.", strict=False)
host.require_composite("dialog", "sheet", "command")


def _storefront():
    from app.views import storefront

    return storefront()


host.region(_storefront)


def kv() -> dict[str, Any]:
    return host.world.kv


def finish(ops, *, message: str | None = None, level: str = "success", keep_menu: bool = False):
    if not keep_menu:
        store.close_menu()
    if message:
        store.flash(message, level=level)
        extra = form_result(ok=level != "error", message=message, target="shop")
        ops = [*list(ops or []), *extra]
    return ops


def go(page: str, **extra):
    store.HOST["page"] = page
    store.HOST.update(extra)
    return finish([*close_overlay(), *select_region("page:shop", page)])


@action("nav.go", caps=())
def nav_go(ctx, page: str = "home"):
    return go(page)


@action("nav.shop", caps=())
def nav_shop(ctx, category: str = "all"):
    store.HOST["category"] = category or "all"
    store.HOST["page"] = "shop"
    store.HOST["page_n"] = 1
    return finish([*close_overlay(), *select_region("page:shop", "shop")])


@action("nav.slide", caps=())
def nav_slide(ctx, index: str = "0"):
    try:
        store.HOST["slide"] = int(index)
    except ValueError:
        store.HOST["slide"] = 0
    return finish(select_region("carousel:hero", str(store.HOST["slide"])))


@action("nav.page", caps=())
def nav_page(ctx, page: str = "1"):
    try:
        store.HOST["page_n"] = max(1, int(page))
    except ValueError:
        store.HOST["page_n"] = 1
    return finish(select_region("page:board", str(store.HOST["page_n"])))


@action("shop.search", caps=())
def shop_search(ctx, q: str = ""):
    store.HOST["query"] = q
    store.HOST["page"] = "shop"
    store.HOST["page_n"] = 1
    return finish(select_region("page:shop", "shop"))


@action("shop.sort", caps=())
def shop_sort(ctx, sort: str = "featured"):
    store.HOST["sort"] = sort
    store.HOST["page"] = "shop"
    store.HOST["page_n"] = 1
    return finish([])


@action("shop.price", caps=())
def shop_price(ctx, price: str = "10000"):
    try:
        store.HOST["price_max"] = int(float(price))
    except ValueError:
        store.HOST["price_max"] = 10000
    store.HOST["page"] = "shop"
    store.HOST["page_n"] = 1
    return finish([])


@action("product.open", caps=())
def product_open(ctx, id: str = ""):
    p = get(id)
    if not p:
        return finish([], message="That piece left the floor", level="error")
    store.HOST["product_id"] = id
    store.HOST["size"] = (p.get("sizes") or ("",))[0] if p.get("sizes") else ""
    store.HOST["pdp_tab"] = "story"
    store.HOST["page"] = "pdp"
    return finish([*close_overlay(), *select_region("page:shop", "pdp")])


@action("product.size", caps=())
def product_size(ctx, opt: str = ""):
    store.HOST["size"] = opt
    return finish([])


@action("pdp.tab", caps=())
def pdp_tab(ctx, tab: str = "story"):
    store.HOST["pdp_tab"] = tab or "story"
    return finish(select_region("tabs:pdp", store.HOST["pdp_tab"]))


@action("guide.open", caps=())
def guide_open(ctx, id: str = ""):
    return finish(open_overlay("dialog", key="guide", id=id))


@action("cart.add", caps=())
def cart_add(ctx, id: str = "", qty: str = "1"):
    try:
        n = int(qty)
    except ValueError:
        n = 1
    msg = store.add_cart(id, qty=n, size=store.HOST.get("size") or "")
    p = get(id)
    if p and p["stock"] <= 0:
        return finish([], message=msg, level="error")
    return finish(open_overlay("sheet", key="cart"), message=msg)


@action("cart.open", caps=())
def cart_open(ctx):
    store.close_menu()
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
        store.HOST["promo"] = key
        return finish(open_overlay("sheet", key="cart"), message=f"{key} · {store.PROMO[key]}% off")
    store.HOST["promo"] = ""
    return finish(open_overlay("sheet", key="cart"), message="Code not recognised", level="error")


@action("ship.set", caps=())
def ship_set(ctx, ship: str = "standard"):
    store.HOST["ship"] = ship if ship in {"standard", "express"} else "standard"
    return finish([])


@action("gift.set", caps=())
def gift_set(ctx, gift: str = ""):
    store.HOST["gift"] = gift in {"true", "1", "on", "gift"}
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
    store.HOST["checkout"] = {
        "name": name.strip(),
        "email": (email or "").strip(),
        "address": address.strip(),
        "city": (city or "").strip(),
        "pin": (pin or "").strip(),
        "pay": pay or "upi",
    }
    if ship:
        store.HOST["ship"] = ship
    if deliver:
        store.HOST["deliver"] = deliver
    if gift:
        store.HOST["gift"] = gift in {"true", "1", "on", "gift"}
    order = store.place_order()
    if not order:
        return finish([], message="Could not place", level="error")
    store.HOST["page"] = "confirm"
    return finish(close_overlay(), message=f"Order {order['id']} placed")


@action("orders.open", caps=())
def orders_open(ctx):
    return go("orders")


@action("order.show", caps=())
def order_show(ctx, id: str = ""):
    store.HOST["order_id"] = id
    store.HOST["page"] = "order"
    return finish(select_region("page:shop", "order"))


@action("account.open", caps=())
def account_open(ctx):
    store.close_menu()
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
    store.close_menu()
    return finish([], message="Signed out")


@action("menu.toggle", caps=())
def menu_toggle(ctx):
    store.HOST["menu_open"] = not bool(store.HOST.get("menu_open"))
    return finish([], keep_menu=True)


@action("menu.close", caps=())
def menu_close(ctx):
    store.close_menu()
    return finish([])


@action("command.open", caps=())
def command_open(ctx):
    store.close_menu()
    store.HOST["command_q"] = store.HOST.get("query") or ""
    return finish(open_overlay("command", key="find"))


@action("command.query", caps=())
def command_query(ctx, q: str = ""):
    store.HOST["command_q"] = q
    return finish(open_overlay("command", key="find", q=q))


@action("ui.close", caps=())
def ui_close(ctx):
    store.close_menu()
    return finish(close_overlay())


@action("notice.dismiss", caps=())
def notice_dismiss(ctx):
    store.clear_notice()
    return finish([])


@action("desk.reset", caps=())
def desk_reset(ctx):
    store.reset()
    host.world.kv.clear()
    host.world.log.clear()
    return finish(close_overlay(), message="Store reset")
