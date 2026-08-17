"""Controls via App.control (live Channel after attach). HTMX is the fallback."""
from __future__ import annotations

import json
from typing import Any

from ux_dom.ui import Button

HX_SWAP = "outerHTML swap:50ms settle:180ms"


def hx(*, silent: bool = False, **extra: Any) -> dict[str, Any]:
    attrs: dict[str, Any] = {
        "hx_target": "#app",
        "hx_swap": HX_SWAP,
        "hx_disabled_elt": "this",
        "hx_sync": "#app:replace",
    }
    if silent:
        attrs["data_desk"] = "silent"
    attrs.update(extra)
    return attrs


def wire(name: str, *, silent: bool = False, **args: Any) -> dict[str, Any]:
    """Prefer App.control after attach(); else mint + HTMX POST /act."""
    from app.host import host

    try:
        bound = host.control(name, **args)
    except Exception:
        bound = None
    if bound and (
        "data_channel_action" in bound
        or "data-channel-action" in bound
    ):
        if silent:
            bound = {**bound, "data_desk": "silent"}
        return bound
    attrs = hx(silent=silent, hx_post=f"/act/{name}")
    attrs["data_action"] = name
    if args:
        payload = dict(args)
        if bound and bound.get("data_cap"):
            payload["__cap"] = bound["data_cap"]
            attrs["data_cap"] = bound["data_cap"]
            attrs["data_args"] = bound.get("data_args") or json.dumps(
                args, separators=(",", ":"), default=str
            )
        attrs["hx_vals"] = json.dumps(payload, separators=(",", ":"))
    return attrs


def act(
    label: Any,
    name: str,
    *,
    variant: str = "default",
    size: str = "md",
    className: str = "",
    silent: bool = False,
    **args: Any,
) -> Button:
    return Button(
        label,
        variant=variant,
        size=size,
        className=className,
        **wire(name, silent=silent, **args),
    )
