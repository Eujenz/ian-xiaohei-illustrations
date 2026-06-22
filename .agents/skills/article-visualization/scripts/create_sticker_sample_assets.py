from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw


DPI = (72, 72)


def _draw_character(draw: ImageDraw.ImageDraw, x: int, y: int, scale: float = 1.0) -> None:
    w = int(70 * scale)
    h = int(64 * scale)
    draw.rounded_rectangle((x, y, x + w, y + h), radius=max(4, int(12 * scale)), fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=max(2, int(3 * scale)))
    eye = max(2, int(4 * scale))
    draw.ellipse((x + int(20 * scale), y + int(24 * scale), x + int(20 * scale) + eye, y + int(24 * scale) + eye), fill=(0, 0, 0, 255))
    draw.ellipse((x + int(44 * scale), y + int(24 * scale), x + int(44 * scale) + eye, y + int(24 * scale) + eye), fill=(0, 0, 0, 255))
    draw.line((x + int(18 * scale), y + h, x + int(8 * scale), y + h + int(28 * scale)), fill=(0, 0, 0, 255), width=max(2, int(3 * scale)))
    draw.line((x + int(52 * scale), y + h, x + int(62 * scale), y + h + int(28 * scale)), fill=(0, 0, 0, 255), width=max(2, int(3 * scale)))


def _draw_blank_label(draw: ImageDraw.ImageDraw, width: int, height: int, scale: float = 1.0) -> None:
    box_w = max(46, int(width * 0.38))
    box_h = max(28, int(height * 0.16))
    x = width - box_w - max(12, int(18 * scale))
    y = height - box_h - max(12, int(18 * scale))
    draw.rounded_rectangle((x, y, x + box_w, y + box_h), radius=max(4, int(6 * scale)), fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=max(2, int(2 * scale)))


def create_asset(path: Path, width: int, height: int, variant: int) -> None:
    image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    scale = min(width / 370, height / 320)
    _draw_character(draw, max(14, int(width * 0.22)), max(12, int(height * 0.28)), scale)
    if variant % 3 == 0:
        draw.arc((int(width * 0.12), int(height * 0.12), int(width * 0.82), int(height * 0.82)), 25, 130, fill=(0, 0, 0, 255), width=max(2, int(4 * scale)))
    elif variant % 3 == 1:
        draw.line((int(width * 0.18), int(height * 0.58), int(width * 0.62), int(height * 0.48)), fill=(0, 0, 0, 255), width=max(2, int(4 * scale)))
    else:
        draw.rectangle((int(width * 0.14), int(height * 0.56), int(width * 0.48), int(height * 0.72)), outline=(0, 0, 0, 255), width=max(2, int(3 * scale)))
    _draw_blank_label(draw, width, height, scale)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, dpi=DPI)


def create_sticker_sample_assets(sticker_set_path: str, output_dir: str) -> list[str]:
    sticker_set = json.loads(Path(sticker_set_path).read_text(encoding="utf-8"))
    output = Path(output_dir)
    written: list[str] = []
    for index, sticker in enumerate(sticker_set.get("stickers", []), start=1):
        path = output / f"{sticker['id']}.textless.png"
        create_asset(path, 370, 320, index)
        written.append(path.name)
    main_path = output / "main.textless.png"
    create_asset(main_path, 240, 240, 100)
    written.append(main_path.name)
    tab_path = output / "tab.textless.png"
    create_asset(tab_path, 96, 74, 101)
    written.append(tab_path.name)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sticker-set", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    try:
        written = create_sticker_sample_assets(args.sticker_set, args.output_dir)
    except Exception as exc:
        print(f"create_sticker_sample_assets failed: {exc}")
        return 1
    print(json.dumps({"written": written}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
