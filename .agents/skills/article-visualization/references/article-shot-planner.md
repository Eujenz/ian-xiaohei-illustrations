# Article Shot Planner

v0.2 adds a deterministic shot planner scaffold. It reads Markdown headings and paragraphs, applies simple marker-based heuristics, and creates a first-draft shot list for human or Codex review.

The planner is intentionally conservative:

- It does not call an LLM or external API.
- It does not generate images.
- It does not inspect images.
- It does not detect blank areas.
- It does not infer overlay positions from pixels.
- Overlay coordinates are draft presets only.
- Textless-first rendering remains mandatory.

Editorial review is expected. The generated shot list and manifest draft are starting points, not final art direction.
