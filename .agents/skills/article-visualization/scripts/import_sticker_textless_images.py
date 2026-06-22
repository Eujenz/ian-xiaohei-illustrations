from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from PIL import Image


def safe_relative(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.name


def expected_ids(sticker_set: dict) -> list[str]:
    return [item["id"] for item in sticker_set.get("stickers", [])] + ["main", "tab"]


def match_id(path: Path, ids: list[str]) -> tuple[str, int] | None:
    stem = path.stem.lower()
    for item_id in ids:
        sid = item_id.lower()
        patterns = [
            (rf"^{re.escape(sid)}$", 0),
            (rf"^{re.escape(sid)}\.textless$", 1),
            (rf"^sticker[-_ ]?{re.escape(sid)}$", 2),
            (rf"^sticker[-_ ]?{re.escape(sid)}[._ -].+", 3),
            (rf"^{re.escape(sid)}[._ -].+", 4),
        ]
        for pattern, priority in patterns:
            if re.match(pattern, stem):
                return item_id, priority
    return None


def import_sticker_textless_images(sticker_set_path: str, source_dir: str, output_dir: str) -> dict:
    sticker_set = json.loads(Path(sticker_set_path).read_text(encoding="utf-8"))
    source = Path(source_dir)
    output = Path(output_dir)
    ids = expected_ids(sticker_set)
    matches: dict[str, tuple[int, Path]] = {}
    unmatched: list[str] = []
    duplicates: list[str] = []
    errors: list[str] = []
    for path in sorted(source.iterdir()):
        if not path.is_file() or path.suffix.lower() != ".png":
            unmatched.append(safe_relative(path, source))
            continue
        try:
            with Image.open(path) as image:
                image.verify()
        except Exception as exc:
            errors.append(f"{path.name}: invalid PNG: {exc}")
            continue
        match = match_id(path, ids)
        if not match:
            unmatched.append(safe_relative(path, source))
            continue
        item_id, priority = match
        if item_id not in matches or priority < matches[item_id][0]:
            if item_id in matches:
                duplicates.append(safe_relative(matches[item_id][1], source))
            matches[item_id] = (priority, path)
        else:
            duplicates.append(safe_relative(path, source))
    output.mkdir(parents=True, exist_ok=True)
    copied = []
    for item_id in ids:
        if item_id not in matches:
            continue
        destination = output / f"{item_id}.textless.png"
        shutil.copy2(matches[item_id][1], destination)
        copied.append({"id": item_id, "source": safe_relative(matches[item_id][1], source), "destination": safe_relative(destination, output.parent)})
    report = {
        "matched": [item["id"] for item in copied],
        "copied": copied,
        "unmatched": unmatched,
        "duplicates": duplicates,
        "missing": [item_id for item_id in ids if item_id not in matches],
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sticker-set", required=True)
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    report = import_sticker_textless_images(args.sticker_set, args.source_dir, args.output_dir)
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
