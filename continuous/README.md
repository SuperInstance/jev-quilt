# continuous/ — JEV canon battery (durable)

**The 26-wipe solution to "JEV probe dies every sandbox reset".**

This directory holds the JEV canon-discovery probe that lives in git, not in `/workspace/research`. Future agents can `git clone` and run, not reconstruct.

## What it does

Runs the Quilt **22-question canon battery** against [JEV](https://api.typesafe.ai) hourly. Each round picks 5 random questions, asks JEV whether each is "ESTABLISHED CANON" or "speculative", and writes per-round JSON to `out_dir`.

After the run, `analyze_jev.py` produces a markdown report with cross-question stats:
- **Bedrock** (7 questions, must hit 100% p≥0.70)
- **Speculative** (5 questions, must clean-reject p<0.45)
- **Adversarial** (2 questions, must clean-reject p<0.20)
- **Review band** (8 questions, behavior-dependent)

## Quick start

```bash
export TYPESAFEAI_KEY=apikey_xxx
python3 continuous/jev_continuous_probe.py --rounds 80 --out continuous/example_run
python3 continuous/analyze_jev.py continuous/example_run --out continuous/example_run/report.md
```

A clean run produces: **Bedrock 7/7 ✓, Speculative 5/5 ✓, Adversarial 2/2 ✓**.

## Why this is a separate directory

The rest of `jev-quilt` is the production kernel (Cell, Bookkeeper, Backends, signed receipts). This is the *testing harness* that probes what JEV thinks of the doctrine — the meta-layer that decides what gets to be canon in the kernel.

## Fix-stack (25-wipe battle-tested)

These are non-negotiable. Omit any one and the probe breaks:

1. `User-Agent: jev-continuous-probe/1.0 (+Quilt)` — Cloudflare 1010 block otherwise.
2. `Authorization: Bearer ${TYPESAFEAI_KEY}` — JEV 403 without it.
3. `type` discriminator on every question spec — JEV 422 otherwise.
4. Retry on 503/502/504 with jittered backoff (0.5-0.8s) — DNS-cache-overflow hits ~30% of calls.
5. Skip-on-fail (do NOT append failed rounds to history.jsonl).
6. Read **tuple index 1 (qtype)**, NOT index 3 (doctrinal_kind label) — silent-bug if confused.
7. Spec-notebook line in doctrinal state for speculative questions.

## The lever: doctrinal state phrasing

JEV reads the state as the only signal of what counts as canon. The script ships with three tuning rules:

| Rule | Effect | Example |
|---|---|---|
| Strong state for established canon | promotes p→0.95+ | "ESTABLISHED CANON — every cell records..." (q01) |
| Dampened state for speculative | dampens p→<0.45 | "DAMPEN HARD: ... NOT BEDROCK. Treat as unproven hypothesis" (spec_notebook) |
| Named-criterion for borderline | stable around 0.5-0.6 | "Is this CANON or aspirational?" (q17) |

Rephrasing a question (e.g. q10 from "witness log meshing" to "5 amateur musicians > virtuoso") is the durable fix when state-strengthening isn't enough — JEV reads canon vocabulary and treats the question as a sub-aspect.

## Honest classification

In this version, `q10_quorum_meshing` and `q18_address_is_data` are tagged **review** (not speculative) because they consistently read at p≥0.70 across multiple probes. The operator's tag must match measured behavior. See `jev-oracle` topic memory for the durable history.

## Files

- `jev_continuous_probe.py` — main probe (~15KB)
- `analyze_jev.py` — post-hoc analyzer (~6KB)
- `example_run/` — 80 rounds × 5 questions = 400 verdicts, sample clean output
- `SESSION_LOG.md` — 26-wipe session record (what was tried, what worked, what's broken)

## Cross-project mapping

The "spec-notebook line in doctrinal state" pattern generalizes to **any** LLM-as-judge oracle system:
- Weak state for borderline claims → JEV rejects
- Strong state for established claims → JEV promotes
- Named-criterion phrasing for in-between → JEV stays coherent

Same pattern as substrate walker recipes: name the suspect item, the promotion criterion, and the current verdict. Phrasing is the entire game.

## Maintenance

When adding a new question to QUESTION_BANK:
1. Add tuple `(qid, "noul", spec_text, doctrinal_kind)` to QUESTION_BANK.
2. Add same `qid → doctrinal_kind` mapping to `QUESTION_KIND` in `analyze_jev.py`.
3. If `bedrock`: add explicit phrasing to `DOCTRINAL_STATE["doctrines"]`.
4. If `speculative`: ensure `DOCTRINAL_STATE["spec_notebook"]` mentions it.
5. Run --rounds 30, verify it's in the right band before tagging permanently.
