# Sticker Spec QA

v0.5 sticker spec QA is deterministic and does not inspect images.

Checks:

- Sticker count is 8, 16, 24, 32, or 40.
- Sticker canvas is at most 370 x 320 px.
- Main image is 240 x 240 px.
- Chat tab image is 96 x 74 px.
- Sticker dimensions are even numbers.
- Transparent background is required.
- Safe margin is at least 10 px.
- RGB color mode and 72 dpi or higher are expected.
- Each image is declared under 1 MB and ZIP under 60 MB.
- Phrase is short enough for chat readability.
- Situation, emotion, and pose are non-empty.
- No URLs, logos, ads, trademarks, or brand references.
- Sticker is not text-only.
- No OCR, image loading, background removal, or image generation in v0.5.
