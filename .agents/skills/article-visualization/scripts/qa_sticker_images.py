from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def safe_relative(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.name


def _image_has_alpha(image: Image.Image) -> bool:
    return image.mode in ("RGBA", "LA") or "transparency" in image.info


def _transparent_pixels(image: Image.Image) -> bool:
    if not _image_has_alpha(image):
        return False
    alpha = image.convert("RGBA").getchannel("A")
    extrema = alpha.getextrema()
    return extrema[0] < 255


def _alpha_margin(image: Image.Image) -> int | None:
    if not _image_has_alpha(image):
        return None
    alpha = image.convert("RGBA").getchannel("A")
    bbox = alpha.point(lambda value: 255 if value > 0 else 0).getbbox()
    if bbox is None:
        return None
    left, top, right, bottom = bbox
    return min(left, top, image.width - right, image.height - bottom)


def _dpi(image: Image.Image) -> tuple[float, float] | None:
    dpi = image.info.get("dpi")
    if not dpi:
        return None
    return float(dpi[0]), float(dpi[1])


def image_report(image_id: str, path: Path, base: Path, expected_size: tuple[int, int] | None, max_size: tuple[int, int], strict_dpi: bool = False) -> dict:
    warnings: list[str] = []
    errors: list[str] = []
    data = {
        "id": image_id,
        "path": safe_relative(path, base),
        "width": None,
        "height": None,
        "mode": None,
        "file_size_bytes": None,
        "has_alpha": False,
        "has_transparent_pixels": False,
        "dpi": None,
        "alpha_margin_px": None,
        "passed": False,
        "warnings": warnings,
        "errors": errors,
    }
    if not path.exists():
        errors.append("file missing")
        return data
    if path.suffix.lower() != ".png":
        errors.append("file is not PNG")
        data["file_size_bytes"] = path.stat().st_size
        return data
    data["file_size_bytes"] = path.stat().st_size
    if data["file_size_bytes"] >= 1000000:
        errors.append("file size must be under 1 MB")
    try:
        image = Image.open(path)
    except Exception as exc:
        errors.append(f"cannot open image: {exc}")
        return data
    data["width"], data["height"], data["mode"] = image.width, image.height, image.mode
    if expected_size and (image.width, image.height) != expected_size:
        errors.append(f"image must be exactly {expected_size[0]} x {expected_size[1]}")
    if image.width > max_size[0] or image.height > max_size[1]:
        errors.append(f"image exceeds {max_size[0]} x {max_size[1]}")
    if image.width % 2 or image.height % 2:
        errors.append("image dimensions must be even numbers")
    if image.mode == "CMYK":
        errors.append("image mode must not be CMYK")
    data["has_alpha"] = _image_has_alpha(image)
    data["has_transparent_pixels"] = _transparent_pixels(image)
    if not data["has_alpha"]:
        errors.append("image must have alpha channel or PNG transparency")
    if not data["has_transparent_pixels"]:
        errors.append("image must contain transparent pixels")
    dpi = _dpi(image)
    data["dpi"] = list(dpi) if dpi else None
    if dpi is None:
        message = "DPI metadata is absent"
        if strict_dpi:
            errors.append(message)
        else:
            warnings.append(message)
    elif dpi[0] < 72 or dpi[1] < 72:
        errors.append("DPI metadata must be at least 72")
    margin = _alpha_margin(image)
    data["alpha_margin_px"] = margin
    if margin is not None and margin < 10:
        warnings.append("visible content is closer than 10px to an edge")
    data["passed"] = not errors
    return data


def _items(sticker_set: dict) -> list[dict]:
    items = []
    for sticker in sticker_set.get("stickers", []):
        items.append({
            "id": sticker["id"],
            "path": sticker["final_image"],
            "fallback": sticker["textless_image"],
            "expected_size": None,
            "max_size": (370, 320),
        })
    if "main_image" in sticker_set:
        items.append({"id": "main", "path": sticker_set["main_image"]["final_image"], "fallback": "textless/main.textless.png", "expected_size": (240, 240), "max_size": (240, 240)})
    if "tab_image" in sticker_set:
        items.append({"id": "tab", "path": sticker_set["tab_image"]["final_image"], "fallback": "textless/tab.textless.png", "expected_size": (96, 74), "max_size": (96, 74)})
    return items


def qa_sticker_images(sticker_set_path: str, strict_dpi: bool = False) -> dict:
    set_path = Path(sticker_set_path)
    base = set_path.parent
    sticker_set = json.loads(set_path.read_text(encoding="utf-8"))
    per_image = []
    for item in _items(sticker_set):
        path = base / item["path"]
        if not path.exists() and item.get("fallback"):
            path = base / item["fallback"]
        per_image.append(image_report(item["id"], path, base, item["expected_size"], item["max_size"], strict_dpi))
    errors = [f"{item['id']}: {error}" for item in per_image for error in item["errors"]]
    warnings = [f"{item['id']}: {warning}" for item in per_image for warning in item["warnings"]]
    checks = {
        "files_exist": all("file missing" not in item["errors"] for item in per_image),
        "png": all("file is not PNG" not in item["errors"] for item in per_image),
        "dimensions": all(not any("exceeds" in error or "exactly" in error or "even" in error for error in item["errors"]) for item in per_image),
        "file_size": all(not any("file size" in error for error in item["errors"]) for item in per_image),
        "transparency": all(item["has_alpha"] and item["has_transparent_pixels"] for item in per_image),
        "dpi": all(item["dpi"] is None or (item["dpi"][0] >= 72 and item["dpi"][1] >= 72) for item in per_image),
    }
    return {"passed": not errors, "checks": checks, "warnings": warnings, "errors": errors, "per_image": per_image}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sticker-set", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--strict-dpi", action="store_true")
    args = parser.parse_args()
    report = qa_sticker_images(args.sticker_set, args.strict_dpi)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
