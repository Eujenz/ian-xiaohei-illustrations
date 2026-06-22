from __future__ import annotations

import argparse
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path


EXCLUDED_NAMES = {".DS_Store", "__pycache__"}
EXCLUDED_SUFFIXES = {".pyc", ".tmp"}
INCLUDED_DIRS = ["overlays", "prompts", "textless", "final", "qa"]


def should_include(path: Path) -> bool:
    if any(part in EXCLUDED_NAMES for part in path.parts):
        return False
    if path.suffix in EXCLUDED_SUFFIXES:
        return False
    return path.is_file()


def collect_export_files(article_dir: str) -> list[Path]:
    base = Path(article_dir)
    files: list[Path] = []
    for name in ("manifest.json", "manifest.generated.json", "manifest.sample.json"):
        path = base / name
        if path.exists():
            files.append(path)
            break
    files.extend(sorted(base.glob("shot-list*.json")))
    for dirname in INCLUDED_DIRS:
        directory = base / dirname
        if directory.exists():
            files.extend(sorted(path for path in directory.rglob("*") if should_include(path)))
    contact_sheet = base / "contact-sheet.png"
    if contact_sheet.exists():
        files.append(contact_sheet)
    return sorted(dict.fromkeys(files))


def export_article_assets(article_dir: str, output: str) -> dict:
    base = Path(article_dir)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    files = collect_export_files(article_dir)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(base).as_posix())
    report = {
        "article_dir": str(base),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output_zip": str(output_path),
        "files_included": [path.relative_to(base).as_posix() for path in files],
        "warnings": [],
        "errors": [],
    }
    output_path.with_suffix(".report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        report = export_article_assets(args.article_dir, args.output)
    except Exception as exc:
        print(f"export_article_assets failed: {exc}")
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
