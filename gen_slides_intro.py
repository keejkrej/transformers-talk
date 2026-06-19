"""Generate slides 10-17 (background intro, applications, follow-ups) for the
'Attention Is All You Need' talk. Mirrors the helper API of /tmp/gen_slides.py.

Coordinates are absolute canvas; slides are 960x540 and laid out at:
    sx(i) = 100 + (i-1) * 1410
    Y = 100

Outputs /tmp/slides/slideN.json for N in 10..17.
"""
import json, math, os

W, H = 960, 540
GAP = 450
START_X, Y = 100, 100
TOTAL = 17  # for "N / 17" page numbers

# palette
BLUE_BG, BLUE_ST = "#e7f5ff", "#1971c2"
BLUE_LITE = "#d0ebff"
GREEN_BG, GREEN_ST = "#e6fcf5", "#0ca678"
VIOLET_BG, VIOLET_ST = "#f3f0ff", "#6741d9"
ORANGE_BG, ORANGE_ST = "#fff4e6", "#e8590c"
YELLOW_BG, YELLOW_ST = "#fff9db", "#f08c00"
RED_BG, RED_ST = "#fff5f5", "#fa5252"
GRAY_BG, GRAY_ST = "#f1f3f5", "#868e96"
INK, SUB = "#1e1e1e", "#495057"

def sx(i): return START_X + (i - 1) * (W + GAP)

def frame(i, name, notes):
    return {"type": "frame", "tempId": f"s{i}", "name": name,
            "x": sx(i), "y": Y, "width": W, "height": H,
            "customData": {"presenterNotes": notes}}

def title(i, t, size=34, y=40, color=INK, fam=7):
    return {"type": "text", "x": sx(i) + 56, "y": Y + y, "width": W - 112, "height": size + 12,
            "text": t, "fontSize": size, "fontFamily": fam, "strokeColor": color, "frameId": f"s{i}"}

def cap(i, t, x=56, y=H - 80, w=W - 112, size=16, color=SUB, fam=5):
    return {"type": "text", "x": sx(i) + x, "y": Y + y, "width": w, "height": size * 2 + 8,
            "text": t, "fontSize": size, "fontFamily": fam, "strokeColor": color, "frameId": f"s{i}"}

def txt(i, x, y, w, h, t, size=18, fam=5, color=INK):
    return {"type": "text", "x": sx(i) + x, "y": Y + y, "width": w, "height": h,
            "text": t, "fontSize": size, "fontFamily": fam, "strokeColor": color, "frameId": f"s{i}"}

def pageno(i, label):
    """Bottom-right page number, e.g. '10 / 17'."""
    return {"type": "text", "x": sx(i) + W - 90, "y": 590, "width": 60, "height": 22,
            "text": label, "fontSize": 18, "fontFamily": 5, "strokeColor": "#495057", "frameId": f"s{i}"}

def rect(tid, i, x, y, w, h, bg, st, label=None, lsize=18, lfam=7, rough=1):
    e = {"type": "rectangle", "tempId": tid, "x": sx(i) + x, "y": Y + y, "width": w, "height": h,
         "backgroundColor": bg, "strokeColor": st, "fillStyle": "solid", "roughness": rough,
         "roundness": {"type": 3}, "frameId": f"s{i}"}
    if label: e["label"] = {"text": label, "fontSize": lsize, "fontFamily": lfam}
    return e

def ell(tid, i, x, y, w, h, bg, st, label=None, lsize=18, lfam=7, rough=1):
    e = {"type": "ellipse", "tempId": tid, "x": sx(i) + x, "y": Y + y, "width": w, "height": h,
         "backgroundColor": bg, "strokeColor": st, "fillStyle": "solid", "roughness": rough,
         "frameId": f"s{i}"}
    if label: e["label"] = {"text": label, "fontSize": lsize, "fontFamily": lfam}
    return e

def arr(i, x, y, pts, start=None, end=None, stroke=INK, head="arrow", rough=1):
    a = {"type": "arrow", "x": sx(i) + x, "y": Y + y, "width": pts[-1][0], "height": pts[-1][1],
         "points": pts, "endArrowhead": head, "roughness": rough, "strokeColor": stroke, "frameId": f"s{i}"}
    if start: a["startBinding"] = {"elementId": start[0], "fixedPoint": start[1], "mode": "inside"}
    if end:   a["endBinding"] = {"elementId": end[0], "fixedPoint": end[1], "mode": "inside"}
    return a

def line(i, x, y, pts, stroke=INK, rough=1, width=2):
    return {"type": "line", "x": sx(i) + x, "y": Y + y, "width": pts[-1][0], "height": pts[-1][1],
            "points": pts, "roughness": rough, "strokeColor": stroke, "strokeWidth": width,
            "frameId": f"s{i}"}

slides = {}

# 10 — The task: machine translation
i = 10; s = []
s.append(frame(i, "The task",
    "* The paper targets machine translation: given text in one language, produce the same meaning in another.\n"
    "* This slide sets the stage before any architecture is on the table.\n"
    "* Translation is hard: word order, idioms, gender, ambiguity — all must be resolved from context."))
s.append(title(i, "The task: machine translation", size=32))
# Left bubble: English
s.append(rect("src", i, 60, 220, 320, 100, BLUE_BG, BLUE_ST,
    label="Hello, world", lsize=24, lfam=7, rough=0))
# Arrow
s.append(arr(i, 390, 270, [[0, 0], [180, 0]],
    start=("src", [1, 0.5]), end=("tgt", [0, 0.5]),
    stroke=INK, head="arrow", rough=0))
# Right bubble: Chinese
s.append(rect("tgt", i, 580, 220, 320, 100, ORANGE_BG, ORANGE_ST,
    label="你好，世界", lsize=26, lfam=7, rough=0))
# Sub-caption language labels
s.append(txt(i, 60, 200, 320, 22, "English", size=14, fam=5, color=SUB))
s.append(txt(i, 580, 200, 320, 22, "Chinese", size=14, fam=5, color=SUB))
# Question under the arrow
s.append(txt(i, 410, 240, 160, 32, "translate", size=18, fam=8, color=INK))
s.append(cap(i, "given text in one language, produce the same meaning in another"))
slides[i] = s

# 11 — Encoder-decoder RNN (prior approach)
i = 11; s = []
s.append(frame(i, "How prior models solved it",
    "* Before 2017, the dominant approach was an encoder–decoder RNN.\n"
    "* The encoder reads the source one token at a time and emits a single context vector c.\n"
    "* The decoder then generates the target one token at a time, conditioned on c."))
s.append(title(i, "How prior models solved it: encoder–decoder RNN", size=28))
# Encoder cells (4 source tokens)
src_tokens = ["x1", "x2", "x3", "x4"]
enc_ids = []
ex = 60; ey = 260; ew = 64; eh = 64; estep = 92
for j, tok in enumerate(src_tokens):
    tid = f"e{j}"
    enc_ids.append(tid)
    s.append(rect(tid, i, ex + j * estep, ey, ew, eh, BLUE_LITE, BLUE_ST,
        label=tok, lsize=18, lfam=7, rough=0))
# Encoder arrows
for j in range(len(enc_ids) - 1):
    s.append(arr(i, ex + j * estep + ew, ey + eh / 2, [[0, 0], [estep - ew, 0]],
        start=(enc_ids[j], [1, 0.5]), end=(enc_ids[j + 1], [0, 0.5]),
        stroke=INK, rough=0))
# Context vector (the bottleneck)
ctx_x = ex + 4 * estep + 20
s.append(rect("ctx", i, ctx_x, ey + eh / 2 - 24, 60, 48, YELLOW_BG, YELLOW_ST,
    label="c", lsize=22, lfam=8, rough=0))
# Arrow from last encoder to context
s.append(arr(i, ex + 3 * estep + ew, ey + eh / 2, [[0, 0], [ctx_x - (ex + 3 * estep + ew), 0]],
    start=(enc_ids[-1], [1, 0.5]), end=("ctx", [0, 0.5]),
    stroke=RED_ST, rough=0))
# Decoder cells (3 target tokens)
tgt_tokens = ["y1", "y2", "y3"]
dec_ids = []
dx = ctx_x + 120; dw = 64; dh = 64; dstep = 92
for j, tok in enumerate(tgt_tokens):
    tid = f"d{j}"
    dec_ids.append(tid)
    s.append(rect(tid, i, dx + j * dstep, ey, dw, dh, ORANGE_BG, ORANGE_ST,
        label=tok, lsize=18, lfam=7, rough=0))
# Context -> first decoder arrow
s.append(arr(i, ctx_x + 60, ey + eh / 2, [[0, 0], [dx - (ctx_x + 60), 0]],
    start=("ctx", [1, 0.5]), end=(dec_ids[0], [0, 0.5]),
    stroke=BLUE_ST, rough=0))
# Decoder arrows
for j in range(len(dec_ids) - 1):
    s.append(arr(i, dx + j * dstep + dw, ey + dh / 2, [[0, 0], [dstep - dw, 0]],
        start=(dec_ids[j], [1, 0.5]), end=(dec_ids[j + 1], [0, 0.5]),
        stroke=INK, rough=0))
# Encoder/decoder labels
s.append(txt(i, 60, 220, 380, 24, "encoder — reads the source", size=14, fam=5, color=BLUE_ST))
s.append(txt(i, dx - 20, 220, 300, 24, "decoder — emits the target", size=14, fam=5, color=ORANGE_ST))
s.append(cap(i, "one fixed-size vector c carries the entire source sentence"))
slides[i] = s

# 12 — Why the bottleneck hurts
i = 12; s = []
s.append(frame(i, "Why the bottleneck hurts",
    "* One vector c has to summarize the whole input sentence.\n"
    "* Long or complex sentences lose information in that squeeze.\n"
    "* Long-range dependencies — word A at the start matters for word Z at the end — are hard to preserve."))
s.append(title(i, "Why the bottleneck hurts", size=36))
# Wide row of source tokens
src = ["The", "cat", "that", "the", "dog", "chased", "yesterday", "ate", "the", "fish"]
n_src = len(src)
sw_total = 800
sw = sw_total / n_src
sy = 200
for j, tok in enumerate(src):
    s.append(rect(f"w{j}", i, 80 + j * sw, sy, sw - 4, 56, BLUE_LITE, BLUE_ST,
        label=tok, lsize=12, lfam=7, rough=0))
# Funnel-in arrows (each source word converges on the bottleneck dot)
bn_x = 480 - 24
bn_y = 320
for j in range(n_src):
    src_cx = 80 + j * sw + (sw - 4) / 2
    src_cy = sy + 28
    # Line from source bottom to bottleneck
    s.append(line(i, src_cx, src_cy, [[0, 0], [bn_x - src_cx + 24, bn_y - src_cy]],
        stroke=GRAY_ST, rough=1, width=1))
# The bottleneck itself — one small dot/circle
s.append(ell("bn", i, bn_x, bn_y, 48, 48, RED_BG, RED_ST,
    label="c", lsize=22, lfam=8, rough=0))
# Funnel-out arrows (bottleneck -> each output)
out = ["The", "fish", "was", "eaten"]
n_out = len(out)
ow_total = 600
ow = ow_total / n_out
oy = 400
for j, tok in enumerate(out):
    tgt_cx = 180 + j * ow + ow / 2
    tgt_cy = oy
    s.append(line(i, bn_x + 24, bn_y + 24, [[0, 0], [tgt_cx - (bn_x + 24), tgt_cy - (bn_y + 24)]],
        stroke=GRAY_ST, rough=1, width=1))
    s.append(rect(f"o{j}", i, 180 + j * ow, oy, ow - 4, 56, ORANGE_BG, ORANGE_ST,
        label=tok, lsize=14, lfam=7, rough=0))
s.append(cap(i, "every word of a long sentence must fit through one fixed-size vector", size=15))
slides[i] = s

# 13 — Where this landed: Google Translate
i = 13; s = []
s.append(frame(i, "Where this landed: Google Translate",
    "* The Transformer was adopted in production by Google Translate around 2018–2019.\n"
    "* It became the default backbone for translation quality across hundreds of language pairs.\n"
    "* The same architecture also spread to BERT (2018), GPT (2018), T5 (2019), and most modern LLMs."))
s.append(title(i, "Where this landed", size=38))
# Big circle "G" stand-in for Google
s.append(ell("g", i, 200, 130, 240, 240, BLUE_BG, BLUE_ST,
    label="G", lsize=120, lfam=7, rough=0))
# Right side: a single bold statement
s.append(rect("hero", i, 480, 180, 420, 130, VIOLET_BG, VIOLET_ST,
    label="Transformer in production\nGoogle Translate · ~2018",
    lsize=24, lfam=7, rough=0))
# Timeline arrow underneath
s.append(arr(i, 200, 410, [[0, 0], [560, 0]], stroke=GRAY_ST, head="arrow", rough=0))
# Three milestone dots on the timeline
for j, (xoff, lab, color) in enumerate([(0, "2014\nSeq2Seq", BLUE_ST),
                                          (280, "2017\nTransformer", VIOLET_ST),
                                          (560, "2018+\nBERT · GPT", ORANGE_ST)]):
    s.append(ell(f"m{j}", i, 200 + xoff - 12, 398, 24, 24, "#ffffff", color, rough=0))
    s.append(txt(i, 200 + xoff - 50, 430, 120, 50, lab, size=12, fam=5, color=SUB))
s.append(cap(i, "one paper, then the production stack switches", y=H - 50))
slides[i] = s

# 14 — The pivot problem & multilingual Transformer
i = 14; s = []
s.append(frame(i, "Why old Google Translate went via English",
    "* Before multilingual Transformers, Google Translate trained a separate model per language pair.\n"
    "* For N languages that is N(N−1)/2 models — so for 100 languages, almost 5,000.\n"
    "* To save work, every non-English pair was translated by pivoting through English: ZH → EN → JA.\n"
    "* Each hop compounds errors, and the meaning drifts.\n"
    "* Multilingual Transformer models (Johnson et al., 2016/2017) train ONE model on all language pairs,\n"
    "  prefixed with a target-language token. The model learns to translate directly between any pair."))
s.append(title(i, "The pivot problem", size=36))
# Left side: the old pivot path
s.append(txt(i, 60, 160, 380, 28, "Old: pivot through English", size=18, fam=7, color=RED_ST))
s.append(rect("zh", i, 60, 220, 100, 80, RED_BG, RED_ST, label="ZH", lsize=26, lfam=7, rough=0))
s.append(rect("en1", i, 200, 220, 100, 80, GRAY_BG, GRAY_ST, label="EN", lsize=26, lfam=7, rough=0))
s.append(rect("ja", i, 340, 220, 100, 80, RED_BG, RED_ST, label="JA", lsize=26, lfam=7, rough=0))
s.append(arr(i, 160, 260, [[0, 0], [40, 0]],
    start=("zh", [1, 0.5]), end=("en1", [0, 0.5]), stroke=GRAY_ST, head="arrow", rough=0))
s.append(arr(i, 300, 260, [[0, 0], [40, 0]],
    start=("en1", [1, 0.5]), end=("ja", [0, 0.5]), stroke=GRAY_ST, head="arrow", rough=0))
s.append(txt(i, 60, 320, 380, 24, "two hops · errors stack · meaning drifts", size=13, fam=5, color=SUB))
# Right side: direct multilingual
s.append(txt(i, 480, 160, 420, 28, "New: one multilingual model", size=18, fam=7, color=GREEN_ST))
s.append(rect("zh2", i, 480, 220, 100, 80, GREEN_BG, GREEN_ST, label="ZH", lsize=26, lfam=7, rough=0))
s.append(rect("mm", i, 640, 220, 140, 80, VIOLET_BG, VIOLET_ST, label="multi-\nlingual", lsize=15, lfam=7, rough=0))
s.append(rect("ja2", i, 820, 220, 100, 80, GREEN_BG, GREEN_ST, label="JA", lsize=26, lfam=7, rough=0))
s.append(arr(i, 580, 260, [[0, 0], [60, 0]],
    start=("zh2", [1, 0.5]), end=("mm", [0, 0.5]), stroke=GREEN_ST, head="arrow", rough=0))
s.append(arr(i, 780, 260, [[0, 0], [40, 0]],
    start=("mm", [1, 0.5]), end=("ja2", [0, 0.5]), stroke=GREEN_ST, head="arrow", rough=0))
s.append(txt(i, 480, 320, 420, 24, "one model · direct translation · no drift", size=13, fam=5, color=SUB))
# Bottom callout
s.append(rect("note", i, 60, 410, 840, 60, YELLOW_BG, YELLOW_ST,
    label="n languages → one model, not n(n−1)/2", lsize=22, lfam=8, rough=0))
slides[i] = s

# 15 — BERT vs GPT
i = 15; s = []
s.append(frame(i, "BERT and GPT: two halves of the same Transformer",
    "* The original Transformer had an encoder (reads the whole input) and a decoder (generates output step by step).\n"
    "* BERT (2018) drops the decoder — it's encoder-only, and learns by masking words and predicting them.\n"
    "* GPT (2018) drops the encoder — it's decoder-only, and learns by predicting the next token.\n"
    "* Same building block, two very different objectives."))
s.append(title(i, "BERT and GPT: two halves of the same Transformer", size=26))
# Left: BERT
s.append(txt(i, 60, 160, 380, 28, "BERT — encoder-only", size=18, fam=7, color=BLUE_ST))
s.append(txt(i, 60, 200, 380, 22, "reads the whole sentence, both directions", size=12, fam=5, color=SUB))
# Show: "I [MASK] cats" with arrows pointing at MASK
bert_tokens = ["I", "[MASK]", "cats"]
bert_ids = []
bx0 = 100; by0 = 240; bw = 80; bh = 64; bstep = 110
for j, tok in enumerate(bert_tokens):
    tid = f"b{j}"
    bert_ids.append(tid)
    bg = YELLOW_BG if j == 1 else BLUE_LITE
    st = YELLOW_ST if j == 1 else BLUE_ST
    s.append(rect(tid, i, bx0 + j * bstep, by0, bw, bh, bg, st,
        label=tok, lsize=18, lfam=7, rough=0))
# Arrows from neighbors into MASK
s.append(arr(i, bx0 + bw, by0 + bh / 2, [[0, 0], [bstep - bw, 0]],
    start=(bert_ids[0], [1, 0.5]), end=(bert_ids[1], [0, 0.5]), stroke=BLUE_ST, head="arrow", rough=0))
s.append(arr(i, bx0 + 2 * bstep, by0 + bh / 2, [[0, 0], [-(bstep - bw), 0]],
    start=(bert_ids[2], [0, 0.5]), end=(bert_ids[1], [1, 0.5]), stroke=BLUE_ST, head="arrow", rough=0))
s.append(rect("bpred", i, bx0 + bstep + bw / 2 - 60, by0 + bh + 40, 120, 56, GREEN_BG, GREEN_ST,
    label="love", lsize=22, lfam=7, rough=0))
s.append(arr(i, bx0 + bstep + bw / 2, by0 + bh, [[0, 0], [0, 40]],
    start=(bert_ids[1], [0.5, 1]), end=("bpred", [0.5, 0]), stroke=GREEN_ST, head="arrow", rough=0))
s.append(txt(i, 60, 380, 380, 22, "objective: predict the masked word", size=14, fam=5, color=BLUE_ST))
# Right: GPT
s.append(txt(i, 480, 160, 420, 28, "GPT — decoder-only", size=18, fam=7, color=ORANGE_ST))
s.append(txt(i, 480, 200, 420, 22, "reads left-to-right, predicts the next token", size=12, fam=5, color=SUB))
gpt_tokens = ["Once", "upon", "a"]
gpt_ids = []
gx0 = 520; gy0 = 240; gw = 80; gh = 64; gstep = 110
for j, tok in enumerate(gpt_tokens):
    tid = f"g{j}"
    gpt_ids.append(tid)
    s.append(rect(tid, i, gx0 + j * gstep, gy0, gw, gh, ORANGE_BG, ORANGE_ST,
        label=tok, lsize=18, lfam=7, rough=0))
# One-way arrows
for j in range(len(gpt_ids) - 1):
    s.append(arr(i, gx0 + j * gstep + gw, gy0 + gh / 2, [[0, 0], [gstep - gw, 0]],
        start=(gpt_ids[j], [1, 0.5]), end=(gpt_ids[j + 1], [0, 0.5]),
        stroke=ORANGE_ST, head="arrow", rough=0))
s.append(rect("gpred", i, gx0 + 2 * gstep + gw / 2 - 60, gy0 + gh + 40, 120, 56, GREEN_BG, GREEN_ST,
    label="time", lsize=22, lfam=7, rough=0))
s.append(arr(i, gx0 + 2 * gstep + gw / 2, gy0 + gh, [[0, 0], [0, 40]],
    start=(gpt_ids[-1], [0.5, 1]), end=("gpred", [0.5, 0]), stroke=GREEN_ST, head="arrow", rough=0))
s.append(txt(i, 480, 380, 420, 22, "objective: predict the next word", size=14, fam=5, color=ORANGE_ST))
slides[i] = s

# 16 — The N² problem with attention
i = 16; s = []
s.append(frame(i, "The N² problem with attention",
    "* Standard attention computes an N×N matrix of similarity scores between every pair of tokens.\n"
    "* Memory and compute both scale as N² in sequence length.\n"
    "* A 2000-token paragraph is fine. A 200k-token book is not. A million-token codebase is hopeless.\n"
    "* This is the bottleneck linear attention tries to fix."))
s.append(title(i, "The N² problem with attention", size=36))
# Three nested N×N squares (matrices) growing in size
sq_y0 = 170
for j, (size_px, n_label, color) in enumerate([(70, "n = 100", GRAY_ST),
                                                 (160, "n = 1k", ORANGE_ST),
                                                 (260, "n = 10k", RED_ST)]):
    xoff = 100 + j * 280
    # Background block (the matrix)
    s.append(rect(f"sq{j}", i, xoff, sq_y0, size_px, size_px, "#ffffff", color, rough=0))
    # Diagonal line
    s.append(line(i, xoff, sq_y0, [[0, 0], [size_px, size_px]],
        stroke=color, rough=1, width=2))
    s.append(txt(i, xoff, sq_y0 + size_px + 14, size_px, 24, n_label,
        size=14, fam=8, color=color))
# Cost annotations under each
for j, (cost, color) in enumerate([("10k cells", GRAY_ST), ("1M cells", ORANGE_ST), ("100M cells", RED_ST)]):
    xoff = 100 + j * 280
    s.append(txt(i, xoff, sq_y0 + 260 + 30, 260, 24, cost,
        size=16, fam=7, color=color))
# Big takeaway line
s.append(rect("takeaway", i, 60, 470, 840, 50, YELLOW_BG, YELLOW_ST,
    label="doubling sequence length = 4× the cost of attention", lsize=22, lfam=8, rough=0))
slides[i] = s

# 17 — Linear attention: reorder the multiplication
i = 17; s = []
s.append(frame(i, "Linear attention: reorder the multiplication",
    "* The trick: replace softmax with a feature map φ (e.g. elu+1). Then (Q Kᵀ) V can be regrouped.\n"
    "* Standard:  softmax(Q Kᵀ) V   →   cost O(N² d).\n"
    "* Linear:   φ(Q) ( φ(K)ᵀ V )   →   cost O(N d²).\n"
    "* The softmax forced the N×N matrix. Remove it, and matrix associativity lets you flip the order.\n"
    "* Trade-off: often weaker quality on small N. Big wins on long sequences."))
s.append(title(i, "Linear attention: reorder the multiplication", size=28))
# Left card: standard
s.append(rect("std", i, 60, 180, 400, 240, RED_BG, RED_ST,
    label="Standard\nsoftmax(Q Kᵀ) V",
    lsize=22, lfam=8, rough=0))
s.append(txt(i, 60, 340, 400, 28, "O(N² d)  ·  N×N matrix", size=18, fam=7, color=RED_ST))
s.append(txt(i, 60, 380, 400, 22, "softmax forces a full similarity matrix first", size=12, fam=5, color=SUB))
# Arrow
s.append(arr(i, 460, 300, [[0, 0], [40, 0]], stroke=INK, head="arrow", rough=0))
s.append(txt(i, 440, 270, 80, 28, "reorder", size=14, fam=8, color=INK))
# Right card: linear
s.append(rect("lin", i, 500, 180, 400, 240, GREEN_BG, GREEN_ST,
    label="Linear\nφ(Q) ( φ(K)ᵀ V )",
    lsize=22, lfam=8, rough=0))
s.append(txt(i, 500, 340, 400, 28, "O(N d²)  ·  no N×N matrix", size=18, fam=7, color=GREEN_ST))
s.append(txt(i, 500, 380, 400, 22, "(A B) C = A (B C) when shapes match", size=12, fam=5, color=SUB))
# Bottom callout
s.append(rect("note17", i, 60, 460, 840, 50, YELLOW_BG, YELLOW_ST,
    label="remove softmax, exploit associativity, win on long sequences", lsize=20, lfam=8, rough=0))
slides[i] = s

# Add page numbers to every slide
for i, s in slides.items():
    s.append(pageno(i, f"{i} / {TOTAL}"))

os.makedirs("/tmp/slides", exist_ok=True)
for i, s in slides.items():
    with open(f"/tmp/slides/slide{i}.json", "w") as f:
        json.dump(s, f)
    print(f"slide {i}: {len(s)} elements")
print("done")