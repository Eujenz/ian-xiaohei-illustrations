import json
from pathlib import Path

from conftest import load_script


ROOT = Path(__file__).resolve().parents[1]
create_shot_list = load_script("create_shot_list")


def test_create_shot_list_returns_three_to_five_shots_for_sample_article():
    article = (ROOT / "examples" / "article.sample.md").read_text(encoding="utf-8")
    result = create_shot_list.create_shot_list(article, "sample-article", 5)
    assert 3 <= len(result["shots"]) <= 5


def test_each_generated_shot_has_required_fields():
    article = (ROOT / "examples" / "article.sample.md").read_text(encoding="utf-8")
    result = create_shot_list.create_shot_list(article, "sample-article", 5)
    required = {"id", "placement", "source_heading", "source_excerpt", "anchor_type", "structure_type", "theme", "core_idea", "metaphor", "character_action", "overlay_labels"}
    assert required.issubset(result["shots"][0])
    assert len(result["shots"][0]["overlay_labels"]) >= 2


def test_structure_type_mapping_covers_core_heuristics():
    assert create_shot_list.classify("pipeline 先 接著 最後")[0] == "workflow"
    assert create_shot_list.classify("不是 舊法 而是 新法")[0] == "before_after"
    assert create_shot_list.classify("系統 瓶頸 卡住 機器")[0] == "system_local"
    assert create_shot_list.classify("schema policy QA 分層")[0] == "method_layering"
    assert create_shot_list.classify("概念 隱喻 穩定 判斷")[0] == "concept_metaphor"
