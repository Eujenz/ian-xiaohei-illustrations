# Sticker Design Policy

Sticker mode is a preparation and post-generation asset scaffold. v0.5 models sticker data, textless prompts, overlay JSON drafts, and deterministic spec QA. v0.6 accepts externally created textless transparent PNGs and continues with deterministic overlays, image QA, contact sheet generation, and an asset report.

Sticker mode does not call image generation APIs, remove backgrounds, infer blank areas, auto-position labels, OCR rendered text, or export a LINE package.

Sticker mode is separate from article illustration mode. Use one simple character, a strong silhouette, transparent background assumptions, and daily-conversation intent. Avoid complex article metaphors, dense scenes, and text-only stickers.

Actual Chinese phrases must stay in sticker-set JSON and overlay JSON. Sticker prompts must say not to render readable Chinese text and must ask for a blank sign, bubble, or label area for later overlay.

The overlay JSON remains the only source of sticker text position. Keep `overlay_text.py` coordinate-only; any future automatic position suggestion must output the same overlay JSON format before rendering.

Avoid ads, URLs, trademarks, logos, brand references, copyrighted characters, political content, religious persuasion, sexual content, violent content, and anything unsuitable for ordinary chat.
