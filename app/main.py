"""
ASGI entry — FastAPI is the process; Document owns the DOM.

    uxdom serve --port 8080
    # or: uxdom dev   ·   uxdom start

Assembly (no hidden builder)::

    app = FastAPI(...)
    document.mount(app)          # runtimes → static + middleware
    DirectoryRouter(...).include(app)
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from app import settings
from app.document import document, page
from app.host import host
from app.views import storefront

PACKAGE = Path(__file__).resolve().parent

# Optional style / HMR lifecycle (kept local — not another framework)
# When `uxdom serve` is running it sets UXDOM_TAILWIND_OWNED=1 and TailwindStyle
# becomes a no-op so the standalone CLI is the single CSS watcher.
_styles: list = []
_hmr: list = []

if settings.WITH_TAILWIND:
    from ux_dom.plugins.style import TailwindStyle

    _styles.append(
        TailwindStyle(
            settings.webassets,
            file_path=PACKAGE / "main.py",
            input_css=settings.INPUT_CSS,
            output_css=settings.OUTPUT_CSS,
            minify=not settings.DEBUG,
        )
    )

if settings.WITH_HMR and settings.DEBUG:
    try:
        from ux_dom.plugins.hmr import HotReload

        _hmr.append(
            HotReload(
                watch_paths=[str(PACKAGE), str(settings.BASE_DIR / "assets")],
            )
        )
    except Exception:
        pass


@asynccontextmanager
async def _lifespan(application: FastAPI):
    for style in _styles:
        try:
            await style.build(watch=settings.DEBUG)
        except Exception:
            pass
    for hmr in _hmr:
        startup = getattr(hmr, "startup", None)
        if startup is not None:
            await startup()
    yield
    for hmr in _hmr:
        shutdown = getattr(hmr, "shutdown", None)
        if shutdown is not None:
            try:
                await shutdown()
            except Exception:
                pass
    for style in _styles:
        stop = getattr(style, "stop", None)
        if stop is not None:
            await stop()


app = FastAPI(title=settings.APP_TITLE, debug=settings.DEBUG, lifespan=_lifespan)

try:
    from ux_dom.routing.fastapi import StreamingRoute

    app.router.route_class = StreamingRoute
except Exception:
    pass

# Document is SSoT — mounts runtime static (x_element.js) + middleware (CSP, HTMX, …)
document.mount(app)

# File-based routes (DirectoryRouter)
from ux_dom.plugins.routing import DirectoryRouting

DirectoryRouting(package_dir=PACKAGE, base_directory="routes").include(app)

# Compiled Tailwind + app images live under WebAssets / assets/
css_dir = Path(settings.webassets.static.css)
css_dir.mkdir(parents=True, exist_ok=True)
app.mount("/css", StaticFiles(directory=str(css_dir), check_dir=False), name="css")

if settings.ASSETS_DIR.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(settings.ASSETS_DIR), check_dir=False),
        name="assets",
    )

for hmr in _hmr:
    route = hmr.asgi_route() if hasattr(hmr, "asgi_route") else None
    if route is not None:
        path, endpoint = route
        name = getattr(hmr, "url_name", getattr(hmr, "name", "hmr"))
        if hasattr(app, "add_api_websocket_route"):
            app.add_api_websocket_route(path, endpoint, name=name)
        elif hasattr(app, "add_websocket_route"):
            app.add_websocket_route(path, endpoint, name=name)

if settings.WITH_CHANNEL:
    host.attach(app)


@app.api_route("/", methods=["GET", "HEAD"])
def _root(request: Request):
    # StreamingRoute does not auto-add HEAD; probes need a 200 on HEAD /
    if request.method == "HEAD":
        return Response(status_code=200, media_type="text/html")
    return RedirectResponse("/index/Index")


@app.post("/act/{name:path}")
async def act_route(name: str, request: Request):
    """HTMX transport for ux-app Actions. Morph target is #app."""
    from ux_dom.response.starlette import HTMLResponse

    args: dict = {}
    ctype = request.headers.get("content-type", "")
    if "application/json" in ctype:
        body = await request.json()
        if isinstance(body, dict):
            args.update(body)
    else:
        form = await request.form()
        for key, value in form.multi_items():
            args[str(key)] = str(value)
    cap = args.pop("__cap", None) or request.headers.get("x-cap")
    result = host.submit(name, args, cap=cap)
    title = settings.APP_TITLE
    tree = page(storefront(), page_title=title)
    if not result.ok and result.kind == "dispatch_error":
        return HTMLResponse(tree, status_code=400)
    return HTMLResponse(tree)


@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return JSONResponse(
        {
            "ok": True,
            "app": settings.APP_TITLE,
            "debug": settings.DEBUG,
            "tailwind": settings.WITH_TAILWIND,
            "channel": settings.WITH_CHANNEL,
            "csp": settings.WITH_CSP,
            "runtimes": [getattr(r, "name", type(r).__name__) for r in document.runtimes()],
        }
    )


def run() -> None:
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.DEBUG,
    )


if __name__ == "__main__":
    run()
