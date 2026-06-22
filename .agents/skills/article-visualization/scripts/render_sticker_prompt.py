from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from resolve_character_rules import get_prompt_snippet
    from resolve_deformation_rules import resolve_deformation
except ImportError:
    from .resolve_character_rules import get_prompt_snippet
    from .resolve_deformation_rules import resolve_deformation


def build_placeholder_block(overlay_json: dict) -> str:
    lines = []
    for label in overlay_json.get("labels", []):
        placeholder = label.get("placeholder") or "blank sign or speech bubble for later text overlay"
        lines.append(f"- {label.get('id', 'label')}: {placeholder}; keep it blank.")
    return "\n".join(lines) if lines else "- Leave one blank phrase area for later overlay."


def get_sticker(sticker_set: dict, sticker_id: str) -> dict:
    if sticker_id == "main":
        return {"id": "main", "emotion": "set identity", "situation": "Main image for the sticker set.", "pose": "character standing clearly with a blank label area"}
    if sticker_id == "tab":
        return {"id": "tab", "emotion": "small navigation mark", "situation": "Chat tab image for quick recognition.", "pose": "character head or simple bust with a blank label area"}
    return next(item for item in sticker_set["stickers"] if item["id"] == sticker_id)


def render_sticker_prompt(sticker: dict, sticker_set: dict, character: dict, overlay_json: dict) -> str:
    shot_like = {
        "structure_type": "character_state",
        "anchor_type": sticker.get("emotion", ""),
    }
    deformation = resolve_deformation(shot_like, character, "line_sticker_set")
    deformation_block = deformation["prompt_snippet"] if deformation else "No character deformation in sticker mode for this sticker."
    return "\n\n".join([
        "## Canvas\nTransparent background, fit within the static sticker canvas, maximum 370 x 320 px for sticker images, simple single-character sticker.",
        f"## Character\n{get_prompt_snippet(character)}",
        f"## Sticker intent\nEmotion: {sticker.get('emotion')}. Situation: {sticker.get('situation')}. Strong readable silhouette at chat size.",
        f"## Pose/action\n{sticker.get('pose')}.",
        f"## Conditional deformation\n{deformation_block}",
        "## Text strategy\nDo not render readable Chinese text. The phrase will be added later from overlay JSON.",
        f"## Placeholder\n{build_placeholder_block(overlay_json)}",
        "## Style\nBlack hand-drawn line, minimal accent color if needed, no complex scene background, not text-only.",
        "## Negative constraints\nNo logos, no URLs, no ads, no trademarks, no brand references, no political content, no religious persuasion, no sexual content, no violent content, no readable Chinese text."
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sticker-set", required=True)
    parser.add_argument("--character", required=True)
    parser.add_argument("--sticker-id", required=True)
    parser.add_argument("--overlay", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    sticker_set = json.loads(Path(args.sticker_set).read_text(encoding="utf-8"))
    character = json.loads(Path(args.character).read_text(encoding="utf-8"))
    overlay_json = json.loads(Path(args.overlay).read_text(encoding="utf-8"))
    prompt = render_sticker_prompt(get_sticker(sticker_set, args.sticker_id), sticker_set, character, overlay_json)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(prompt, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
