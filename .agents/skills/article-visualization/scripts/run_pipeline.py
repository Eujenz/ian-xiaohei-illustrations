from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

try:
    from overlay_text import overlay
    from qa_text import qa_overlay
    from render_prompt import render_visual_prompt
    from validate_manifest import check_all_files_exist, validate_manifest_schema, validate_shot_list
except ImportError:
    from .overlay_text import overlay
    from .qa_text import qa_overlay
    from .render_prompt import render_visual_prompt
    from .validate_manifest import check_all_files_exist, validate_manifest_schema, validate_shot_list


ROOT = Path(__file__).resolve().parents[1]


def run(article_dir: str, force: bool = False, font: str | None = None) -> dict:
    base = Path(article_dir)
    manifest_path = base / "manifest.sample.json"
    if not manifest_path.exists():
        manifest_path = base / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    character = json.loads((ROOT / "characters" / manifest.get("character_id", "default") / "character.json").read_text(encoding="utf-8"))
    blocking = validate_manifest_schema(manifest) + validate_shot_list(manifest) + check_all_files_exist(manifest, str(base))
    summary = {"prompts_generated": 0, "text_qa_passed": 0, "text_qa_failed": 0, "overlays_rendered": 0, "waiting_for_textless_image": 0, "blocking_errors": blocking}
    if blocking:
        return summary
    for shot in manifest["shots"]:
        overlay_path = base / shot["overlay_file"]
        overlay_json = json.loads(overlay_path.read_text(encoding="utf-8"))
        report = qa_overlay(overlay_json)
        qa_path = base / "qa" / f"{shot['id']}.qa-text.json"
        qa_path.parent.mkdir(parents=True, exist_ok=True)
        qa_path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
        summary["text_qa_passed" if report.passed else "text_qa_failed"] += 1
        prompt_path = base / shot["visual_prompt_file"]
        if force or not prompt_path.exists():
            prompt = render_visual_prompt(shot, character, manifest.get("style_profile", {}), {"mode": manifest.get("mode", "article_visualization")}, overlay_json)
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(prompt, encoding="utf-8")
            summary["prompts_generated"] += 1
        print(f"IMAGE GENERATION SKIPPED: paste this prompt into your image tool: {prompt_path}")
        textless = base / shot["textless_image"]
        final = base / shot["final_image"]
        if textless.exists():
            if force or not final.exists():
                overlay(str(textless), overlay_json, str(final), font)
                summary["overlays_rendered"] += 1
        else:
            summary["waiting_for_textless_image"] += 1
    summary["blocking_errors"] += check_all_files_exist(manifest, str(base))
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--article-dir", required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--font")
    args = parser.parse_args()
    try:
        summary = run(args.article_dir, args.force, args.font)
    except Exception as exc:
        print(f"run_pipeline failed: {exc}")
        return 1
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if summary["blocking_errors"] or summary["text_qa_failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
