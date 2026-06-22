# Sticker Visual QA

v0.6 sticker visual QA is deterministic image-file QA for post-generation assets.

Checks:

- Textless or final PNG exists.
- Static sticker images are at most 370 x 320 px.
- Main image is exactly 240 x 240 px.
- Chat tab image is exactly 96 x 74 px.
- Sticker dimensions are even numbers.
- File size is under 1 MB per image.
- PNG has alpha or transparency and contains transparent pixels.
- Image mode is not CMYK.
- DPI metadata is 72 or higher when present.
- Visible alpha bounds warn if content is closer than 10 px to the edge.

Non-goals:

- No OCR.
- No blank-area detection.
- No automatic label positioning.
- No background removal.
- No image generation.
- No LINE ZIP export.
