"""Shared storefront atoms. Screens compose these; they own the verbs."""
from __future__ import annotations

from typing import Any

from ux_dom.dom import button, div, h2, img, p, span
from ux_dom.ui.tokens import cn, surface, type_scale

from app import store
from app.wiring import wire


def product_card(item: dict[str, Any], *, open_fn) -> Any:
    sold = item["stock"] <= 0
    return div(
        button(
            img(
                src=item["img"],
                alt=item["name"],
                className="product-photo aspect-[4/5] w-full object-cover transition-transform duration-500 ease-[var(--ease-harbor)] group-hover:scale-[1.03]",
            ),
            type="button",
            **wire(open_fn, id=item["id"]),
            className="group block w-full overflow-hidden rounded-2xl",
        ),
        div(
            p(item["name"], className="mt-3 text-sm text-[var(--fg)]"),
            p(
                "Sold out" if sold else store.inr(item["price"]),
                className="mt-0.5 text-sm tabular-nums text-[var(--fg-muted)]",
            ),
            className="min-w-0",
        ),
        className="min-w-0",
    )


def section(title: str, blurb: str, rows: list[dict[str, Any]], *, open_fn) -> Any:
    return div(
        div(
            h2(title, className="font-display text-2xl tracking-tight text-[var(--fg)] sm:text-3xl"),
            p(blurb, className="mt-1 max-w-md text-sm text-[var(--fg-muted)]"),
            className="mb-5",
        ),
        div(
            *[product_card(item, open_fn=open_fn) for item in rows],
            className="grid grid-cols-2 gap-4 lg:grid-cols-4",
        ),
        className="mt-14",
    )


def spec(k: str, v: str) -> Any:
    return div(
        p(k, className="text-[11px] uppercase tracking-[0.16em] text-[var(--fg-subtle)]"),
        p(v, className="mt-1 text-sm text-[var(--fg)]"),
    )


def money_rows(promo: str = "", ship: str = "standard", gift: bool = False) -> Any:
    rows = [
        ("Subtotal", store.inr(store.subtotal())),
        ("Off", f"−{store.inr(store.discount(promo))}" if store.discount(promo) else "—"),
        ("Ship", "Free" if store.shipping(promo, ship) == 0 else store.inr(store.shipping(promo, ship))),
        ("Wrap", store.inr(store.gift_fee(gift)) if store.gift_fee(gift) else "—"),
        ("GST", store.inr(store.tax(promo))),
        ("Total", store.inr(store.total(promo, ship, gift))),
    ]
    return div(
        *[
            div(
                span(k, className="text-sm text-[var(--fg-muted)]"),
                span(v, className="text-sm tabular-nums text-[var(--fg)]"),
                className="flex justify-between py-1.5",
            )
            for k, v in rows
        ],
        className=cn(surface["l1"], "mt-4 rounded-xl px-4 py-3"),
    )


def cat_face(key: str) -> str:
    from app.catalog import PRODUCTS

    for item in PRODUCTS:
        if item["category"] == key:
            return item["img"]
    return "/assets/img/hero.jpg"
