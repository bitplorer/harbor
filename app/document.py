"""Two-stage Document — order is deliberate (see HtmlDocument.render).

Stage A (this module): Document(head=…, body=…).use(…)
  → common_head / common_body (after page head / end of body)

Stage B (page()): doc(*content, head=…, body=…)
  → call-time head first in <head>, call-time body early in <body>

    <head>  [B page title/css]  then  [A shared + XElement]
    <body>  content  [B]  placeholders  [A HTMX last]
"""
from __future__ import annotations

from ux_dom import Document
from ux_dom.dom import link, meta, title
from ux_dom.runtime import Channel, Csp, Htmx, XElement

from app import settings

# Stage A — shared chrome + runtimes (common_head / common_body)
# Order: UI runtimes first, then CSP last among shell plugins so middleware
# wraps the app after other mounts (Csp only adds middleware — no head tags).
document = Document(
    head=[
        meta(charset="utf-8"),
        meta(name="viewport", content="width=device-width, initial-scale=1, viewport-fit=cover"),
    ],
    body=[],  # end-of-body scripts come from Htmx().document_body()
    ensure_csrf_token=False,
    webassets=settings.webassets if settings.WITH_TAILWIND else None,
).use(
    XElement(),  # → common_head (after page title)
    Htmx(middleware=True, version="2.0.4"),  # → common_body (after content)
)

if settings.WITH_CHANNEL:
    _ch = Channel.optional(mount_via_ux_dom=False)
    if _ch is not None:
        document.use(_ch)  # → common_head

# CSP — zero-choice default: Csp.auto() follows settings.DEBUG
#   DEBUG=True  → Csp.dev()  (CDN scripts + style="..." OK)
#   DEBUG=False → Csp.prod() (no CDN hosts, tighter policy)
if settings.WITH_CSP:
    document.use(
        Csp.auto(
            debug=settings.DEBUG,
            report_only=True,
            font_src=["'self'", "data:", "https://fonts.gstatic.com"],
            style_hosts=["https://fonts.googleapis.com"],
        )
    )


def page(*content, page_title: str | None = None):
    """Stage B — page content + call-time head (title, optional CSS)."""
    from app.components.chrome import WaitChrome

    call_head = [
        title(page_title or settings.APP_TITLE),
        link(rel="preconnect", href="https://fonts.googleapis.com"),
        link(rel="preconnect", href="https://fonts.gstatic.com", crossorigin=True),
        link(
            rel="stylesheet",
            href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500&family=Sora:wght@400;500;600&display=swap",
        ),
    ]
    if settings.WITH_TAILWIND:
        call_head.append(link(href=f"/css/{settings.OUTPUT_CSS}", rel="stylesheet"))
    # Wait chrome lives outside #app so it persists across HTMX morphs.
    return document(WaitChrome(), *content, head=call_head)
