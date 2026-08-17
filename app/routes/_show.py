"""Shared GET helper for DirectoryRouter pages."""
from __future__ import annotations

from app.document import page
from app.shell import storefront


def show(key: str, title: str):
    return page(storefront(page=key), page_title=title)
