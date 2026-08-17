"""Persistent wait chrome — outside #app so morphs never tear it down."""
from __future__ import annotations

from ux_dom import Component
from ux_dom.dom import div
from ux_dom.ui import Skeleton


class WaitChrome(Component):
    """Hairline sweep + flashing skeleton veil while an action settles."""

    def render(self):
        bones = [
            div(
                Skeleton(className="aspect-[4/3] w-full rounded-xl"),
                Skeleton(className="mt-3 h-3 w-2/3"),
                Skeleton(className="mt-2 h-3 w-1/3"),
                className="min-w-0",
            )
            for _ in range(3)
        ]
        return div(
            div(
                div(className="desk-sweep"),
                id="desk-progress",
                className="pointer-events-none fixed inset-x-0 top-0 z-[80] h-0.5 overflow-hidden",
                **{"aria-hidden": "true"},
            ),
            div(
                div(
                    *bones,
                    className="mx-auto grid w-full max-w-6xl grid-cols-1 gap-4 px-4 pt-24 sm:grid-cols-3",
                ),
                id="desk-veil",
                className="pointer-events-none fixed inset-0 z-[45] bg-[color-mix(in_oklab,var(--ink)_55%,transparent)] backdrop-blur-[1px]",
                **{"aria-hidden": "true", "aria-live": "polite", "aria-label": "Updating floor"},
            ),
        )
