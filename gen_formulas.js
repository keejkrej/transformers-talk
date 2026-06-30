#!/usr/bin/env node
/*
 * gen_formulas.js — render LaTeX formulas to standalone SVG files for the
 * transformers-talk slide deck.
 *
 * Uses mathjax-node (pure JS, no TeX install required). SVGs are written to
 * assets/formulas/<name>.svg so the math is crisp and reproducible. Drag the
 * SVGs into the Excalidraw scene manually (the MCP cannot upload binaries).
 *
 * Usage:
 *   node gen_formulas.js            # render every formula in FORMULAS
 *   node gen_formulas.js attention  # render only formulas whose name matches
 *
 * Requirements (installed on first run via npx):
 *   npm i -g mathjax-node   # or let the script auto-install locally
 */

const fs = require("fs");
const path = require("path");

const OUT_DIR = path.join(__dirname, "assets", "formulas");

// One entry per formula that appears on a slide. Keep names stable so the
// Excalidraw hand-placement stays consistent across regenerations.
const FORMULAS = [
  // Slide 1 — Title
  { name: "s01_attention_core", tex: "\\text{Attention}(Q,K,V)=\\operatorname{softmax}\\!\\left(\\frac{QK^{T}}{\\sqrt{d_k}}\\right)V" },
  { name: "s01_transformer_stack", tex: "\\text{Transformer}=6\\times\\text{Encoder}+6\\times\\text{Decoder}" },

  // Slide 2 — Recurrence is sequential
  { name: "s02_rnn_step", tex: "h_t = f(h_{t-1},\\, x_t)" },
  { name: "s02_no_parallelism", tex: "\\text{parallelism: none — } h_t \\text{ blocked until } h_{t-1} \\text{ is ready}" },

  // Slide 3 — Self-attention
  { name: "s03_path_length", tex: "\\text{path length: } O(1) \\text{ between any pair}" },
  { name: "s03_attention_i", tex: "\\text{attention}(i)=\\operatorname{softmax}\\!\\left(\\frac{Q_i K^{T}}{\\sqrt{d_k}}\\right)V" },

  // Slide 4 — Scaled dot-product attention
  { name: "s04_attention_full", tex: "\\operatorname{Attention}(Q,K,V)=\\operatorname{softmax}\\!\\left(\\frac{Q\\cdot K^{T}}{\\sqrt{d_k}}\\right)\\cdot V" },
  { name: "s04_head_i", tex: "\\text{head}_i = \\operatorname{Attention}(X W_i^{Q},\\, X W_i^{K},\\, X W_i^{V})" },
  { name: "s04_mask", tex: "\\text{mask (decoder): set illegal positions to } -\\infty \\text{ before softmax}" },

  // Slide 5 — Multi-head attention
  { name: "s05_multihead", tex: "\\operatorname{MultiHead}(Q,K,V)=\\operatorname{Concat}(\\text{head}_1,\\dots,\\text{head}_h)\\,W^{O}" },
  { name: "s05_head_def", tex: "\\text{head}_i=\\operatorname{Attention}(Q W_i^{Q},\\, K W_i^{K},\\, V W_i^{V})" },
  { name: "s05_dims", tex: "h=8 \\quad d_k=d_v=64 \\quad d_{\\text{model}}=512" },

  // Slide 6 — Positional encoding
  { name: "s06_pe_sin", tex: "PE_{(pos,\\,2i)}=\\sin\\!\\left(\\frac{pos}{10000^{2i/d}}\\right)" },
  { name: "s06_pe_cos", tex: "PE_{(pos,\\,2i+1)}=\\cos\\!\\left(\\frac{pos}{10000^{2i/d}}\\right)" },
  { name: "s06_input_pe", tex: "X' = \\text{Embedding}(X) + PE(pos)" },
  { name: "s06_pe_linear", tex: "PE(pos+k) \\text{ is a linear transform of } PE(pos)" },

  // Slide 7 — Transformer architecture
  { name: "s07_ffn", tex: "\\operatorname{FFN}(x)=\\max(0,\\, x W_1 + b_1)\\,W_2 + b_2" },
  { name: "s07_decoder_prob", tex: "P(y_t\\mid y_{<t},\\, \\text{src})=\\operatorname{softmax}(\\operatorname{Linear}(h_t))" },

  // Slide 8 — Results
  { name: "s08_bleu", tex: "\\text{BLEU}=\\text{BP}\\cdot\\exp\\!\\left(\\sum_n w_n \\log p_n\\right)" },
  { name: "s08_benchmarks", tex: "\\text{EN}\\to\\text{DE WMT 2014} \\quad \\text{EN}\\to\\text{FR newstest2014}" },

  // Slide 9 — Why it matters
  { name: "s09_param_scale", tex: "\\text{BERT}_{\\text{Large}}\\approx340\\text{M} \\quad \\text{GPT-3}\approx175\\text{B} \\quad \\text{GPT-4}\approx?" },
  { name: "s09_attention_core", tex: "\\text{all built on } \\operatorname{Attention}(Q,K,V)=\\operatorname{softmax}\\!\\left(\\frac{QK^{T}}{\\sqrt{d_k}}\\right)V" },

  // Slide 10 — The task
  { name: "s10_objective", tex: "\\hat{P}=\\arg\\max_{P}\\prod_{t} P(y_t\\mid x,\\, y_{1..t-1})" },
  { name: "s10_loglik", tex: "\\text{maximize } \\sum_{(x,y)} \\log P(y\\mid x) \\text{ over parallel corpus}" },

  // Slide 11 — Encoder-decoder RNN
  { name: "s11_encoder", tex: "h_t = f(h_{t-1},\\, x_t),\\qquad c = h_T" },
  { name: "s11_decoder", tex: "s_t = g(s_{t-1},\\, y_{t-1},\\, c),\\qquad P(y_t\\mid\\cdots)=\\operatorname{softmax}(\\cdot)" },

  // Slide 12 — Bottleneck
  { name: "s12_mutinfo", tex: "I(c;\\, x_1,\\dots,x_T) \\le \\dim(c)" },
  { name: "s12_longrange", tex: "x_1 \\to x_T \\text{ must survive } T \\text{ compressions}" },

  // Slide 13 — Where this landed
  { name: "s13_rollout", tex: "\\text{translation.google.com }\\sim2018:\\ 100+ \\text{ language pairs}" },
  { name: "s13_bleu_gain", tex: "\\Delta\\text{BLEU}\\approx +1\\text{ to }+3 \\text{ (low/high resource)}" },

  // Slide 14 — Pivot problem
  { name: "s14_pivot_loss", tex: "E_{\\text{pivot}}\\approx E_{\\text{ZH}\\to\\text{EN}} + E_{\\text{EN}\\to\\text{JA}} + \\text{drift}" },
  { name: "s14_direct", tex: "E_{\\text{direct}}=E_{\\text{ZH}\\to\\text{JA}} \\text{ learned directly}" },
  { name: "s14_model_count", tex: "n \\text{ languages } \\Rightarrow 1 \\text{ model, not } \\tfrac{n(n-1)}{2}" },

  // Slide 15 — BERT and GPT
  { name: "s15_bert_loss", tex: "\\mathcal{L}_{\\text{BERT}}=-\\mathbb{E}_{x}\\log P(x_{\\text{masked}}\\mid x_{\\text{context}})" },
  { name: "s15_gpt_loss", tex: "\\mathcal{L}_{\\text{GPT}}=-\\mathbb{E}_{x}\\sum_t \\log P(x_t\\mid x_{<t})" },
  { name: "s15_split", tex: "\\text{BERT}\\to\\text{representation} \\qquad \\text{GPT}\\to\\text{generation}" },

  // Slide 16 — N^2 problem
  { name: "s16_score_matrix", tex: "S = QK^{T} \\in \\mathbb{R}^{n\\times n},\\quad \\text{then } SV" },
  { name: "s16_cost", tex: "\\text{flops}\\approx 2n^{2}d + 2nd^{2} \\qquad \\text{memory}\\approx O(n^{2})" },
  { name: "s16_doubling", tex: "\\text{doubling sequence length } = 4\\times \\text{ attention cost}" },

  // Slide 17 — Linear attention
  { name: "s17_standard", tex: "\\operatorname{softmax}(QK^{T})\\,V \\quad O(N^{2}d)" },
  { name: "s17_linear", tex: "\\varphi(Q)\\bigl(\\varphi(K)^{T}V\\bigr) \\quad O(Nd^{2})" },
  { name: "s17_feature_map", tex: "\\varphi(x)=\\operatorname{elu}(x)+1" },
  { name: "s17_summary", tex: "S_i = \\sum_{j\\le i} \\varphi(k_j)\\, v_j^{T} \\ \\Rightarrow\\ O(Nd^{2})" },
  { name: "s17_assoc", tex: "(AB)C = A(BC) \\text{ when shapes match}" },
];

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function ensureMathjaxNode() {
  try {
    return require("mathjax-node");
  } catch (e) {
    // not installed; try a local node_modules from a sibling install
    return null;
  }
}

async function renderOne(mj, entry) {
  const result = await mj.typeset({
    math: entry.tex,
    format: "TeX",
    svg: true,
    linebreaks: false,
  });
  if (!result || !result.svg) {
    throw new Error(`no svg for ${entry.name}`);
  }
  const outPath = path.join(OUT_DIR, `${entry.name}.svg`);
  fs.writeFileSync(outPath, result.svg);
  return outPath;
}

async function main() {
  ensureDir(OUT_DIR);
  let mj = ensureMathjaxNode();
  if (!mj) {
    console.log("mathjax-node not found, installing locally via npm...");
    const { execSync } = require("child_process");
    execSync("npm i --no-save mathjax-node", { stdio: "inherit", cwd: __dirname });
    mj = require("mathjax-node");
  }
  await mj.start();

  const filter = process.argv[2];
  const targets = filter
    ? FORMULAS.filter((f) => f.name.includes(filter) || f.name.startsWith(filter))
    : FORMULAS;

  let ok = 0;
  let fail = 0;
  for (const entry of targets) {
    try {
      const p = await renderOne(mj, entry);
      ok++;
      console.log(`ok   ${entry.name} -> ${path.relative(__dirname, p)}`);
    } catch (err) {
      fail++;
      console.error(`FAIL ${entry.name}: ${err.message}`);
    }
  }
  console.log(`\nrendered ${ok}/${targets.length} (${fail} failed)`);
  process.exit(fail ? 1 : 0);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
