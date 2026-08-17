"""Saved — /wish/Wish."""
from __future__ import annotations

from ux_dom import Component

from app.routes._show import show

__all__ = ["Wish"]


class Wish(Component):
    routes = ["get"]

    def render(self):
        from app.views import storefront

        return storefront()

    @classmethod
    def get(cls):
        return show("wish", "Saved · Harbor & Co.")
