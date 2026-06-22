from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
URL_RE = re.compile(r"https?://|www\.", re.IGNORECASE)
BRAND_TERMS = {"LINE", "NVIDIA", "OpenAI", "Google", "Apple", "Microsoft", "Meta"}
ALLOWED_COUNTS = {8, 16, 24, 32, 40}


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_label_bounds(overlay: dict) -> list[str]:
    errors = []
    canvas = overlay.get("canvas", {})
    width = canvas.get("width", 0)
    height = canvas.get("height", 0)
    for label in overlay.get("labels", []):
        x, y = label.get("x"), label.get("y")
        box_width, box_height = label.get("box_width"), label.get("box_height")
        if not all(isinstance(value, int) for value in (x, y, box_width, box_height)):
            errors.append(f"{overlay.get('shot_id')}: label coordinates must be integers")
            continue
        if x < 0 or y < 0 or x + box_width > width or y + box_height > height:
            errors.append(f"{overlay.get('shot_id')}: label {label.get('id')} is out of bounds")
    return errors


def overlay_errors(sticker_set_path: Path, sticker_set: dict) -> list[str]:
    base = sticker_set_path.parent
    errors: list[str] = []
    for sticker in sticker_set.get("stickers", []):
        overlay = load_json(base / sticker["overlay_file"])
        canvas = overlay.get("canvas", {})
        width = canvas.get("width", 0)
        height = canvas.get("height", 0)
        if width > 370 or height > 320:
            errors.append(f"{sticker['id']}: sticker overlay exceeds 370 x 320")
        if width % 2 or height % 2:
            errors.append(f"{sticker['id']}: sticker dimensions must be even numbers")
        errors.extend(validate_label_bounds(overlay))
    for key, expected in (("main_image", (240, 240)), ("tab_image", (96, 74))):
        if key not in sticker_set:
            continue
        overlay = load_json(base / sticker_set[key]["overlay_file"])
        canvas = overlay.get("canvas", {})
        if (canvas.get("width"), canvas.get("height")) != expected:
            errors.append(f"{key}: overlay must be {expected[0]} x {expected[1]}")
        errors.extend(validate_label_bounds(overlay))
    return errors


def policy_errors(sticker_set: dict) -> list[str]:
    errors: list[str] = []
    for sticker in sticker_set.get("stickers", []):
        phrase = sticker.get("phrase", "")
        fields = [phrase, sticker.get("emotion", ""), sticker.get("situation", ""), sticker.get("pose", "")]
        if URL_RE.search(" ".join(fields)):
            errors.append(f"{sticker['id']}: URL-like text is not allowed")
        if any(term in " ".join(fields) for term in BRAND_TERMS):
            errors.append(f"{sticker['id']}: brand or service name is not allowed in sample content")
        if len(phrase) > 6:
            errors.append(f"{sticker['id']}: phrase is too long for chat readability")
        for key in ("emotion", "situation", "pose"):
            if not str(sticker.get(key, "")).strip():
                errors.append(f"{sticker['id']}: {key} must be non-empty")
        if len(sticker.get("pose", "").split()) < 3:
            errors.append(f"{sticker['id']}: pose must include a character action")
    return errors


def qa_sticker_spec(sticker_set_path: str) -> dict:
    path = Path(sticker_set_path)
    sticker_set = load_json(path)
    schema = load_json(ROOT / "schemas" / "sticker-set.schema.json")
    errors = [error.message for error in Draft202012Validator(schema).iter_errors(sticker_set)]
    warnings: list[str] = []
    canvas = sticker_set.get("canvas", {})
    checks = {
        "schema": not errors,
        "allowed_count": sticker_set.get("count") in ALLOWED_COUNTS,
        "sticker_count_matches": sticker_set.get("count") == len(sticker_set.get("stickers", [])),
        "transparent_background": canvas.get("transparent_background") is True,
        "safe_margin": canvas.get("safe_margin_px", 0) >= 10,
        "color_mode_rgb": canvas.get("color_mode") == "RGB",
        "min_dpi": canvas.get("min_dpi", 0) >= 72,
        "file_size_limits": canvas.get("max_file_size_bytes", 999999999) <= 1000000 and canvas.get("max_zip_size_bytes", 999999999) <= 60000000,
        "overlay_bounds": True,
        "conversation_usefulness": True,
        "policy_text": True,
    }
    if not checks["allowed_count"]:
        errors.append("count must be one of 8, 16, 24, 32, 40")
    if not checks["sticker_count_matches"]:
        errors.append("count must match stickers length")
    overlay_check_errors = overlay_errors(path, sticker_set)
    if overlay_check_errors:
        checks["overlay_bounds"] = False
        errors.extend(overlay_check_errors)
    text_errors = policy_errors(sticker_set)
    if text_errors:
        checks["conversation_usefulness"] = False
        checks["policy_text"] = False
        errors.extend(text_errors)
    return {"passed": not errors, "checks": checks, "warnings": warnings, "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sticker-set", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = qa_sticker_spec(args.sticker_set)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
