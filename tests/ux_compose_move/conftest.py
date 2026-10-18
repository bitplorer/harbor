"""These tests do not touch the shop host (ux-app), so skip its reset."""
from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _reset_harbor():
    yield
