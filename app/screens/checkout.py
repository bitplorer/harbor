"""Checkout + confirmation."""
from __future__ import annotations

from typing import Any

from ux_app import Component, Session
from ux_app.overlay import close_overlay, open_overlay
from ux_dom.dom import div, form, p
from ux_dom.ui import (
    Button,
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
    DatePicker,
    EmptyState,
    FormSection,
    Input,
    Label,
    PageHeader,
    Progress,
    RadioGroup,
    Separator,
    Switch,
)

from app import store
from app.ui import money_rows
from app.wiring import act, finish, go, wire


def empty_checkout() -> dict[str, str]:
    return {"name": "", "email": "", "address": "", "city": "", "pin": "", "pay": "upi"}


class Checkout(Component):
    id = "checkout"
    ship: str = Session("standard")
    gift: bool = Session(False)
    deliver: str = Session("")
    checkout: Any = Session(None)

    def start(self, ctx) -> Any:
        if not store.cart_lines():
            return finish(open_overlay("sheet", key="cart"), message="Bag is empty", level="error")
        return go("checkout")

    def ship_set(self, ctx, ship: str = "standard") -> Any:
        self.ship = ship if ship in {"standard", "express"} else "standard"
        return finish([])

    def gift_set(self, ctx, gift: str = "") -> Any:
        self.gift = gift in {"true", "1", "on", "gift"}
        return finish([])

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
            promo=cart.promo or "",
        )
        if not order:
            return finish([], message="Could not place", level="error")
        cart.promo = ""
        self.gift = False
        orders.order_id = order["id"]
        chrome.page = "confirm"
        return finish(close_overlay(), message=f"Order {order['id']} placed")

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
        from app.host import cart, shop

        draft = self.checkout if isinstance(self.checkout, dict) else {}
        if not store.cart_lines():
            return EmptyState(title="Nothing to check out", action=act("Shop", shop.browse, category="all"))
        promo = cart.promo or ""
        ship = self.ship or "standard"
        gift = bool(self.gift)
        return div(
            PageHeader("Checkout", "We pack from the Gorakhpur floor.", className="mb-6"),
            Card(
                CardHeader(CardTitle("Ship to"), CardDescription("Name and address stay on the bench.")),
                CardContent(
                    form(
                        FormSection(
                            div(Label("Name"), Input(name="name", value=draft.get("name") or "")),
                            div(Label("Email"), Input(name="email", value=draft.get("email") or ""), className="mt-3"),
                            div(Label("Address"), Input(name="address", value=draft.get("address") or ""), className="mt-3"),
                            div(Label("City"), Input(name="city", value=draft.get("city") or ""), className="mt-3"),
                            div(Label("PIN"), Input(name="pin", value=draft.get("pin") or ""), className="mt-3"),
                            title="Address",
                        ),
                        FormSection(
                            div(
                                Label("Ship"),
                                RadioGroup(
                                    name="ship",
                                    options=[
                                        ("standard", "Standard · ₹80 or free over ₹8,000"),
                                        ("express", "Express · ₹180"),
                                    ],
                                    value=ship,
                                ),
                            ),
                            div(Label("Deliver on"), DatePicker(name="deliver", value=self.deliver or ""), className="mt-4"),
                            div(
                                Label("Pay"),
                                RadioGroup(
                                    name="pay",
                                    options=[("upi", "UPI"), ("card", "Card"), ("cod", "Cash on delivery")],
                                    value=draft.get("pay") or "upi",
                                ),
                                className="mt-4",
                            ),
                            div(
                                Label("Gift wrap"),
                                Switch(name="gift", checked=gift, value="gift"),
                                className="mt-4 flex items-center justify-between",
                            ),
                            title="How it arrives",
                            className="mt-6",
                        ),
                        Separator(className="my-6"),
                        money_rows(promo=promo, ship=ship, gift=gift),
                        div(
                            Button("Place order", type="submit", className="min-h-11"),
                            act("Back to bag", cart.show, variant="ghost"),
                            className="mt-6 flex flex-wrap gap-2",
                        ),
                        **wire(self.place),
                    )
                ),
                className="max-w-xl",
            ),
        )


class Confirm(Component):
    id = "confirm"

    def render(self) -> Any:
        from app.host import orders, shop

        oid = store.HOST.get("last_order") or ""
        order = next((o for o in store.HOST["orders"] if o["id"] == oid), None)
        return div(
            p("It's on the bench.", className="text-[11px] uppercase tracking-[0.22em] text-[var(--fg-subtle)]"),
            PageHeader(
                order["id"] if order else "Thank you.",
                "Packed from the Gorakhpur floor." if order else "Order placed.",
                className="mt-2 mb-6",
            ),
            Card(
                CardContent(
                    p(order["address"] if order else "", className="text-sm text-[var(--fg-muted)]"),
                    p(store.inr(order["total"]) if order else "", className="mt-2 font-display text-3xl tabular-nums tracking-tight"),
                    Progress(value=order.get("progress") or 35, className="mt-4") if order else None,
                    className="p-5",
                ),
                className="max-w-md",
            ),
            div(
                act("Track order", orders.detail, id=oid),
                act("Keep shopping", shop.browse, variant="outline", category="all"),
                className="mt-6 flex flex-wrap gap-2",
            ),
        )
