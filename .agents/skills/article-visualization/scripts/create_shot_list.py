from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


STRUCTURE_MARKERS = [
    ("workflow", "process", ["pipeline", "流程", "先", "接著", "最後", "步驟", "產生"]),
    ("before_after", "contrast", ["不是", "而是", "對比", "傳統", "更穩", "拆出來"]),
    ("system_local", "bottleneck", ["瓶頸", "卡住", "系統", "機器", "隔離", "局部"]),
    ("method_layering", "layering", ["schema", "policy", "QA", "分層", "定義", "檢查"]),
    ("concept_metaphor", "abstract_claim", ["概念", "隱喻", "想成", "判斷", "吵雜", "穩定"]),
]

METAPHORS = {
    "workflow": "a low-tech conveyor path moving from article notes to a blank image and then to labeled output",
    "before_after": "two worktables comparing unstable in-image text with stable overlay labels",
    "system_local": "a jammed text machine separated from a clean drawing machine",
    "method_layering": "stacked trays labeled only as blank placeholders for schema, policy, and QA layers",
    "concept_metaphor": "a hand-drawn funnel filtering noisy paper scraps into one useful judgment block",
}

ACTIONS = {
    "workflow": "handoff",
    "before_after": "sort",
    "system_local": "repair",
    "method_layering": "stack",
    "concept_metaphor": "carry",
}


def parse_markdown(text: str) -> list[dict]:
    sections: list[dict] = []
    heading = "Untitled"
    paragraphs: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#"):
            if paragraphs:
                sections.append({"heading": heading, "paragraphs": paragraphs})
                paragraphs = []
            heading = re.sub(r"^#+\s*", "", line)
        else:
            paragraphs.append(line)
    if paragraphs:
        sections.append({"heading": heading, "paragraphs": paragraphs})
    return sections


def classify(text: str) -> tuple[str, str]:
    for structure_type, anchor_type, markers in STRUCTURE_MARKERS:
        if any(marker in text for marker in markers):
            return structure_type, anchor_type
    return "concept_metaphor", "abstract_claim"


def short_label(text: str, fallback: str) -> str:
    cleaned = re.sub(r"[^\w\u4e00-\u9fff]+", "", text)
    chinese = "".join(ch for ch in cleaned if "\u4e00" <= ch <= "\u9fff")
    return (chinese[:4] or fallback)[:8]


def build_overlay_labels(structure_type: str, heading: str) -> list[dict]:
    presets = {
        "workflow": ["前段", "後段"],
        "before_after": ["舊法", "新法"],
        "system_local": ["瓶頸", "隔離"],
        "method_layering": ["規則", "檢查"],
        "concept_metaphor": ["雜訊", "判斷"],
    }
    labels = presets.get(structure_type, [short_label(heading, "重點"), "下一步"])
    return [
        {"id": "label_01", "text": labels[0], "anchor": "primary_anchor", "placeholder": "blank note near the primary visual anchor", "max_chars": 8},
        {"id": "label_02", "text": labels[1], "anchor": "secondary_anchor", "placeholder": "blank callout near the secondary visual anchor", "max_chars": 8},
    ]


def create_shot_list(article_text: str, article_slug: str = "sample-article", max_shots: int = 5) -> dict:
    sections = parse_markdown(article_text)
    candidates: list[dict] = []
    for section in sections:
        paragraph = " ".join(section["paragraphs"])
        structure_type, anchor_type = classify(section["heading"] + " " + paragraph)
        candidates.append({
            "source_heading": section["heading"],
            "source_excerpt": paragraph[:180],
            "anchor_type": anchor_type,
            "structure_type": structure_type,
            "theme": section["heading"],
            "core_idea": paragraph[:90],
            "metaphor": METAPHORS.get(structure_type, METAPHORS["concept_metaphor"]),
            "character_action": ACTIONS.get(structure_type, "carry"),
            "overlay_labels": build_overlay_labels(structure_type, section["heading"]),
        })
    selected = candidates[:max_shots]
    while len(selected) < min(3, max_shots) and candidates:
        selected.append(candidates[len(selected) % len(candidates)])
    shots = []
    for index, shot in enumerate(selected, start=1):
        shots.append({"id": f"{index:02d}", "placement": "body" if index > 1 else "hero", **shot})
    return {"article_slug": article_slug, "shots": shots}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-shots", type=int, default=5)
    args = parser.parse_args()
    article_path = Path(args.article)
    result = create_shot_list(article_path.read_text(encoding="utf-8"), article_path.stem, args.max_shots)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
