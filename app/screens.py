"""Harbor screens — one Component per slot. Methods are actions; render is real."""

from __future__ import annotations

from typing import Any

from ux_app import Component, Session
from ux_app.overlay import close_overlay, open_overlay, select_region

from app import store
from app.carousel import featured_rows
from app.catalog import get


def _finish(*args: Any, **kwargs: Any) -> Any:
    from app.host import finish

    return finish(*args, **kwargs)


def _go(page: str) -> Any:
    from app.host import chrome

    chrome.page = page
    return _finish([*close_overlay(), *select_region("page:shop", page)])


def empty_checkout() -> dict[str, str]:
    return {
        "name": "",
        "email": "",
        "address": "",
        "city": "",
        "pin": "",
        "pay": "upi",
    }


class Home(Component):
    id = "home"
    slide: int = Session(0)

    def next(self, ctx) -> Any:
        n = max(1, len(featured_rows()))
        self.slide = (int(self.slide or 0) + 1) % n
        return _finish(select_region("carousel:hero", str(int(self.slide or 0))))

    def prev(self, ctx) -> Any:
        n = max(1, len(featured_rows()))
        self.slide = (int(self.slide or 0) - 1) % n
        return _finish(select_region("carousel:hero", str(int(self.slide or 0))))

    def render(self) -> Any:
        from app.views import home_body

        return home_body()


class Chrome(Component):
    id = "chrome"
    page: str = Session("home")
    menu_open: bool = Session(False)
    notice: Any = Session(None)
    command_q: str = Session("")

    def go(self, ctx, page: str = "home") -> Any:
        return _go(page)

    def toggle(self, ctx) -> Any:
        self.menu_open = not bool(self.menu_open)
        return _finish([], keep_menu=True)

    def close_menu(self, ctx) -> Any:
        self.menu_open = False
        return _finish([])

    def find(self, ctx) -> Any:
        from app.host import shop

        self.menu_open = False
        self.command_q = shop.query or ""
        return _finish(open_overlay("command", key="find"))

    def query_find(self, ctx, q: str = "") -> Any:
        self.command_q = q
        return _finish(open_overlay("command", key="find", q=q))

    def dismiss(self, ctx) -> Any:
        self.notice = None
        return _finish([])

    def close_ui(self, ctx) -> Any:
        self.menu_open = False
        return _finish(close_overlay())

    def reset(self, ctx) -> Any:
        from app.host import checkout, home, host, orders, product, shop

        store.reset()
        home.slide = 0
        self.page = "home"
        self.menu_open = False
        self.notice = None
        self.command_q = ""
        shop._reset_filters()
        product._reset_view()
        checkout._reset_draft()
        orders.order_id = ""
        from app.host import cart

        cart.promo = ""
        host.world.kv.clear()
        host.world.log.clear()
        return _finish(close_overlay(), message="Store reset")

    def render(self) -> Any:
        from app.views import topbar

        return topbar(self.page or "home")


class Shop(Component):
    id = "shop"
    category: str = Session("all")
    query: str = Session("")
    sort: str = Session("featured")
    page_n: int = Session(1)
    price_max: int = Session(10000)

    def browse(self, ctx, category: str = "all") -> Any:
        from app.host import chrome

        self.category = category or "all"
        self.page_n = 1
        chrome.page = "shop"
        return _finish([*close_overlay(), *select_region("page:shop", "shop")])

    def search(self, ctx, q: str = "") -> Any:
        from app.host import chrome

        self.query = q
        self.page_n = 1
        chrome.page = "shop"
        return _finish(select_region("page:shop", "shop"))

    def sort_by(self, ctx, sort: str = "featured") -> Any:
        from app.host import chrome

        self.sort = sort
        self.page_n = 1
        chrome.page = "shop"
        return _finish([])

    def price(self, ctx, price: str = "10000") -> Any:
        from app.host import chrome

        try:
            self.price_max = int(float(price))
        except ValueError:
            self.price_max = 10000
        self.page_n = 1
        chrome.page = "shop"
        return _finish([])

    def page(self, ctx, page: str = "1") -> Any:
        try:
            self.page_n = max(1, int(page))
        except ValueError:
            self.page_n = 1
        return _finish(select_region("page:board", str(int(self.page_n or 1))))

    def _reset_filters(self) -> None:
        self.category = "all"
        self.query = ""
        self.sort = "featured"
        self.page_n = 1
        self.price_max = 10000

    def render(self) -> Any:
        from app.views import shop_body

        return shop_body()


class Product(Component):
    id = "product"
    product_id: str = Session("")
    size: str = Session("")
    pdp_tab: str = Session("story")

    def open(self, ctx, id: str = "") -> Any:
        from app.host import chrome

        p = get(id)
        if not p:
            return _finish([], message="That piece left the floor", level="error")
        self.product_id = id
        self.size = (p.get("sizes") or ("",))[0] if p.get("sizes") else ""
        self.pdp_tab = "story"
        chrome.page = "pdp"
        return _finish([*close_overlay(), *select_region("page:shop", "pdp")])

    def size_set(self, ctx, opt: str = "") -> Any:
        self.size = opt
        return _finish([])

    def tab(self, ctx, tab: str = "story") -> Any:
        self.pdp_tab = tab or "story"
        return _finish(select_region("tabs:pdp", self.pdp_tab))

    def guide(self, ctx, id: str = "") -> Any:
        return _finish(open_overlay("dialog", key="guide", id=id))

    def _reset_view(self) -> None:
        self.product_id = ""
        self.size = ""
        self.pdp_tab = "story"

    def render(self) -> Any:
        from app.views import pdp_body

        return pdp_body()


class Cart(Component):
    id = "cart"
    promo: str = Session("")

    def add(self, ctx, id: str = "", qty: str = "1") -> Any:
        from app.host import product

        try:
            n = int(qty)
        except ValueError:
            n = 1
        msg = store.add_cart(id, qty=n, size=product.size or "")
        p = get(id)
        if p and p["stock"] <= 0:
            return _finish([], message=msg, level="error")
        return _finish(open_overlay("sheet", key="cart"), message=msg)

    def open(self, ctx) -> Any:
        from app.host import chrome

        chrome.menu_open = False
        return _finish(open_overlay("sheet", key="cart"))

    def qty(self, ctx, id: str = "", qty: str = "1", opt: str = "") -> Any:
        try:
            n = int(qty)
        except ValueError:
            n = 1
        store.set_qty(id, n, opt)
        return _finish(open_overlay("sheet", key="cart"))

    def remove(self, ctx, id: str = "", opt: str = "") -> Any:
        store.remove_cart(id, opt)
        return _finish(open_overlay("sheet", key="cart"), message="Removed")

    def show(self, ctx) -> Any:
        return _go("cart")

    def promo_apply(self, ctx, code: str = "") -> Any:
        key = (code or "").strip().upper()
        if key in store.PROMO:
            self.promo = key
            return _finish(open_overlay("sheet", key="cart"), message=f"{key} · {store.PROMO[key]}% off")
        self.promo = ""
        return _finish(open_overlay("sheet", key="cart"), message="Code not recognised", level="error")

    def render(self) -> Any:
        from app.views import cart_body

        return cart_body()


class Checkout(Component):
    id = "checkout"
    ship: str = Session("standard")
    gift: bool = Session(False)
    deliver: str = Session("")
    checkout: Any = Session(None)

    def start(self, ctx) -> Any:
        if not store.cart_lines():
            return _finish(open_overlay("sheet", key="cart"), message="Bag is empty", level="error")
        return _go("checkout")

    def ship_set(self, ctx, ship: str = "standard") -> Any:
        self.ship = ship if ship in {"standard", "express"} else "standard"
        return _finish([])

    def gift_set(self, ctx, gift: str = "") -> Any:
        self.gift = gift in {"true", "1", "on", "gift"}
        return _finish([])

    def place(
        self,
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
    ) -> Any:
        from app.host import cart, chrome, orders

        if not store.cart_lines():
            return _finish([], message="Bag is empty", level="error")
        if not (name or "").strip() or not (address or "").strip():
            return _finish([], message="Name and address are required", level="error")
        draft = {
            "name": name.strip(),
            "email": (email or "").strip(),
            "address": address.strip(),
            "city": (city or "").strip(),
            "pin": (pin or "").strip(),
            "pay": pay or "upi",
        }
        self.checkout = draft
        if ship:
            self.ship = ship
        if deliver:
            self.deliver = deliver
        if gift:
            self.gift = gift in {"true", "1", "on", "gift"}
        order = store.place_order(
            checkout=draft,
            ship=self.ship or "standard",
            gift=bool(self.gift),
            deliver=self.deliver or "",
        )
        if not order:
            return _finish([], message="Could not place", level="error")
        cart.promo = ""
        self.gift = False
        orders.order_id = order["id"]
        chrome.page = "confirm"
        return _finish(close_overlay(), message=f"Order {order['id']} placed")

    def _reset_draft(self) -> None:
        acc = store.HOST["account"]
        self.ship = "standard"
        self.gift = False
        self.deliver = ""
        self.checkout = {
            "name": acc.get("name") or "",
            "email": acc.get("email") or "",
            "address": acc.get("address") or "",
            "city": acc.get("city") or "",
            "pin": acc.get("pin") or "",
            "pay": "upi",
        }

    def render(self) -> Any:
        from app.views import checkout_body

        return checkout_body()


class Confirm(Component):
    id = "confirm"

    def render(self) -> Any:
        from app.views import confirm_body

        return confirm_body()


class Orders(Component):
    id = "orders"
    order_id: str = Session("")

    def show(self, ctx) -> Any:
        return _go("orders")

    def detail(self, ctx, id: str = "") -> Any:
        from app.host import chrome

        self.order_id = id
        chrome.page = "order"
        return _finish(select_region("page:shop", "order"))

    def render(self) -> Any:
        from app.views import orders_body

        return orders_body()


class Order(Component):
    id = "order"

    def render(self) -> Any:
        from app.views import order_body

        return order_body()


class Wish(Component):
    id = "wish"

    def toggle(self, ctx, id: str = "") -> Any:
        on = store.toggle_wish(id)
        p = get(id)
        name = p["name"] if p else "Piece"
        return _finish([], message=f"Saved {name}" if on else f"Dropped {name}")

    def show(self, ctx) -> Any:
        return _go("wish")

    def render(self) -> Any:
        from app.views import wish_body

        return wish_body()


class Account(Component):
    id = "account"

    def show(self, ctx) -> Any:
        from app.host import chrome

        chrome.menu_open = False
        return _go("account")

    def signin(self, ctx, email: str = "", name: str = "") -> Any:
        acc = dict(store.HOST["account"])
        acc["signed_in"] = True
        if email:
            acc["email"] = email
        if name:
            acc["name"] = name
        store.HOST["account"] = acc
        return _finish([], message=f"Signed in as {acc['name']}")

    def signout(self, ctx) -> Any:
        from app.host import chrome

        acc = dict(store.HOST["account"])
        acc["signed_in"] = False
        store.HOST["account"] = acc
        chrome.menu_open = False
        return _finish([], message="Signed out")

    def render(self) -> Any:
        from app.views import account_body

        return account_body()
