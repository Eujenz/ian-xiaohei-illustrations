from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


def draw_sample(path: Path, variant: int) -> None:
    image = Image.new("RGB", (1536, 864), "white")
    draw = ImageDraw.Draw(image)
    if variant == 1:
        draw.polygon([(520, 200), (1010, 200), (845, 560), (690, 560)], outline="black", width=5)
        draw.rectangle((180, 290, 420, 430), outline="black", width=4)
        draw.rectangle((1040, 330, 1245, 480), outline="black", width=4)
        draw.rounded_rectangle((245, 168, 385, 226), radius=6, outline="black", width=3)
        draw.rounded_rectangle((1080, 232, 1220, 290), radius=6, outline="black", width=3)
    else:
        draw.rectangle((250, 310, 520, 520), outline="black", width=5)
        draw.rectangle((980, 310, 1250, 520), outline="black", width=5)
        draw.line((540, 415, 960, 415), fill="black", width=5)
        draw.polygon([(960, 415), (920, 392), (920, 438)], fill="black")
        draw.rounded_rectangle((315, 170, 445, 224), radius=6, outline="black", width=3)
        draw.rounded_rectangle((1040, 170, 1190, 224), radius=6, outline="black", width=3)
    draw.rounded_rectangle((720, 595, 805, 680), radius=14, fill="black")
    draw.ellipse((744, 624, 752, 632), fill="white")
    draw.ellipse((775, 624, 783, 632), fill="white")
    draw.line((742, 680, 730, 725), fill="black", width=4)
    draw.line((785, 680, 798, 725), fill="black", width=4)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def main() -> int:
    draw_sample(EXAMPLES / "textless" / "01.textless.png", 1)
    draw_sample(EXAMPLES / "textless" / "02.textless.png", 2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
