from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from validate_style_profile import load_style, validate_style_profile
except ImportError:
    from .validate_style_profile import load_style, validate_style_profile


def list_styles(styles_dir: str) -> list[dict]:
    rows: list[dict] = []
    for style_path in sorted(Path(styles_dir).glob("*/style.json")):
        style = load_style(style_path)
        report = validate_style_profile(style)
        rows.append({
            "style_id": style.get("style_id", style_path.parent.name),
            "display_name": style.get("display_name", ""),
            "valid": report["passed"],
            "errors_count": len(report["errors"]),
            "warnings_count": len(report["warnings"]),
            "style_block_count": len(style.get("prompt_rules", {}).get("style_block", [])),
            "negative_rules_count": len(style.get("prompt_rules", {}).get("negative_rules", [])),
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--styles-dir", required=True)
    args = parser.parse_args()
    rows = list_styles(args.styles_dir)
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0 if all(row["valid"] for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
