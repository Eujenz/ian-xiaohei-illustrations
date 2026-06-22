from __future__ import annotations

import argparse
import json
from pathlib import Path


CANVAS = {
    "sticker_max_width": 370,
    "sticker_max_height": 320,
    "main_width": 240,
    "main_height": 240,
    "tab_width": 96,
    "tab_height": 74,
    "transparent_background": True,
    "safe_margin_px": 10,
    "color_mode": "RGB",
    "min_dpi": 72,
    "max_file_size_bytes": 1000000,
    "max_zip_size_bytes": 60000000,
}

SAMPLE_ITEMS = [
    ("01", "收到", "acknowledgement", "Confirming that a message has been received.", "character holding a small blank receipt card"),
    ("02", "好的", "agreement", "Agreeing calmly in a work chat.", "character giving a quiet thumbs-up beside a blank bubble"),
    ("03", "等等", "pause", "Asking the other person to wait briefly.", "character gently holding up one hand near a blank sign"),
    ("04", "加油", "encouragement", "Encouraging someone during a difficult task.", "character pushing a tiny cart forward with effort"),
    ("05", "不急", "reassurance", "Telling someone there is no rush.", "character sitting beside a small blank placard with relaxed posture"),
    ("06", "完成", "completion", "Marking a task as finished.", "character placing a check-shaped object near a blank label"),
    ("07", "我看看", "checking", "Offering to inspect something.", "character leaning over a simple magnifier and blank note"),
    ("08", "謝謝", "thanks", "Expressing gratitude.", "character bowing slightly beside a blank speech bubble"),
]


def overlay_for(item_id: str, phrase: str, width: int, height: int, style: str = "callout") -> dict:
    box_width = min(width - 20, 120)
    box_height = min(height - 20, 48)
    return {
        "shot_id": item_id,
        "canvas": {"width": width, "height": height, "target_ratio": "sticker"},
        "labels": [
            {
                "id": "label_01",
                "text": phrase,
                "anchor": "blank_phrase_area",
                "placeholder": "blank sign or speech bubble reserved for later text overlay",
                "x": max(10, width - box_width - 12),
                "y": max(10, height - box_height - 12),
                "box_width": box_width,
                "box_height": box_height,
                "font_size": 24 if width > 120 else 16,
                "rotation": 0,
                "align": "center",
                "style": style,
                "max_chars": 6,
            }
        ],
    }


def create_sticker_set(character_id: str, sticker_set_id: str, output_dir: str, count: int = 8) -> dict:
    if count not in {8, 16, 24, 32, 40}:
        raise ValueError("count must be one of 8, 16, 24, 32, 40")
    if count > len(SAMPLE_ITEMS):
        raise ValueError("v0.5 sample generator only provides 8 phrases")
    base = Path(output_dir)
    (base / "overlays").mkdir(parents=True, exist_ok=True)
    (base / "prompts").mkdir(parents=True, exist_ok=True)
    (base / "qa").mkdir(parents=True, exist_ok=True)
    stickers = []
    for item_id, phrase, emotion, situation, pose in SAMPLE_ITEMS[:count]:
        overlay_path = base / "overlays" / f"{item_id}.overlay.json"
        overlay_path.write_text(json.dumps(overlay_for(item_id, phrase, 370, 320), ensure_ascii=False, indent=2), encoding="utf-8")
        stickers.append({
            "id": item_id,
            "phrase": phrase,
            "emotion": emotion,
            "situation": situation,
            "pose": pose,
            "visual_prompt_file": f"prompts/{item_id}.visual.md",
            "overlay_file": f"overlays/{item_id}.overlay.json",
            "textless_image": f"textless/{item_id}.textless.png",
            "final_image": f"final/{item_id}.png",
            "qa_status": "pending",
        })
    (base / "overlays" / "main.overlay.json").write_text(json.dumps(overlay_for("main", "主圖", 240, 240, "plain"), ensure_ascii=False, indent=2), encoding="utf-8")
    (base / "overlays" / "tab.overlay.json").write_text(json.dumps(overlay_for("tab", "標籤", 96, 74, "plain"), ensure_ascii=False, indent=2), encoding="utf-8")
    sticker_set = {
        "mode": "line_sticker_set",
        "sticker_set_id": sticker_set_id,
        "character_id": character_id,
        "status": "draft",
        "count": count,
        "canvas": CANVAS,
        "text_strategy": "overlay_after_generation",
        "stickers": stickers,
        "main_image": {
            "visual_prompt_file": "prompts/main.visual.md",
            "overlay_file": "overlays/main.overlay.json",
            "final_image": "final/main.png",
        },
        "tab_image": {
            "visual_prompt_file": "prompts/tab.visual.md",
            "overlay_file": "overlays/tab.overlay.json",
            "final_image": "final/tab.png",
        },
        "metadata": {
            "transparent_background_assumption": True,
            "version": "v0.5.0"
        },
    }
    (base / "sticker-set.sample.json").write_text(json.dumps(sticker_set, ensure_ascii=False, indent=2), encoding="utf-8")
    return sticker_set


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--character-id", required=True)
    parser.add_argument("--sticker-set-id", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--count", type=int, default=8)
    args = parser.parse_args()
    try:
        sticker_set = create_sticker_set(args.character_id, args.sticker_set_id, args.output_dir, args.count)
    except Exception as exc:
        print(f"create_sticker_set failed: {exc}")
        return 1
    print(json.dumps({"created": sticker_set["sticker_set_id"], "count": sticker_set["count"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
