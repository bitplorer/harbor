# Harbor & Co. — S-tier takeover brief

You are a principal design-systems engineer sitting with a principal
Python architect. You inherit **Harbor & Co.**, a working coastal-goods
shop. Almost every feature already exists. The code is messy. You do
not start over. You do not add a second stack. You do not invent APIs
the cores already own.

This brief is the contract. Read the cores, then execute it.

---

## 0. What we actually found (do not rediscover)

Three GitHub trees were read end-to-end before this brief was written.

### [bitplorer/ux-dom](https://github.com/bitplorer/ux-dom) — the DOM

- `Document(head, body).use(XElement, Htmx, Channel.optional, Csp.auto)`
  is a **two-stage** shell: Stage A = shared head/body + runtimes;
  Stage B = `document(*content, head=…)` per page. Order is law
  (`docs/guides/DOCUMENT_TWO_STAGE.md`).
- Tags: `from ux_dom.dom import div, button, form, img, …`
- Kit: `from ux_dom.ui import Button, Card, Sheet, Dialog, Tabs, …`
- Tokens: `surface` (L0 page → L3 popover), `type_scale`, `cn`, `ink`.
- HTMX 2 is the fallback transport. `#app` is the morph target.
- **Wait chrome lives outside `#app`** so morphs never tear it down.
- `DirectoryRouter` / `DirectoryRouting` discovers `Component.routes`
  from `app/routes/*.py`. Thin `show(key, title)` is the whole page GET.
- `Channel.optional()` returns `None` when `ux-channel` is absent —
  the shop must still run.
- Tailwind `@source` scans `app/**/*.py`. CSS is a first-class asset,
  not an afterthought.

### [bitplorer/ux-app](https://github.com/bitplorer/ux-app) — the author layer

Verified against `ARCHITECTURE.md`, `src/ux_app/app.py`, `component.py`:

```python
from ux_app import App, Component, Session
from ux_app.overlay import open_overlay, close_overlay, select_region

class Cart(Component):
    id = "cart"
    promo: str = Session("")          # chrome — not money

    def add(self, ctx, id: str = "", qty: str = "1"):
        msg = ledger.add_cart(id, qty=int(qty or 1), size=product.size)
        return finish(open_overlay("sheet", key="cart"), message=msg)

    def render(self):
        return self.panel(page=True)
```

- Dataclass fields default to the **session** plane, keyed `{id}.{field}`.
  A dirty Session field becomes `update("{id}")` → `ui.dom.morph`.
- Actions return `list[Op]`. `caps=()` is the public opt-out.
- Boot sequence is rigid:
  `App.boot(title, strict=False)` → `host.add(Component)` →
  `host.require_composite("dialog","sheet","command")` →
  `host.region(storefront)` → `host.attach(asgi)`.
- `App.control(cart.add, id=sku)` mints signed attrs. Product style is
  a **callable**, never `"cart.add"`.
- HTMX `POST /act/{name}` is the no-channel fallback. Channel attach
  is a no-op when the package is missing.
- Overlays: `open_overlay("sheet"|"dialog"|"command", key=…)`.
  Carousel / tabs: `select_region("carousel:hero", "1")`.
- Isolation is mechanical: product modules **never** import
  `ux_channel` / `cek_*`. Only `ux_app/adapter/**` may. Doctor fails
  the scan if they do.
- Two clocks: Host Actions are authority; Alpine/preview is perception
  only. Alpine is last-resort, never the open path for a sheet.

### [bitplorer/harbor](https://github.com/bitplorer/harbor) — the patient

A real shop: 12 SKUs, photography, INR, UPI, Gorakhpur floor voice.
The rot is structural, not missing features.

| Smell | Where | Fix |
|---|---|---|
| God markup | `views.py` ~729 lines | Each body lives on its Component |
| Thin shells | `screens.py` `return shop_body()` | State + actions + `render()` in one class |
| UI leak | `store._shop()` / `_cart()` peeking `host.shop` | `listing(ShopQuery)` — filters are arguments |
| Import cycles | `screens` ↔ `host` ↔ `views` | catalog → store → wiring/ui → screens/chrome → host → main |
| String routes | 10 identical `routes/*.py` | Keep DirectoryRouter; share `show()` |
| Token soup | raw `stone-950` + hex in CSS | `@theme` tokens (`--ink` / `--paper` / `--line`), then utilities |
| finish() on host | `host.finish` imported by screens | `wiring.finish` — host stays a composition root |

First order id is `HC-24001`. Promos: `HARBOR10` (10%), `COAST20` (20%).
Soap trio is sold out (`stock = 0`). Overshirt has sizes S–XL.

---

## 1. Non-negotiable laws

1. **Python only.** No React, no TypeScript, no JSX, no Vite app as the
   product. Markup is `ux_dom.dom`. Styling is Tailwind tokens consumed
   by `ux_dom.ui`. Wiring and state are `ux_app`.
2. **Read the cores before you type.** Inventing a parallel Component,
   store, or overlay is a defect.
3. **Locality of behaviour.** A screen is one `ux_app.Component`:
   Session fields + action methods + `render()`. A stranger opens one
   file and understands one slot.
4. **Separation of concerns.** Product truth (cart lines, stock, orders,
   prices, wish, account) lives in `store`. UI chrome (page, slide,
   menu, notice, filters, draft) lives on Session fields. Domain code
   never imports a Component. Components never write money into Session.
5. **Callables, not strings.** `act("Add", cart.add, id=sku)`.
   Caps are minted by `App.control`.
6. **Product modules never import `ux_channel` or `cek_*`.** Channel is
   reached through `App.attach` / `App.control` / `open_overlay` /
   `select_region`. Isolation is a doctor check, not a comment.
7. **Channel-first overlays.** Dialog / Sheet / Command / Tabs / Carousel
   open-state comes from session cells set by Host Ops.
8. **Keep every feature.** Losing a path is a regression. See §3.
9. **Do not hide coupling behind globals.** `store.listing(ShopQuery)`.
   Shipping / promo / gift are arguments, not Component peeks.
10. **Screens may lazy-import `host` inside methods** to reach a sibling
    (`chrome.page = "shop"`). Never at module top.

---

## 2. Architecture you will leave behind

```
app/
  domain/catalog.py     # PRODUCTS, CATEGORIES, get, related
  store.py              # cart, wish, orders, account, money  (pure)
  wiring.py             # act, wire, hx, finish, go
  ui.py                 # product_card, section, shared atoms
  chrome.py             # Chrome: topbar, menu, find, toasts, overlay
  shell.py              # Shell + storefront()
  screens/*.py          # one Component per slot
  host.py               # App.boot, add, region  (composition root)
  document.py           # Document.use
  main.py               # FastAPI + /act + DirectoryRouter
  components/chrome.py  # WaitChrome — outside #app
  routes/_show.py       # show(key, title) → page(storefront(page=key))
  routes/*.py           # thin DirectoryRouter pages
```

Dependency direction is one-way:

```
catalog → store → wiring/ui → screens/chrome → host → main
```

No arrows backwards.

---

## 3. Feature inventory (regression gate)

A guest can walk this path without a missing verb:

| Path | Must still do |
|---|---|
| Home | Editorial hero, carousel (image + title share product id), category tiles, floor tempo, featured + just-in |
| Shop | Search, category chips, sort (featured/new/price), price slider, paginate, empty state |
| PDP | Photo, price, stock, size (overshirt), tabs (story/notes/care), reviews, size guide dialog, related, sold-out alert (soap), save, add to bag |
| Find | Command palette, live filter, open a piece |
| Bag | Sheet + full page, qty +/–, remove, promo `HARBOR10` / `COAST20`, money rows |
| Checkout | Address, ship standard/express, date, UPI/card/COD, gift wrap ₹180, free ship ≥ ₹8,000 |
| Confirm | Order id, total, progress, track |
| Orders | Book table, detail timeline (Packed → road → door), `HC-24001` on first place |
| Wish | Toggle from PDP, grid, empty state |
| Account | Sign in / out, default Gorakhpur address, reset store |
| Chrome | Sticky topbar + safe-area, clerk menu, toasts that dismiss, wait veil outside `#app` |

---

## 4. Design bar

Harbor is a coastal goods house, not a SaaS dashboard.

- Display: **Fraunces**. Body: **Sora**. Two families, no more.
- Surfaces: near-black stone. Tokens: `--ink` / `--paper` / `--line` /
  `--bg` / `--fg` / `--fg-muted` / `--fg-subtle`. One restrained accent
  — warm linen on dark. Never purple. Never gold fill. Never Inter.
- Photography is the luxury. Type sits on the image. Cards do not
  compete with the photo. Hairline inset outline on product photos.
- Concentric radii. 44px targets (`min-h-11`). Safe-area on the sticky
  topbar and the mobile dock.
- Motion: 150–250ms, `--ease-harbor`, opacity + transform only.
  `prefers-reduced-motion` kills it.
- Empty / sold-out / error / pending states are designed, not leftover.
- Mobile ~390px first. No horizontal overflow. **Shop / Saved / Bag /
  Find stay reachable** (topbar + a mobile dock — Shop is not
  `hidden sm:inline-flex` with no replacement).
- No emoji. No gradient blobs. No lorem. Floor voice stays (Gorakhpur,
  linen, clay, oak, waxed canvas).

---

## 5. Execution order

1. Inventory every user-visible path. That list is the regression gate.
2. Extract a pure `store` (no Component imports). Green the money tests.
3. Move each `*_body()` onto its Component. Delete `views.py`.
4. Point DirectoryRouter `show()` at `storefront()`. Serve `/` as the
   live session page (do not clobber `/act` morphs with a forced home).
5. Restyle the shell: editorial hero, image category tiles, quieter
   filters, honest bag sheet, order timeline, mobile dock.
6. Keep `tests/test_chrome_planes.py` honest: Session ≠ SessionVar,
   carousel image+title share an id, no stringly `act`, no `ux_channel`
   import, cart/orders stay in the store bag. Scan `screens/*.py` +
   `chrome.py` + `ui.py` (there is no `views.py`).
7. Serve on `0.0.0.0:8080`. Walk every path in a real browser.
   Screenshot desktop and 390px. Console must be clean.

---

## 6. What “done” looks like

A guest can walk the floor, filter, open a piece, pick a size, save it,
add to bag, apply `HARBOR10`, check out with gift wrap, and track
`HC-24001` — and a reader can open `screens/product.py` and see the
whole PDP without hopping through three modules. The page looks like a
shop someone would remember, not a kit demo.
