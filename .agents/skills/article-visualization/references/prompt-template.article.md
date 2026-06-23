# Article Prompt Template

1. Canvas spec
2. Scene concept
3. Character block
4. Conditional deformation block
5. Chinese handwritten labels
6. Text rendering priority
7. Style vitality block
8. Negative constraints

Native text mode is the default. Include the exact short Chinese labels in the image prompt and ask the model to render them directly as handwritten annotations integrated with the illustration.

Use legacy textless overlay mode only when exact deterministic text is required. In that mode, do not render readable Chinese text and leave blank placeholders for labels that will be added later by `overlay_text.py`.

Style vitality block:

- Pure white background with sparse, slightly wobbly black hand-drawn line art.
- Use clean low-tech physical metaphors instead of formal diagrams.
- Make the character do the strange conceptual work inside the mechanism.
- Keep the expression deadpan and serious, not cute.
- Use a few short handwritten Chinese annotations, not long explanations.
- Preserve large whitespace and avoid PPT, UI, corporate vector, dense chart, and title-block composition.
