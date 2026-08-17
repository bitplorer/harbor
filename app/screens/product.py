"""PDP — size, tabs, reviews, related, size guide."""
from __future__ import annotations

from typing import Any

from ux_app import Component, Session
from ux_app.overlay import close_overlay, open_overlay, select_region
from ux_app.ui import stamp_region
from ux_dom.dom import div, p
from ux_dom.ui import Alert, AlertDescription, AlertTitle, Breadcrumb, Button, Dialog, PageHeader, Tabs
from ux_dom.ui import EmptyState
from ux_dom.dom import img
from ux_dom.ui.tokens import type_scale

from app.catalog import get, related
from app import store
from app.ui import section, spec
from app.wiring import act, finish


class Product(Component):
    id = "product"
    product_id: str = Session("")
    size: str = Session("")
    pdp_tab: str = Session("story")

    def open(self, ctx, id: str = "") -> Any:
        from app.host import chrome

        item = get(id)
        if not item:
            return finish([], message="That piece left the floor", level="error")
        self.product_id = id
        self.size = (item.get("sizes") or ("",))[0] if item.get("sizes") else ""
        self.pdp_tab = "story"
        chrome.page = "pdp"
        return finish([*close_overlay(), *select_region("page:shop", "pdp")])

    def size_set(self, ctx, opt: str = "") -> Any:
        self.size = opt
        return finish([])

    def tab(self, ctx, tab: str = "story") -> Any:
        self.pdp_tab = tab or "story"
        return finish(select_region("tabs:pdp", self.pdp_tab))

    def guide(self, ctx, id: str = "") -> Any:
        return finish(open_overlay("dialog", key="guide", id=id))

    def _reset_view(self) -> None:
        self.product_id = ""
        self.size = ""
        self.pdp_tab = "story"

    def guide_dialog(self) -> Any:
        from app.host import chrome

        return Dialog(
            open=True,
            title="How it wears",
            body=p(
                "S easy, M true, L over a knit. The overshirt is unlined so it layers.",
                className="text-sm leading-relaxed text-[var(--fg-muted)]",
            ),
            footer=act("Close", chrome.close_ui, variant="outline", silent=True),
        )

    def render(self) -> Any:
        from app.host import cart, shop, wish

        item = get(self.product_id or "")
        if not item:
            return EmptyState(
                title="Gone",
                description="That piece left the floor.",
                action=act("Shop", shop.browse, category="all"),
            )
        sold = item["stock"] <= 0
        saved = store.wished(item["id"])
        size = self.size or ""
        tab = self.pdp_tab or "story"
        story = p(item["desc"], className="text-sm leading-relaxed text-[var(--fg-muted)]")
        reviews = div(
            *[
                div(
                    p(f"{rev['name']} · {rev['stars']}/5", className="text-xs text-[var(--fg-subtle)]"),
                    p(rev["text"], className="mt-1 text-sm text-[var(--fg)]"),
                    className="border-t border-[var(--line)] py-3 first:border-0 first:pt-0",
                )
                for rev in item["reviews"]
            ]
        )
        care = div(*[spec(a, b) for a, b in item["specs"]], className="grid grid-cols-3 gap-3")
        sizes = None
        if item.get("sizes"):
            sizes = div(
                p("Size", className=f"{type_scale['caption']} mb-2"),
                div(
                    *[
                        act(s, self.size_set, variant="secondary" if size == s else "outline", size="sm", opt=s)
                        for s in item["sizes"]
                    ],
                    className="flex flex-wrap gap-2",
                ),
                className="mt-5",
            )
        return div(
            Breadcrumb(items=[("Home", "/index/Index"), ("Shop", "/shop/Shop"), (item["name"], None)]),
            act("← Floor", shop.browse, variant="ghost", size="sm", category=item["category"], className="mt-3"),
            Alert(
                AlertTitle("Waiting on the next pour"),
                AlertDescription("This piece is sold through. Save it and we will write."),
                variant="warning",
                className="mt-4",
            )
            if sold
            else None,
            div(
                img(src=item["img"], alt=item["name"], className="product-photo w-full rounded-[1.5rem] object-cover"),
                div(
                    p(item["category"].title(), className="text-[11px] uppercase tracking-[0.18em] text-[var(--fg-subtle)]"),
                    PageHeader(
                        item["name"],
                        f"{store.inr(item['price'])} · {item['rating']} / 5 · {item['stock']} left" if not sold else "Sold out",
                        className="mt-2",
                    ),
                    sizes,
                    div(
                        act("Add to bag", cart.add, id=item["id"], className="flex-1 min-h-11") if not sold else Button("Notify me", disabled=True),
                        act("Saved" if saved else "Save", wish.toggle, variant="outline", id=item["id"]),
                        act("Size guide", self.guide, variant="ghost", id=item["id"]) if item.get("sizes") else None,
                        className="mt-6 flex flex-wrap gap-2",
                    ),
                    stamp_region(
                        div(
                            div(
                                *[
                                    act(label, self.tab, variant="secondary" if tab == key else "ghost", size="sm", tab=key)
                                    for key, label in (("story", "Story"), ("reviews", "Notes"), ("care", "Care"))
                                ],
                                className="mt-8 flex flex-wrap gap-2",
                            ),
                            Tabs(
                                items=[("story", "Story", story), ("reviews", "Notes", reviews), ("care", "Care", care)],
                                active=tab,
                                className="mt-2",
                            ),
                        ),
                        uid="tabs:pdp",
                    ),
                    className="mt-6 lg:mt-0",
                ),
                className="mt-6 grid gap-8 lg:grid-cols-2 lg:items-start",
            ),
            section("With this", "Same shelf, or next to it.", related(item["id"]), open_fn=self.open),
        )
