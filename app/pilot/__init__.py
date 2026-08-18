"""Parallel ux-behavior pilot seat.

Does not replace app.host (ux-app). Enable with:

    HARBOR_BEHAVIOR_PILOT=1

Requires: pip install ux-behavior
"""

from __future__ import annotations

from app.pilot.cart import BehaviorCart, build_behavior_app

__all__ = ["BehaviorCart", "build_behavior_app"]
