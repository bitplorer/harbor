"""Account — GET /account (ux-compose DirectoryRoutes: URL = file path)."""
from __future__ import annotations

from ux_dom import Component

from app.routes._show import show

__all__ = ["Account"]


class Account(Component):
    def render(self):
        return show("account", "Account · Harbor & Co.")
