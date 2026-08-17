"""Orders book + order detail."""
from __future__ import annotations

from typing import Any

from ux_app import Component, Session
from ux_app.overlay import select_region
from ux_dom.dom import div, img, p, span
from ux_dom.ui import (
    Badge,
    EmptyState,
    PageHeader,
    Progress,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
)

from app import store
from app.wiring import act, finish, go


class Orders(Component):
    id = "orders"
    order_id: str = Session("")

    def show(self, ctx) -> Any:
        return go("orders")

    def detail(self, ctx, id: str = "") -> Any:
        from app.host import chrome

        self.order_id = id
        chrome.page = "order"
        return finish(select_region("page:shop", "order"))

    def render(self) -> Any:
        from app.host import shop

        rows = store.HOST.get("orders") or []
        if not rows:
            return div(
                PageHeader("Orders", "The house book.", className="mb-6"),
                EmptyState(
                    title="No orders yet",
                    description="Place one from the bag.",
                    action=act("Shop", shop.browse, category="all"),
                ),
            )
        return div(
            PageHeader("Orders", "The house book.", className="mb-6"),
            div(
                Table(
                    TableHeader(
                        TableRow(
                            TableHead("Order"),
                            TableHead("When"),
                            TableHead("Status"),
                            TableHead("Total", className="text-right"),
                        )
                    ),
                    TableBody(
                        *[
                            TableRow(
                                TableCell(act(o["id"], self.detail, variant="ghost", size="sm", id=o["id"])),
                                TableCell(o["at"], className="text-[var(--fg-muted)]"),
                                TableCell(Badge(o["status"], variant="secondary")),
                                TableCell(store.inr(o["total"]), className="text-right tabular-nums"),
                            )
                            for o in rows
                        ]
                    ),
                ),
                className="overflow-x-auto rounded-2xl border border-[var(--line)]",
            ),
        )


class Order(Component):
    id = "order"

    def render(self) -> Any:
        from app.host import orders

        oid = orders.order_id or ""
        order = next((o for o in store.HOST["orders"] if o["id"] == oid), None)
        if not order:
            return EmptyState(title="Order missing", action=act("Orders", orders.show))
        steps = ("Packed", "On the road", "At the door")
        current = order.get("status") or "Packed"
        return div(
            act("← Orders", orders.show, variant="ghost", size="sm"),
            PageHeader(order["id"], f"{order['status']} · {order['at']} · {order['pay'].upper()}", className="mt-3"),
            p(order["address"], className="mt-1 text-sm text-[var(--fg-subtle)]"),
            div(
                *[
                    div(
                        span(
                            str(i + 1),
                            className="flex h-7 w-7 items-center justify-center rounded-full border border-[var(--line)] text-xs "
                            + ("bg-[var(--fg)] text-[var(--bg)]" if step == current else "text-[var(--fg-muted)]"),
                        ),
                        span(step, className="mt-2 text-xs text-[var(--fg-muted)]"),
                        className="flex flex-1 flex-col items-center",
                    )
                    for i, step in enumerate(steps)
                ],
                className="mt-6 flex max-w-md",
            ),
            Progress(value=order.get("progress") or 35, className="mt-4 max-w-md"),
            div(
                *[
                    div(
                        img(src=ln["img"], alt=ln["name"], className="h-16 w-16 rounded-lg object-cover"),
                        p(f"{ln['name']} × {ln['qty']}", className="flex-1 text-sm"),
                        span(store.inr(ln["line"]), className="text-sm tabular-nums"),
                        className="flex items-center gap-3 py-3",
                    )
                    for ln in order["lines"]
                ],
                className="mt-6 divide-y divide-[var(--line)]",
            ),
            p(store.inr(order["total"]), className="mt-4 font-display text-2xl tabular-nums"),
        )
