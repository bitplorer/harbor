"""Shared page chrome — Harbor shell, id=app is the morph target."""
from __future__ import annotations

from ux_app.ui import stamp_region
from ux_dom import Component
from ux_dom.dom import div


class Shell(Component):
    """Frame that HTMX replaces. Wait chrome stays outside this node."""

    def render(self, *children, active: str = "home"):
        from app.host import chrome, host
        from app.views import overlay, toasts

        return stamp_region(
            div(
                chrome.render(),
                toasts(),
                div(*children, className="mx-auto w-full max-w-6xl px-4 pb-24 pt-6 sm:px-6"),
                overlay(),
                id="app",
                className="relative min-h-screen overflow-x-hidden bg-stone-950 text-stone-100",
                **{"data-active": active},
            ),
            uid=host.region_uid,
        )
