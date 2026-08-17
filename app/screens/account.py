"""Account — sign in, address, sign out."""
from __future__ import annotations

from typing import Any

from ux_app import Component
from ux_dom.dom import div, form, p
from ux_dom.ui import Button, Card, CardContent, CardDescription, CardHeader, CardTitle, Input, Label, PageHeader

from app import store
from app.wiring import act, finish, go, wire


class Account(Component):
    id = "account"

    def show(self, ctx) -> Any:
        from app.host import chrome

        chrome.menu_open = False
        return go("account")

    def signin(self, ctx, email: str = "", name: str = "") -> Any:
        acc = dict(store.HOST["account"])
        acc["signed_in"] = True
        if email:
            acc["email"] = email
        if name:
            acc["name"] = name
        store.HOST["account"] = acc
        return finish([], message=f"Signed in as {acc['name']}")

    def signout(self, ctx) -> Any:
        from app.host import chrome

        acc = dict(store.HOST["account"])
        acc["signed_in"] = False
        store.HOST["account"] = acc
        chrome.menu_open = False
        return finish([], message="Signed out")

    def render(self) -> Any:
        from app.host import chrome, orders, wish

        acc = store.HOST["account"]
        if not acc["signed_in"]:
            return div(
                PageHeader("Sign in", "Enter the house.", className="mb-6"),
                Card(
                    CardContent(
                        form(
                            div(Label("Name"), Input(name="name", value=acc["name"])),
                            div(Label("Email"), Input(name="email", value=acc["email"]), className="mt-3"),
                            Button("Enter the house", type="submit", className="mt-5 min-h-11"),
                            **wire(self.signin),
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
                    p(ship, className="text-sm text-[var(--fg-muted)]"),
                    p(acc["phone"], className="mt-1 text-sm text-[var(--fg-subtle)]"),
                ),
                className="max-w-md",
            ),
            div(
                act("Orders", orders.show),
                act("Saved", wish.show, variant="outline"),
                act("Sign out", self.signout, variant="ghost"),
                act("Reset store", chrome.reset, variant="ghost", className="text-[var(--fg-subtle)]"),
                className="mt-6 flex flex-wrap gap-2",
            ),
        )
