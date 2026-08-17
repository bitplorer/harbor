"""Chrome — topbar, menu, find, toasts, overlay. Session only."""
from __future__ import annotations

from typing import Any

from ux_app import Component, Session
from ux_app.overlay import close_overlay, open_overlay, select_region
from ux_dom.dom import button, div, form, p, span
from ux_dom.ui import Avatar, AvatarFallback, Button, Dialog, DropdownMenu, Input, Kbd, Sheet, ToastHost
from ux_dom.ui.tokens import cn, surface, type_scale

from app import store
from app.catalog import PRODUCTS
from app.wiring import act, finish, hx, wire


class Chrome(Component):
    id = "chrome"
    page: str = Session("home")
    menu_open: bool = Session(False)
    notice: Any = Session(None)
    command_q: str = Session("")

    def go(self, ctx, page: str = "home") -> Any:
        self.page = page
        return finish([*close_overlay(), *select_region("page:shop", page)])

    def toggle(self, ctx) -> Any:
        self.menu_open = not bool(self.menu_open)
        return finish([], keep_menu=True)

    def close_menu(self, ctx) -> Any:
        self.menu_open = False
        return finish([])

    def find(self, ctx) -> Any:
        from app.host import shop

        self.menu_open = False
        self.command_q = shop.query or ""
        return finish(open_overlay("command", key="find"))

    def query_find(self, ctx, q: str = "") -> Any:
        self.command_q = q
        return finish(open_overlay("command", key="find", q=q))

    def dismiss(self, ctx) -> Any:
        self.notice = None
        return finish([])

    def close_ui(self, ctx) -> Any:
        self.menu_open = False
        return finish(close_overlay())

    def reset(self, ctx) -> Any:
        from app.host import cart, checkout, home, host, orders, product, shop

        store.reset()
        home.slide = 0
        self.page = "home"
        self.menu_open = False
        self.notice = None
        self.command_q = ""
        shop._reset_filters()
        product._reset_view()
        checkout._reset_draft()
        orders.order_id = ""
        cart.promo = ""
        host.world.kv.clear()
        host.world.log.clear()
        return finish(close_overlay(), message="Store reset")

    def render(self) -> Any:
        from app.host import account, cart, orders, shop, wish

        acc = store.HOST["account"]
        bag = store.cart_count()
        saved = len(store.HOST.get("wish") or [])
        menu_open = bool(self.menu_open)
        initials = "".join(part[0] for part in acc["name"].split()[:2]).upper() or "SA"
        return div(
            button(
                type="button",
                className="fixed inset-0 z-40 bg-transparent",
                **wire(self.close_menu, silent=True),
                **{"aria-label": "Close menu"},
            )
            if menu_open
            else None,
            div(
                act(
                    "Harbor & Co.",
                    self.go,
                    variant="ghost",
                    size="sm",
                    className="font-display px-1 text-lg tracking-tight",
                    page="home",
                ),
                div(
                    act("Shop", shop.browse, variant="ghost", size="sm", category="all", className="hidden sm:inline-flex"),
                    act("Find", self.find, variant="outline", size="sm"),
                    act(
                        f"Saved {saved}" if saved else "Saved",
                        wish.show,
                        variant="ghost",
                        size="sm",
                        className="hidden sm:inline-flex",
                    ),
                    act(f"Bag {bag}" if bag else "Bag", cart.open, variant="secondary", size="sm"),
                    div(
                        Button(
                            Avatar(AvatarFallback(initials), className="h-8 w-8 text-xs"),
                            variant="ghost",
                            size="icon",
                            className="relative z-50 rounded-full",
                            **wire(self.toggle, silent=True),
                        ),
                        self._menu(menu_open, acc, account, orders, cart),
                        className="relative z-50",
                        id="clerk-wrap",
                    ),
                    className="flex items-center gap-1 sm:gap-2",
                ),
                className="relative z-50 mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-3 sm:px-6",
            ),
            className="sticky top-0 z-50 border-b border-[var(--line)] bg-[color-mix(in_oklab,var(--bg)_92%,transparent)] pt-[env(safe-area-inset-top)] backdrop-blur",
            id="topbar",
        )

    def dock(self) -> Any:
        from app.host import cart, shop, wish

        bag = store.cart_count()
        saved = len(store.HOST.get("wish") or [])
        return div(
            act("Shop", shop.browse, variant="ghost", size="sm", category="all", className="min-h-11 flex-1"),
            act("Find", self.find, variant="ghost", size="sm", className="min-h-11 flex-1"),
            act(
                f"Saved {saved}" if saved else "Saved",
                wish.show,
                variant="ghost",
                size="sm",
                className="min-h-11 flex-1",
            ),
            act(
                f"Bag {bag}" if bag else "Bag",
                cart.open,
                variant="secondary",
                size="sm",
                className="min-h-11 flex-1",
            ),
            id="mobile-dock",
            className="fixed inset-x-0 bottom-0 z-40 flex gap-1 border-t border-[var(--line)] bg-[color-mix(in_oklab,var(--bg)_94%,transparent)] px-2 py-2 pb-[max(0.5rem,env(safe-area-inset-bottom))] backdrop-blur sm:hidden",
        )

    def _menu(self, open_: bool, acc: dict[str, Any], account, orders, cart) -> Any:
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
        return (
            div(
                p(
                    acc["name"] if acc["signed_in"] else "Guest",
                    className="px-3 py-2 text-xs text-[var(--fg-muted)]",
                ),
                DropdownMenu(items=items, open=open_, className="absolute right-0 top-full z-50 mt-2 w-44"),
                role="menu",
                id="clerk-menu",
                className="relative",
            )
            if open_
            else None
        )

    def toasts(self) -> Any:
        notice = self.notice
        if not notice:
            return div(id="notices", className="hidden")
        return div(
            ToastHost(
                items=[{"text": notice.get("text") or "", "level": notice.get("level") or "info"}],
                className="min-w-0 flex-1",
            ),
            act("Dismiss", self.dismiss, variant="ghost", size="sm", silent=True),
            id="toast-stack",
            className="pointer-events-auto fixed inset-x-3 top-16 z-40 flex items-start gap-1 sm:inset-x-auto sm:right-4 sm:w-80",
            hx_post="/act/chrome.dismiss",
            hx_trigger="load delay:3.2s",
            **hx(silent=True),
        )

    def overlay(self) -> Any:
        from app.host import cart, kv, product

        open_ = bool(kv().get("ui.overlay.open"))
        kind = kv().get("ui.overlay.kind") or ""
        payload = kv().get("ui.overlay.payload") or {}
        if not isinstance(payload, dict):
            payload = {}
        if kind == "sheet":
            from app.host import checkout

            return Sheet(
                open=open_,
                title="Bag",
                body=cart.panel(page=False, actions=False),
                footer=div(
                    act("Checkout", checkout.start, className="min-h-11"),
                    act("Close", self.close_ui, variant="ghost", silent=True),
                    className="flex w-full flex-wrap gap-2",
                ),
                side="right",
                className="flex max-h-dvh w-full max-w-md flex-col overflow-y-auto",
            )
        if kind == "command":
            return self._find(open_)
        if kind == "dialog" and payload.get("key") == "guide":
            return product.guide_dialog()
        return Dialog(open=False, id="overlay")

    def _find(self, open_: bool) -> Any:
        from app.host import product

        if not open_:
            return Dialog(open=False, id="overlay")
        q = (self.command_q or "").strip().lower()
        rows = PRODUCTS
        if q:
            rows = [p for p in PRODUCTS if q in p["name"].lower() or q in p["blurb"].lower()]
        items = [
            act(
                f"{p['name']}  {store.inr(p['price'])}",
                product.open,
                variant="ghost",
                size="sm",
                className="w-full justify-start",
                id=p["id"],
            )
            for p in rows[:8]
        ] or [p("No match", className="px-2 py-3 text-sm text-[var(--fg-subtle)]")]
        return div(
            button(
                type="button",
                className="fixed inset-0 z-[60] bg-black/60",
                **wire(self.close_ui, silent=True),
                **{"aria-label": "Close find"},
            ),
            div(
                div(
                    p("Find a piece", className=cn(type_scale["caption"])),
                    span(Kbd("⌘"), Kbd("K"), className="flex gap-1 text-[var(--fg-subtle)]"),
                    className="mb-2 flex items-center justify-between",
                ),
                form(
                    Input(name="q", value=self.command_q or "", placeholder="Linen, oak, tote", autofocus=True),
                    hx_post="/act/chrome.query_find",
                    hx_trigger="keyup changed delay:250ms",
                    **hx(silent=True),
                ),
                div(*items, className="mt-2 flex max-h-72 flex-col gap-1 overflow-auto"),
                className=cn(
                    surface["l2"],
                    "fixed left-1/2 top-[16%] z-[70] w-[min(32rem,calc(100vw-1.5rem))] -translate-x-1/2 rounded-xl p-3",
                ),
                id="overlay",
                **{"data-open": "1"},
            ),
        )
