"""Checkout — GET /checkout (ux-compose DirectoryRoutes: URL = file path)."""
from __future__ import annotations

from ux_dom import Component

from app.routes._show import show

__all__ = ["Checkout"]


class Checkout(Component):
    def render(self):
        return show("checkout", "Checkout · Harbor & Co.")
