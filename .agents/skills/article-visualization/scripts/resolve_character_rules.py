from __future__ import annotations


def resolve_action(shot: dict, character: dict) -> dict:
    tokens = {shot.get("anchor_type"), shot.get("structure_type")}
    for action in character.get("action_library", []):
        if tokens.intersection(action.get("best_for", [])):
            return action
    return {"id": shot.get("character_action", "act"), "prompt_snippet": f"The character performs: {shot.get('character_action', 'act')}."}


def get_prompt_snippet(character: dict) -> str:
    negatives = "; ".join(character.get("negative_rules", []))
    return f"{character.get('visual_identity', '')}. Role: {character.get('core_role', '')}. Avoid: {negatives}."
