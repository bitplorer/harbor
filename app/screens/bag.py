"""Bag — lines, promo, sheet + page."""
from __future__ import annotations

from typing import Any

from ux_app import Component, Session
from ux_app.overlay import open_overlay
from ux_dom.dom import div, form, img, p, span
from ux_dom.ui import Button, EmptyState, Input, PageHeader

from app import store
from app.catalog import get
from app.ui import money_rows
from app.wiring import act, finish, go, wire


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
        item = get(id)
        if item and item["stock"] <= 0:
            return finish([], message=msg, level="error")
        return finish(open_overlay("sheet", key="cart"), message=msg)

    def open(self, ctx) -> Any:
        from app.host import chrome

        chrome.menu_open = False
        return finish(open_overlay("sheet", key="cart"))

    def qty(self, ctx, id: str = "", qty: str = "1", opt: str = "") -> Any:
        try:
            n = int(qty)
        except ValueError:
            n = 1
        store.set_qty(id, n, opt)
        return finish(open_overlay("sheet", key="cart"))

    def remove(self, ctx, id: str = "", opt: str = "") -> Any:
        store.remove_cart(id, opt)
        return finish(open_overlay("sheet", key="cart"), message="Removed")

    def show(self, ctx) -> Any:
        return go("cart")

    def promo_apply(self, ctx, code: str = "") -> Any:
        key = (code or "").strip().upper()
        if key in store.PROMO:
            self.promo = key
            return finish(open_overlay("sheet", key="cart"), message=f"{key} · {store.PROMO[key]}% off")
        self.promo = ""
        return finish(open_overlay("sheet", key="cart"), message="Code not recognised", level="error")

    def panel(self, *, page: bool, actions: bool = True) -> Any:
        from app.host import checkout, chrome, shop

        promo = self.promo or ""
        lines = store.cart_lines()
        if not lines:
            return EmptyState(
                title="Bag is empty",
                description="Walk the floor. Linen and clay are waiting.",
                action=act("Shop", shop.browse, category="all"),
            )
        return div(
            div(*[self._line(row) for row in lines], className="divide-y divide-[var(--line)]"),
            money_rows(promo=promo),
            form(
                Input(name="code", placeholder="HARBOR10 or COAST20", value=promo),
                Button("Apply", type="submit", variant="outline", size="sm"),
                **wire(self.promo_apply),
                className="mt-4 flex gap-2",
            ),
            div(
                act("Checkout", checkout.start, className="min-h-11 flex-1"),
                act("Keep shopping", shop.browse, variant="ghost", category="all")
                if page
                else act("Close", chrome.close_ui, variant="ghost", silent=True),
                className="mt-5 flex flex-wrap gap-2",
            )
            if actions
            else None,
        )

    def _line(self, row: dict[str, Any]) -> Any:
        return div(
            img(src=row["img"], alt=row["name"], className="product-photo h-20 w-20 shrink-0 rounded-xl object-cover"),
            div(
                p(row["name"], className="text-sm text-[var(--fg)]"),
                p(
                    f"{store.inr(row['price'])}" + (f" · {row['size']}" if row["size"] else ""),
                    className="text-xs text-[var(--fg-subtle)]",
                ),
                div(
                    act("–", self.qty, variant="outline", size="sm", id=row["id"], qty=str(row["qty"] - 1), opt=row["size"]),
                    span(str(row["qty"]), className="min-w-[1.5rem] text-center text-sm tabular-nums"),
                    act("+", self.qty, variant="outline", size="sm", id=row["id"], qty=str(row["qty"] + 1), opt=row["size"]),
                    act("Remove", self.remove, variant="ghost", size="sm", id=row["id"], opt=row["size"]),
                    className="mt-2 flex items-center gap-2",
                ),
                className="min-w-0 flex-1",
            ),
            p(store.inr(row["line"]), className="text-sm tabular-nums text-[var(--fg)]"),
            className="flex gap-3 py-4",
        )

    def render(self) -> Any:
        return div(
            PageHeader("Bag", "Linen and clay wait at the bench.", className="mb-6"),
            self.panel(page=True),
        )
