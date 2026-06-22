# Rendering Policy

v0.1 is textless-first. Image prompts must never ask a model to render readable Chinese text. Overlay labels become blank visual placeholders in prompts, while actual Chinese label text remains only in overlay JSON, manifests, QA reports, and deterministic final PNGs.

Generation is overlay-after-generation: render or supply a textless image first, then apply coordinate-based labels with `overlay_text.py`.

`overlay_text.py` interface contract: consume image path, coordinate overlay JSON, optional font path, and output path. It must not perform OCR, blank-area detection, layout inference, semantic region detection, automatic repositioning, segmentation, whitespace detection, or AI/vision calls.

`structure_type` and `anchor_type` influence prompt rendering and optional character deformation. Character deformation is disabled by default. A deformation snippet may be injected only when mode, structure_type, and anchor_type match an allowed rule and the character remains recognizable.

LINE sticker image generation and package export remain future work. v0.5 may prepare sticker-set JSON, textless sticker prompts, overlay JSON drafts, and deterministic spec QA only.
