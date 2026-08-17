from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _reset_harbor():
    from app import store
    from app.host import chrome, home, host

    store.reset()
    home.slide = 0
    chrome.reset_chrome()
    acc = store.HOST["account"]
    chrome.checkout = {
        "name": acc.get("name") or "",
        "email": acc.get("email") or "",
        "address": acc.get("address") or "",
        "city": acc.get("city") or "",
        "pin": acc.get("pin") or "",
        "pay": "upi",
    }
    host.world.kv.clear()
    yield
