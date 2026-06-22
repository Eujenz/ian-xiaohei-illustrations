# Sticker Text QA

Sticker text QA validates sticker-set JSON and overlay JSON only.

The checks are deterministic: phrase length, non-empty phrase, no URLs, no brand references in sample content, no text-only pose, label boxes within canvas, and short daily-use phrase suitability.

No OCR is used in v0.5 or v0.6. Text QA does not inspect final PNG pixels.
