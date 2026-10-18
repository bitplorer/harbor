# Harbor & Co. — retired example

This repository is a **frozen teaching shop** built on retired [ux-app](https://github.com/bitplorer/ux-app). It is **not** a product template and not a library dependency.

**Greenfield shop / app path:** [ux-compose](https://github.com/bitplorer/ux-compose)

```bash
uxcompose create-app myapp --level 1
uxcompose serve dev
```

Compose already carries the teaching surface:

- `examples/` — Component / MorphState / overlays / forms
- `apps/atelier_shop` — shop Components on the product seat
- `apps/nook`, `apps/pulse` — product-shaped apps

Do not `pip install` this tree for a new product. Delete this repository from GitHub Settings → Danger Zone when you no longer want the snapshot.

## 2026-10: moved onto ux-compose routing (ux-dom F-11 / F-18)

- Page routes: `ux_compose.routing.DirectoryRoutes` + `ux_compose.routing.fastapi.bind`
  (was ux-dom's leftover `DirectoryRouter` / `DirectoryRouting` / `StreamingRoute`).
  URL = file path under `app/routes/`: `/shop`, `/product`, … (the old `/shop/Shop` form is gone).
- `WebAssets` → `ux_compose.assets`; Tailwind CLI → `ux_compose.tailwind` (`python -m app.tailwindcss`).
  CSS output is `assets/static/file/css/output.css`, served at `/css/output.css`.
- Removed ux-dom imports that no longer exist: `plugins.style.TailwindStyle`, `plugins.hmr.HotReload`,
  `settings.commands.TailwindCommand`, top-level `WebAssets`. Browser HMR is `uxcompose serve dev`.
- Document plugins import from top-level `ux_dom` (`XElement`, `Htmx`, `Csp`, `Channel`), not `ux_dom.runtime`.
- Known gap: `ux-app` (retired) is no longer installable, so the shop screens still cannot run.
