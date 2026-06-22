from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from validate_manifest import validate_manifest_schema, validate_shot_list
except ImportError:
    from .validate_manifest import validate_manifest_schema, validate_shot_list


def swap_character(manifest: dict, character_id: str, include_shot_overrides: bool = False, prompt_output_dir: str | None = None) -> tuple[dict, dict]:
    source_character_id = manifest.get("character_id")
    changed = {"character_id": [source_character_id, character_id], "shot_character_ids": [], "prompt_paths": []}
    swapped = json.loads(json.dumps(manifest, ensure_ascii=False))
    swapped["character_id"] = character_id
    if include_shot_overrides:
        for shot in swapped.get("shots", []):
            if "character_id" in shot:
                changed["shot_character_ids"].append(shot["id"])
                shot["character_id"] = character_id
    if prompt_output_dir:
        prompt_dir = Path(prompt_output_dir)
        for shot in swapped.get("shots", []):
            old_path = shot.get("visual_prompt_file")
            new_path = (prompt_dir / f"{shot['id']}.visual.md").as_posix()
            shot["visual_prompt_file"] = new_path
            changed["prompt_paths"].append([old_path, new_path])
    swapped["character_replacement"] = {
        "source_character_id": source_character_id,
        "target_character_id": character_id,
        "created_by": "swap_character.py"
    }
    return swapped, changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--character-id", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--include-shot-overrides", action="store_true")
    parser.add_argument("--prompt-output-dir")
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    prompt_output_dir = args.prompt_output_dir
    if prompt_output_dir:
        manifest_dir = Path(args.manifest).parent.resolve()
        prompt_dir = Path(prompt_output_dir).resolve()
        try:
            prompt_output_dir = prompt_dir.relative_to(manifest_dir).as_posix()
        except ValueError:
            prompt_output_dir = Path(prompt_output_dir).as_posix()
    swapped, changed = swap_character(manifest, args.character_id, args.include_shot_overrides, prompt_output_dir)
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
