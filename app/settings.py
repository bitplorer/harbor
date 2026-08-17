"""Paths and feature flags."""
from __future__ import annotations

import os
from pathlib import Path

from ux_dom import WebAssets

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.environ.get("DEBUG", "1") not in ("0", "false", "False")

ASSETS_DIR = BASE_DIR / "assets"
CSS_DIR = ASSETS_DIR / "css"
INPUT_CSS = "css/input.css"
OUTPUT_CSS = "output.css"

webassets = WebAssets(base_dir=ASSETS_DIR, dry_run=False)

APP_TITLE = "Harbor & Co."
WITH_TAILWIND = True
WITH_CHANNEL = os.environ.get("WITH_CHANNEL", "1") not in ("0", "false", "False")
WITH_HMR = os.environ.get("WITH_HMR", "0") not in ("0", "false", "False")
WITH_CSP = True
