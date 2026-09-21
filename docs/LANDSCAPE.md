# Landscape — Jev-class System One models (researched 2026-09-21)

The category is five days old and already crowded. What exists, what we take,
what we deliberately do differently.

## The closed original

**Jev (TypeSafe AI, launched 2026-09-15, $40M seed DCVC).** A "System One
model": send *state* + typed *questions*, get back typed decisions —
**Choice** (distribution over options), **Score** (rubric levels), **Noul**
(yes/no probability) — every answer calibrated, single parallel pass,
70–500 ms (some report 10–15 ms), per-request micro-metering
(~$0.02–0.05 / 1k queries). Trained with RLCD (Reinforcement Learning for
Calibrated Decisions). Cannot generate text; cannot make type errors;
**can still pick the wrong valid option with a confident face** — the
structural guarantee is schema conformance, not correctness. SDK:
`typesafe-sdk`. Early access.

## The open ecosystem (exploded 2026-09-16 → now)

| Project | Base | Shape | Note |
|---|---|---|---|
| SemIf (TheoLeeCJ, MIT, ~1.9k★) | Qwen3.5-4B logit readout | Jev interface on open models | 3090/WebGPU; renamed from openjev; the reference local backend |
| openjev (razorback16) | DiffusionGemma 26B | Jev-wire-compatible decision server | Docker, vLLM, Codiv-hosted free tier |
| openjev-sglang (ekzhang) | Qwen3.6-35B | same via SGLang | `jev-latest` alias |
| Verdict (heman10x) | ModernBERT 151M | non-autoregressive, <35 ms, abstention slot | WebGPU in-browser |
| jevlike (vinnylarouge) | trainable small model | one pass, N options | **ships Doom, chess, Wikispeedia demos** — the boat's existence proof |
| NanoJev | Qwen3-0.6B + decision heads | one forward, batch questions | edge daemons, maze 95% |
| jev-ultrafast (browser-use) | Jev API | picks DOM op + element; small LLM writes text only when typing | **law 3's existence proof** |
| SimpleJev (featherless) | HF logit readout | `/v1/classifier` server | wraps existing HF models |

Directories: `systemonemodels.org`, `awesomejev.app`, JevBench v1.2
(benchmarkheaven). SDKs: `typesafe-ai/typesafe-sdk-js`,
`system-one-adapter-python`. MCP servers: `jkudish/jev-mcp`,
`itsmostafa/typesafe-mcp`.

## Honest caveats (write these into the kernel, not just the docs)

1. **Calibration ≠ correctness.** OSS clones "rarely emit type errors but can
   pick the wrong valid option with a confident face" (HN, JevBench). → our
   law 5: viability floor is binary, receipts expose drift, confidence gates
   LINK rights.
2. **Softmax probabilities are not "confidence of being right."** → cells
   carry *declared* semantics for every percentage (law: a cell's type says
   whether its 0.73 is a Choice weight, a similarity score, or a tone coeff).
3. **The model cannot explain.** Explanations are a different cell's job
   (law 3) — a System Two cell may *narrate* a decision, but it never
   *gates* it.

## What jev-quilt takes

- The three primitives (Choice/Score/Noul) as decision payloads.
- The wire abstractions from SemIf/openjev for local backends.
- jevlike's existence proof that small trainable decision models play games.
- jev-ultrafast's split: decide in one pass, render elsewhere.

## What jev-quilt deliberately is not

- Not a Jev clone (no model training here; we *serve* decisions over a
  cellular substrate using whatever backend resolves).
- Not an agent framework (cells are not agents; agents may *be* cells).
- Not a spreadsheet app (plugins project the kernel into spreadsheets; the
  kernel does not live in any one program).
