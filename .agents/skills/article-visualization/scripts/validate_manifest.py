from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator


def _default_schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "schemas" / "manifest.schema.json"


def validate_manifest_schema(manifest: dict, schema_path: str | None = None) -> list[str]:
    schema = json.loads(Path(schema_path or _default_schema_path()).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    return [error.message for error in validator.iter_errors(manifest)]


def validate_shot_list(manifest: dict) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for shot in manifest.get("shots", []):
        if shot.get("id") in seen:
            errors.append(f"duplicate shot id {shot.get('id')}")
        seen.add(shot.get("id"))
        if manifest.get("text_strategy") != "overlay_after_generation":
            errors.append("text_strategy must be overlay_after_generation")
    return errors


def check_all_files_exist(manifest: dict, base_path: str, strict_assets: bool = False) -> list[str]:
    errors: list[str] = []
    base = Path(base_path)
    for shot in manifest.get("shots", []):
        overlay_file = base / shot["overlay_file"]
        if not overlay_file.exists():
            errors.append(f"missing overlay_file: {shot['overlay_file']}")
        textless = base / shot["textless_image"]
        if strict_assets and not textless.exists():
            errors.append(f"missing textless_image: {shot['textless_image']}")
        if shot.get("qa_status") == "done" and not (base / shot["final_image"]).exists():
            errors.append(f"missing final_image for done shot: {shot['final_image']}")
    return errors
