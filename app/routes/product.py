"""Product page — GET /product (ux-compose DirectoryRoutes: URL = file path)."""
from __future__ import annotations

from ux_dom import Component

from app.routes._show import show

__all__ = ["Product"]


class Product(Component):
    def render(self):
        return show("pdp", "Piece · Harbor & Co.")
