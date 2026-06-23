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


def build_native_label_list(labels: list[dict]) -> str:
    label_texts = [str(label.get("text", "")).strip() for label in labels if str(label.get("text", "")).strip()]
    if not label_texts:
        return "No Chinese labels requested."
    return " / ".join(label_texts)


def build_style_vitality_block(style: dict) -> str:
    prompt_rules = style.get("prompt_rules", {}) if isinstance(style, dict) else {}
    if isinstance(prompt_rules.get("style_block"), list) and prompt_rules["style_block"]:
        lines = []
        if style.get("display_name"):
            lines.append(f"Style profile: {style.get('display_name')} ({style.get('style_id', 'inline-style')}).")
        lines.extend(prompt_rules["style_block"])
        if prompt_rules.get("placeholder_policy"):
            lines.append(prompt_rules["placeholder_policy"])
        return "\n".join(lines)
    vitality = style.get("style_vitality", {}) if isinstance(style, dict) else {}
    whitespace = vitality.get("min_whitespace", "at least 35% blank white space")
    subject_scale = vitality.get("subject_scale", "the main subject should occupy about 40%-60% of the canvas")
    return "\n".join([
        "Pure white background with sparse, slightly wobbly black hand-drawn line art.",
        "Use a clean low-tech physical metaphor: switches, levers, carts, gears, funnels, workbenches, meters, labels, scraps, parcels, or small machines.",
        "The character must do the strange conceptual work inside the mechanism, with a deadpan serious expression; never place the character as a cute mascot or idle observer.",
        "Make the scene clear but not instructional, interesting but not childish, strange but clean.",
        "Avoid formal diagram language: no PPT slide composition, no corporate vector infographic, no realistic UI, no dense chart, no title block.",
        f"Composition target: {subject_scale}; preserve {whitespace}.",
        "Use light accent colors sparingly: orange for paths/arrows, red for warnings or friction, blue for secondary state, green/yellow only when a physical object needs separation.",
        "All label areas must remain blank visual plaques, signs, callouts, or notes for deterministic overlay.",
    ])


def build_negative_constraints(style: dict) -> str:
    base_rules = [
        "No readable Chinese text",
        "no sticker phrases",
        "no PPT style",
        "no infographic UI",
        "no vector corporate art",
        "no decorative mascot posing",
    ]
    prompt_rules = style.get("prompt_rules", {}) if isinstance(style, dict) else {}
    for rule in prompt_rules.get("negative_rules", []):
        existing = {item.lower() for item in base_rules}
        if rule.lower() not in existing:
            base_rules.append(rule)
    return "; ".join(base_rules) + "."


def native_visual_dna(style: dict) -> str:
    lines = [
        "Pure white background. Minimalist hand-drawn line art. Slightly wobbly pen or pencil lines. Lots of empty white space.",
        "Sparse handwritten Chinese annotations are part of the image, not added later.",
        "Clean absurd product-sketch feeling. One clear physical metaphor. No gradients, no shadows, no paper texture, no complex background.",
        "No commercial vector style, no PPT infographic look, no cute mascot poster, no children's illustration, no realistic UI.",
    ]
    prompt_rules = style.get("prompt_rules", {}) if isinstance(style, dict) else {}
    if isinstance(prompt_rules.get("style_block"), list):
        lines.extend(prompt_rules["style_block"])
    return "\n".join(lines)


def render_native_text_prompt(shot: dict, character: dict, style: dict, policy: dict, overlay_json: dict | None = None) -> str:
    labels = (overlay_json or {}).get("labels", [])
    action = resolve_action(shot, character)
    deformation = resolve_deformation(shot, character, policy.get("mode", "article_visualization"))
    deformation_block = deformation["prompt_snippet"] if deformation else "No character deformation for this shot."
    action_text = action.get("prompt_snippet") or action.get("description") or f"The character performs: {action.get('id', 'act')}."
    return "\n\n".join([
        "Generate one standalone 16:9 horizontal Chinese article illustration.",
        f"Visual DNA:\n{native_visual_dna(style)}",
        f"Character:\n{get_prompt_snippet(character)} Action: {action_text}",
        f"Conditional deformation:\n{deformation_block}",
        f"Theme:\n{shot.get('theme')}",
        f"Structure type:\n{shot.get('structure_type')}",
        f"Core idea:\n{shot.get('core_idea')}",
        f"Composition:\nUse a low-tech physical metaphor: {shot.get('metaphor')}. The character must perform the core conceptual action inside the scene, not decorate a corner.",
        f"Chinese handwritten labels:\n{build_native_label_list(labels)}",
        "Text rendering priority:\nRender the Chinese labels directly in the illustration as sparse handwritten annotations or pencil labels. Visual consistency is the highest priority. Keep labels short, legible, hand-drawn, and integrated with the line art. Do not leave blank placeholder labels for later overlay.",
        "Color use:\nBlack or dark blue for main line art and primary text. Orange only for main flow/path/arrows. Red only for key warnings, problems, reminders, or results. Blue only for secondary notes, feedback, system state, AI, or automation hints.",
        "Constraints:\nOne image explains only one core structure. Keep the main subject around 40%-60% of the canvas. Preserve at least 35% blank white space. Use at most 5-8 short handwritten Chinese labels. Do not write a title in the top-left corner. Do not write the structure type on the image. Do not make it a formal diagram, course slide, dense explainer, UI screenshot, or PPT slide. Clear but not instructional, interesting but not childish, strange but clean."
    ])


def render_visual_prompt(shot: dict, character: dict, style: dict, policy: dict, overlay_json: dict | None = None) -> str:
    if policy.get("text_strategy") == "image_text_native":
        return render_native_text_prompt(shot, character, style, policy, overlay_json)
    labels = (overlay_json or {}).get("labels", [])
    action = resolve_action(shot, character)
    deformation = resolve_deformation(shot, character, policy.get("mode", "article_visualization"))
    deformation_block = deformation["prompt_snippet"] if deformation else "No character deformation for this shot."
    action_text = action.get("prompt_snippet") or action.get("description") or f"The character performs: {action.get('id', 'act')}."
    return "\n\n".join([
        "## 1. Canvas spec\n16:9 horizontal article illustration, 1536x864 canvas, mostly white background.",
        f"## 2. Scene concept\nTheme: {shot.get('theme')}. Core idea: {shot.get('core_idea')}. Use a low-tech physical metaphor: {shot.get('metaphor')}.",
        f"## 3. Character block\n{get_prompt_snippet(character)} Action: {action_text}",
        f"## 4. Conditional deformation block\n{deformation_block}",
        "## 5. Text strategy block\nDo not render readable Chinese text. Leave blank placeholders for labels that will be added later by overlay_text.py.",
        f"## 6. Blank label placeholder block\n{build_label_placeholders(labels)}",
        f"## 7. Style vitality block\n{build_style_vitality_block(style)}",
        f"## 8. Negative constraints\n{build_negative_constraints(style)}"
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
    prompt = render_visual_prompt(
        shot,
        character,
        manifest.get("style_profile", {}),
        {
            "mode": manifest.get("mode", "article_visualization"),
            "text_strategy": manifest.get("text_strategy", "overlay_after_generation"),
        },
        overlay_json,
    )
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(prompt, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
