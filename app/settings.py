"""Paths and feature flags."""
from __future__ import annotations

import os
from pathlib import Path

from ux_compose.assets import WebAssets

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.environ.get("DEBUG", "1") not in ("0", "false", "False")

ASSETS_DIR = BASE_DIR / "assets"

# ux-compose owns app asset folders + the Tailwind compiler (F-11).
# input:  assets/css/input.css
# output: assets/static/file/css/output.css, served at /css/output.css
webassets = WebAssets(base_dir=ASSETS_DIR, dry_run=False)
CSS_HREF = webassets.css_href

APP_TITLE = "Harbor & Co."
WITH_TAILWIND = True
WITH_CHANNEL = os.environ.get("WITH_CHANNEL", "1") not in ("0", "false", "False")
WITH_CSP = True
