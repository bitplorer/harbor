"""Saved — GET /wish (ux-compose DirectoryRoutes: URL = file path)."""
from __future__ import annotations

from ux_dom import Component

from app.routes._show import show

__all__ = ["Wish"]


class Wish(Component):
    def render(self):
        return show("wish", "Saved · Harbor & Co.")
