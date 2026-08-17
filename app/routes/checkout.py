"""Checkout — /checkout/Checkout."""
from __future__ import annotations

from ux_dom import Component

from app.routes._show import show

__all__ = ["Checkout"]


class Checkout(Component):
    routes = ["get"]

    def render(self):
        from app.views import storefront

        return storefront()

    @classmethod
    def get(cls):
        return show("checkout", "Checkout · Harbor & Co.")
