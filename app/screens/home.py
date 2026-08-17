"""Home — hero, rotation, categories, floor tempo."""
from __future__ import annotations

from typing import Any

from ux_app import Component, Session
from ux_app.overlay import select_region
from ux_app.ui import stamp_region
from ux_dom.dom import button, div, img, p, span
from ux_dom.ui import Card, CardContent, CardDescription, CardHeader, CardTitle, Chart, StatusStrip
from ux_dom.ui.tokens import cn, surface

from app.carousel import featured_rows, hero_at
from app.catalog import CATEGORIES, PRODUCTS
from app.ui import cat_face, section
from app.wiring import act, finish, wire


class Home(Component):
    id = "home"
    slide: int = Session(0)

    def next(self, ctx) -> Any:
        n = max(1, len(featured_rows()))
        self.slide = (int(self.slide or 0) + 1) % n
        return finish(select_region("carousel:hero", str(int(self.slide or 0))))

    def prev(self, ctx) -> Any:
        n = max(1, len(featured_rows()))
        self.slide = (int(self.slide or 0) - 1) % n
        return finish(select_region("carousel:hero", str(int(self.slide or 0))))

    def render(self) -> Any:
        from app.host import product, shop

        featured = [p for p in PRODUCTS if p.get("featured")]
        fresh = [p for p in PRODUCTS if p.get("new")]
        slot = hero_at(self.slide)
        hero = slot["hero"]
        idx = slot["idx"]
        carousel = stamp_region(
            div(
                img(
                    src=hero["img"],
                    alt=hero["name"],
                    id=slot["photo_id"],
                    className="product-photo h-52 w-full rounded-[1.25rem] object-cover sm:h-72",
                ),
                div(
                    p("On rotation", className="text-[11px] uppercase tracking-[0.22em] text-[var(--fg-subtle)]"),
                    p(hero["name"], className="mt-2 font-display text-2xl tracking-tight text-[var(--fg)] sm:text-3xl"),
                    p(hero["blurb"], className="mt-1 max-w-md text-sm leading-relaxed text-[var(--fg-muted)]"),
                    div(
                        act("Prev", self.prev, variant="outline", size="sm"),
                        act("View", product.open, size="sm", id=hero["id"]),
                        act("Next", self.next, variant="outline", size="sm"),
                        className="mt-5 flex flex-wrap gap-2",
                    ),
                    className="mt-4",
                ),
                className=cn(surface["l1"], "rounded-[1.75rem] p-3 sm:p-4"),
                id=slot["card_id"],
                **{"data-hero": hero["id"], "data-slide": str(idx)},
            ),
            uid="carousel:hero",
        )
        tiles = []
        for key, label in CATEGORIES:
            if key == "all":
                continue
            n = sum(1 for p in PRODUCTS if p["category"] == key)
            tiles.append(
                button(
                    img(src=cat_face(key), alt="", className="absolute inset-0 h-full w-full object-cover opacity-50"),
                    span(className="absolute inset-0 bg-gradient-to-t from-[var(--ink)] via-[color-mix(in_oklab,var(--ink)_40%,transparent)] to-transparent"),
                    span(label, className="relative font-display text-xl tracking-tight text-[var(--paper)]"),
                    span(f"{n} pieces", className="relative mt-1 block text-xs text-[var(--fg-muted)]"),
                    type="button",
                    **wire(shop.browse, category=key),
                    className="relative min-h-[7.5rem] overflow-hidden rounded-2xl p-4 text-left",
                )
            )
        return div(
            StatusStrip(
                items=[("Live floor", "default"), ("Gorakhpur", "secondary"), ("Packed today", "outline")],
                message="New flax this morning.",
                className="mb-6",
            ),
            div(
                img(
                    src="/assets/img/hero.jpg",
                    alt="Morning room at Harbor & Co.",
                    className="product-photo absolute inset-0 h-full w-full object-cover",
                ),
                div(className="absolute inset-0 bg-gradient-to-t from-[var(--ink)] via-[color-mix(in_oklab,var(--ink)_45%,transparent)] to-[color-mix(in_oklab,var(--ink)_10%,transparent)]"),
                div(
                    p("Harbor & Co.", className="text-[11px] uppercase tracking-[0.28em] text-[var(--linen)]"),
                    p(
                        "Goods for the house and the coast.",
                        className="mt-3 max-w-xl font-display text-[2rem] leading-[1.15] tracking-tight text-[var(--paper)] sm:text-5xl",
                    ),
                    p(
                        "Linen, clay, oak, and waxed canvas. Made to be used.",
                        className="mt-3 max-w-md text-sm leading-relaxed text-[var(--fg-muted)]",
                    ),
                    div(
                        act("Shop the floor", shop.browse, category="all"),
                        act("New this week", shop.sort_by, variant="outline", sort="new"),
                        className="mt-6 flex flex-wrap gap-2",
                    ),
                    className="relative z-10 mt-auto w-full max-w-6xl px-4 pb-24 pt-24 sm:px-6 sm:pb-8",
                ),
                className="relative -mx-4 flex min-h-[28rem] flex-col overflow-hidden rounded-none sm:-mx-6 sm:min-h-[34rem] sm:rounded-[1.75rem]",
            ),
            div(carousel, className="mt-12"),
            div(*tiles, className="mt-10 grid grid-cols-2 gap-3 sm:grid-cols-4"),
            Card(
                CardHeader(CardTitle("Floor tempo"), CardDescription("Pieces leaving the bench this week.")),
                CardContent(Chart(series=[4, 6, 5, 9, 7, 11, 8], kind="bar", className="h-24")),
                className="mt-12",
            ),
            section("On the table", "Pieces we keep on the floor.", featured, open_fn=product.open),
            section("Just in", "This week's arrivals.", fresh, open_fn=product.open),
        )
