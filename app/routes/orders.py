"""Orders — GET /orders (ux-compose DirectoryRoutes: URL = file path)."""
from __future__ import annotations

from ux_dom import Component

from app.routes._show import show

__all__ = ["Orders"]


class Orders(Component):
    def render(self):
        return show("orders", "Orders · Harbor & Co.")
