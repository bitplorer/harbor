"""Controls via App.control (callables). HTMX is the fallback."""
from __future__ import annotations

import json
from typing import Any, Callable

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


def action_name(fn: Any) -> str:
    if isinstance(fn, str):
        return fn
    existing = getattr(fn, "__ux_action__", None)
    if existing is not None and getattr(existing, "name", None):
        return str(existing.name)
    owner = getattr(fn, "__self__", None)
    ident = getattr(owner, "id", None) if owner is not None else None
    if ident:
        return f"{ident}.{getattr(fn, '__name__', 'action')}"
    return getattr(fn, "__name__", "action")


def wire(fn: Callable[..., Any] | str, *, silent: bool = False, **args: Any) -> dict[str, Any]:
    """Prefer App.control(callable) after attach(); else mint + HTMX POST /act."""
    from app.host import host

    try:
        bound = host.control(fn, **args)
    except Exception:
        bound = None
    name = None
    if bound:
        name = bound.get("data_action") or bound.get("data-action")
    if not name:
        name = action_name(fn)
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
    fn: Callable[..., Any] | str,
    *,
    variant: str = "default",
    size: str = "md",
    className: str = "",
    silent: bool = False,
    **args: Any,
) -> Button:
    from ux_dom.ui import Button

    return Button(
        label,
        variant=variant,
        size=size,
        className=className,
        **wire(fn, silent=silent, **args),
    )
