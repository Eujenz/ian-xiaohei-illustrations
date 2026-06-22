import json
from pathlib import Path

from jsonschema import Draft202012Validator

from conftest import load_script


ROOT = Path(__file__).resolve().parents[1]
create_shot_list = load_script("create_shot_list")
create_manifest_draft = load_script("create_manifest_draft")
render_prompt = load_script("render_prompt")


def test_create_manifest_draft_creates_manifest_and_overlay_json_files(tmp_path):
    article = (ROOT / "examples" / "article.sample.md").read_text(encoding="utf-8")
    shot_list = create_shot_list.create_shot_list(article, "sample-article", 3)
    manifest = create_manifest_draft.create_manifest_draft(shot_list, "sample-article", "default", str(tmp_path))
    assert len(manifest["shots"]) == 3
    for shot in manifest["shots"]:
        assert (tmp_path / shot["overlay_file"]).exists()


def test_generated_overlay_json_passes_schema_validation(tmp_path):
    article = (ROOT / "examples" / "article.sample.md").read_text(encoding="utf-8")
    shot_list = create_shot_list.create_shot_list(article, "sample-article", 3)
    manifest = create_manifest_draft.create_manifest_draft(shot_list, "sample-article", "default", str(tmp_path))
    schema = json.loads((ROOT / "schemas" / "overlay.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    overlay_json = json.loads((tmp_path / manifest["shots"][0]["overlay_file"]).read_text(encoding="utf-8"))
    assert list(validator.iter_errors(overlay_json)) == []


def test_generated_visual_prompt_does_not_contain_overlay_chinese_labels(tmp_path):
    article = (ROOT / "examples" / "article.sample.md").read_text(encoding="utf-8")
    shot_list = create_shot_list.create_shot_list(article, "sample-article", 3)
    manifest = create_manifest_draft.create_manifest_draft(shot_list, "sample-article", "default", str(tmp_path))
    character = json.loads((ROOT / "characters" / "default" / "character.json").read_text(encoding="utf-8"))
    shot = manifest["shots"][0]
    overlay_json = json.loads((tmp_path / shot["overlay_file"]).read_text(encoding="utf-8"))
    prompt = render_prompt.render_visual_prompt(shot, character, manifest["style_profile"], {"mode": manifest["mode"]}, overlay_json)
    for label in overlay_json["labels"]:
        assert label["text"] not in prompt
