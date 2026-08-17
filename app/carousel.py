"""Hero carousel — image and title share one product id."""
from __future__ import annotations

from typing import Any

from app.catalog import PRODUCTS


def featured_rows() -> list[dict[str, Any]]:
    rows = [p for p in PRODUCTS if p.get("featured")]
    return rows or list(PRODUCTS)


def hero_at(slide: int) -> dict[str, Any]:
    rows = featured_rows()
    idx = int(slide or 0) % max(1, len(rows))
    hero = rows[idx]
    return {
        "idx": idx,
        "count": len(rows),
        "hero": hero,
        "card_id": f"hero-card-{hero['id']}",
        "photo_id": f"hero-photo-{hero['id']}",
    }
