---
name: article-visualization
description: Article visualization, Chinese article illustration, concept illustration, native handwritten Chinese labels, character replacement, style replacement, and LINE sticker preparation. Use for converting Chinese articles, methodology posts, knowledge content, and sticker concepts into hand-drawn visual assets. Do not use for PPT decks, commercial key visuals, vector diagrams, photo editing, or UI mockups.
---

Use this skill for Chinese article visualization and concept illustration.

Default to native text image generation for article illustrations: ask the image model to render a few short handwritten Chinese labels directly in the image, following the original `ian-xiaohei-illustrations` approach. Visual consistency is higher priority than perfect deterministic text.

Use `text_strategy: image_text_native` as the primary article workflow. Keep labels short, sparse, and handwritten inside the visual prompt. Do not create blank label placeholders for later overlay unless the user explicitly asks for deterministic text safety.

Run visual QA conceptually before overlay. Run text QA after overlay JSON exists and before final asset export. Treat LINE sticker mode as future work, not v0.1.

Character must participate in the core visual action, never as decorative mascot.

Article prompts should carry Xiaohei-style vitality: pure white space, sparse wobbly black line art, clean low-tech physical metaphors, deadpan serious character action, short handwritten Chinese annotations, and a strange-but-clear object sketch feeling.

Primary native-text pipeline contract:

`manifest -> native visual prompt with Chinese labels -> generated final image -> visual QA -> contact sheet -> asset bundle`

Legacy deterministic overlay contract:

`manifest -> visual prompt -> textless image -> overlay JSON -> final image -> QA report`

Legacy post-generation overlay workflow:

After users paste generated visual prompts into an image tool and save textless PNGs, use `import_textless_images.py` or place files into `textless/`. Then run `run_asset_pipeline.py` to apply deterministic overlays, QA text, create a contact sheet, and export final assets.

Native text asset workflow:

After users generate final PNGs that already include Chinese handwritten labels, use `import_native_images.py` or place files into `final/`. Then run `run_asset_pipeline.py` to create a contact sheet and export final assets without calling `overlay_text.py`.

v0.4 character replacement workflow:

Validate character profiles before use. Character replacement may change `manifest.character_id`, per-shot character IDs when explicitly requested, and regenerated visual prompts. It must not change overlay JSON, overlay label text, overlay coordinates, textless images, final images, article source, shot core ideas, metaphors, structure types, or anchor types.

Style replacement workflow:

Validate style profiles before use. Style replacement may change `manifest.style_id`, `manifest.style_profile`, and regenerated visual prompts. It must not change article source, shot core ideas, metaphors, structure types, anchor types, or character identity. In native text mode, style profiles should guide both illustration and handwritten label appearance.

v0.5 sticker preparation workflow:

Sticker mode is separate from article visualization mode. Use `create_sticker_set.py` to draft sticker-set JSON and overlay JSON, `render_sticker_prompt.py` to create textless sticker prompts, and `qa_sticker_spec.py` to validate declared static sticker specs. Do not generate sticker images or export LINE ZIP packages in v0.5.

v0.6 sticker asset workflow:

After textless transparent PNGs exist, use `import_sticker_textless_images.py` or place files into `textless/`. Run `run_sticker_asset_pipeline.py` to apply deterministic overlays, run sticker image QA, create a contact sheet, and write a sticker asset report. This workflow does not call image generation APIs, OCR, blank-area detection, automatic label positioning, background removal, or LINE ZIP export. `overlay_text.py` remains coordinate-only and is not responsible for sticker-specific alpha preservation.
