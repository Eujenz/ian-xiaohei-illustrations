# Native Text Generation

Use this workflow when visual consistency is the top priority.

Contract:

```text
manifest -> native visual prompt with Chinese labels -> generated final image -> visual QA -> contact sheet -> asset bundle
```

The image model renders the Chinese labels directly. This follows the original `ian-xiaohei-illustrations` approach and avoids the mismatch that can happen when typed labels are layered onto a hand-drawn image later.

Prompt rules:

- Include the exact short Chinese labels in the prompt.
- Use at most 5-8 labels per image.
- Keep each label short, preferably 2-8 Chinese characters.
- Ask for handwritten Chinese annotations, not typeset UI labels.
- Use color sparingly: black for primary labels, orange for flow/path, red for warnings/results, blue for AI/system/secondary notes.
- Do not ask for a top-left title or structure-type label.
- Do not leave blank label placeholders for later overlay.

Known tradeoff:

Native text has the best style consistency but can produce typos. Prefer local image editing or one targeted regeneration if the label errors are unacceptable. Use legacy deterministic overlay only when exact text must be guaranteed.

Asset workflow:

1. Generate final PNGs from native-text prompts.
2. Save or import them into `final/`.
3. Run `import_native_images.py` if importing from an external folder.
4. Run `run_asset_pipeline.py` to create the contact sheet and ZIP bundle. This does not call `overlay_text.py` for `text_strategy: image_text_native`.
