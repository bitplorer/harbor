# Harbor × ux-behavior pilot

Parallel author seat for **Cart** only. Live storefront stays on **ux-app**.

## Enable

```bash
pip install "ux-behavior @ git+https://github.com/bitplorer/ux-behavior.git"
# optional live wire
pip install "ux-channel @ git+https://github.com/bitplorer/ux-channel.git#subdirectory=python"
```

```python
from app.pilot import build_behavior_app
from ux_behavior.local import LocalRuntime

app = build_behavior_app()
rt = LocalRuntime.bind(app)
ops = rt.call("cart", "add", id="linen-scarf", qty="1")
```

## Mapping

| bag.Cart (ux-app) | pilot BehaviorCart |
|-------------------|--------------------|
| `finish(open_overlay("sheet", key="cart"), message=…)` | `open("sheet", key="cart")` + `notify(…)` |
| `go("cart")` | `go("/cart")` |
| `Session` promo | instance `self.promo` |
| shared `app.store` | same |

## Not switched yet

- `app/host.py` still `App.boot` from ux-app
- Screens, chrome, HTMX `act`/`wire` still ux-app
- Full cutover needs Host control/mint path on Behavior

## Next pilot steps

1. In-process tests against `BehaviorCart` + `store`
2. Optional `HARBOR_BEHAVIOR_PILOT=1` dual register (later)
3. Port Chrome close/menu after Cart is stable
