import json
from pathlib import Path

from conftest import load_script


ROOT = Path(__file__).resolve().parents[1]
render_prompt = load_script("render_prompt")


def make_prompt() -> tuple[str, dict]:
    manifest = json.loads((ROOT / "examples" / "manifest.sample.json").read_text(encoding="utf-8"))
    character = json.loads((ROOT / "characters" / "default" / "character.json").read_text(encoding="utf-8"))
    overlay = json.loads((ROOT / "examples" / "overlays" / "01.overlay.json").read_text(encoding="utf-8"))
    prompt = render_prompt.render_visual_prompt(manifest["shots"][0], character, manifest["style_profile"], {"mode": manifest["mode"]}, overlay)
    return prompt, overlay


def test_render_prompt_does_not_include_actual_chinese_overlay_label_text():
    prompt, overlay = make_prompt()
    for label in overlay["labels"]:
        assert label["text"] not in prompt


def test_render_prompt_includes_blank_placeholder_descriptions():
    prompt, _ = make_prompt()
    assert "blank handwritten note near messy input scraps" in prompt
    assert "Do not render readable Chinese text" in prompt


def test_render_prompt_includes_style_vitality_contract():
    prompt, _ = make_prompt()
    assert "## 7. Style vitality block" in prompt
    assert "deadpan serious expression" in prompt
    assert "strange conceptual work" in prompt
    assert "low-tech physical metaphor" in prompt
    assert "no PPT slide composition" in prompt


def test_native_text_prompt_includes_chinese_labels_for_llm_rendering():
    manifest = json.loads((ROOT / "examples" / "manifest.sample.json").read_text(encoding="utf-8"))
    character = json.loads((ROOT / "characters" / "default" / "character.json").read_text(encoding="utf-8"))
    overlay = json.loads((ROOT / "examples" / "overlays" / "01.overlay.json").read_text(encoding="utf-8"))
    prompt = render_prompt.render_visual_prompt(
        manifest["shots"][0],
        character,
        manifest["style_profile"],
        {"mode": manifest["mode"], "text_strategy": "image_text_native"},
        overlay,
    )
    for label in overlay["labels"]:
        assert label["text"] in prompt
    assert "Chinese handwritten labels" in prompt
    assert "Render the Chinese labels directly in the illustration" in prompt
    assert "Do not leave blank placeholder labels" in prompt
