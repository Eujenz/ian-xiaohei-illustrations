from __future__ import annotations


def resolve_deformation(shot: dict, character: dict, mode: str) -> dict | None:
    defaults = character.get("deformation_defaults", {})
    if mode == "line_sticker_set" and not defaults.get("allowed_in_sticker_mode", False):
        return None
    for rule in character.get("deformation_rules", []):
        trigger = rule.get("trigger", {})
        if (
            rule.get("allowed") is True
            and shot.get("structure_type") in trigger.get("structure_type", [])
            and shot.get("anchor_type") in trigger.get("anchor_type", [])
        ):
            return rule
    return None


def inject_deformation_snippet(prompt: str, rule: dict | None) -> str:
    if not rule:
        return prompt
    return f"{prompt}\n\nDeformation: {rule['prompt_snippet']}"
