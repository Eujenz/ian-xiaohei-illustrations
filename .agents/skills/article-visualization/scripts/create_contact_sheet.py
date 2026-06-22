from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def collect_images(images_dir: str | None = None, image_paths: list[str] | None = None) -> list[Path]:
    paths: list[Path] = []
    if images_dir:
        paths.extend(sorted(path for path in Path(images_dir).iterdir() if path.is_file() and path.suffix.lower() == ".png"))
    if image_paths:
        paths.extend(Path(path) for path in image_paths)
    return [path for path in paths if path.exists()]


def create_contact_sheet(images: list[str] | list[Path], output: str, cols: int = 3, thumb_width: int = 360) -> str:
    paths = [Path(path) for path in images]
    if not paths:
        raise ValueError("No images supplied for contact sheet.")
    cols = max(1, cols)
    font = ImageFont.load_default()
    label_height = 28
    padding = 18
    thumbs: list[tuple[Path, Image.Image]] = []
    thumb_height = 0
    for path in paths:
        image = Image.open(path).convert("RGB")
        ratio = thumb_width / image.width
        size = (thumb_width, max(1, int(image.height * ratio)))
        thumb = image.resize(size, Image.Resampling.LANCZOS)
        thumb_height = max(thumb_height, thumb.height)
        thumbs.append((path, thumb))
    rows = (len(thumbs) + cols - 1) // cols
    cell_width = thumb_width + padding * 2
    cell_height = thumb_height + label_height + padding * 2
    sheet = Image.new("RGB", (cell_width * cols, cell_height * rows), "white")
    draw = ImageDraw.Draw(sheet)
    for index, (path, thumb) in enumerate(thumbs):
        col = index % cols
        row = index // cols
        x = col * cell_width + padding
        y = row * cell_height + padding
        sheet.paste(thumb, (x, y))
        draw.text((x, y + thumb_height + 6), path.name, fill="#111111", font=font)
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--images")
    parser.add_argument("--image", action="append", default=[])
    parser.add_argument("--output", required=True)
    parser.add_argument("--cols", type=int, default=3)
    args = parser.parse_args()
    try:
        paths = collect_images(args.images, args.image)
        create_contact_sheet(paths, args.output, args.cols)
    except Exception as exc:
        print(f"create_contact_sheet failed: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
