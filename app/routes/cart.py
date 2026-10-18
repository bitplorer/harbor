"""Bag — GET /cart (ux-compose DirectoryRoutes: URL = file path)."""
from __future__ import annotations

from ux_dom import Component

from app.routes._show import show

__all__ = ["Cart"]


class Cart(Component):
    def render(self):
        return show("cart", "Bag · Harbor & Co.")
