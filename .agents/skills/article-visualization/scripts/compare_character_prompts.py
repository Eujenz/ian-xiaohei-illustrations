from __future__ import annotations

import argparse
import json
from pathlib import Path


def _prompt_id(path: Path) -> str:
    return path.name.split(".")[0]


def _manifest_prompt_ids(manifest_path: str | None) -> list[str] | None:
    if not manifest_path:
        return None
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    return [Path(shot["visual_prompt_file"]).name.split(".")[0] for shot in manifest.get("shots", [])]


def compare_prompts(original_dir: str, swapped_dir: str, overlay_dir: str | None = None, manifest_path: str | None = None) -> dict:
    original = {_prompt_id(path): path for path in Path(original_dir).glob("*.md")}
    swapped = {_prompt_id(path): path for path in Path(swapped_dir).glob("*.md")}
    scoped_ids = _manifest_prompt_ids(manifest_path)
    ids = sorted(scoped_ids if scoped_ids is not None else set(original) | set(swapped))
    report = {
        "compared_count": 0,
        "changed_prompts": [],
        "missing_original": [],
        "missing_swapped": [],
        "checks": {
            "swapped_differs_from_original": True,
            "textless_instruction_preserved": True,
            "placeholder_block_preserved": True,
            "no_overlay_label_leak": True
        },
        "warnings": {
            "extra_original": [],
            "extra_swapped": [],
            "messages": []
        },
        "errors": []
    }
    if scoped_ids is not None:
        expected = set(scoped_ids)
        report["warnings"]["extra_original"] = sorted(set(original) - expected)
        report["warnings"]["extra_swapped"] = sorted(set(swapped) - expected)
    overlays = {}
    if overlay_dir:
        for path in Path(overlay_dir).glob("*.json"):
            overlays[_prompt_id(path)] = json.loads(path.read_text(encoding="utf-8"))
    for prompt_id in ids:
        if prompt_id not in original:
            report["missing_original"].append(prompt_id)
            continue
        if prompt_id not in swapped:
            report["missing_swapped"].append(prompt_id)
            continue
        original_text = original[prompt_id].read_text(encoding="utf-8")
        swapped_text = swapped[prompt_id].read_text(encoding="utf-8")
        report["compared_count"] += 1
        if original_text != swapped_text:
            report["changed_prompts"].append(prompt_id)
        else:
            report["checks"]["swapped_differs_from_original"] = False
            report["errors"].append(f"{prompt_id}: swapped prompt did not differ from original")
        for label, text in (("original", original_text), ("swapped", swapped_text)):
            if "Do not render readable Chinese text" not in text:
                report["checks"]["textless_instruction_preserved"] = False
                report["errors"].append(f"{prompt_id}: {label} prompt missing textless instruction")
            if "Blank label placeholder block" not in text:
                report["checks"]["placeholder_block_preserved"] = False
                report["errors"].append(f"{prompt_id}: {label} prompt missing placeholder block")
        if prompt_id in overlays:
            labels = overlays[prompt_id].get("labels", [])
            leaked = [item["text"] for item in labels if item.get("text") and item["text"] in swapped_text]
            if leaked:
                report["checks"]["no_overlay_label_leak"] = False
                report["errors"].append(f"{prompt_id}: swapped prompt leaked labels {leaked}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--original-dir", required=True)
    parser.add_argument("--swapped-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--overlay-dir")
    parser.add_argument("--manifest")
    args = parser.parse_args()
    report = compare_prompts(args.original_dir, args.swapped_dir, args.overlay_dir, args.manifest)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
