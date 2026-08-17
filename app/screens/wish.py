"""Saved pieces."""
from __future__ import annotations

from typing import Any

from ux_app import Component
from ux_dom.dom import div
from ux_dom.ui import EmptyState, PageHeader

from app import store
from app.catalog import PRODUCTS
from app.ui import product_card
from app.wiring import act, finish, go


class Wish(Component):
    id = "wish"

    def toggle(self, ctx, id: str = "") -> Any:
        on = store.toggle_wish(id)
        from app.catalog import get

        item = get(id)
        name = item["name"] if item else "Piece"
        return finish([], message=f"Saved {name}" if on else f"Dropped {name}")

    def show(self, ctx) -> Any:
        return go("wish")

    def render(self) -> Any:
        from app.host import product, shop

        ids = store.HOST.get("wish") or []
        rows = [p for p in PRODUCTS if p["id"] in ids]
        return div(
            PageHeader("Saved", "Pieces kept aside.", className="mb-6"),
            EmptyState(
                title="Nothing saved",
                description="Heart a piece from the floor.",
                action=act("Shop", shop.browse, category="all"),
            )
            if not rows
            else div(*[product_card(p, open_fn=product.open) for p in rows], className="grid grid-cols-2 gap-4 lg:grid-cols-3"),
        )
