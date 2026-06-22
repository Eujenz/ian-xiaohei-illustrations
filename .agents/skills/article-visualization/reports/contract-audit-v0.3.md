# Contract Audit v0.3

## Summary

Status: pass after patch.

This audit inspected the repo-scoped Article Visualization Skill before adding v0.3 deterministic post-generation asset pipeline tools.

## Checklist

- Skill placement: pass. `.agents/skills/article-visualization/SKILL.md` and `agents/openai.yaml` exist.
- Textless-first policy: pass. `render_prompt.py` explicitly says not to render readable Chinese text and uses overlay `placeholder` text, not label text.
- Overlay contract: pass. `overlay_text.py` consumes image path, coordinate overlay JSON, optional font path, and output path. It does not OCR, detect blank areas, segment, infer layout, or reposition labels.
- Overlay schema: pass. `overlay.schema.json` requires `x`, `y`, `box_width`, `box_height`, and `font_size`, while allowing `anchor` and `placeholder`.
- QA separation: pass after patch. `qa_text.py` reads overlay JSON only and does not load images.
- Deformation rules: pass. `resolve_deformation_rules.py` requires structure type and anchor type matches, and blocks `line_sticker_set` deformation unless explicitly allowed.
- v0.2 planner boundaries: pass. Planning scripts are deterministic and do not call external APIs.

## Files Inspected

- `SKILL.md`
- `agents/openai.yaml`
- `scripts/overlay_text.py`
- `scripts/render_prompt.py`
- `scripts/qa_text.py`
- `scripts/resolve_deformation_rules.py`
- `scripts/create_shot_list.py`
- `scripts/create_manifest_draft.py`
- `scripts/run_article_planning.py`
- `schemas/overlay.schema.json`
- `schemas/manifest.schema.json`
- `characters/default/character.json`
- `examples/prompts/*.visual.md`
- `examples/overlays/*.overlay.json`

## Patches Made

- Rewrote `qa_text.py` with a clean simplified/traditional heuristic character set and preserved deterministic overlay-JSON-only behavior.
- Tightened bounds checking so a coordinate type error in one label does not skip checks for unrelated labels.

## Remaining Non-blockers

- Visual QA remains a documentation/stub workflow, as intended.
- Image generation remains intentionally external to this Skill.
