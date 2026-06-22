from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_character(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _schema_errors(character: dict, schema_path: str | Path | None = None) -> list[str]:
    schema = json.loads(Path(schema_path or ROOT / "schemas" / "character-profile.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    return [error.message for error in validator.iter_errors(character)]


def _duplicate_errors(items: list[dict], label: str) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for item in items:
        item_id = item.get("id")
        if item_id in seen:
            errors.append(f"duplicate {label} id: {item_id}")
        seen.add(item_id)
    return errors


def validate_character_profile(character: dict, schema_path: str | Path | None = None) -> dict:
    errors = _schema_errors(character, schema_path)
    warnings: list[str] = []

    character_id = character.get("character_id")
    if not character_id or not SLUG_RE.match(str(character_id)):
        errors.append("character_id must be slug-safe lowercase letters, numbers, and hyphens")
    if not str(character.get("display_name", "")).strip():
        errors.append("display_name must be non-empty")

    visual_identity = character.get("visual_identity", {})
    if not isinstance(visual_identity, dict):
        errors.append("visual_identity must be an object")
    else:
        for key in ("base_silhouette", "eyes", "line_style", "default_pose_language"):
            if not str(visual_identity.get(key, "")).strip():
                errors.append(f"visual_identity.{key} must be non-empty")

    core_role = character.get("core_role", {})
    if not isinstance(core_role, dict):
        errors.append("core_role must be an object")
    else:
        if core_role.get("must_be_core_actor") is not True:
            errors.append("core_role.must_be_core_actor must be true")
        if not str(core_role.get("forbidden_role", "")).strip():
            errors.append("core_role.forbidden_role must be non-empty")

    actions = character.get("action_library", [])
    if len(actions) < 3:
        errors.append("action_library must contain at least 3 actions")
    errors.extend(_duplicate_errors(actions, "action"))
    for action in actions:
        for key in ("id", "description", "best_for"):
            if key not in action:
                errors.append(f"action {action.get('id', '<unknown>')} missing {key}")
        if not isinstance(action.get("best_for", []), list):
            errors.append(f"action {action.get('id', '<unknown>')} best_for must be a list")

    deformation_rules = character.get("deformation_rules", [])
    errors.extend(_duplicate_errors(deformation_rules, "deformation rule"))
    for rule in deformation_rules:
        trigger = rule.get("trigger", {})
        if not isinstance(trigger.get("structure_type"), list):
            errors.append(f"deformation rule {rule.get('id', '<unknown>')} trigger.structure_type must be a list")
        if not isinstance(trigger.get("anchor_type"), list):
            errors.append(f"deformation rule {rule.get('id', '<unknown>')} trigger.anchor_type must be a list")
        if not str(rule.get("prompt_snippet", "")).strip():
            errors.append(f"deformation rule {rule.get('id', '<unknown>')} missing prompt_snippet")

    defaults = character.get("deformation_defaults", {})
    for key in ("allow_deformation_by_default", "allowed_in_sticker_mode", "requires_explicit_trigger"):
        if key not in defaults:
            errors.append(f"deformation_defaults.{key} must be explicitly defined")
    if not character.get("negative_rules"):
        errors.append("negative_rules must be non-empty")

    return {"passed": not errors, "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--character", required=True)
    args = parser.parse_args()
    report = validate_character_profile(load_character(args.character))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
