from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from validate_character_profile import validate_character_profile
except ImportError:
    from .validate_character_profile import validate_character_profile


def build_template(character_id: str, display_name: str) -> dict:
    return {
        "character_id": character_id,
        "display_name": display_name,
        "visual_identity": {
            "base_silhouette": "small pebble-like body with short stick arms",
            "eyes": "two tiny dot eyes",
            "line_style": "simple black hand-drawn line",
            "default_pose_language": "quiet, focused operator energy"
        },
        "core_role": {
            "description": "A generic abstract operator that participates in the main visual action.",
            "must_be_core_actor": True,
            "forbidden_role": "decorative mascot, branded IP, or background ornament"
        },
        "action_library": [
            {"id": "carry", "description": "Carry raw material into the visual mechanism.", "best_for": ["concept_metaphor", "filtering"], "prompt_snippet": "The pebble operator carries raw material toward the main mechanism."},
            {"id": "pull", "description": "Pull a rope, handle, or simple lever.", "best_for": ["workflow", "map_route"], "prompt_snippet": "The pebble operator pulls a simple rope connected to the workflow."},
            {"id": "sort", "description": "Sort notes, blocks, or tokens into piles.", "best_for": ["system_local", "filtering"], "prompt_snippet": "The pebble operator sorts small notes into clear piles."},
            {"id": "point", "description": "Point at the central comparison or transition.", "best_for": ["before_after", "contrast"], "prompt_snippet": "The pebble operator points at the key difference between two stations."},
            {"id": "repair", "description": "Repair a pipe or low-tech machine.", "best_for": ["bottleneck", "method_layering"], "prompt_snippet": "The pebble operator repairs a small low-tech machine."}
        ],
        "deformation_defaults": {
            "allow_deformation_by_default": False,
            "allowed_in_sticker_mode": False,
            "requires_explicit_trigger": True
        },
        "deformation_rules": [
            {
                "id": "pebble_funnel",
                "allowed": True,
                "trigger": {"structure_type": ["concept_metaphor"], "anchor_type": ["filtering"]},
                "description": "The pebble body becomes a simple funnel while remaining recognizable.",
                "max_intensity": "medium",
                "prompt_snippet": "Conditionally deform the pebble operator into a simple funnel-like body while keeping the tiny dot eyes and stick arms."
            },
            {
                "id": "wedged_in_pipe",
                "allowed": True,
                "trigger": {"structure_type": ["system_local"], "anchor_type": ["bottleneck"]},
                "description": "The operator is gently wedged in a pipe-shaped bottleneck.",
                "max_intensity": "low",
                "prompt_snippet": "Show the pebble operator lightly wedged inside a pipe-shaped bottleneck, still recognizable."
            },
            {
                "id": "flattened_note",
                "allowed": True,
                "trigger": {"structure_type": ["character_state"], "anchor_type": ["overload"]},
                "description": "The pebble operator is flattened like a note under overload.",
                "max_intensity": "low",
                "prompt_snippet": "Show the pebble operator mildly flattened like a note, still recognizable."
            }
        ],
        "negative_rules": [
            "no branded character treatment",
            "no complex clothing",
            "no cute mascot pose",
            "no corner decoration",
            "no children's cartoon style",
            "no unrecognizable deformation"
        ]
    }


def write_profile(output_dir: str, character_id: str, display_name: str, force: bool = False) -> dict:
    out = Path(output_dir)
    if out.exists() and not force:
        raise FileExistsError(f"{output_dir} already exists; pass --force to overwrite")
    out.mkdir(parents=True, exist_ok=True)
    character = build_template(character_id, display_name)
    report = validate_character_profile(character)
    if not report["passed"]:
        raise ValueError("; ".join(report["errors"]))
    (out / "character.json").write_text(json.dumps(character, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "identity.md").write_text("# Identity\n\nSmall pebble-like body, two tiny dot eyes, short stick arms, quiet focused operator energy.\n", encoding="utf-8")
    (out / "action-library.md").write_text("# Action Library\n\ncarry, pull, sort, point, repair.\n", encoding="utf-8")
    (out / "deformation-rules.md").write_text("# Deformation Rules\n\nDeformation is disabled by default. Rules: pebble_funnel, wedged_in_pipe, flattened_note.\n", encoding="utf-8")
    (out / "negative-rules.md").write_text("# Negative Rules\n\nNo branded character treatment. No mascot pose. No corner decoration. No unrecognizable deformation.\n", encoding="utf-8")
    return character


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--characters-dir", required=True)
    parser.add_argument("--character-id", required=True)
    parser.add_argument("--display-name", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    try:
        character = write_profile(args.output_dir, args.character_id, args.display_name, args.force)
    except Exception as exc:
        print(f"create_character_profile failed: {exc}")
        return 1
    print(json.dumps({"created": character["character_id"], "output_dir": args.output_dir}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
