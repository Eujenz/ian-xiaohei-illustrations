import inspect
from pathlib import Path

from conftest import load_script


ROOT = Path(__file__).resolve().parents[1]
run_article_planning = load_script("run_article_planning")
overlay_text = load_script("overlay_text")


def test_run_article_planning_completes_without_external_api(tmp_path):
    summary = run_article_planning.run(
        str(ROOT / "examples" / "article.sample.md"),
        str(tmp_path),
        "sample-article",
        "default",
        5,
    )
    assert summary["candidate_shots"] >= 3
    assert Path(summary["manifest_path"]).exists()
    assert len(summary["overlay_files"]) == summary["candidate_shots"]
    assert len(summary["prompt_files"]) == summary["candidate_shots"]
    assert summary["image_generation"] == "skipped"


def test_overlay_text_interface_remains_coordinate_renderer():
    signature = inspect.signature(overlay_text.overlay)
    assert list(signature.parameters) == ["image_path", "overlay_json", "output_path", "font_path"]
