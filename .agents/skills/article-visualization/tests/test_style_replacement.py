import json
from pathlib import Path

from conftest import load_script


ROOT = Path(__file__).resolve().parents[1]
validate_style_profile = load_script("validate_style_profile")
list_styles = load_script("list_styles")
swap_style = load_script("swap_style")
render_prompt = load_script("render_prompt")
validate_manifest = load_script("validate_manifest")


def load_style(style_id: str) -> dict:
    return json.loads((ROOT / "styles" / style_id / "style.json").read_text(encoding="utf-8"))


def load_character(character_id: str = "default") -> dict:
    return json.loads((ROOT / "characters" / character_id / "character.json").read_text(encoding="utf-8"))


def load_manifest() -> dict:
    return json.loads((ROOT / "examples" / "manifest.sample.json").read_text(encoding="utf-8"))


def load_overlay(shot_id: str = "01") -> dict:
    return json.loads((ROOT / "examples" / "overlays" / f"{shot_id}.overlay.json").read_text(encoding="utf-8"))


def test_builtin_styles_validate():
    for style_id in ("xiaohei-vitality", "technical-pencil", "editorial-ink"):
        assert validate_style_profile.validate_style_profile(load_style(style_id))["passed"]


def test_invalid_style_id_fails():
    style = load_style("technical-pencil")
    style["style_id"] = "Bad ID"
    report = validate_style_profile.validate_style_profile(style)
    assert not report["passed"]


def test_list_styles_finds_builtin_styles():
    rows = list_styles.list_styles(str(ROOT / "styles"))
    ids = {row["style_id"] for row in rows}
    assert {"xiaohei-vitality", "technical-pencil", "editorial-ink"}.issubset(ids)
    assert all(row["valid"] for row in rows)


def test_swap_style_changes_style_only_for_protected_fields():
    manifest = load_manifest()
    style = load_style("technical-pencil")
    swapped, changed = swap_style.swap_style(manifest, style, prompt_output_dir="prompts-style-swap")
    assert swapped["style_id"] == "technical-pencil"
    assert swapped["style_profile"]["style_id"] == "technical-pencil"
    assert changed["style_id"] == [None, "technical-pencil"]
    protected = ["overlay_file", "textless_image", "final_image", "core_idea", "metaphor", "structure_type", "anchor_type"]
    for before, after in zip(manifest["shots"], swapped["shots"]):
        for key in protected:
            assert before[key] == after[key]


def test_swapped_style_manifest_validates():
    swapped, _ = swap_style.swap_style(load_manifest(), load_style("editorial-ink"), prompt_output_dir="prompts-style-swap")
    assert validate_manifest.validate_manifest_schema(swapped) == []
    assert validate_manifest.validate_shot_list(swapped) == []


def test_render_prompt_changes_with_style_and_preserves_overlay_contract():
    manifest = load_manifest()
    shot = manifest["shots"][0]
    overlay = load_overlay("01")
    default_prompt = render_prompt.render_visual_prompt(shot, load_character(), manifest["style_profile"], {"mode": manifest["mode"]}, overlay)
    technical_prompt = render_prompt.render_visual_prompt(shot, load_character(), load_style("technical-pencil"), {"mode": manifest["mode"]}, overlay)
    editorial_prompt = render_prompt.render_visual_prompt(shot, load_character("lazy-yolk"), load_style("editorial-ink"), {"mode": manifest["mode"]}, overlay)
    assert default_prompt != technical_prompt
    assert technical_prompt != editorial_prompt
    assert "Technical Pencil Sketch" in technical_prompt
    assert "engineering notebook sketch" in technical_prompt
    assert "Editorial Ink Objects" in editorial_prompt
    assert "lazy egg-yolk operator" in editorial_prompt
    for prompt in (technical_prompt, editorial_prompt):
        assert "Do not render readable Chinese text" in prompt
        for label in overlay["labels"]:
            assert label["text"] not in prompt
