from __future__ import annotations

import argparse
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image
from jsonschema import Draft202012Validator

try:
    from create_sticker_contact_sheet import create_sticker_contact_sheet
    from overlay_text import overlay
    from qa_sticker_images import qa_sticker_images
    from qa_sticker_spec import qa_sticker_spec
except ImportError:
    from .create_sticker_contact_sheet import create_sticker_contact_sheet
    from .overlay_text import overlay
    from .qa_sticker_images import qa_sticker_images
    from .qa_sticker_spec import qa_sticker_spec


ROOT = Path(__file__).resolve().parents[1]


def safe_relative(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.name


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_schema(sticker_set: dict) -> list[str]:
    schema = load_json(ROOT / "schemas" / "sticker-set.schema.json")
    return [error.message for error in Draft202012Validator(schema).iter_errors(sticker_set)]


def _preserve_source_alpha(textless_path: Path, rendered_path: Path, final_path: Path) -> None:
    source = Image.open(textless_path).convert("RGBA")
    rendered = Image.open(rendered_path).convert("RGBA")
    if rendered.size != source.size:
        rendered = rendered.resize(source.size, Image.Resampling.NEAREST)
    rendered.putalpha(source.getchannel("A"))
    final_path.parent.mkdir(parents=True, exist_ok=True)
    rendered.save(final_path, dpi=source.info.get("dpi", (72, 72)))


def render_overlay_preserving_alpha(textless_path: Path, overlay_json: dict, final_path: Path, font: str | None = None) -> None:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        overlay(str(textless_path), overlay_json, str(tmp_path), font)
        _preserve_source_alpha(textless_path, tmp_path, final_path)
    finally:
        tmp_path.unlink(missing_ok=True)


def _pipeline_items(sticker_set: dict) -> list[dict]:
    items = []
    for sticker in sticker_set.get("stickers", []):
        items.append({
            "id": sticker["id"],
            "overlay_file": sticker["overlay_file"],
            "prompt_file": sticker["visual_prompt_file"],
            "textless_image": sticker["textless_image"],
            "final_image": sticker["final_image"],
        })
    if "main_image" in sticker_set:
        main = sticker_set["main_image"]
        items.append({
            "id": "main",
            "overlay_file": main["overlay_file"],
            "prompt_file": main["visual_prompt_file"],
            "textless_image": "textless/main.textless.png",
            "final_image": main["final_image"],
        })
    if "tab_image" in sticker_set:
        tab = sticker_set["tab_image"]
        items.append({
            "id": "tab",
            "overlay_file": tab["overlay_file"],
            "prompt_file": tab["visual_prompt_file"],
            "textless_image": "textless/tab.textless.png",
            "final_image": tab["final_image"],
        })
    return items


def empty_report(sticker_set: dict) -> dict:
    return {
        "mode": "line_sticker_set",
        "sticker_set_id": sticker_set.get("sticker_set_id", ""),
        "character_id": sticker_set.get("character_id", ""),
        "base_dir": ".",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "sticker_count": len(sticker_set.get("stickers", [])),
            "textless_found_count": 0,
            "final_generated_count": 0,
            "image_qa_passed_count": 0,
            "image_qa_failed_count": 0,
            "errors_count": 0,
            "warnings_count": 0,
        },
        "stickers": [],
        "main_image": {},
        "tab_image": {},
        "contact_sheet": None,
        "reports": {},
        "warnings": [],
        "errors": [],
    }


def run_sticker_asset_pipeline(sticker_dir: str, sticker_set_name: str = "sticker-set.sample.json", force: bool = False, font: str | None = None, skip_contact_sheet: bool = False, strict_dpi: bool = False) -> dict:
    base = Path(sticker_dir)
    sticker_set_path = base / sticker_set_name
    sticker_set = load_json(sticker_set_path)
    report = empty_report(sticker_set)
    errors = validate_schema(sticker_set)
    if errors:
        report["errors"].extend(errors)
    spec_report = qa_sticker_spec(str(sticker_set_path))
    spec_path = base / "qa" / "sticker-spec.sample.json"
    spec_path.parent.mkdir(parents=True, exist_ok=True)
    spec_path.write_text(json.dumps(spec_report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["reports"]["sticker_spec"] = safe_relative(spec_path, base)
    if not spec_report["passed"]:
        report["errors"].extend(spec_report["errors"])

    generated = 0
    found = 0
    for item in _pipeline_items(sticker_set):
        textless = base / item["textless_image"]
        final = base / item["final_image"]
        overlay_path = base / item["overlay_file"]
        status = "waiting_for_textless_image"
        if textless.exists():
            found += 1
            if final.exists() and not force:
                status = "final_exists"
            else:
                try:
                    render_overlay_preserving_alpha(textless, load_json(overlay_path), final, font)
                    generated += 1
                    status = "final_generated"
                except Exception as exc:
                    status = "failed"
                    report["errors"].append(f"{item['id']}: overlay failed: {exc}")
        item_report = {
            "id": item["id"],
            "textless_image": item["textless_image"],
            "final_image": item["final_image"],
            "overlay_file": item["overlay_file"],
            "prompt_file": item["prompt_file"],
            "qa_image_report": "qa/sticker-image.sample.json",
            "status": status,
        }
        if item["id"] == "main":
            report["main_image"] = item_report
        elif item["id"] == "tab":
            report["tab_image"] = item_report
        else:
            report["stickers"].append(item_report)

    image_report = qa_sticker_images(str(sticker_set_path), strict_dpi)
    image_report_path = base / "qa" / "sticker-image.sample.json"
    image_report_path.write_text(json.dumps(image_report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["reports"]["sticker_images"] = safe_relative(image_report_path, base)
    if image_report["errors"]:
        report["errors"].extend(image_report["errors"])
    report["warnings"].extend(image_report["warnings"])

    if not skip_contact_sheet:
        contact_path = base / "contact-sheet.png"
        if force or not contact_path.exists():
            create_sticker_contact_sheet(str(sticker_set_path), str(contact_path))
        report["contact_sheet"] = safe_relative(contact_path, base)

    report["summary"]["textless_found_count"] = found
    report["summary"]["final_generated_count"] = generated
    report["summary"]["image_qa_passed_count"] = sum(1 for item in image_report["per_image"] if item["passed"])
    report["summary"]["image_qa_failed_count"] = sum(1 for item in image_report["per_image"] if not item["passed"])
    report["summary"]["errors_count"] = len(report["errors"])
    report["summary"]["warnings_count"] = len(report["warnings"])

    asset_report_path = base / "qa" / "sticker-asset-report.sample.json"
    report["reports"]["sticker_asset"] = safe_relative(asset_report_path, base)
    asset_report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sticker-dir", required=True)
    parser.add_argument("--sticker-set", default="sticker-set.sample.json")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--font")
    parser.add_argument("--skip-contact-sheet", action="store_true")
    parser.add_argument("--strict-dpi", action="store_true")
    args = parser.parse_args()
    try:
        report = run_sticker_asset_pipeline(args.sticker_dir, args.sticker_set, args.force, args.font, args.skip_contact_sheet, args.strict_dpi)
    except Exception as exc:
        print(f"run_sticker_asset_pipeline failed: {exc}")
        return 1
    print(json.dumps({
        "sticker_count": report["summary"]["sticker_count"],
        "textless_found_count": report["summary"]["textless_found_count"],
        "final_generated_count": report["summary"]["final_generated_count"],
        "image_qa_passed_count": report["summary"]["image_qa_passed_count"],
        "image_qa_failed_count": report["summary"]["image_qa_failed_count"],
        "contact_sheet": report["contact_sheet"],
        "errors": report["errors"],
    }, ensure_ascii=False, indent=2))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
