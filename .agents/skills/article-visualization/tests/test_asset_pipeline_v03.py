import json
import shutil
import zipfile
from pathlib import Path

from jsonschema import Draft202012Validator
from PIL import Image

from conftest import load_script


ROOT = Path(__file__).resolve().parents[1]
import_textless_images = load_script("import_textless_images")
create_contact_sheet = load_script("create_contact_sheet")
export_article_assets = load_script("export_article_assets")
run_asset_pipeline = load_script("run_asset_pipeline")
overlay_text = load_script("overlay_text")


def make_article_dir(tmp_path: Path) -> Path:
    article_dir = tmp_path / "my-article"
    article_dir.mkdir()
    shutil.copy(ROOT / "examples" / "manifest.sample.json", article_dir / "manifest.json")
    shutil.copytree(ROOT / "examples" / "overlays", article_dir / "overlays")
    (article_dir / "textless").mkdir()
    (article_dir / "final").mkdir()
    (article_dir / "prompts").mkdir()
    (article_dir / "qa").mkdir()
    return article_dir


def test_import_textless_images_matches_shot_ids_from_filenames(tmp_path):
    article_dir = make_article_dir(tmp_path)
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    Image.new("RGB", (320, 180), "white").save(source_dir / "01.png")
    Image.new("RGB", (320, 180), "white").save(source_dir / "shot-02.png")
    report = import_textless_images.import_textless_images(str(article_dir), str(source_dir))
    assert report["matched"] == ["01", "02"]
    assert (article_dir / "textless" / "01.textless.png").exists()
    assert (article_dir / "textless" / "02.textless.png").exists()


def test_import_textless_images_prefers_exact_id_and_reports_relative_paths(tmp_path):
    article_dir = make_article_dir(tmp_path)
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    Image.new("RGB", (320, 180), "white").save(source_dir / "01.duplicate.png")
    Image.new("RGB", (320, 180), "white").save(source_dir / "01.PNG")
    Image.new("RGB", (320, 180), "white").save(source_dir / "unused.png")
    report = import_textless_images.import_textless_images(str(article_dir), str(source_dir))
    copied = {item["shot_id"]: item for item in report["copied"]}
    assert copied["01"]["source"] == "01.PNG"
    assert copied["01"]["destination"] == "textless/01.textless.png"
    assert "01.duplicate.png" in report["skipped"]
    assert not any(":" in value for value in [report["article_dir"], report["source_dir"], copied["01"]["destination"]])


def test_create_contact_sheet_creates_output_png(tmp_path):
    images_dir = tmp_path / "images"
    images_dir.mkdir()
    Image.new("RGB", (320, 180), "white").save(images_dir / "01.final.png")
    Image.new("RGB", (320, 180), "white").save(images_dir / "02.final.png")
    output = tmp_path / "contact-sheet.png"
    paths = create_contact_sheet.collect_images(str(images_dir))
    create_contact_sheet.create_contact_sheet(paths, str(output), cols=2)
    assert output.exists()


def test_export_article_assets_creates_zip_with_expected_files(tmp_path):
    article_dir = make_article_dir(tmp_path)
    (article_dir / "prompts" / "01.visual.md").write_text("prompt", encoding="utf-8")
    Image.new("RGB", (320, 180), "white").save(article_dir / "final" / "01.final.png")
    output = article_dir / "export" / "my-article-assets.zip"
    report = export_article_assets.export_article_assets(str(article_dir), str(output))
    assert output.exists()
    with zipfile.ZipFile(output) as archive:
        names = set(archive.namelist())
    assert "manifest.json" in names
    assert "overlays/01.overlay.json" in names
    assert "prompts/01.visual.md" in names
    assert "final/01.final.png" in names
    assert report["files_included"]


def test_run_asset_pipeline_runs_on_fixture_with_sample_textless_pngs(tmp_path):
    article_dir = make_article_dir(tmp_path)
    shutil.copy(ROOT / "examples" / "textless" / "01.textless.png", article_dir / "textless" / "01.textless.png")
    shutil.copy(ROOT / "examples" / "textless" / "02.textless.png", article_dir / "textless" / "02.textless.png")
    font = overlay_text.find_system_cjk_font() or "C:/Windows/Fonts/arial.ttf"
    report = run_asset_pipeline.run_asset_pipeline(str(article_dir), font=font, force=True)
    assert report["shots_total"] == 2
    assert report["overlays_validated"] == 2
    assert report["finals_generated"] == 2
    assert not report["missing_textless_images"]
    assert (article_dir / "final" / "01.final.png").exists()
    assert (article_dir / "contact-sheet.png").exists()
    assert report["export_zip"]
    assert report["contact_sheet"] == "contact-sheet.png"
    assert report["export_zip"].startswith("export/")
    assert ":" not in report["contact_sheet"]
    assert ":" not in report["export_zip"]
    schema = json.loads((ROOT / "schemas" / "asset-report.schema.json").read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(report)) == []
