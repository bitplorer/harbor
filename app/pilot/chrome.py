"""Chrome actions on ux-behavior — parallel to app.chrome.Chrome close/menu.

Author seat only. Does not own topbar markup.
"""

from __future__ import annotations

from typing import Any

try:
    from ux_behavior import Component, action, close, notify, open, select
except ImportError:  # pragma: no cover
    Component = object  # type: ignore

    def action(*a, **k):  # type: ignore
        def deco(fn):
            return fn

        return deco

    def close():  # type: ignore
        return []

    def open(*a, **k):  # type: ignore
        return []

    def select(*a, **k):  # type: ignore
        return []

    def notify(*a, **k):  # type: ignore
        return type("Op", (), {})()


class BehaviorChrome(Component):
    id = "chrome"

    def __init__(self) -> None:
        self.page: str = "home"
        self.menu_open: bool = False
        self.notice: dict[str, str] | None = None
        self.command_q: str = ""

    def render(self) -> str:
        return f"<div id='chrome' data-page='{self.page}' data-menu='{int(self.menu_open)}'></div>"

    @action(caps=())
    def go(self, page: str = "home") -> list[Any]:
        self.page = page
        self.menu_open = False
        return list(close()) + list(select("page:shop", page))

    @action(caps=())
    def toggle(self) -> None:
        self.menu_open = not self.menu_open
        return None  # dirty projection

    @action(caps=())
    def close_menu(self) -> None:
        self.menu_open = False
        return None

    @action(caps=())
    def close_ui(self) -> list[Any]:
        self.menu_open = False
        return list(close())

    @action(caps=())
    def find(self) -> list[Any]:
        self.menu_open = False
        return list(open("command", key="find"))

    @action(caps=())
    def dismiss(self) -> None:
        self.notice = None
        return None

    @action(caps=())
    def reset_notice(self, message: str = "Store reset") -> list[Any]:
        self.menu_open = False
        self.notice = {"text": message, "level": "success"}
        return list(close()) + [notify(message)]
