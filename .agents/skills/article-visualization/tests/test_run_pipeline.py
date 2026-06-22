import json
import shutil
from pathlib import Path

from conftest import load_script


ROOT = Path(__file__).resolve().parents[1]
run_pipeline = load_script("run_pipeline")
create_sample_assets = load_script("create_sample_assets")


def copy_examples(tmp_path: Path) -> Path:
    target = tmp_path / "examples"
    shutil.copytree(ROOT / "examples", target)
    return target


def test_run_pipeline_generates_prompts_and_qa_reports_without_image_generation(tmp_path):
    article_dir = copy_examples(tmp_path)
    shutil.rmtree(article_dir / "textless")
    (article_dir / "textless").mkdir()
    summary = run_pipeline.run(str(article_dir), force=True)
    assert summary["prompts_generated"] == 2
    assert summary["text_qa_passed"] == 2
    assert summary["waiting_for_textless_image"] == 2
    assert (article_dir / "prompts" / "01.visual.md").exists()
    assert (article_dir / "qa" / "01.qa-text.json").exists()


def test_run_pipeline_can_render_final_image_when_sample_textless_image_exists(tmp_path):
    article_dir = copy_examples(tmp_path)
    # Generate samples in the canonical examples dir, then copy only PNGs into temp.
    create_sample_assets.main()
    shutil.copy(ROOT / "examples" / "textless" / "01.textless.png", article_dir / "textless" / "01.textless.png")
    shutil.copy(ROOT / "examples" / "textless" / "02.textless.png", article_dir / "textless" / "02.textless.png")
    summary = run_pipeline.run(str(article_dir), force=True)
    assert summary["overlays_rendered"] == 2
    assert (article_dir / "final" / "01.final.png").exists()
