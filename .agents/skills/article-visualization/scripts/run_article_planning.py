from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

try:
    from create_manifest_draft import create_manifest_draft
    from create_shot_list import create_shot_list
    from qa_text import qa_overlay
    from render_prompt import render_visual_prompt
except ImportError:
    from .create_manifest_draft import create_manifest_draft
    from .create_shot_list import create_shot_list
    from .qa_text import qa_overlay
    from .render_prompt import render_visual_prompt


ROOT = Path(__file__).resolve().parents[1]


def run(article: str, output_dir: str, article_slug: str, character_id: str = "default", max_shots: int = 5) -> dict:
    base = Path(output_dir)
    article_text = Path(article).read_text(encoding="utf-8")
    shot_list = create_shot_list(article_text, article_slug, max_shots)
    shot_list_path = base / "shot-list.generated.json"
    shot_list_path.write_text(json.dumps(shot_list, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = create_manifest_draft(shot_list, article_slug, character_id, output_dir)
    manifest_path = base / "manifest.generated.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    character = json.loads((ROOT / "characters" / character_id / "character.json").read_text(encoding="utf-8"))
    prompt_paths: list[str] = []
    qa_paths: list[str] = []
    overlay_paths: list[str] = []
    for shot in manifest["shots"]:
        overlay_path = base / shot["overlay_file"]
        overlay_paths.append(str(overlay_path))
        overlay_json = json.loads(overlay_path.read_text(encoding="utf-8"))
        prompt = render_visual_prompt(
            shot,
            character,
            manifest["style_profile"],
            {"mode": manifest["mode"], "text_strategy": manifest["text_strategy"]},
            overlay_json,
        )
        prompt_path = base / shot["visual_prompt_file"]
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(prompt, encoding="utf-8")
        prompt_paths.append(str(prompt_path))
        report = qa_overlay(overlay_json)
        qa_path = base / "qa" / f"{shot['id']}.generated.qa-text.json"
        qa_path.parent.mkdir(parents=True, exist_ok=True)
        qa_path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
        qa_paths.append(str(qa_path))
    return {
        "candidate_shots": len(shot_list["shots"]),
        "shot_list_path": str(shot_list_path),
        "manifest_path": str(manifest_path),
        "overlay_files": overlay_paths,
        "prompt_files": prompt_paths,
        "qa_text_reports": qa_paths,
        "image_generation": "external_native_text",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--article-slug", required=True)
    parser.add_argument("--character-id", default="default")
    parser.add_argument("--max-shots", type=int, default=5)
    args = parser.parse_args()
    summary = run(args.article, args.output_dir, args.article_slug, args.character_id, args.max_shots)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
