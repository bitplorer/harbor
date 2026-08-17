"""Shop — search, category, sort, price, paginate."""
from __future__ import annotations

from typing import Any

from ux_app import Component, Session
from ux_app.overlay import close_overlay, select_region
from ux_dom.dom import div, form, p, span
from ux_dom.ui import Button, EmptyState, Input, Label, PageHeader, Select, Slider
from ux_dom.ui.tokens import type_scale

from app import store
from app.catalog import CATEGORIES
from app.store import ShopQuery
from app.ui import product_card
from app.wiring import act, finish, wire


class Shop(Component):
    id = "shop"
    category: str = Session("all")
    query: str = Session("")
    sort: str = Session("featured")
    page_n: int = Session(1)
    price_max: int = Session(10000)

    def filters(self) -> ShopQuery:
        return ShopQuery(
            category=self.category or "all",
            query=self.query or "",
            sort=self.sort or "featured",
            page_n=int(self.page_n or 1),
            price_max=int(self.price_max or 10000),
        )

    def browse(self, ctx, category: str = "all") -> Any:
        from app.host import chrome

        self.category = category or "all"
        self.page_n = 1
        chrome.page = "shop"
        return finish([*close_overlay(), *select_region("page:shop", "shop")])

    def search(self, ctx, q: str = "") -> Any:
        from app.host import chrome

        self.query = q
        self.page_n = 1
        chrome.page = "shop"
        return finish(select_region("page:shop", "shop"))

    def sort_by(self, ctx, sort: str = "featured") -> Any:
        from app.host import chrome

        self.sort = sort
        self.page_n = 1
        chrome.page = "shop"
        return finish([])

    def price(self, ctx, price: str = "10000") -> Any:
        from app.host import chrome

        try:
            self.price_max = int(float(price))
        except ValueError:
            self.price_max = 10000
        self.page_n = 1
        chrome.page = "shop"
        return finish([])

    def page(self, ctx, page: str = "1") -> Any:
        try:
            self.page_n = max(1, int(page))
        except ValueError:
            self.page_n = 1
        return finish(select_region("page:board", str(int(self.page_n or 1))))

    def _reset_filters(self) -> None:
        self.category = "all"
        self.query = ""
        self.sort = "featured"
        self.page_n = 1
        self.price_max = 10000

    def render(self) -> Any:
        from app.host import product

        q = self.filters()
        rows, page_n, pages = store.page_rows(q)
        total = len(store.listing(q))
        cat = q.category
        return div(
            PageHeader("The floor", "Linen to waxed canvas. Filter, then walk it.", className="mb-6"),
            form(
                Input(name="q", value=q.query, placeholder="Search the floor", className="min-w-0 flex-1"),
                Button("Search", type="submit", variant="secondary", size="sm"),
                **wire(self.search),
                className="flex gap-2",
            ),
            div(
                *[
                    act(
                        label,
                        self.browse,
                        variant="secondary" if cat == key else "ghost",
                        size="sm",
                        className="rounded-full",
                        category=key,
                    )
                    for key, label in CATEGORIES
                ],
                className="mt-4 flex flex-wrap gap-2",
            ),
            div(
                form(
                    Label("Sort"),
                    Select(
                        name="sort",
                        options=[
                            ("featured", "Featured"),
                            ("new", "New"),
                            ("price_asc", "Price ↑"),
                            ("price_desc", "Price ↓"),
                        ],
                        value=q.sort,
                        className="mt-1",
                    ),
                    Button("Apply", type="submit", variant="ghost", size="sm", className="mt-2"),
                    **wire(self.sort_by),
                    className="min-w-0 flex-1",
                ),
                form(
                    Label(f"Up to {store.inr(q.price_max)}"),
                    Slider(name="price", min=1000, max=10000, step=500, value=q.price_max, show_value=True, className="mt-2"),
                    Button("Apply", type="submit", variant="outline", size="sm", className="mt-3"),
                    **wire(self.price),
                    className="min-w-0 flex-1",
                ),
                className="mt-5 grid gap-5 sm:grid-cols-2",
            ),
            p(f"{total} pieces", className=f"{type_scale['caption']} mt-5"),
            div(*[product_card(item, open_fn=product.open) for item in rows], className="mt-4 grid grid-cols-2 gap-4 lg:grid-cols-3")
            if rows
            else EmptyState(
                title="Nothing on that search",
                description="Clear it and walk the floor again.",
                action=act("Clear", self.search, variant="outline", q=""),
            ),
            div(
                act(
                    "Prev",
                    self.page,
                    variant="outline",
                    size="sm",
                    page=str(page_n - 1),
                    className="" if page_n > 1 else "pointer-events-none opacity-40",
                ),
                span(f"{page_n} / {pages}", className="px-3 text-sm tabular-nums text-[var(--fg-muted)]"),
                act(
                    "Next",
                    self.page,
                    variant="outline",
                    size="sm",
                    page=str(page_n + 1),
                    className="" if page_n < pages else "pointer-events-none opacity-40",
                ),
                className="mt-8 flex items-center justify-center gap-2",
            )
            if rows
            else None,
        )
