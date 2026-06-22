from __future__ import annotations


def resolve_action(shot: dict, character: dict) -> dict:
    tokens = {shot.get("anchor_type"), shot.get("structure_type")}
    for action in character.get("action_library", []):
        if tokens.intersection(action.get("best_for", [])):
            return action
    return {"id": shot.get("character_action", "act"), "prompt_snippet": f"The character performs: {shot.get('character_action', 'act')}."}


def _visual_identity_text(character: dict) -> str:
    identity = character.get("visual_identity", "")
    if isinstance(identity, dict):
        parts = [
            identity.get("base_silhouette", ""),
            identity.get("eyes", ""),
            identity.get("line_style", ""),
            identity.get("default_pose_language", ""),
        ]
        return "; ".join(part for part in parts if part)
    return str(identity)


def _core_role_text(character: dict) -> str:
    role = character.get("core_role", "")
    if isinstance(role, dict):
        return f"{role.get('description', '')} Forbidden role: {role.get('forbidden_role', '')}."
    return str(role)


def get_prompt_snippet(character: dict) -> str:
    negatives = "; ".join(character.get("negative_rules", []))
    return f"{_visual_identity_text(character)}. Role: {_core_role_text(character)} Avoid: {negatives}."
