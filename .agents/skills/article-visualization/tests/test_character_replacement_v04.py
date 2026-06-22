import copy
import inspect
import json
from pathlib import Path

from conftest import load_script


ROOT = Path(__file__).resolve().parents[1]
validate_character_profile = load_script("validate_character_profile")
list_characters = load_script("list_characters")
swap_character = load_script("swap_character")
render_prompt = load_script("render_prompt")
resolve_deformation_rules = load_script("resolve_deformation_rules")
overlay_text = load_script("overlay_text")
validate_manifest = load_script("validate_manifest")


def load_character(character_id: str) -> dict:
    return json.loads((ROOT / "characters" / character_id / "character.json").read_text(encoding="utf-8"))


def load_manifest() -> dict:
    return json.loads((ROOT / "examples" / "manifest.sample.json").read_text(encoding="utf-8"))


def load_overlay(shot_id: str = "01") -> dict:
    return json.loads((ROOT / "examples" / "overlays" / f"{shot_id}.overlay.json").read_text(encoding="utf-8"))


def test_default_character_validates():
    assert validate_character_profile.validate_character_profile(load_character("default"))["passed"]


def test_sample_alt_character_validates():
    assert validate_character_profile.validate_character_profile(load_character("sample-alt"))["passed"]


def test_invalid_character_id_fails():
    character = load_character("sample-alt")
    character["character_id"] = "Bad ID"
    report = validate_character_profile.validate_character_profile(character)
    assert not report["passed"]


def test_duplicate_action_ids_fail():
    character = load_character("sample-alt")
    character["action_library"][1]["id"] = character["action_library"][0]["id"]
    report = validate_character_profile.validate_character_profile(character)
    assert not report["passed"]
    assert any("duplicate action id" in error for error in report["errors"])


def test_duplicate_deformation_rule_ids_fail():
    character = load_character("sample-alt")
    character["deformation_rules"][1]["id"] = character["deformation_rules"][0]["id"]
    report = validate_character_profile.validate_character_profile(character)
    assert not report["passed"]
    assert any("duplicate deformation rule id" in error for error in report["errors"])


def test_missing_core_actor_flag_fails():
    character = load_character("sample-alt")
    del character["core_role"]["must_be_core_actor"]
    report = validate_character_profile.validate_character_profile(character)
    assert not report["passed"]


def test_list_characters_finds_default_and_sample_alt():
    rows = list_characters.list_characters(str(ROOT / "characters"))
    ids = {row["character_id"] for row in rows}
    assert {"default", "sample-alt"}.issubset(ids)
    assert all(row["valid"] for row in rows)


def test_swap_character_changes_character_id_only_for_protected_fields():
    manifest = load_manifest()
    swapped, changed = swap_character.swap_character(manifest, "sample-alt", prompt_output_dir="prompts-character-swap")
    assert swapped["character_id"] == "sample-alt"
    assert changed["character_id"] == ["default", "sample-alt"]
    protected = ["overlay_file", "textless_image", "final_image", "core_idea", "metaphor", "structure_type", "anchor_type"]
    for before, after in zip(manifest["shots"], swapped["shots"]):
        for key in protected:
            assert before[key] == after[key]


def test_swapped_manifest_validates():
    manifest = load_manifest()
    swapped, _ = swap_character.swap_character(manifest, "sample-alt", prompt_output_dir="prompts-character-swap")
    assert validate_manifest.validate_manifest_schema(swapped) == []
    assert validate_manifest.validate_shot_list(swapped) == []


def test_render_prompt_with_sample_alt_changes_character_block_and_preserves_textless_rule():
    manifest = load_manifest()
    shot = manifest["shots"][0]
    overlay = load_overlay("01")
    default_prompt = render_prompt.render_visual_prompt(shot, load_character("default"), manifest["style_profile"], {"mode": manifest["mode"]}, overlay)
    alt_prompt = render_prompt.render_visual_prompt(shot, load_character("sample-alt"), manifest["style_profile"], {"mode": manifest["mode"]}, overlay)
    assert default_prompt != alt_prompt
    assert "small pebble-like body" in alt_prompt
    assert "Do not render readable Chinese text" in alt_prompt
    for label in overlay["labels"]:
        assert label["text"] not in alt_prompt


def test_deformation_resolver_behavior_remains_condition_based():
    manifest = load_manifest()
    default_rule = resolve_deformation_rules.resolve_deformation(manifest["shots"][0], load_character("default"), "article_visualization")
    assert default_rule["id"] == "funnel_body"
    no_rule = resolve_deformation_rules.resolve_deformation(manifest["shots"][1], load_character("sample-alt"), "line_sticker_set")
    assert no_rule is None


def test_overlay_text_public_interface_is_unchanged():
    signature = inspect.signature(overlay_text.overlay)
    assert list(signature.parameters) == ["image_path", "overlay_json", "output_path", "font_path"]
