"""Owning Components for UI chrome. Domain (cart, wish, orders) stays in store."""

from __future__ import annotations

from typing import Any

from ux_app import Component, Session


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
    """Floor carousel. ``slide`` is a plain int, not a SessionVar."""

    id = "home"
    slide: int = Session(0)

    def render(self) -> str:
        return ""


class Chrome(Component):
    """Nav, overlays, filters, PDP tabs — Channel draft after App.attach."""

    id = "chrome"
    page: str = Session("home")
    menu_open: bool = Session(False)
    notice: Any = Session(None)
    pdp_tab: str = Session("story")
    command_q: str = Session("")
    category: str = Session("all")
    query: str = Session("")
    sort: str = Session("featured")
    page_n: int = Session(1)
    price_max: int = Session(10000)
    product_id: str = Session("")
    size: str = Session("")
    ship: str = Session("standard")
    gift: bool = Session(False)
    deliver: str = Session("")
    promo: str = Session("")
    order_id: str = Session("")
    checkout: Any = Session(None)

    def render(self) -> str:
        return ""

    def reset_chrome(self) -> None:
        self.page = "home"
        self.menu_open = False
        self.notice = None
        self.pdp_tab = "story"
        self.command_q = ""
        self.category = "all"
        self.query = ""
        self.sort = "featured"
        self.page_n = 1
        self.price_max = 10000
        self.product_id = ""
        self.size = ""
        self.ship = "standard"
        self.gift = False
        self.deliver = ""
        self.promo = ""
        self.order_id = ""
        self.checkout = empty_checkout()
