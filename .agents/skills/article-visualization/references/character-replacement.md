# Character Replacement

v0.4 makes character profiles first-class, validated, discoverable, and swappable.

Character replacement may change:

- `manifest.character_id`
- per-shot `character_id` only when explicitly requested
- regenerated visual prompts
- the character visual identity block
- action phrasing
- deformation snippet when the resolver matches

Character replacement must not change:

- overlay JSON files
- overlay label text
- overlay coordinates
- textless image paths
- final image paths
- article source
- shot `core_idea`
- shot `metaphor`
- shot `structure_type`
- shot `anchor_type`

Deformation rules are resolved by `resolve_deformation_rules.py`. A rule is used only when mode, shot `structure_type`, and shot `anchor_type` match an allowed character rule. Sticker mode remains future work and remains blocked unless a character explicitly allows it.

To regenerate prompts after swapping, run `swap_character.py` with `--prompt-output-dir`, then run `run_pipeline.py` with `--manifest` pointing to the swapped manifest. This writes prompts into the swap output directory and leaves the original prompt files untouched.

Overlay JSON remains untouched because deterministic label text and coordinates are independent of character identity. Final images are not automatically regenerated unless textless images are available; prompt changes alone do not create new image assets.
