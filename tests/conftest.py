from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _reset_harbor():
    from app import store
    from app.host import cart, checkout, chrome, home, host, orders, product, shop

    store.reset()
    home.slide = 0
    chrome.page = "home"
    chrome.menu_open = False
    chrome.notice = None
    chrome.command_q = ""
    shop._reset_filters()
    product._reset_view()
    checkout._reset_draft()
    cart.promo = ""
    orders.order_id = ""
    host.world.kv.clear()
    yield
