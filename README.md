# Harbor & Co.

Example shop on **ux-dom** + **ux-app** + **ux-channel**.

Python HTML only — no React. ux-dom owns the Document and UI kit. ux-app is the author façade (`App.boot`, `attach`, `region`, `control`, `@action`). ux-channel owns the live wire (caps, `@ch.region`, remorph). Product code never imports `ux_channel`.

Scaffolded with `uxdom create-app` (template: `shop`).

## Stack

| Package | Role |
|---|---|
| [ux-dom](https://github.com/bitplorer/ux-dom) | Document, DirectoryRouter, Tailwind, UI kit |
| [ux-app](https://github.com/bitplorer/ux-app) | Actions, Caps, `App.attach` / `App.region`, Component Session/Client |
| [ux-channel](https://github.com/bitplorer/ux-channel) | Intent → Result, regions, morph |

```python
from ux_app import App, Component, Session

host = App.boot(title="Harbor & Co.", strict=False)
home = host.add(Home)
chrome = host.add(Chrome)
host.region(storefront)     # Channel slot app.root
host.attach(app)            # live wire, no ux_channel import
host.control(cart.add, id=sku)   # callable, not "cart.add"

class Home(Component):
    id = "home"
    slide: int = Session(0)   # value, not a SessionVar

    def next(self, ctx):
        self.slide = int(self.slide or 0) + 1

    def render(self):
        ...

class Chrome(Component):
    id = "chrome"
    menu_open: bool = Session(False)

    def render(self):
        return topbar(...)
```

UI chrome lives on Component Session fields (`Home.slide`, `Chrome.page` / `menu_open` / `notice`, shop filters, PDP tabs, checkout draft). Cart lines, orders, wish, stock, and prices stay in the product store. `act` / `wire` take bound methods.

## Quick start

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[channel]"
cp .env.example .env
uxdom serve          # Tailwind --watch + app on :8080
# or: uxdom dev      # same, with reload
#     uxdom start    # prod
```

`uxdom serve` loads `.env` / `.env.local` / `.env.development` (process env wins).

Editable cores from git (when not on PyPI yet):

```bash
pip install "ux-dom @ git+https://github.com/bitplorer/ux-dom.git"
pip install "ux-app @ git+https://github.com/bitplorer/ux-app.git"
pip install "ux-channel @ git+https://github.com/bitplorer/ux-channel.git#subdirectory=python"
```

## Layout

```
app/
  main.py           # FastAPI + document.mount + DirectoryRouter + /act
  document.py       # Document.use(XElement, Htmx, Channel, Csp)
  settings.py       # WebAssets + feature flags
  host.py           # App.boot, host.add(screens), host.region, finish
  screens.py        # Home/Chrome/Shop/Cart/… methods + render()
  carousel.py       # hero card/photo ids keyed by product
  hx.py             # App.control(callable) → Channel attrs (HTMX fallback)
  views.py          # storefront markup (ux-dom UI kit)
  components/       # Shell + WaitChrome
  routes/           # file routes: Index, Shop, Cart, …
assets/css/         # Tailwind input
assets/img/         # product photography
.env.example        # DEBUG + UX_CHANNEL_SECRET
```

## Try

- Walk the floor, filter, paginate
- Open a piece — tabs, size guide, save
- Add to bag — sheet + toast
- Find — command palette
- Checkout — address, date, gift wrap, place an order
