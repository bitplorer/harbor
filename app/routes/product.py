"""Product page — /product/Product."""
from __future__ import annotations

from ux_dom import Component

from app.routes._show import show

__all__ = ["Product"]


class Product(Component):
    routes = ["get"]

    def render(self):
        from app.views import storefront

        return storefront()

    @classmethod
    def get(cls):
        return show("pdp", "Piece · Harbor & Co.")
