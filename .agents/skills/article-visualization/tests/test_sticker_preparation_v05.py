import copy
import inspect
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from conftest import load_script


ROOT = Path(__file__).resolve().parents[1]
create_sticker_set = load_script("create_sticker_set")
qa_sticker_spec = load_script("qa_sticker_spec")
render_sticker_prompt = load_script("render_sticker_prompt")
overlay_text = load_script("overlay_text")


def make_sticker_set(tmp_path: Path) -> tuple[Path, dict]:
    sticker_set = create_sticker_set.create_sticker_set("sample-alt", "sample-sticker-set", str(tmp_path), 8)
    return tmp_path / "sticker-set.sample.json", sticker_set


def test_sticker_set_schema_accepts_valid_sample(tmp_path):
    _, sticker_set = make_sticker_set(tmp_path)
    schema = json.loads((ROOT / "schemas" / "sticker-set.schema.json").read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(sticker_set)) == []


def test_sticker_set_schema_rejects_invalid_count(tmp_path):
    _, sticker_set = make_sticker_set(tmp_path)
    sticker_set["count"] = 9
    schema = json.loads((ROOT / "schemas" / "sticker-set.schema.json").read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(sticker_set))


def test_sticker_set_schema_rejects_missing_phrase(tmp_path):
    _, sticker_set = make_sticker_set(tmp_path)
    del sticker_set["stickers"][0]["phrase"]
    schema = json.loads((ROOT / "schemas" / "sticker-set.schema.json").read_text(encoding="utf-8"))
    assert list(Draft202012Validator(schema).iter_errors(sticker_set))


def test_create_sticker_set_creates_8_stickers_plus_main_and_tab_overlays(tmp_path):
    make_sticker_set(tmp_path)
    overlays = sorted((tmp_path / "overlays").glob("*.json"))
    names = {path.name for path in overlays}
    assert len([name for name in names if name[0].isdigit()]) == 8
    assert {"main.overlay.json", "tab.overlay.json"}.issubset(names)


def test_generated_overlays_have_coordinate_labels_inside_canvas(tmp_path):
    make_sticker_set(tmp_path)
    for overlay_path in (tmp_path / "overlays").glob("*.json"):
        overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
        canvas = overlay["canvas"]
        for label in overlay["labels"]:
            assert label["x"] >= 0
            assert label["y"] >= 0
            assert label["x"] + label["box_width"] <= canvas["width"]
            assert label["y"] + label["box_height"] <= canvas["height"]


def test_qa_sticker_spec_passes_valid_sample(tmp_path):
    sticker_set_path, _ = make_sticker_set(tmp_path)
    report = qa_sticker_spec.qa_sticker_spec(str(sticker_set_path))
    assert report["passed"]


def test_qa_sticker_spec_rejects_invalid_canvas_size(tmp_path):
    sticker_set_path, sticker_set = make_sticker_set(tmp_path)
    overlay_path = tmp_path / sticker_set["stickers"][0]["overlay_file"]
    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
    overlay["canvas"]["width"] = 372
    overlay_path.write_text(json.dumps(overlay, ensure_ascii=False), encoding="utf-8")
    report = qa_sticker_spec.qa_sticker_spec(str(sticker_set_path))
    assert not report["passed"]


def test_qa_sticker_spec_rejects_url_in_phrase(tmp_path):
    sticker_set_path, sticker_set = make_sticker_set(tmp_path)
    sticker_set["stickers"][0]["phrase"] = "http://x"
    sticker_set_path.write_text(json.dumps(sticker_set, ensure_ascii=False), encoding="utf-8")
    report = qa_sticker_spec.qa_sticker_spec(str(sticker_set_path))
    assert not report["passed"]


def test_render_sticker_prompt_does_not_include_actual_chinese_phrase(tmp_path):
    sticker_set_path, sticker_set = make_sticker_set(tmp_path)
    character = json.loads((ROOT / "characters" / "sample-alt" / "character.json").read_text(encoding="utf-8"))
    overlay = json.loads((tmp_path / sticker_set["stickers"][0]["overlay_file"]).read_text(encoding="utf-8"))
    prompt = render_sticker_prompt.render_sticker_prompt(sticker_set["stickers"][0], sticker_set, character, overlay)
    assert sticker_set["stickers"][0]["phrase"] not in prompt
    assert "Do not render readable Chinese text" in prompt
    assert "Transparent background" in prompt


def test_sticker_mode_does_not_inject_deformation_by_default(tmp_path):
    _, sticker_set = make_sticker_set(tmp_path)
    character = json.loads((ROOT / "characters" / "sample-alt" / "character.json").read_text(encoding="utf-8"))
    overlay = json.loads((tmp_path / sticker_set["stickers"][0]["overlay_file"]).read_text(encoding="utf-8"))
    prompt = render_sticker_prompt.render_sticker_prompt(sticker_set["stickers"][0], sticker_set, character, overlay)
    assert "No character deformation in sticker mode" in prompt


def test_overlay_text_interface_still_unchanged_for_sticker_preparation():
    signature = inspect.signature(overlay_text.overlay)
    assert list(signature.parameters) == ["image_path", "overlay_json", "output_path", "font_path"]
