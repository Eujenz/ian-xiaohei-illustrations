from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_overlay(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_overlay_basic(overlay_json: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(overlay_json.get("labels"), list):
        errors.append("labels must be a list")
    canvas = overlay_json.get("canvas", {})
    if not isinstance(canvas.get("width"), int) or not isinstance(canvas.get("height"), int):
        errors.append("canvas.width and canvas.height are required integers")
    for i, label in enumerate(overlay_json.get("labels", [])):
        for key in ("id", "text", "x", "y", "box_width", "box_height", "font_size"):
            if key not in label:
                errors.append(f"labels[{i}] missing {key}")
        for key in ("x", "y", "box_width", "box_height", "font_size"):
            if key in label and not isinstance(label[key], int):
                errors.append(f"labels[{i}].{key} must be integer")
    return errors


def find_system_cjk_font() -> str | None:
    candidates = [
        "C:/Windows/Fonts/msjh.ttc",
        "C:/Windows/Fonts/msjhl.ttc",
        "C:/Windows/Fonts/mingliu.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None


def _text_position(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, label: dict) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    align = label.get("align", "left")
    x = 0
    if align == "center":
        x = max(0, (label["box_width"] - text_width) // 2)
    elif align == "right":
        x = max(0, label["box_width"] - text_width)
    y = max(0, (label["box_height"] - text_height) // 2)
    return x, y


def draw_label(base_image: Image.Image, label: dict, font_path: str) -> None:
    font = ImageFont.truetype(font_path, label["font_size"])
    layer = Image.new("RGBA", (label["box_width"], label["box_height"]), (255, 255, 255, 0))
    draw = ImageDraw.Draw(layer)
    style = label.get("style", "plain")
    if style in {"handwritten_note", "callout"}:
        draw.rounded_rectangle((0, 0, label["box_width"] - 1, label["box_height"] - 1), radius=4, fill=(255, 255, 255, 235), outline=(25, 25, 25, 255), width=2)
    elif style == "arrow_label":
        draw.rectangle((0, 0, label["box_width"] - 1, label["box_height"] - 1), fill=(255, 255, 255, 220), outline=(25, 25, 25, 255), width=2)
        draw.line((0, label["box_height"] - 1, -22, label["box_height"] + 18), fill=(25, 25, 25, 255), width=2)
    tx, ty = _text_position(draw, label["text"], font, label)
    draw.text((tx, ty), label["text"], font=font, fill=label.get("color", "#111111"))
    rotation = float(label.get("rotation", 0))
    if rotation:
        layer = layer.rotate(rotation, expand=True, resample=Image.Resampling.BICUBIC)
    base_image.alpha_composite(layer, (label["x"], label["y"]))


def overlay(image_path: str, overlay_json: dict, output_path: str, font_path: str | None = None) -> None:
    errors = validate_overlay_basic(overlay_json)
    if errors:
        raise ValueError("; ".join(errors))
    resolved_font = font_path or find_system_cjk_font()
    if not resolved_font:
        raise RuntimeError("No CJK-capable system font found. Rerun with --font /path/to/CJK-font.ttf.")
    image = Image.open(image_path).convert("RGBA")
    rendered = image.copy()
    for label in overlay_json.get("labels", []):
        draw_label(rendered, label, resolved_font)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    rendered.convert("RGB").save(output_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--overlay", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--font")
    args = parser.parse_args()
    try:
        overlay(args.image, load_overlay(args.overlay), args.output, args.font)
    except Exception as exc:
        print(f"overlay_text failed: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
