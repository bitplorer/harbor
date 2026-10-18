"""Home route — GET / (ux-compose DirectoryRoutes: URL = file path)."""
from __future__ import annotations

from ux_dom import Component

from app.routes._show import show

__all__ = ["Index"]


class Index(Component):
    def render(self):
        return show("home", "Harbor & Co.")
