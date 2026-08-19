"""Cart actions on ux-behavior — parallel to app.screens.bag.Cart.

Author seat only. Markup still comes from harbor panels when Host wires it.
Uses the same app.store domain so cart state is shared with the live shop.
"""

from __future__ import annotations

from typing import Any

from app import store
from app.catalog import get

try:
    from ux_behavior import Behavior, Component, action, go, notify, open
except ImportError:  # pragma: no cover
    Behavior = None  # type: ignore
    Component = object  # type: ignore

    def action(*a, **k):  # type: ignore
        def deco(fn):
            return fn

        return deco

    def open(*a, **k):  # type: ignore
        return []

    def notify(*a, **k):  # type: ignore
        return type("Op", (), {"pair": ("log", "append")})()

    def go(*a, **k):  # type: ignore
        return type("Op", (), {"pair": ("nav", "push")})()


class BehaviorCart(Component):
    id = "cart"

    def __init__(self) -> None:
        self.promo: str = ""

    def render(self) -> str:
        lines = store.cart_lines()
        if not lines:
            return "<div id='cart'><p>Bag is empty</p></div>"
        body = "".join(f"<li>{r['name']} × {r['qty']}</li>" for r in lines)
        return f"<div id='cart'><ul>{body}</ul><p>promo={self.promo}</p></div>"

    @action(caps=())
    def add(self, id: str = "", qty: str = "1") -> list[Any]:
        try:
            n = int(qty)
        except ValueError:
            n = 1
        msg = store.add_cart(id, qty=n, size="")
        item = get(id)
        if item and item["stock"] <= 0:
            return list(open("sheet", key="cart")) + [notify(msg, level="error")]
        return list(open("sheet", key="cart")) + [notify(msg)]

    @action(caps=())
    def qty(self, id: str = "", qty: str = "1", opt: str = "") -> list[Any]:
        try:
            n = int(qty)
        except ValueError:
            n = 1
        store.set_qty(id, n, opt)
        return list(open("sheet", key="cart"))

    @action(caps=())
    def remove(self, id: str = "", opt: str = "") -> list[Any]:
        store.remove_cart(id, opt)
        return list(open("sheet", key="cart")) + [notify("Removed")]

    @action(caps=())
    def open_bag(self) -> list[Any]:
        return list(open("sheet", key="cart"))

    @action(caps=())
    def show(self) -> list[Any]:
        return [go("/cart")]

    @action(caps=())
    def promo_apply(self, code: str = "") -> list[Any]:
        key = (code or "").strip().upper()
        if key in store.PROMO:
            self.promo = key
            msg = f"{key} · {store.PROMO[key]}% off"
        else:
            self.promo = ""
            msg = "Code not recognised"
        return list(open("sheet", key="cart")) + [
            notify(msg, level="info" if self.promo else "error")
        ]
