"""Account — /account/Account."""
from __future__ import annotations

from ux_dom import Component

from app.routes._show import show

__all__ = ["Account"]


class Account(Component):
    routes = ["get"]

    def render(self):
        from app.shell import storefront

        return storefront()

    @classmethod
    def get(cls):
        return show("account", "Account · Harbor & Co.")
