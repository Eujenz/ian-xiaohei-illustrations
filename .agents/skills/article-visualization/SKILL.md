---
name: article-visualization
description: Article visualization, Chinese article illustration, concept illustration, textless visual prompts, overlay Chinese labels, character replacement, and future LINE sticker preparation. Use for converting Chinese articles, methodology posts, and knowledge content into hand-drawn 16:9 visual assets with deterministic text overlay. Do not use for PPT decks, commercial key visuals, vector diagrams, photo editing, or direct AI-rendered Chinese text.
---

Use this skill for Chinese article visualization and concept illustration.

Default to textless image generation. Never ask image models to render readable Chinese text. Use blank visual placeholders in prompts and overlay JSON for all final Chinese labels.

Run visual QA conceptually before overlay. Run text QA after overlay JSON exists and before final asset export. Treat LINE sticker mode as future work, not v0.1.

Character must participate in the core visual action, never as decorative mascot.

Preserve the pipeline contract:

`manifest -> visual prompt -> textless image -> overlay JSON -> final image -> QA report`

v0.3 post-generation workflow:

After users paste generated visual prompts into an image tool and save textless PNGs, use `import_textless_images.py` or place files into `textless/`. Then run `run_asset_pipeline.py` to apply deterministic overlays, QA text, create a contact sheet, and export final assets.

v0.4 character replacement workflow:

Validate character profiles before use. Character replacement may change `manifest.character_id`, per-shot character IDs when explicitly requested, and regenerated visual prompts. It must not change overlay JSON, overlay label text, overlay coordinates, textless images, final images, article source, shot core ideas, metaphors, structure types, or anchor types.
