# Project notes — `transformers-talk`

Seminar talk slide deck for **"Attention Is All You Need"** (Vaswani et al., 2017),
built with the Excalidraw MCP and pushed to a workspace scene.

## User preferences

- **One object per page** (with a title if needed). Deviate from traditional
  PowerPoint style — prefer intuitive drawings that deliver one concept per
  slide. A slide is a diagram, not a bullet list.
- Keep code artifacts (generators, intermediate JSON, converted notes) in the
  repo so the work is reproducible.
- Record findings and preferences in `CLAUDE.md` so they transfer across sessions.

## Repo layout

```
assets/attention_is_all_you_need.pdf   # gitignored source
assets/attention_is_all_you_need.md    # pymupdf-extracted text
gen_slides.py                          # builds slides 1-9 (core paper)
gen_slides_intro.py                    # builds slides 10-17 (background + follow-ups)
slides/slideN.json                       # one JSON file per slide (intermediate)
```

Both scripts write `slides/slideN.json`. Each file is then pushed to the
Excalidraw scene one slide at a time via `edit_scene_content`.

## Excalidraw MCP findings

- Always call `read_excalidraw_format` before the first `edit_scene_content`
  in a session.
- Frames use `type: "frame"` with `tempId` for in-call references and a
  `name`. Frame child coordinates are **absolute canvas**, not relative to the
  frame — `x = START_X + (i-1)*(W+GAP)` for 1-indexed slides.
- `customData.presenterNotes` holds the narration for a frame.
- Shape-owned text goes on the shape's `label`, not as a floating text element.
- Arrows that point at shapes must include explicit `startBinding` and/or
  `endBinding`: `{ elementId, fixedPoint, mode: "inside" }`. For shape-to-shape
  arrows include both ends.
- Bindings track element movement (`mode: "inside"`), but the arrow's own
  `x`, `y`, and `points` are still authored manually and are *not* auto-shifted
  if you move the bound shape — geometry has to be re-authored on resize.
- `add` payloads must **not** include `id`; use `tempId` for cross-references
  within the same `edit_scene_content` call. `update` and `delete` use the real
  persisted IDs (load with `get_scene_content` first).
- No emoji in element text — the format guide forbids them.
- Stroke colors must include the `#` prefix.
- Fonts: `fontFamily: 7` (Lilita One) for titles, `5` (Excalifont) for body,
  `8` (Comic Shanns) for code/math.
- The MCP `edit_scene_content` will return `Internal error` on duplicate `add`
  keys or stray `|` characters in the JSON string. Also avoid concatenating
  multiple JSON arrays with `+` inside the string; send one JSON array per call.
  Split large payloads into smaller batches (frames alone, then text, then
  shapes, then arrows) to stay under the per-call size limit.
- `tempId` references only resolve **inside a single `edit_scene_content` call**.
  Once a frame is persisted, later calls must use its real `id` as `frameId`,
  and arrows must bind to real element `id`s.
- The `take_screenshot` MCP render does not show floating `text` elements; it
  only renders shape-owned labels, lines, and rectangles. To verify text, open
  the scene in the Excalidraw app or use `search_scene_content`.

## Talk structure (17 slides)

Slides 1-9 cover the original paper; slides 10-17 are background + follow-ups the
audience requested. Every slide now has a "N / 17" page number so the deck can
be reordered later.

**Core paper (slides 1-9)**

1. Title — paper, authors, venue.
2. Recurrence is sequential — chain of cells with a "wait" label.
3. Self-attention — one query attends to every other token.
4. Scaled dot-product attention — formula + linear pipeline.
5. Multi-head attention — fan-out / fan-in diagram (h=8, d_k=64).
6. Positional encoding — three sine waves of increasing frequency.
7. Transformer architecture — encoder ×6, decoder ×6, K/V cross-attention.
8. Results — three metric callouts (28.4 BLEU, 41.8 BLEU, 3.5 days).
9. Why it matters — one statement + chips of descendant models.

**Background & follow-ups (slides 10-17)**

10. The task — machine translation as a one-sentence problem statement.
11. How prior models solved it — encoder–decoder RNN and the context vector c.
12. Why the bottleneck hurts — one tiny vector must carry the whole sentence.
13. Where this landed — Google Translate adopted the Transformer (~2018).
14. The pivot problem — ZH → EN → JA vs. direct ZH → JA with one multilingual
    model (Johnson et al., 2016/2017).
15. BERT and GPT — encoder-only masked LM vs. decoder-only next-token
    prediction, two halves of the original architecture.
16. The N² problem — attention cost grows quadratically with sequence length.
17. Linear attention — the kernel reordering that drops attention back to O(N).
