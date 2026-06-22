from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from resolve_character_rules import get_prompt_snippet, resolve_action
    from resolve_deformation_rules import resolve_deformation
except ImportError:
    from .resolve_character_rules import get_prompt_snippet, resolve_action
    from .resolve_deformation_rules import resolve_deformation


def build_label_placeholders(labels: list[dict]) -> str:
    if not labels:
        return "- No label placeholders requested."
    lines = []
    for label in labels:
        placeholder = label.get("placeholder") or f"blank placeholder near {label.get('anchor', 'the relevant object')}"
        lines.append(f"- {label.get('id')}: {placeholder}; leave it blank for later overlay.")
    return "\n".join(lines)


def render_visual_prompt(shot: dict, character: dict, style: dict, policy: dict, overlay_json: dict | None = None) -> str:
    labels = (overlay_json or {}).get("labels", [])
    action = resolve_action(shot, character)
    deformation = resolve_deformation(shot, character, policy.get("mode", "article_visualization"))
    deformation_block = deformation["prompt_snippet"] if deformation else "No character deformation for this shot."
    return "\n\n".join([
        "## 1. Canvas spec\n16:9 horizontal article illustration, 1536x864 canvas, mostly white background.",
        f"## 2. Scene concept\nTheme: {shot.get('theme')}. Core idea: {shot.get('core_idea')}. Use a low-tech physical metaphor: {shot.get('metaphor')}.",
        f"## 3. Character block\n{get_prompt_snippet(character)} Action: {action.get('prompt_snippet')}",
        f"## 4. Conditional deformation block\n{deformation_block}",
        "## 5. Text strategy block\nDo not render readable Chinese text. Leave blank placeholders for labels that will be added later by overlay_text.py.",
        f"## 6. Blank label placeholder block\n{build_label_placeholders(labels)}",
        "## 7. Style constraints\nHand-drawn black line art, slightly shaky ink line, mostly white background, lots of whitespace, light accent colors only when needed.",
        "## 8. Negative constraints\nNo readable Chinese text, no sticker phrases, no PPT style, no infographic UI, no vector corporate art, no decorative mascot posing."
    ])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--character", required=True)
    parser.add_argument("--overlay")
    parser.add_argument("--shot-id", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    character = json.loads(Path(args.character).read_text(encoding="utf-8"))
    overlay_json = json.loads(Path(args.overlay).read_text(encoding="utf-8")) if args.overlay else None
    shot = next(s for s in manifest["shots"] if s["id"] == args.shot_id)
    prompt = render_visual_prompt(shot, character, manifest.get("style_profile", {}), {"mode": manifest.get("mode", "article_visualization")}, overlay_json)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(prompt, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
