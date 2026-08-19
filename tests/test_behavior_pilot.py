"""ux-behavior Cart + Chrome pilot (required under .[dev])."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("ux_behavior")

from app import store
from app.catalog import PRODUCTS
from app.pilot import build_behavior_app, pilot_enabled, register_pilot
from ux_behavior.local import LocalRuntime


@pytest.fixture(autouse=True)
def _reset_store():
    store.reset()
    yield
    store.reset()


def test_behavior_cart_add():
    app = build_behavior_app()
    rt = LocalRuntime.bind(app)
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


def test_behavior_chrome_close_ui():
    app = build_behavior_app()
    rt = LocalRuntime.bind(app)
    app.get("chrome").menu_open = True
    ops = rt.call("chrome", "close_ui")
    assert app.get("chrome").menu_open is False
    assert any(getattr(o, "pair", None) == ("kv", "set") for o in ops)


def test_behavior_chrome_toggle_dirty():
    app = build_behavior_app()
    rt = LocalRuntime.bind(app)
    ops = rt.call("chrome", "toggle")
    assert app.get("chrome").menu_open is True
    # dirty projection → refresh morph
    assert any(getattr(o, "pair", None) == ("ui.dom", "morph") for o in ops)


def test_register_pilot_flag(monkeypatch):
    monkeypatch.delenv("HARBOR_BEHAVIOR_PILOT", raising=False)
    assert pilot_enabled() is False
    assert register_pilot() is None
    monkeypatch.setenv("HARBOR_BEHAVIOR_PILOT", "1")
    assert pilot_enabled() is True
    root = register_pilot()
    assert root is not None
    assert "cart" in root.components()
    assert "chrome" in root.components()
