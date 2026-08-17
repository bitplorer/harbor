"""Harbor storefront — ux-dom UI kit, ux-app actions, official Shell."""
from __future__ import annotations

from typing import Any

from ux_dom.dom import button, div, form, h2, img, p, span
from ux_dom.ui import (
    Alert,
    AlertDescription,
    AlertTitle,
    Avatar,
    AvatarFallback,
    Badge,
    Breadcrumb,
    Button,
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
    Chart,
    DatePicker,
    Dialog,
    DropdownMenu,
    EmptyState,
    FormSection,
    Input,
    Kbd,
    Label,
    PageHeader,
    Progress,
    RadioGroup,
    Select,
    Separator,
    Sheet,
    Slider,
    StatusStrip,
    Switch,
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
    Tabs,
    ToastHost,
)
from ux_dom.ui.tokens import cn, surface, type_scale

from app import store
from app.carousel import hero_at
from app.catalog import CATEGORIES, PRODUCTS, get, related
from app.host import (
    PAGES,
    account,
    cart,
    checkout,
    chrome,
    home,
    kv,
    orders,
    product,
    shop,
    wish,
)
from app.hx import act, hx, wire
from ux_app.ui import stamp_region


def storefront(page: str | None = None) -> Any:
    from app.components.layout import Shell

    key = page or chrome.page or "home"
    body = PAGES.get(key, home.render)()
    return Shell(body, active=key)


def topbar(active: str = "home") -> Any:
    acc = store.HOST["account"]
    bag = store.cart_count()
    saved = len(store.HOST.get("wish") or [])
    menu_open = bool(chrome.menu_open)
    initials = "".join(part[0] for part in acc["name"].split()[:2]).upper() or "SA"
    return div(
        button(
            type="button",
            className="fixed inset-0 z-40 bg-transparent",
            **wire(chrome.close_menu, silent=True),
            **{"aria-label": "Close menu"},
        )
        if menu_open
        else None,
        div(
            act("Harbor & Co.", chrome.go, variant="ghost", size="sm", className="font-display px-1 text-lg", page="home"),
            div(
                act("Shop", shop.browse, variant="ghost", size="sm", category="all", className="hidden sm:inline-flex"),
                act("Find", chrome.find, variant="outline", size="sm"),
                act(f"Saved {saved}" if saved else "Saved", wish.show, variant="ghost", size="sm", className="hidden sm:inline-flex"),
                act(f"Bag {bag}" if bag else "Bag", cart.open, variant="secondary", size="sm"),
                div(
                    Button(
                        Avatar(AvatarFallback(initials), className="h-8 w-8 text-xs"),
                        variant="ghost",
                        size="icon",
                        className="relative z-50 rounded-full",
                        **wire(chrome.toggle, silent=True),
                    ),
                    _menu(menu_open, acc),
                    className="relative z-50",
                    id="clerk-wrap",
                ),
                className="flex items-center gap-1 sm:gap-2",
            ),
            className="relative z-50 mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-3 sm:px-6",
        ),
        className="sticky top-0 z-50 border-b border-stone-800/80 bg-stone-950/95 pt-[env(safe-area-inset-top)] backdrop-blur",
        id="topbar",
    )


def _menu(open_: bool, acc: dict[str, Any]) -> Any:
    items = [
        act("Account", account.show, variant="ghost", size="sm", className="w-full justify-start"),
        act("Orders", orders.show, variant="ghost", size="sm", className="w-full justify-start"),
        act("Bag", cart.show, variant="ghost", size="sm", className="w-full justify-start"),
        act(
            "Sign out" if acc["signed_in"] else "Sign in",
            account.signout if acc["signed_in"] else account.show,
            variant="ghost",
            size="sm",
            className="w-full justify-start",
        ),
    ]
    return div(
        p(acc["name"] if acc["signed_in"] else "Guest", className="px-3 py-2 text-xs text-stone-400"),
        DropdownMenu(items=items, open=open_, className="absolute right-0 top-full z-50 mt-2 w-44"),
        role="menu",
        id="clerk-menu",
        className="relative",
    ) if open_ else None


def toasts() -> Any:
    notice = chrome.notice
    if not notice:
        return div(id="notices", className="hidden")
    return div(
        ToastHost(items=[{"text": notice.get("text") or "", "level": notice.get("level") or "info"}], className="min-w-0 flex-1"),
        act("Dismiss", chrome.dismiss, variant="ghost", size="sm", silent=True),
        id="toast-stack",
        className="pointer-events-auto fixed inset-x-3 top-16 z-40 flex items-start gap-1 sm:inset-x-auto sm:right-4 sm:w-80",
        hx_post="/act/chrome.dismiss",
        hx_trigger="load delay:3.2s",
        **hx(silent=True),
    )


def overlay() -> Any:
    open_ = bool(kv().get("ui.overlay.open"))
    kind = kv().get("ui.overlay.kind") or ""
    payload = kv().get("ui.overlay.payload") or {}
    if not isinstance(payload, dict):
        payload = {}
    if kind == "sheet":
        return Sheet(open=open_, title="Bag", body=_cart_body(page=False), side="right")
    if kind == "command":
        return _find(open_)
    if kind == "dialog" and payload.get("key") == "guide":
        return Dialog(
            open=open_,
            title="How it wears",
            body=p("S easy, M true, L over a knit. The overshirt is unlined so it layers.", className="text-sm text-stone-300"),
            footer=act("Close", chrome.close_ui, variant="outline", silent=True),
        )
    return Dialog(open=False, id="overlay")


def _find(open_: bool) -> Any:
    if not open_:
        return Dialog(open=False, id="overlay")
    q = (chrome.command_q or "").strip().lower()
    rows = PRODUCTS
    if q:
        rows = [p for p in PRODUCTS if q in p["name"].lower() or q in p["blurb"].lower()]
    items = [
        act(f"{p['name']}  {store.inr(p['price'])}", product.open, variant="ghost", size="sm", className="w-full justify-start", id=p["id"])
        for p in rows[:8]
    ] or [p("No match", className="px-2 py-3 text-sm text-stone-500")]
    return div(
        button(
            type="button",
            className="fixed inset-0 z-[60] bg-black/60",
            **wire(chrome.close_ui, silent=True),
            **{"aria-label": "Close find"},
        ),
        div(
            div(
                p("Find a piece", className=cn(type_scale["caption"])),
                span(Kbd("⌘"), Kbd("K"), className="flex gap-1 text-stone-500"),
                className="mb-2 flex items-center justify-between",
            ),
            form(
                Input(name="q", value=chrome.command_q or "", placeholder="Linen, oak, tote", autofocus=True),
                hx_post="/act/command.query",
                hx_trigger="keyup changed delay:250ms",
                **hx(silent=True),
            ),
            div(*items, className="mt-2 flex max-h-72 flex-col gap-1 overflow-auto"),
            className=cn(surface["l2"], "fixed left-1/2 top-[16%] z-[70] w-[min(32rem,calc(100vw-1.5rem))] -translate-x-1/2 rounded-xl p-3"),
            id="overlay",
            **{"data-open": "1"},
        ),
    )


def home_body() -> Any:
    featured = [p for p in PRODUCTS if p.get("featured")]
    fresh = [p for p in PRODUCTS if p.get("new")]
    slot = hero_at(home.slide)
    hero = slot["hero"]
    idx = slot["idx"]
    carousel = stamp_region(
        div(
            img(
                src=hero["img"],
                alt=hero["name"],
                id=slot["photo_id"],
                className="product-photo h-48 w-full rounded-2xl object-cover sm:h-64",
            ),
            div(
                p(hero["name"], className="font-display text-2xl text-stone-50"),
                p(hero["blurb"], className="mt-1 text-sm text-stone-400"),
                div(
                    act("Prev", home.prev, variant="outline", size="sm"),
                    act("View", product.open, size="sm", id=hero["id"]),
                    act("Next", home.next, variant="outline", size="sm"),
                    className="mt-4 flex flex-wrap gap-2",
                ),
                className="mt-4",
            ),
            className=cn(surface["l1"], "rounded-2xl p-3 sm:p-4"),
            id=slot["card_id"],
            **{"data-hero": hero["id"], "data-slide": str(idx)},
        ),
        uid="carousel:hero",
    )
    return div(
        StatusStrip(
            items=[("Live floor", "default"), ("Gorakhpur", "secondary"), ("Packed today", "outline")],
            message="New flax this morning.",
            className="mb-6",
        ),
        div(
            img(src="/assets/img/hero.jpg", alt="Morning room at Harbor & Co.", className="product-photo h-56 w-full rounded-2xl object-cover sm:h-80"),
            div(
                p("Harbor & Co.", className="text-xs uppercase tracking-[0.22em] text-stone-400"),
                PageHeader(
                    "Goods for the house and the coast.",
                    "Linen, clay, oak, and waxed canvas. Made to be used.",
                    actions=div(
                        act("Shop the floor", shop.browse, category="all"),
                        act("New this week", shop.sort_by, variant="outline", sort="new"),
                        className="flex flex-wrap gap-2",
                    ),
                    className="mt-4",
                ),
            ),
        ),
        div(
            p("On rotation", className=cn(type_scale["caption"], "mb-3")),
            carousel,
            className="mt-10",
        ),
        div(
            *[_cat_tile(key, label) for key, label in CATEGORIES if key != "all"],
            className="mt-10 grid grid-cols-2 gap-3 sm:grid-cols-4",
        ),
        Card(
            CardHeader(CardTitle("Floor tempo"), CardDescription("Pieces leaving the bench this week.")),
            CardContent(Chart(series=[4, 6, 5, 9, 7, 11, 8], kind="bar", className="h-24")),
            className="mt-10",
        ),
        _section("On the table", "Pieces we keep on the floor.", featured),
        _section("Just in", "This week's arrivals.", fresh),
    )


def _cat_tile(key: str, label_text: str) -> Any:
    n = sum(1 for p in PRODUCTS if p["category"] == key)
    return button(
        span(label_text, className="font-display text-xl text-stone-50"),
        span(f"{n} pieces", className="mt-1 block text-xs text-stone-500"),
        type="button",
        **wire(shop.browse, category=key),
        className=cn(surface["l1"], "rounded-2xl p-4 text-left min-h-[5.5rem]"),
    )


def _section(title: str, blurb: str, rows: list[dict[str, Any]]) -> Any:
    return div(
        div(
            h2(title, className="font-display text-2xl text-stone-50"),
            p(blurb, className="mt-1 text-sm text-stone-500"),
            className="mb-4",
        ),
        div(*[_card(p) for p in rows], className="grid grid-cols-2 gap-4 lg:grid-cols-4"),
        className="mt-12",
    )


def _card(item: dict[str, Any]) -> Any:
    sold = item["stock"] <= 0
    return div(
        button(
            img(src=item["img"], alt=item["name"], className="product-photo aspect-[4/3] w-full object-cover"),
            type="button",
            **wire(product.open, id=item["id"]),
            className="block w-full overflow-hidden rounded-2xl",
        ),
        p(item["name"], className="mt-3 text-sm text-stone-100"),
        p("Sold out" if sold else store.inr(item["price"]), className="mt-0.5 text-sm tabular-nums text-stone-400"),
        className="min-w-0",
    )


def shop_body() -> Any:
    rows, page_n, pages = store.page_rows()
    cat = shop.category or "all"
    sort = shop.sort or "featured"
    q = shop.query or ""
    cap = int(shop.price_max or 10000)
    return div(
        PageHeader("The floor", "Linen to waxed canvas. Filter, then walk it.", className="mb-6"),
        form(
            Input(name="q", value=q, placeholder="Search the floor", className="min-w-0 flex-1"),
            Button("Search", type="submit", variant="secondary", size="sm"),
            **wire(shop.search),
            className="flex gap-2",
        ),
        div(
            *[
                act(label_text, shop.browse, variant="secondary" if cat == key else "ghost", size="sm", className="rounded-full", category=key)
                for key, label_text in CATEGORIES
            ],
            className="mt-4 flex flex-wrap gap-2",
        ),
        form(
            Label("Sort"),
            Select(
                name="sort",
                options=[("featured", "Featured"), ("new", "New"), ("price_asc", "Price ↑"), ("price_desc", "Price ↓")],
                value=sort,
                className="mt-1",
            ),
            Button("Apply", type="submit", variant="ghost", size="sm", className="mt-2"),
            **wire(shop.sort_by),
            className="mt-4 max-w-xs",
        ),
        form(
            Label(f"Up to {store.inr(cap)}"),
            Slider(name="price", min=1000, max=10000, step=500, value=cap, show_value=True, className="mt-2"),
            Button("Apply", type="submit", variant="outline", size="sm", className="mt-3"),
            **wire(shop.price),
            className="mt-5 max-w-md",
        ),
        p(f"{len(store.listing())} pieces", className=cn(type_scale["caption"], "mt-4")),
        div(*[_card(p) for p in rows], className="mt-4 grid grid-cols-2 gap-4 lg:grid-cols-3")
        if rows
        else EmptyState(title="Nothing on that search", description="Clear it and walk the floor again.", action=act("Clear", shop.search, variant="outline", q="")),
        div(
            act("Prev", shop.page, variant="outline", size="sm", page=str(page_n - 1), className="" if page_n > 1 else "pointer-events-none opacity-40"),
            span(f"{page_n} / {pages}", className="px-3 text-sm tabular-nums text-stone-400"),
            act("Next", shop.page, variant="outline", size="sm", page=str(page_n + 1), className="" if page_n < pages else "pointer-events-none opacity-40"),
            className="mt-8 flex items-center justify-center gap-2",
        )
        if rows
        else None,
    )


def pdp_body() -> Any:
    item = get(product.product_id or "")
    if not item:
        return EmptyState(title="Gone", description="That piece left the floor.", action=act("Shop", shop.browse, category="all"))
    sold = item["stock"] <= 0
    saved = store.wished(item["id"])
    size = product.size or ""
    tab = product.pdp_tab or "story"
    story = p(item["desc"], className="text-sm leading-relaxed text-stone-300")
    reviews = div(
        *[
            div(
                p(f"{rev['name']} · {rev['stars']}/5", className="text-xs text-stone-500"),
                p(rev["text"], className="mt-1 text-sm text-stone-200"),
                className="border-t border-stone-800 py-3 first:border-0 first:pt-0",
            )
            for rev in item["reviews"]
        ]
    )
    care = div(*[_spec(a, b) for a, b in item["specs"]], className="grid grid-cols-3 gap-3")
    return div(
        Breadcrumb(items=[("Home", "/index/Index"), ("Shop", "/shop/Shop"), (item["name"], None)]),
        act("← Floor", shop.browse, variant="ghost", size="sm", category=item["category"], className="mt-3"),
        Alert(AlertTitle("Waiting on the next pour"), AlertDescription("This piece is sold through. Save it and we will write."), variant="warning", className="mt-4")
        if sold
        else None,
        div(
            img(src=item["img"], alt=item["name"], className="product-photo w-full rounded-2xl object-cover"),
            div(
                p(item["category"].title(), className="text-xs uppercase tracking-[0.18em] text-stone-500"),
                PageHeader(
                    item["name"],
                    f"{store.inr(item['price'])} · {item['rating']} / 5 · {item['stock']} left" if not sold else "Sold out",
                    className="mt-2",
                ),
                _sizes(item, size) if item.get("sizes") else None,
                div(
                    act("Add to bag", cart.add, id=item["id"], className="flex-1") if not sold else Button("Notify me", disabled=True),
                    act("Saved" if saved else "Save", wish.toggle, variant="outline", id=item["id"]),
                    act("Size guide", product.guide, variant="ghost", id=item["id"]) if item.get("sizes") else None,
                    className="mt-6 flex flex-wrap gap-2",
                ),
                stamp_region(
                    div(
                        div(
                            *[
                                act(label, product.tab, variant="secondary" if tab == key else "ghost", size="sm", tab=key)
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
        _section("With this", "Same shelf, or next to it.", related(item["id"])),
    )


def _sizes(item: dict[str, Any], current: str) -> Any:
    return div(
        p("Size", className=cn(type_scale["caption"], "mb-2")),
        div(
            *[
                act(s, product.size_set, variant="secondary" if current == s else "outline", size="sm", opt=s)
                for s in item["sizes"]
            ],
            className="flex flex-wrap gap-2",
        ),
        className="mt-5",
    )


def _spec(k: str, v: str) -> Any:
    return div(
        p(k, className="text-xs text-stone-500"),
        p(v, className="mt-1 text-sm text-stone-200"),
    )


def cart_body() -> Any:
    return div(
        PageHeader("Bag", "Linen and clay wait at the bench.", className="mb-6"),
        _cart_body(page=True),
    )


def _cart_body(*, page: bool) -> Any:
    lines = store.cart_lines()
    if not lines:
        return EmptyState(
            title="Bag is empty",
            description="Walk the floor. Linen and clay are waiting.",
            action=act("Shop", shop.browse, category="all"),
        )
    return div(
        div(*[_line(r) for r in lines], className="divide-y divide-stone-800"),
        _totals(),
        form(
            Input(name="code", placeholder="HARBOR10 or COAST20", value=cart.promo or ""),
            Button("Apply", type="submit", variant="outline", size="sm"),
            **wire(cart.promo_apply),
            className="mt-4 flex gap-2",
        ),
        div(
            act("Checkout", checkout.start),
            act("Keep shopping", shop.browse, variant="ghost", category="all") if page else act("Close", chrome.close_ui, variant="ghost", silent=True),
            className="mt-5 flex flex-wrap gap-2",
        ),
    )


def _line(r: dict[str, Any]) -> Any:
    return div(
        img(src=r["img"], alt=r["name"], className="product-photo h-20 w-20 shrink-0 rounded-xl object-cover"),
        div(
            p(r["name"], className="text-sm text-stone-100"),
            p(f"{store.inr(r['price'])}" + (f" · {r['size']}" if r["size"] else ""), className="text-xs text-stone-500"),
            div(
                act("–", cart.qty, variant="outline", size="sm", id=r["id"], qty=str(r["qty"] - 1), opt=r["size"]),
                span(str(r["qty"]), className="min-w-[1.5rem] text-center text-sm tabular-nums"),
                act("+", cart.qty, variant="outline", size="sm", id=r["id"], qty=str(r["qty"] + 1), opt=r["size"]),
                act("Remove", cart.remove, variant="ghost", size="sm", id=r["id"], opt=r["size"]),
                className="mt-2 flex items-center gap-2",
            ),
            className="min-w-0 flex-1",
        ),
        p(store.inr(r["line"]), className="text-sm tabular-nums text-stone-200"),
        className="flex gap-3 py-4",
    )


def _totals() -> Any:
    rows = [
        ("Subtotal", store.inr(store.subtotal())),
        ("Off", f"−{store.inr(store.discount())}" if store.discount() else "—"),
        ("Ship", "Free" if store.shipping() == 0 else store.inr(store.shipping())),
        ("Wrap", store.inr(store.gift_fee()) if store.gift_fee() else "—"),
        ("GST", store.inr(store.tax())),
        ("Total", store.inr(store.total())),
    ]
    return div(
        *[
            div(
                span(k, className="text-sm text-stone-500"),
                span(v, className="text-sm tabular-nums text-stone-100"),
                className="flex justify-between py-1",
            )
            for k, v in rows
        ],
        className="mt-4 rounded-xl border border-stone-800 px-4 py-3",
    )


def checkout_body() -> Any:
    d = checkout.checkout if isinstance(checkout.checkout, dict) else {}
    if not store.cart_lines():
        return EmptyState(title="Nothing to check out", action=act("Shop", shop.browse, category="all"))
    return div(
        PageHeader("Checkout", "We pack from the Gorakhpur floor.", className="mb-6"),
        Card(
            CardHeader(CardTitle("Ship to"), CardDescription("Name and address stay on the bench.")),
            CardContent(
                form(
                    FormSection(
                        div(Label("Name"), Input(name="name", value=d.get("name") or "")),
                        div(Label("Email"), Input(name="email", value=d.get("email") or ""), className="mt-3"),
                        div(Label("Address"), Input(name="address", value=d.get("address") or ""), className="mt-3"),
                        div(Label("City"), Input(name="city", value=d.get("city") or ""), className="mt-3"),
                        div(Label("PIN"), Input(name="pin", value=d.get("pin") or ""), className="mt-3"),
                        title="Address",
                    ),
                    FormSection(
                        div(
                            Label("Ship"),
                            RadioGroup(
                                name="ship",
                                options=[("standard", "Standard · ₹80 or free over ₹8,000"), ("express", "Express · ₹180")],
                                value=checkout.ship or "standard",
                            ),
                        ),
                        div(Label("Deliver on"), DatePicker(name="deliver", value=checkout.deliver or ""), className="mt-4"),
                        div(
                            Label("Pay"),
                            RadioGroup(name="pay", options=[("upi", "UPI"), ("card", "Card"), ("cod", "Cash on delivery")], value=d.get("pay") or "upi"),
                            className="mt-4",
                        ),
                        div(
                            Label("Gift wrap"),
                            Switch(name="gift", checked=bool(checkout.gift), value="gift"),
                            className="mt-4 flex items-center justify-between",
                        ),
                        title="How it arrives",
                        className="mt-6",
                    ),
                    Separator(className="my-6"),
                    _totals(),
                    div(
                        Button("Place order", type="submit"),
                        act("Back to bag", cart.show, variant="ghost"),
                        className="mt-6 flex flex-wrap gap-2",
                    ),
                    **wire(checkout.place),
                )
            ),
            className="max-w-xl",
        ),
    )


def confirm_body() -> Any:
    oid = store.HOST.get("last_order") or ""
    order = next((o for o in store.HOST["orders"] if o["id"] == oid), None)
    return div(
        PageHeader("Thank you.", "It's on the bench." if order else "Order placed.", className="mb-6"),
        Card(
            CardContent(
                p(order["address"] if order else "", className="text-sm text-stone-300"),
                p(store.inr(order["total"]) if order else "", className="mt-2 text-lg tabular-nums"),
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


def orders_body() -> Any:
    rows = store.HOST.get("orders") or []
    if not rows:
        return div(
            PageHeader("Orders", "The house book.", className="mb-6"),
            EmptyState(title="No orders yet", description="Place one from the bag.", action=act("Shop", shop.browse, category="all")),
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
                            TableCell(act(o["id"], orders.detail, variant="ghost", size="sm", id=o["id"])),
                            TableCell(o["at"], className="text-stone-400"),
                            TableCell(Badge(o["status"], variant="secondary")),
                            TableCell(store.inr(o["total"]), className="text-right tabular-nums"),
                        )
                        for o in rows
                    ]
                ),
            ),
            className="overflow-x-auto rounded-2xl border border-stone-800",
        ),
    )


def order_body() -> Any:
    oid = orders.order_id or ""
    order = next((o for o in store.HOST["orders"] if o["id"] == oid), None)
    if not order:
        return EmptyState(title="Order missing", action=act("Orders", orders.show))
    return div(
        act("← Orders", orders.show, variant="ghost", size="sm"),
        PageHeader(order["id"], f"{order['status']} · {order['at']} · {order['pay'].upper()}", className="mt-3"),
        p(order["address"], className="mt-1 text-sm text-stone-500"),
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
            className="mt-6 divide-y divide-stone-800",
        ),
        p(store.inr(order["total"]), className="mt-4 text-lg tabular-nums"),
    )


def wish_body() -> Any:
    ids = store.HOST.get("wish") or []
    rows = [p for p in PRODUCTS if p["id"] in ids]
    return div(
        PageHeader("Saved", "Pieces kept aside.", className="mb-6"),
        EmptyState(title="Nothing saved", description="Heart a piece from the floor.", action=act("Shop", shop.browse, category="all"))
        if not rows
        else div(*[_card(p) for p in rows], className="grid grid-cols-2 gap-4 lg:grid-cols-3"),
    )


def account_body() -> Any:
    acc = store.HOST["account"]
    if not acc["signed_in"]:
        return div(
            PageHeader("Sign in", "Enter the house.", className="mb-6"),
            Card(
                CardContent(
                    form(
                        div(Label("Name"), Input(name="name", value=acc["name"])),
                        div(Label("Email"), Input(name="email", value=acc["email"]), className="mt-3"),
                        Button("Enter the house", type="submit", className="mt-5"),
                        **wire(account.signin),
                    ),
                    className="p-5",
                ),
                className="max-w-md",
            ),
        )
    ship = f"{acc['address']}, {acc['city']} {acc['pin']}"
    return div(
        PageHeader(acc["name"], acc["email"], className="mb-6"),
        Card(
            CardHeader(CardTitle("Ship to"), CardDescription("Default bench address.")),
            CardContent(
                p(ship, className="text-sm text-stone-300"),
                p(acc["phone"], className="mt-1 text-sm text-stone-500"),
            ),
            className="max-w-md",
        ),
        div(
            act("Orders", orders.show),
            act("Saved", wish.show, variant="outline"),
            act("Sign out", account.signout, variant="ghost"),
            className="mt-6 flex flex-wrap gap-2",
        ),
    )
