from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _flatten(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    background = Image.new("RGBA", image.size, (246, 246, 246, 255))
    background.alpha_composite(image)
    return background.convert("RGB").resize(size, Image.Resampling.LANCZOS)


def collect_preview_paths(sticker_set_path: str) -> list[tuple[str, Path]]:
    set_path = Path(sticker_set_path)
    base = set_path.parent
    sticker_set = json.loads(set_path.read_text(encoding="utf-8"))
    paths: list[tuple[str, Path]] = []
    for sticker in sticker_set.get("stickers", []):
        final = base / sticker["final_image"]
        textless = base / sticker["textless_image"]
        paths.append((sticker["id"], final if final.exists() else textless))
    for item_id, final, fallback in (
        ("main", sticker_set.get("main_image", {}).get("final_image"), "textless/main.textless.png"),
        ("tab", sticker_set.get("tab_image", {}).get("final_image"), "textless/tab.textless.png"),
    ):
        if final:
            final_path = base / final
            paths.append((item_id, final_path if final_path.exists() else base / fallback))
    return [(item_id, path) for item_id, path in paths if path.exists()]


def create_sticker_contact_sheet(sticker_set_path: str, output: str, cols: int = 5) -> str:
    items = collect_preview_paths(sticker_set_path)
    if not items:
        raise ValueError("No sticker images available for contact sheet")
    cell_w, cell_h = 180, 178
    preview = (148, 128)
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    for index, (item_id, path) in enumerate(items):
        col = index % cols
        row = index // cols
        x = col * cell_w + 16
        y = row * cell_h + 12
        sheet.paste(_flatten(path, preview), (x, y))
        draw.text((x, y + preview[1] + 8), item_id, fill="#111111", font=font)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sticker-set", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--cols", type=int, default=5)
    args = parser.parse_args()
    try:
        create_sticker_contact_sheet(args.sticker_set, args.output, args.cols)
    except Exception as exc:
        print(f"create_sticker_contact_sheet failed: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
