from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from validate_manifest import validate_manifest_schema, validate_shot_list
    from validate_style_profile import load_style, validate_style_profile
except ImportError:
    from .validate_manifest import validate_manifest_schema, validate_shot_list
    from .validate_style_profile import load_style, validate_style_profile


def swap_style(manifest: dict, style: dict, prompt_output_dir: str | None = None) -> tuple[dict, dict]:
    source_style_id = manifest.get("style_id") or manifest.get("style_profile", {}).get("style_id")
    target_style_id = style.get("style_id")
    changed = {"style_id": [source_style_id, target_style_id], "prompt_paths": []}
    swapped = json.loads(json.dumps(manifest, ensure_ascii=False))
    swapped["style_id"] = target_style_id
    swapped["style_profile"] = style
    if prompt_output_dir:
        prompt_dir = Path(prompt_output_dir)
        for shot in swapped.get("shots", []):
            old_path = shot.get("visual_prompt_file")
            new_path = (prompt_dir / f"{shot['id']}.visual.md").as_posix()
            shot["visual_prompt_file"] = new_path
            changed["prompt_paths"].append([old_path, new_path])
    swapped["style_replacement"] = {
        "source_style_id": source_style_id,
        "target_style_id": target_style_id,
        "created_by": "swap_style.py"
    }
    return swapped, changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--style", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--prompt-output-dir")
    args = parser.parse_args()

    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    style = load_style(args.style)
    style_report = validate_style_profile(style)
    if not style_report["passed"]:
        print(json.dumps({"passed": False, "errors": style_report["errors"]}, ensure_ascii=False, indent=2))
        return 1

    prompt_output_dir = args.prompt_output_dir
    if prompt_output_dir:
        manifest_dir = Path(args.manifest).parent.resolve()
        prompt_dir = Path(prompt_output_dir).resolve()
        try:
            prompt_output_dir = prompt_dir.relative_to(manifest_dir).as_posix()
        except ValueError:
            prompt_output_dir = Path(prompt_output_dir).as_posix()

    swapped, changed = swap_style(manifest, style, prompt_output_dir)
    errors = validate_manifest_schema(swapped) + validate_shot_list(swapped)
    if errors:
        print(json.dumps({"passed": False, "errors": errors}, ensure_ascii=False, indent=2))
        return 1
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(swapped, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"passed": True, "changed": changed}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
