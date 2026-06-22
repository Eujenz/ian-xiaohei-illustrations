from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class QAReport:
    passed: bool
    checks: dict[str, bool]
    warnings: list[str]
    errors: list[str]


def check_all_text_from_manifest(overlay_json: dict) -> list[str]:
    return [f"{label.get('id', '<unknown>')} has empty text" for label in overlay_json.get("labels", []) if not str(label.get("text", "")).strip()]


def check_no_typo(overlay_json: dict) -> list[str]:
    simplified = set("后发里台云")
    traditional = set("後發裡臺雲")
    text = "".join(str(label.get("text", "")) for label in overlay_json.get("labels", []))
    warnings = ["Simple heuristic only; this is not a full spell-check."]
    if any(ch in text for ch in simplified) and any(ch in text for ch in traditional):
        warnings.append("Suspicious mixed simplified/traditional Chinese characters detected.")
    return warnings


def check_label_length(overlay_json: dict, default_max_chars: int = 8) -> list[str]:
    errors: list[str] = []
    for label in overlay_json.get("labels", []):
        max_chars = int(label.get("max_chars", default_max_chars))
        if len(str(label.get("text", ""))) > max_chars:
            errors.append(f"{label.get('id', '<unknown>')} exceeds max_chars {max_chars}")
    return errors


def check_text_in_bounds(overlay_json: dict, canvas: dict) -> list[str]:
    errors: list[str] = []
    width = canvas.get("width")
    height = canvas.get("height")
    for label in overlay_json.get("labels", []):
        label_errors: list[str] = []
        for key in ("x", "y", "box_width", "box_height"):
            if not isinstance(label.get(key), int):
                label_errors.append(f"{label.get('id', '<unknown>')} {key} must be integer")
        if label_errors:
            errors.extend(label_errors)
            continue
        x, y = label["x"], label["y"]
        box_width, box_height = label["box_width"], label["box_height"]
        if x < 0 or y < 0:
            errors.append(f"{label.get('id', '<unknown>')} has negative coordinates")
        if x + box_width > width or y + box_height > height:
            errors.append(f"{label.get('id', '<unknown>')} is out of canvas bounds")
    return errors


def qa_overlay(overlay_json: dict) -> QAReport:
    errors: list[str] = []
    warnings = check_no_typo(overlay_json)
    text_errors = check_all_text_from_manifest(overlay_json)
    length_errors = check_label_length(overlay_json)
    bounds_errors = check_text_in_bounds(overlay_json, overlay_json.get("canvas", {}))
    errors.extend(text_errors + length_errors + bounds_errors)
    checks = {
        "all_text_non_empty": not text_errors,
        "simple_typo_heuristic": True,
        "label_length": not length_errors,
        "text_in_bounds": not bounds_errors,
    }
    return QAReport(passed=not errors, checks=checks, warnings=warnings, errors=errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--overlay", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    overlay_json = json.loads(Path(args.overlay).read_text(encoding="utf-8"))
    report = qa_overlay(overlay_json)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
