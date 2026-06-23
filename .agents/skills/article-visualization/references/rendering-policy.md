# Rendering Policy

Primary article rendering is native-text-first. Image prompts should ask the model to render a few short handwritten Chinese labels directly in the image, following the original `ian-xiaohei-illustrations` method. Visual consistency is higher priority than deterministic text precision.

Use `text_strategy: image_text_native` for ordinary article visualization. Generated PNGs under `final/` are already the final assets; `run_asset_pipeline.py` should create a contact sheet and export the bundle without applying `overlay_text.py`.

Article prompts should include style vitality: pure white space, sparse wobbly black line art, low-tech physical metaphors, a deadpan square worker doing the core conceptual action, short handwritten Chinese annotations, and a strange-but-clean product sketch feeling.

Legacy deterministic overlay is still available only when exact text is more important than visual unity. In that mode, image prompts must stay textless and `overlay_text.py` consumes explicit coordinates.

`overlay_text.py` interface contract: consume image path, coordinate overlay JSON, optional font path, and output path. It must not perform OCR, blank-area detection, layout inference, semantic region detection, automatic repositioning, segmentation, whitespace detection, or AI/vision calls.

`structure_type` and `anchor_type` influence prompt rendering and optional character deformation. Character deformation is disabled by default. A deformation snippet may be injected only when mode, structure_type, and anchor_type match an allowed rule and the character remains recognizable.

LINE sticker image generation and package export remain future work. v0.5 may prepare sticker-set JSON, textless sticker prompts, overlay JSON drafts, and deterministic spec QA only.
