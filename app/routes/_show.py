"""Shared GET helper for DirectoryRouter pages."""
from __future__ import annotations

from app.document import page
from app.views import storefront


def show(key: str, title: str):
    # File routes render by URL. Session page is only for /act morphs so a
    # preview poll on GET / cannot clobber an in-flight shop session.
    return page(storefront(page=key), page_title=title)
