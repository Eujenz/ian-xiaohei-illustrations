from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "export_article_assets.py"
SPEC = importlib.util.spec_from_file_location("article_visualization_export_article_assets", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Unable to load {MODULE_PATH}")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

export_article_assets = MODULE.export_article_assets
main = MODULE.main


if __name__ == "__main__":
    raise SystemExit(main())
