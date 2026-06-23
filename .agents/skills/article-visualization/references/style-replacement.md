# Style Replacement

Style replacement makes visual styles first-class and swappable, parallel to character replacement.

Style replacement may change:

- `manifest.style_id`
- `manifest.style_profile`
- regenerated visual prompts
- prompt output paths when explicitly requested

Style replacement must not change:

- overlay JSON files
- overlay label text
- overlay coordinates
- textless image paths unless the caller explicitly creates a new article directory
- final image paths unless the caller explicitly creates a new article directory
- article source
- shot `theme`
- shot `core_idea`
- shot `metaphor`
- shot `structure_type`
- shot `anchor_type`
- character profile

Available starter styles:

- `xiaohei-vitality`: sparse white-space, wobbly black line, strange low-tech physical metaphors, deadpan character action.
- `technical-pencil`: engineering notebook sketch, cutaway machines, gauges, restrained accents.
- `editorial-ink`: minimal editorial object metaphor with confident ink line and surreal props.

Use `validate_style_profile.py` before adding a style. Use `list_styles.py` to inspect available styles. Use `swap_style.py` to apply a style profile to a manifest and optionally redirect regenerated prompts to a new prompt directory.

The text contract remains unchanged: style prompts may ask for blank plaques, blank callouts, and blank tags, but actual Chinese label text stays in overlay JSON and is rendered by `overlay_text.py`.
