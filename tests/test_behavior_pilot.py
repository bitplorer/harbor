"""Optional ux-behavior Cart pilot — skips if package missing."""

from __future__ import annotations

import pytest

pytest.importorskip("ux_behavior")

from app import store
from app.pilot import build_behavior_app
from ux_behavior.local import LocalRuntime


@pytest.fixture(autouse=True)
def _reset_store():
    store.reset()
    yield
    store.reset()


def test_behavior_cart_add():
    app = build_behavior_app()
    rt = LocalRuntime.bind(app)
    # use a known catalog id if present
    from app.catalog import PRODUCTS

    pid = PRODUCTS[0]["id"]
    ops = rt.call("cart", "add", id=pid, qty="1")
    assert store.cart_count() >= 1
    assert any(getattr(o, "pair", None) == ("log", "append") for o in ops)


def test_behavior_cart_promo():
    app = build_behavior_app()
    rt = LocalRuntime.bind(app)
    ops = rt.call("cart", "promo_apply", code="HARBOR10")
    assert app.get("cart").promo == "HARBOR10"
    assert ops
