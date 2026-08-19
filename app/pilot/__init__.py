"""Parallel ux-behavior pilot seat.

Does not replace app.host (ux-app) by default.

Enable dual-boot registration::

    HARBOR_BEHAVIOR_PILOT=1

Requires: pip install -e ".[dev]"  # pulls ux-behavior
"""

from __future__ import annotations

import os
from typing import Any

from app.pilot.cart import BehaviorCart
from app.pilot.chrome import BehaviorChrome

__all__ = [
    "BehaviorCart",
    "BehaviorChrome",
    "build_behavior_app",
    "pilot_enabled",
    "register_pilot",
]


def pilot_enabled() -> bool:
    return os.environ.get("HARBOR_BEHAVIOR_PILOT", "").strip() in {
        "1",
        "true",
        "yes",
        "on",
    }


def build_behavior_app(*, title: str = "Harbor pilot") -> Any:
    try:
        from ux_behavior import Behavior
    except ImportError as exc:  # pragma: no cover
        raise ImportError("ux-behavior is not installed") from exc
    app = Behavior.boot(title=title)
    app.add(BehaviorCart)
    app.add(BehaviorChrome)
    return app


def register_pilot(host: Any | None = None) -> Any | None:
    """When HARBOR_BEHAVIOR_PILOT=1, build and return a Behavior root.

    Live ux-app ``host`` is left intact. Returns None when disabled or missing.
    """
    if not pilot_enabled():
        return None
    try:
        return build_behavior_app()
    except ImportError:
        return None
