"""Session cart, wishlist, orders, and account."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import Any

from app.catalog import PRODUCTS, get

PROMO = {"HARBOR10": 10, "COAST20": 20}
PAGE_SIZE = 6


def _fresh() -> dict[str, Any]:
    return {
        "page": "home",
        "product_id": "",
        "category": "all",
        "query": "",
        "sort": "featured",
        "size": "",
        "cart": [],
        "wish": [],
        "promo": "",
        "ship": "standard",
        "notice": None,
        "menu_open": False,
        "command_q": "",
        "pdp_tab": "story",
        "slide": 0,
        "page_n": 1,
        "price_max": 10000,
        "gift": False,
        "deliver": "",
        "account": {
            "signed_in": False,
            "name": "Shivam Agarwal",
            "email": "shivam@harbor.test",
            "phone": "9794 000 112",
            "address": "Civil Lines",
            "city": "Gorakhpur",
            "pin": "273001",
        },
        "checkout": {
            "name": "Shivam Agarwal",
            "email": "shivam@harbor.test",
            "address": "Civil Lines",
            "city": "Gorakhpur",
            "pin": "273001",
            "pay": "upi",
        },
        "orders": [],
        "last_order": "",
        "order_id": "",
    }


HOST: dict[str, Any] = _fresh()


def reset() -> None:
    HOST.clear()
    HOST.update(_fresh())


def flash(text: str, *, level: str = "success") -> None:
    HOST["notice"] = {"text": text, "level": level}


def clear_notice() -> None:
    HOST["notice"] = None


def close_menu() -> None:
    HOST["menu_open"] = False


def inr(n: int) -> str:
    return f"₹{int(n):,}"


def listing() -> list[dict[str, Any]]:
    rows = list(PRODUCTS)
    cat = HOST.get("category") or "all"
    q = (HOST.get("query") or "").strip().lower()
    cap = int(HOST.get("price_max") or 10000)
    if cat != "all":
        rows = [p for p in rows if p["category"] == cat]
    if q:
        rows = [
            p
            for p in rows
            if q in p["name"].lower() or q in p["blurb"].lower() or q in p["category"]
        ]
    rows = [p for p in rows if int(p["price"]) <= cap]
    sort = HOST.get("sort") or "featured"
    if sort == "price_asc":
        rows.sort(key=lambda p: p["price"])
    elif sort == "price_desc":
        rows.sort(key=lambda p: -p["price"])
    elif sort == "new":
        rows.sort(key=lambda p: (not p.get("new"), p["name"]))
    else:
        rows.sort(key=lambda p: (not p.get("featured"), p["name"]))
    return rows


def page_rows() -> tuple[list[dict[str, Any]], int, int]:
    rows = listing()
    total = max(1, (len(rows) + PAGE_SIZE - 1) // PAGE_SIZE) if rows else 1
    n = max(1, min(int(HOST.get("page_n") or 1), total))
    start = (n - 1) * PAGE_SIZE
    return rows[start : start + PAGE_SIZE], n, total


def cart_lines() -> list[dict[str, Any]]:
    lines = []
    for row in HOST.get("cart") or []:
        p = get(row["id"])
        if not p:
            continue
        qty = max(1, int(row.get("qty") or 1))
        lines.append(
            {
                "id": p["id"],
                "name": p["name"],
                "img": p["img"],
                "price": p["price"],
                "qty": qty,
                "size": row.get("size") or "",
                "line": p["price"] * qty,
                "stock": p["stock"],
            }
        )
    return lines


def cart_count() -> int:
    return sum(int(r.get("qty") or 0) for r in HOST.get("cart") or [])


def subtotal() -> int:
    return sum(r["line"] for r in cart_lines())


def discount() -> int:
    rate = PROMO.get((HOST.get("promo") or "").upper(), 0)
    return int(subtotal() * rate / 100)


def shipping() -> int:
    sub = subtotal() - discount()
    if sub <= 0:
        return 0
    if sub >= 8000:
        return 0
    return 180 if HOST.get("ship") == "express" else 80


def tax() -> int:
    return int((subtotal() - discount()) * 0.05)


def gift_fee() -> int:
    return 180 if HOST.get("gift") else 0


def total() -> int:
    return max(0, subtotal() - discount() + shipping() + tax() + gift_fee())


def add_cart(pid: str, *, qty: int = 1, size: str = "") -> str:
    p = get(pid)
    if not p:
        return "That piece is gone."
    if p["stock"] <= 0:
        return f"{p['name']} is waiting on the next run."
    qty = max(1, min(qty, p["stock"]))
    cart = list(HOST.get("cart") or [])
    for row in cart:
        if row["id"] == pid and (row.get("size") or "") == size:
            row["qty"] = min(p["stock"], int(row["qty"]) + qty)
            HOST["cart"] = cart
            return f"Updated {p['name']}"
    cart.append({"id": pid, "qty": qty, "size": size})
    HOST["cart"] = cart
    return f"Added {p['name']}"


def set_qty(pid: str, qty: int, size: str = "") -> None:
    cart = []
    for row in HOST.get("cart") or []:
        if row["id"] == pid and (row.get("size") or "") == size:
            if qty <= 0:
                continue
            p = get(pid)
            cap = p["stock"] if p else qty
            row = dict(row)
            row["qty"] = max(1, min(int(qty), cap))
        cart.append(row)
    HOST["cart"] = cart


def remove_cart(pid: str, size: str = "") -> None:
    HOST["cart"] = [
        r
        for r in (HOST.get("cart") or [])
        if not (r["id"] == pid and (r.get("size") or "") == size)
    ]


def toggle_wish(pid: str) -> bool:
    wish = list(HOST.get("wish") or [])
    if pid in wish:
        wish.remove(pid)
        HOST["wish"] = wish
        return False
    wish.append(pid)
    HOST["wish"] = wish
    return True


def wished(pid: str) -> bool:
    return pid in (HOST.get("wish") or [])


def place_order() -> dict[str, Any] | None:
    lines = cart_lines()
    if not lines:
        return None
    n = len(HOST.get("orders") or []) + 1
    oid = f"HC-240{n:02d}"
    draft = dict(HOST.get("checkout") or {})
    order = {
        "id": oid,
        "at": datetime.now().strftime("%d %b · %H:%M"),
        "status": "Packed",
        "progress": 35,
        "lines": deepcopy(lines),
        "total": total(),
        "ship": HOST.get("ship") or "standard",
        "pay": draft.get("pay") or "upi",
        "gift": bool(HOST.get("gift")),
        "deliver": HOST.get("deliver") or "",
        "address": f"{draft.get('address')}, {draft.get('city')} {draft.get('pin')}",
        "name": draft.get("name") or HOST["account"]["name"],
    }
    orders = list(HOST.get("orders") or [])
    orders.insert(0, order)
    HOST["orders"] = orders
    HOST["last_order"] = oid
    HOST["order_id"] = oid
    HOST["cart"] = []
    HOST["promo"] = ""
    HOST["gift"] = False
    return order
