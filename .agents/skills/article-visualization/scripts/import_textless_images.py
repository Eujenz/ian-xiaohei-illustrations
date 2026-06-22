from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


IMAGE_SUFFIXES = {".png"}


def load_manifest(article_dir: str) -> tuple[Path, dict]:
    manifest_path = Path(article_dir) / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"manifest.json not found in {article_dir}")
    return manifest_path, json.loads(manifest_path.read_text(encoding="utf-8"))


def shot_id_from_filename(path: Path, shot_ids: set[str]) -> str | None:
    stem = path.stem.lower()
    for shot_id in sorted(shot_ids):
        sid = shot_id.lower()
        patterns = [
            rf"^{re.escape(sid)}$",
            rf"^{re.escape(sid)}[._ -].+",
            rf"^shot[-_ ]?{re.escape(sid)}$",
            rf"^shot[-_ ]?{re.escape(sid)}[._ -].+",
        ]
        if any(re.match(pattern, stem) for pattern in patterns):
            return shot_id
    return None


def import_textless_images(article_dir: str, source_dir: str, mode: str = "filename") -> dict:
    if mode != "filename":
        raise ValueError("Only filename mode is supported in v0.3.")
    base = Path(article_dir)
    source = Path(source_dir)
    manifest_path, manifest = load_manifest(article_dir)
    shots = manifest.get("shots", [])
    shot_ids = {shot["id"] for shot in shots}
    matches: dict[str, Path] = {}
    skipped: list[str] = []
    for image_path in sorted(source.iterdir()):
        if not image_path.is_file() or image_path.suffix.lower() not in IMAGE_SUFFIXES:
            skipped.append(str(image_path))
            continue
        shot_id = shot_id_from_filename(image_path, shot_ids)
        if shot_id and shot_id not in matches:
            matches[shot_id] = image_path
        else:
            skipped.append(str(image_path))
    copied: list[dict] = []
    textless_dir = base / "textless"
    textless_dir.mkdir(parents=True, exist_ok=True)
    for shot in shots:
        shot_id = shot["id"]
        if shot_id not in matches:
            continue
        destination = textless_dir / f"{shot_id}.textless.png"
        shutil.copy2(matches[shot_id], destination)
        if "textless_image" in shot:
            shot["textless_image"] = f"textless/{shot_id}.textless.png"
        copied.append({"shot_id": shot_id, "source": str(matches[shot_id]), "destination": str(destination)})
    if copied:
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    missing = [shot_id for shot_id in sorted(shot_ids) if shot_id not in matches]
    report = {
        "article_dir": str(base),
        "source_dir": str(source),
        "mode": mode,
        "matched": sorted(matches.keys()),
        "copied": copied,
        "skipped": skipped,
        "missing": missing,
    }
    reports_dir = base / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "import-textless.report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article-dir", required=True)
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--mode", choices=["filename"], default="filename")
    args = parser.parse_args()
    try:
        report = import_textless_images(args.article_dir, args.source_dir, args.mode)
    except Exception as exc:
        print(f"import_textless_images failed: {exc}")
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
