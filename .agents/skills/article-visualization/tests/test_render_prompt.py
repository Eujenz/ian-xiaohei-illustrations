import json
from pathlib import Path

from conftest import load_script


ROOT = Path(__file__).resolve().parents[1]
render_prompt = load_script("render_prompt")


def test_render_prompt_does_not_include_actual_chinese_overlay_label_text():
    manifest = json.loads((ROOT / "examples" / "manifest.sample.json").read_text(encoding="utf-8"))
    character = json.loads((ROOT / "characters" / "default" / "character.json").read_text(encoding="utf-8"))
    overlay = json.loads((ROOT / "examples" / "overlays" / "01.overlay.json").read_text(encoding="utf-8"))
    prompt = render_prompt.render_visual_prompt(manifest["shots"][0], character, manifest["style_profile"], {"mode": manifest["mode"]}, overlay)
    assert "雜訊" not in prompt
    assert "判斷" not in prompt


def test_render_prompt_includes_blank_placeholder_descriptions():
    manifest = json.loads((ROOT / "examples" / "manifest.sample.json").read_text(encoding="utf-8"))
    character = json.loads((ROOT / "characters" / "default" / "character.json").read_text(encoding="utf-8"))
    overlay = json.loads((ROOT / "examples" / "overlays" / "01.overlay.json").read_text(encoding="utf-8"))
    prompt = render_prompt.render_visual_prompt(manifest["shots"][0], character, manifest["style_profile"], {"mode": manifest["mode"]}, overlay)
    assert "blank handwritten note near messy input scraps" in prompt
    assert "Do not render readable Chinese text" in prompt
