from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_style(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _schema_errors(style: dict, schema_path: str | Path | None = None) -> list[str]:
    schema = json.loads(Path(schema_path or ROOT / "schemas" / "style-profile.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    return [error.message for error in validator.iter_errors(style)]


def validate_style_profile(style: dict, schema_path: str | Path | None = None) -> dict:
    errors = _schema_errors(style, schema_path)
    warnings: list[str] = []

    style_id = style.get("style_id")
    if not style_id or not SLUG_RE.match(str(style_id)):
        errors.append("style_id must be slug-safe lowercase letters, numbers, and hyphens")
    if not str(style.get("display_name", "")).strip():
        errors.append("display_name must be non-empty")

    visual_dna = style.get("visual_dna", {})
    if not isinstance(visual_dna, dict):
        errors.append("visual_dna must be an object")
    else:
        for key in ("background", "line_art", "metaphor_logic", "composition", "character_treatment", "accent_colors"):
            if not str(visual_dna.get(key, "")).strip():
                errors.append(f"visual_dna.{key} must be non-empty")

    prompt_rules = style.get("prompt_rules", {})
    if not isinstance(prompt_rules, dict):
        errors.append("prompt_rules must be an object")
    else:
        style_block = prompt_rules.get("style_block", [])
        if not isinstance(style_block, list) or len(style_block) < 3:
            errors.append("prompt_rules.style_block must contain at least 3 entries")
        if not str(prompt_rules.get("placeholder_policy", "")).strip():
            errors.append("prompt_rules.placeholder_policy must be non-empty")
        negative_rules = prompt_rules.get("negative_rules", [])
        if not isinstance(negative_rules, list) or not negative_rules:
            errors.append("prompt_rules.negative_rules must be non-empty")
        if not any("readable Chinese text" in str(rule) for rule in negative_rules):
            warnings.append("Style should explicitly forbid readable Chinese text.")

    return {"passed": not errors, "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--style", required=True)
    args = parser.parse_args()
    report = validate_style_profile(load_style(args.style))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
