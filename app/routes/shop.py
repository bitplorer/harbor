"""Shop catalog — GET /shop (ux-compose DirectoryRoutes: URL = file path)."""
from __future__ import annotations

from ux_dom import Component

from app.routes._show import show

__all__ = ["Shop"]


class Shop(Component):
    def render(self):
        return show("shop", "Shop · Harbor & Co.")
