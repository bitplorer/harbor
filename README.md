# Harbor & Co.

Coastal goods shop on **ux-dom** + **ux-app**. Python HTML only — no React.

One `Component` per screen: Session fields, actions, and `render()` live together. Product truth (cart, stock, orders, prices) stays in a pure store. Chrome (page, sheet, find, toasts) stays on Session. Product modules never import `ux_channel`.

## Stack

| Package | Role |
|---|---|
| [ux-dom](https://github.com/bitplorer/ux-dom) | Document, DirectoryRouter, Tailwind, UI kit |
| [ux-app](https://github.com/bitplorer/ux-app) | `App.boot` / `add` / `region` / `attach` / `control`, Component Session |
| [ux-channel](https://github.com/bitplorer/ux-channel) | Optional live wire. HTMX `POST /act/{name}` is the fallback |

```python
from ux_app import App, Component, Session

class Cart(Component):
    id = "cart"
    promo: str = Session("")          # chrome — not money

    def add(self, ctx, id: str = "", qty: str = "1"):
        msg = store.add_cart(id, qty=int(qty or 1), size=product.size)
        return finish(open_overlay("sheet", key="cart"), message=msg)

    def render(self):
        return self.panel(page=True)
```

`host.control(cart.add, id=sku)` — callables, never `"cart.add"`.

## Layout

```
catalog → store → wiring/ui → screens/chrome → host → main
```

```
app/
  domain/catalog.py   # 12 SKUs, categories, related
  store.py            # cart, wish, orders, money — no Component imports
  wiring.py           # act, wire, finish, go  (App.control)
  ui.py               # product_card, section, money_rows
  chrome.py           # topbar, dock, find, toasts, overlay
  shell.py            # #app morph target + storefront()
  screens/*.py        # Home Shop Product Cart Checkout Confirm Orders Wish Account
  host.py             # App.boot, add, region
  document.py         # Document.use(XElement, Htmx, Channel.optional, Csp)
  main.py             # FastAPI + /act + DirectoryRouter
  routes/             # thin GET pages → show(key, title)
assets/css/input.css  # Fraunces + Sora, --ink / --paper / --line
assets/img/           # product photography
tests/                # planes, callables, money, isolation
```

## Quick start

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[channel]"
cp .env.example .env
uxdom serve          # Tailwind --watch + app on :8080
# or: uvicorn app.main:app --host 0.0.0.0 --port 8080
```

Cores from git (when not on PyPI yet):

```bash
pip install "ux-dom @ git+https://github.com/bitplorer/ux-dom.git"
pip install "ux-app @ git+https://github.com/bitplorer/ux-app.git"
pip install "ux-channel @ git+https://github.com/bitplorer/ux-channel.git#subdirectory=python"
```

```bash
pytest
```

## Try

- Walk the floor, filter, sort, paginate
- Open a piece — size, tabs, reviews, size guide, related
- Save it. Add to bag. Apply `HARBOR10` or `COAST20`
- Checkout — address, ship, date, UPI, gift wrap
- First order is `HC-24001`
- Find palette. Account. Reset the floor
