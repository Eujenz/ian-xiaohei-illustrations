from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

try:
    from create_contact_sheet import collect_images, create_contact_sheet
    from export_article_assets import export_article_assets
    from overlay_text import overlay
    from qa_text import qa_overlay
    from validate_manifest import check_all_files_exist, validate_manifest_schema, validate_shot_list
except ImportError:
    from .create_contact_sheet import collect_images, create_contact_sheet
    from .export_article_assets import export_article_assets
    from .overlay_text import overlay
    from .qa_text import qa_overlay
    from .validate_manifest import check_all_files_exist, validate_manifest_schema, validate_shot_list


def find_manifest(article_dir: str) -> Path:
    base = Path(article_dir)
    for name in ("manifest.json", "manifest.generated.json", "manifest.sample.json"):
        path = base / name
        if path.exists():
            return path
    raise FileNotFoundError(f"No manifest found in {article_dir}")


def empty_report(article_slug: str) -> dict:
    return {
        "article_slug": article_slug,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "shots_total": 0,
        "overlays_validated": 0,
        "finals_generated": 0,
        "finals_skipped": 0,
        "missing_textless_images": [],
        "contact_sheet": None,
        "export_zip": None,
        "errors": [],
        "warnings": [],
    }


def write_report(article_dir: str, report: dict) -> Path:
    report_path = Path(article_dir) / "reports" / "asset-pipeline.report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path


def run_asset_pipeline(article_dir: str, font: str | None = None, force: bool = False) -> dict:
    base = Path(article_dir)
    manifest_path = find_manifest(article_dir)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report = empty_report(manifest.get("article_slug", base.name))
    report["shots_total"] = len(manifest.get("shots", []))
    manifest_errors = validate_manifest_schema(manifest) + validate_shot_list(manifest) + check_all_files_exist(manifest, str(base))
    if manifest_errors:
        report["errors"].extend(manifest_errors)
        write_report(article_dir, report)
        return report

    for shot in manifest["shots"]:
        shot_id = shot["id"]
        overlay_path = base / shot["overlay_file"]
        overlay_json = json.loads(overlay_path.read_text(encoding="utf-8"))
        qa_report = qa_overlay(overlay_json)
        qa_path = base / "qa" / f"{shot_id}.qa-text.json"
        qa_path.parent.mkdir(parents=True, exist_ok=True)
        qa_path.write_text(json.dumps(asdict(qa_report), ensure_ascii=False, indent=2), encoding="utf-8")
        if qa_report.passed:
            report["overlays_validated"] += 1
        else:
            report["errors"].extend(f"{shot_id}: {error}" for error in qa_report.errors)
            continue

        textless_path = base / shot["textless_image"]
        final_path = base / shot["final_image"]
        if final_path.exists() and not force:
            report["finals_skipped"] += 1
            continue
        if not textless_path.exists():
            report["missing_textless_images"].append(shot_id)
            continue
        try:
            overlay(str(textless_path), overlay_json, str(final_path), font)
        except Exception as exc:
            report["errors"].append(f"{shot_id}: overlay failed: {exc}")
            continue
        report["finals_generated"] += 1

    final_images = collect_images(str(base / "final"))
    if final_images:
        contact_sheet = base / "contact-sheet.png"
        create_contact_sheet(final_images, str(contact_sheet), cols=3)
        report["contact_sheet"] = str(contact_sheet)

    all_finals_exist = all((base / shot["final_image"]).exists() for shot in manifest.get("shots", []))
    if all_finals_exist:
        export_path = base / "export" / f"{manifest.get('article_slug', base.name)}-assets.zip"
        export_article_assets(str(base), str(export_path))
        report["export_zip"] = str(export_path)
    elif report["missing_textless_images"]:
        report["warnings"].append("Asset ZIP was not exported because not all final images exist.")

    write_report(article_dir, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article-dir", required=True)
    parser.add_argument("--font")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        report = run_asset_pipeline(args.article_dir, args.font, args.force)
    except Exception as exc:
        print(f"run_asset_pipeline failed: {exc}")
        return 1
    print(json.dumps({
        "shots_total": report["shots_total"],
        "overlays_validated": report["overlays_validated"],
        "finals_generated": report["finals_generated"],
        "finals_skipped": report["finals_skipped"],
        "missing_textless_images": report["missing_textless_images"],
        "export_zip": report["export_zip"],
        "errors": report["errors"],
    }, ensure_ascii=False, indent=2))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
