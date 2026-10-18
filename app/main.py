"""
ASGI entry — FastAPI is the process; Document owns the DOM.

    uvicorn app.main:app --host 0.0.0.0 --port 8080

Assembly::

    app = FastAPI(...)
    document.mount(app)
    bind_routes(app, DirectoryRoutes(package_dir=PACKAGE, base_directory="routes"))

Page routes are ux-compose ``DirectoryRoutes`` (F-11/F-18): the URL is the
file path under ``app/routes/`` and the class name is never in the URL.
CSS is compiled by the Tailwind CLI that ux-compose resolves
(``python -m app.tailwindcss``). Browser HMR is ``uxcompose serve dev``.
"""
from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from ux_compose.routing import DirectoryRoutes
from ux_compose.routing.fastapi import bind as bind_routes

from app import settings
from app.document import document, page
from app.host import host
from app.shell import storefront

PACKAGE = Path(__file__).resolve().parent


async def _compile_css_once() -> None:
    """Best effort: compile CSS at boot if a Tailwind CLI is already available."""
    from app.tailwindcss import compile_argv

    argv = compile_argv(ensure=False)
    if not argv:
        return
    try:
        proc = await asyncio.create_subprocess_exec(*argv, cwd=str(settings.BASE_DIR))
        await proc.wait()
    except Exception:
        pass


@asynccontextmanager
async def _lifespan(application: FastAPI):
    if settings.WITH_TAILWIND:
        await _compile_css_once()
    yield


app = FastAPI(title=settings.APP_TITLE, debug=settings.DEBUG, lifespan=_lifespan)

document.mount(app)

routes = DirectoryRoutes(package_dir=PACKAGE, base_directory="routes")
# Route units return the full page (document + call-time head), so no wrap.
bind_routes(app, routes, document=None)

settings.webassets.mount_css(app)

if settings.ASSETS_DIR.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=str(settings.ASSETS_DIR), check_dir=False),
        name="assets",
    )

if settings.WITH_CHANNEL:
    host.attach(app)


@app.head("/")
def _root_head():
    # GET / is the routes/index.py unit (DirectoryRoutes). HEAD is a cheap probe.
    return Response(status_code=200, media_type="text/html")


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
    tree = page(storefront(), page_title=settings.APP_TITLE)
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
        reload=False,
    )


if __name__ == "__main__":
    run()
