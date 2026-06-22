from __future__ import annotations

import argparse
import json
from pathlib import Path


CANVAS = {"width": 1536, "height": 864, "target_ratio": "16:9"}
PRESETS = {
    "concept_metaphor": [(260, 190), (1060, 240), (1110, 620)],
    "workflow": [(250, 170), (700, 170), (1080, 170)],
    "before_after": [(280, 190), (970, 190), (1120, 610)],
    "system_local": [(500, 180), (880, 230), (1010, 590)],
    "method_layering": [(260, 170), (260, 310), (260, 450)],
    "fallback": [(230, 170), (980, 250), (1080, 620)],
}


def label_with_coordinates(label: dict, structure_type: str, index: int) -> dict:
    positions = PRESETS.get(structure_type, PRESETS["fallback"])
    x, y = positions[index % len(positions)]
    return {
        "id": label.get("id", f"label_{index + 1:02d}"),
        "text": label["text"],
        "anchor": label.get("anchor", f"anchor_{index + 1}"),
        "placeholder": label.get("placeholder", "blank visual placeholder for later text overlay"),
        "x": x,
        "y": y,
        "box_width": 150,
        "box_height": 58,
        "font_size": 30,
        "rotation": -3 if index % 2 == 0 else 3,
        "align": "center",
        "style": "handwritten_note" if index % 2 == 0 else "callout",
        "max_chars": int(label.get("max_chars", 8)),
    }


def create_manifest_draft(shot_list: dict, article_slug: str, character_id: str, output_dir: str) -> dict:
    base = Path(output_dir)
    manifest = {
        "mode": "article_visualization",
        "article_slug": article_slug,
        "character_id": character_id,
        "text_strategy": "overlay_after_generation",
        "style_profile": {
            "canvas": "16:9 horizontal article illustration",
            "line": "hand-drawn black line art",
            "background": "mostly white background",
        },
        "shots": [],
    }
    for shot in shot_list["shots"]:
        shot_id = shot["id"]
        overlay_rel = f"overlays/{shot_id}.generated.overlay.json"
        overlay_json = {
            "shot_id": shot_id,
            "canvas": CANVAS,
            "labels": [label_with_coordinates(label, shot["structure_type"], i) for i, label in enumerate(shot["overlay_labels"])],
        }
        overlay_path = base / overlay_rel
        overlay_path.parent.mkdir(parents=True, exist_ok=True)
        overlay_path.write_text(json.dumps(overlay_json, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["shots"].append({
            "id": shot_id,
            "placement": shot.get("placement", "body"),
            "anchor_type": shot["anchor_type"],
            "theme": shot["theme"],
            "core_idea": shot["core_idea"],
            "structure_type": shot["structure_type"],
            "metaphor": shot["metaphor"],
            "character_action": shot["character_action"],
            "visual_prompt_file": f"prompts/{shot_id}.generated.visual.md",
            "overlay_file": overlay_rel,
            "textless_image": f"textless/{shot_id}.textless.png",
            "final_image": f"final/{shot_id}.final.png",
            "qa_status": "pending",
        })
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shot-list", required=True)
    parser.add_argument("--article-slug", required=True)
    parser.add_argument("--character-id", default="default")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    shot_list = json.loads(Path(args.shot_list).read_text(encoding="utf-8"))
    manifest = create_manifest_draft(shot_list, args.article_slug, args.character_id, args.output_dir)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
