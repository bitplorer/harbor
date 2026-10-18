"""CLI helper: python -m app.tailwindcss

Compiles assets/css/input.css with the Tailwind CLI that ux-compose resolves
(``uxcompose build`` uses the same resolver).
"""
from __future__ import annotations

import subprocess
from typing import Optional, Sequence

from ux_compose.tailwind import argv_with_io, ensure_tailwind, resolve_tailwind_argv

from app import settings


def compile_argv(*, ensure: bool = False, watch: bool = False) -> Optional[list[str]]:
    """Full Tailwind argv for Harbor's CSS, or None if no CLI is available."""
    cwd = settings.BASE_DIR
    base: Optional[Sequence[str]] = ensure_tailwind(cwd=cwd) if ensure else resolve_tailwind_argv(cwd=cwd)
    if not base:
        return None
    return argv_with_io(
        base,
        input_css=settings.webassets.input_css,
        output_css=settings.webassets.output_css,
        minify=not settings.DEBUG and not watch,
        watch=watch,
    )


def main() -> None:
    argv = compile_argv(ensure=True)
    assert argv is not None
    subprocess.run(argv, check=True, cwd=settings.BASE_DIR)


if __name__ == "__main__":
    main()
