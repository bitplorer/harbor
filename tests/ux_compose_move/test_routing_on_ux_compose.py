"""F-11/F-18: Harbor routes through ux-compose, not ux-dom's DirectoryRouter.

The shop screens import ux-app (retired). These tests stub the page helper so
route discovery and the HTTP bind are exercised without it.
"""
from __future__ import annotations

import ast
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "app"

# ux-dom modules Harbor must not import (moved to ux-compose or deleted).
GONE = (
    "ux_dom.routing",
    "ux_dom.plugins.routing",
    "ux_dom.runtime",
    "ux_dom.plugins.style",
    "ux_dom.plugins.hmr",
    "ux_dom.settings.commands",
)
EXPECTED = {
    "/": "Index",
    "/account": "Account",
    "/cart": "Cart",
    "/checkout": "Checkout",
    "/confirm": "Confirm",
    "/orders": "Orders",
    "/product": "Product",
    "/shop": "Shop",
    "/wish": "Wish",
}


def _imports():
    for py in sorted(APP.rglob("*.py")):
        if "__pycache__" in py.parts:
            continue
        for node in ast.walk(ast.parse(py.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                yield py, node.lineno, node.module, [a.name for a in node.names]
            elif isinstance(node, ast.Import):
                for a in node.names:
                    yield py, node.lineno, a.name, []


def test_no_ux_dom_routing_or_removed_modules():
    hits = [
        f"{py.relative_to(ROOT)}:{line} {mod}"
        for py, line, mod, _ in _imports()
        if any(mod == g or mod.startswith(g + ".") for g in GONE)
    ]
    assert hits == []


def test_web_assets_and_tailwind_come_from_ux_compose():
    hits = [
        f"{py.relative_to(ROOT)}:{line}"
        for py, line, mod, names in _imports()
        if mod == "ux_dom" and ("WebAssets" in names or "TailwindCommand" in names)
    ]
    assert hits == []
    src = (APP / "settings.py").read_text(encoding="utf-8")
    assert "from ux_compose.assets import WebAssets" in src
    assert "from ux_compose.tailwind import" in (APP / "tailwindcss.py").read_text(encoding="utf-8")


def test_main_binds_ux_compose_directory_routes():
    src = (APP / "main.py").read_text(encoding="utf-8")
    assert "from ux_compose.routing import DirectoryRoutes" in src
    assert "from ux_compose.routing.fastapi import bind as bind_routes" in src
    assert "DirectoryRouting" not in src and "StreamingRoute" not in src


def test_route_units_have_no_http_verb_classmethods():
    for py in sorted((APP / "routes").glob("[a-z]*.py")):
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for cls in [n for n in tree.body if isinstance(n, ast.ClassDef)]:
            names = {
                n.name if isinstance(n, ast.FunctionDef) else getattr(n.targets[0], "id", "")
                for n in cls.body
                if isinstance(n, (ast.FunctionDef, ast.Assign))
            }
            assert "routes" not in names, py.name
            assert "get" not in names, py.name
            assert "render" in names, py.name


@pytest.fixture
def stub_show(monkeypatch):
    """Replace app.routes._show (pulls ux-app) with a marker page."""
    from ux_dom.dom import div

    mod = types.ModuleType("app.routes._show")
    mod.show = lambda key, title: div(f"page:{key}|{title}", id="app")
    monkeypatch.setitem(sys.modules, "app.routes._show", mod)
    for name in list(sys.modules):
        if name.startswith("app.routes.") and name != "app.routes._show":
            monkeypatch.delitem(sys.modules, name, raising=False)
    monkeypatch.syspath_prepend(str(ROOT))
    return mod


def test_directory_routes_discovers_every_page(stub_show):
    from ux_compose.routing import DirectoryRoutes

    core = DirectoryRoutes(package_dir=APP, base_directory="routes")
    core.discover()
    table = {r["path"]: r["name"] for r in core.route_table()}
    assert table == EXPECTED


def test_bound_routes_serve_full_page(stub_show):
    fastapi = pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient
    from ux_compose.routing import DirectoryRoutes
    from ux_compose.routing.fastapi import bind

    app = fastapi.FastAPI()
    bind(app, DirectoryRoutes(package_dir=APP, base_directory="routes"), document=None)
    client = TestClient(app)
    home = client.get("/")
    assert home.status_code == 200
    assert "page:home|Harbor &amp; Co." in home.text
    shop = client.get("/shop")
    assert shop.status_code == 200 and "page:shop|" in shop.text
    # Old ux-dom DirectoryRouter URLs (class name in path) are gone.
    assert client.get("/shop/Shop").status_code == 404
