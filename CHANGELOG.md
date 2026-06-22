# Changelog

## v0.6.0

- Added post-generation static sticker asset pipeline.
- Added sample transparent sticker textless asset generation.
- Added sticker textless PNG importer for common file names.
- Added deterministic sticker image QA for PNG dimensions, file size, transparency, DPI, and margin warnings.
- Added sticker contact sheet generation.
- Added `run_sticker_asset_pipeline.py` and `sticker-asset-report.schema.json`.
- Added pytest coverage for sticker textless imports, image QA, final PNG rendering, contact sheet generation, and asset report schema.
- Preserved the `overlay_text.py` coordinate-only boundary; v0.6 does not add image generation, OCR, automatic positioning, background removal, or LINE ZIP export.

## v0.5.0

- Added static sticker preparation scaffold.
- Added real `sticker-set.schema.json` for declared sticker specs.
- Added `create_sticker_set.py`, `render_sticker_prompt.py`, and `qa_sticker_spec.py`.
- Added sticker design policy, prompt template, and deterministic sticker QA references.
- Added sample sticker-set JSON, overlay drafts, prompt examples, and sticker spec QA report.
- Added pytest coverage for sticker schema, prompt textless contract, overlay bounds, and spec QA.

## v0.4.1

- Scoped character prompt comparison by manifest when `--manifest` is provided.
- Extra prompt files outside the manifest are now reported as warnings instead of noisy missing swapped prompts.

## v0.4.0

- Added character profile validation with deterministic schema and business-rule checks.
- Added character discovery, safe template creation, manifest character swapping, and prompt comparison tools.
- Added generic `sample-alt` character profile.
- Hardened character prompt rendering while preserving textless-first and overlay-only contracts.
- Added character replacement documentation and pytest coverage.

## v0.3.0

- Added v0.3 contract audit report.
- Added `import_textless_images.py` for importing externally generated textless PNGs by shot filename.
- Implemented deterministic contact sheet generation.
- Added article asset ZIP export with an adjacent JSON report.
- Added `run_asset_pipeline.py` for the post-generation phase: text QA, deterministic overlays, contact sheet, and asset bundle.
- Added `asset-report.schema.json`.
- Added tests for import, contact sheet, export, asset pipeline, and continued prompt/overlay contracts.

## v0.2.0

- Added deterministic Markdown article shot planner scaffold.
- Added `create_shot_list.py` for heuristic shot-list generation without LLMs or external APIs.
- Added `create_manifest_draft.py` for manifest draft and overlay JSON draft generation.
- Added `run_article_planning.py` to generate shot list, manifest, overlays, prompts, and text QA reports.
- Updated `shot-list.schema.json` for v0.2 planner output.
- Added generated example shot list, manifest, overlays, visual prompts, and QA reports.
- Added pytest coverage for planner heuristics, manifest draft generation, generated overlays, prompt textless contract, and planning runner.

## v0.1.0

- Added repo-scoped `article-visualization` Codex Skill scaffold under `.agents/skills/article-visualization/`.
- Added textless-first visual prompt rendering.
- Added coordinate-only `overlay_text.py` renderer for deterministic Chinese label overlay.
- Added `qa_text.py` for deterministic overlay JSON text QA.
- Added `validate_manifest.py` for manifest schema and file reference checks.
- Added resumable `run_pipeline.py`.
- Added deterministic sample textless assets, final PNG fixtures, overlay JSON, QA reports, and visual prompts.
- Added pytest coverage for schemas, prompt rendering, deformation rules, text QA, overlay rendering, and pipeline execution.
