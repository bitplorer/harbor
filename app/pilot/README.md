# Harbor × ux-behavior pilot (depth)

Parallel author seat for **Cart** + **Chrome** close/menu. Live storefront stays on **ux-app**.

## Install (CI / dev)

```bash
pip install -e ".[dev]"   # includes ux-behavior
# or
pip install -e ".[behavior]"
```

## Dual-boot flag

```bash
export HARBOR_BEHAVIOR_PILOT=1
# then import app.host — sets app.host.behavior_host when available
```

Default is **off**. ux-app `host` is never replaced.

## In-process

```python
from app.pilot import build_behavior_app
from ux_behavior.local import LocalRuntime

app = build_behavior_app()
rt = LocalRuntime.bind(app)
rt.call("cart", "add", id="…", qty="1")
rt.call("chrome", "close_ui")
```

## Mapping

| ux-app | ux-behavior pilot |
|--------|-------------------|
| `finish(open_overlay("sheet"), message=…)` | `open("sheet", key="cart")` + `notify` |
| `close_overlay()` | `close()` |
| `select_region("page:shop", page)` | `select("page:shop", page)` |
| `Session` fields | instance attrs + dirty projection |

## Tests

```bash
pytest tests/test_behavior_pilot.py -q
```
