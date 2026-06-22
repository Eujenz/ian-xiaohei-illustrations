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
