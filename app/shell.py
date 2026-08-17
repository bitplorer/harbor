"""Shared page chrome — Harbor shell, id=app is the morph target."""
from __future__ import annotations

from ux_app.ui import stamp_region
from ux_dom import Component
from ux_dom.dom import div, p


class Shell(Component):
    """Frame that HTMX replaces. Wait chrome stays outside this node."""

    def render(self, *children, active: str = "home"):
        from app.host import chrome, host

        return stamp_region(
            div(
                chrome.render(),
                chrome.toasts(),
                div(*children, className="mx-auto w-full max-w-6xl px-4 pb-28 pt-6 sm:px-6 sm:pb-16"),
                div(
                    p("Packed from the Gorakhpur floor. Linen, clay, oak, waxed canvas.", className="text-xs text-[var(--fg-subtle)]"),
                    className="mx-auto mt-8 mb-16 w-full max-w-6xl border-t border-[var(--line)] px-4 py-8 sm:mb-0 sm:px-6",
                ),
                chrome.overlay(),
                chrome.dock(),
                id="app",
                className="relative min-h-screen overflow-x-hidden bg-[var(--bg)] text-[var(--fg)]",
                **{"data-active": active},
            ),
            uid=host.region_uid,
        )


def storefront(page: str | None = None):
    from app.host import PAGES, chrome, home

    key = page or chrome.page or "home"
    body = PAGES.get(key, home.render)()
    return Shell(body, active=key)
