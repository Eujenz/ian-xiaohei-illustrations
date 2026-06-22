import json
from pathlib import Path

from jsonschema import Draft202012Validator
from PIL import Image

from conftest import load_script


ROOT = Path(__file__).resolve().parents[1]
create_sticker_set = load_script("create_sticker_set")
create_sticker_sample_assets = load_script("create_sticker_sample_assets")
import_sticker_textless_images = load_script("import_sticker_textless_images")
qa_sticker_images = load_script("qa_sticker_images")
create_sticker_contact_sheet = load_script("create_sticker_contact_sheet")
run_sticker_asset_pipeline = load_script("run_sticker_asset_pipeline")
overlay_text = load_script("overlay_text")


def make_sticker_dir(tmp_path: Path) -> Path:
    create_sticker_set.create_sticker_set("sample-alt", "sample-sticker-set", str(tmp_path), 8)
    return tmp_path


def test_create_sticker_sample_assets_writes_transparent_textless_pngs(tmp_path):
    sticker_dir = make_sticker_dir(tmp_path)
    sticker_set_path = sticker_dir / "sticker-set.sample.json"
    written = create_sticker_sample_assets.create_sticker_sample_assets(str(sticker_set_path), str(sticker_dir / "textless"))
    assert len(written) == 10
    for name in ["01.textless.png", "08.textless.png", "main.textless.png", "tab.textless.png"]:
        path = sticker_dir / "textless" / name
        image = Image.open(path)
        assert image.mode == "RGBA"
        assert image.getchannel("A").getextrema()[0] < 255
    assert Image.open(sticker_dir / "textless" / "main.textless.png").size == (240, 240)
    assert Image.open(sticker_dir / "textless" / "tab.textless.png").size == (96, 74)


def test_import_sticker_textless_images_matches_common_names_and_uses_relative_paths(tmp_path):
    sticker_dir = make_sticker_dir(tmp_path / "stickers")
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    Image.new("RGBA", (370, 320), (255, 255, 255, 0)).save(source_dir / "01.png")
    Image.new("RGBA", (370, 320), (255, 255, 255, 0)).save(source_dir / "sticker-02.png")
    Image.new("RGBA", (370, 320), (255, 255, 255, 0)).save(source_dir / "03.textless.png")
    Image.new("RGBA", (370, 320), (255, 255, 255, 0)).save(source_dir / "unused.png")
    report = import_sticker_textless_images.import_sticker_textless_images(
        str(sticker_dir / "sticker-set.sample.json"),
        str(source_dir),
        str(sticker_dir / "textless"),
    )
    assert report["matched"] == ["01", "02", "03"]
    copied = {item["id"]: item for item in report["copied"]}
    assert copied["03"]["source"] == "03.textless.png"
    assert copied["03"]["destination"] == "textless/03.textless.png"
    assert "unused.png" in report["unmatched"]
    assert not any(":" in item["destination"] for item in report["copied"])


def test_qa_sticker_images_accepts_textless_fallbacks(tmp_path):
    sticker_dir = make_sticker_dir(tmp_path)
    sticker_set_path = sticker_dir / "sticker-set.sample.json"
    create_sticker_sample_assets.create_sticker_sample_assets(str(sticker_set_path), str(sticker_dir / "textless"))
    report = qa_sticker_images.qa_sticker_images(str(sticker_set_path), strict_dpi=True)
    assert report["passed"]
    assert len(report["per_image"]) == 10
    assert report["checks"]["transparency"]


def test_run_sticker_asset_pipeline_generates_finals_contact_sheet_and_schema_report(tmp_path):
    sticker_dir = make_sticker_dir(tmp_path)
    sticker_set_path = sticker_dir / "sticker-set.sample.json"
    create_sticker_sample_assets.create_sticker_sample_assets(str(sticker_set_path), str(sticker_dir / "textless"))
    font = overlay_text.find_system_cjk_font() or "C:/Windows/Fonts/arial.ttf"
    report = run_sticker_asset_pipeline.run_sticker_asset_pipeline(str(sticker_dir), force=True, font=font, strict_dpi=True)

    assert report["summary"]["sticker_count"] == 8
    assert report["summary"]["textless_found_count"] == 10
    assert report["summary"]["final_generated_count"] == 10
    assert report["summary"]["image_qa_passed_count"] == 10
    assert report["summary"]["image_qa_failed_count"] == 0
    assert report["errors"] == []
    assert (sticker_dir / "final" / "01.png").exists()
    assert (sticker_dir / "final" / "main.png").exists()
    assert (sticker_dir / "contact-sheet.png").exists()
    final = Image.open(sticker_dir / "final" / "01.png")
    assert final.mode == "RGBA"
    assert final.getchannel("A").getextrema()[0] < 255
    assert ":" not in report["contact_sheet"]
    assert all(":" not in item["final_image"] for item in report["stickers"])
    schema = json.loads((ROOT / "schemas" / "sticker-asset-report.schema.json").read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(report)) == []


def test_create_sticker_contact_sheet_uses_final_then_textless_fallback(tmp_path):
    sticker_dir = make_sticker_dir(tmp_path)
    sticker_set_path = sticker_dir / "sticker-set.sample.json"
    create_sticker_sample_assets.create_sticker_sample_assets(str(sticker_set_path), str(sticker_dir / "textless"))
    output = sticker_dir / "contact-sheet.png"
    create_sticker_contact_sheet.create_sticker_contact_sheet(str(sticker_set_path), str(output), cols=4)
    assert output.exists()
    sheet = Image.open(output)
    assert sheet.width == 720
    assert sheet.height == 534
