import json
from pathlib import Path

from conftest import load_script


ROOT = Path(__file__).resolve().parents[1]
resolver = load_script("resolve_deformation_rules")


def character():
    return json.loads((ROOT / "characters" / "default" / "character.json").read_text(encoding="utf-8"))


def test_deformation_resolver_returns_no_deformation_when_no_rule_matches():
    shot = {"structure_type": "workflow", "anchor_type": "handoff"}
    assert resolver.resolve_deformation(shot, character(), "article_visualization") is None


def test_deformation_resolver_returns_funnel_body_for_shot_01():
    manifest = json.loads((ROOT / "examples" / "manifest.sample.json").read_text(encoding="utf-8"))
    rule = resolver.resolve_deformation(manifest["shots"][0], character(), "article_visualization")
    assert rule["id"] == "funnel_body"


def test_deformation_resolver_blocks_deformation_in_line_sticker_set_mode_by_default():
    manifest = json.loads((ROOT / "examples" / "manifest.sample.json").read_text(encoding="utf-8"))
    assert resolver.resolve_deformation(manifest["shots"][0], character(), "line_sticker_set") is None
