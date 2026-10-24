# JEV Hourly Report — r421

**Run:** 2026-10-24T15:0xZ · 1 round · status OK · 0 fails · 5 verdicts
**Model:** jev-1.14.0 · script `jev_continuous_probe.py` md5 `3a255fa4642ec4a83173ab04d773d485`
**Corpus:** `research/jev_sessions/history.jsonl` — 424 lines → **412 unique rounds** after dedup by round number (13 known dups, r384–r391)

## Verdict

**NO DRIFT.** mean_p 0.5540 is an **ordinary 3-bedrock draw**, not a movement in the substrate.
- 3/5 bedrock canon hits (q04 0.88, q07 0.79, q02 0.75) — all three >= 0.70
- Max |dev| vs same-model baseline on drawn qids: **0.0233** (q07) — well under the 0.05 threshold
- Script `drift_events=0` **agrees** with the recomputation this round (no phantom event)

## r421 verdicts

| qid | p | kind | bedrock canon (>=0.70) |
|-----|---|------|------------------------|
| q04 | 0.88 | bedrock | **HIT** |
| q18 | 0.25 | speculative | — |
| q07 | 0.79 | bedrock | **HIT** |
| q02 | 0.75 | bedrock | **HIT** |
| q19 | 0.10 | adversarial | — |

**mean_p = 0.5540** · bedrock_hits = 3/5

## Drift analysis — recomputed (drawn qids only, same-model baseline)

The script's `drift_check()` compares every qid's last value to a 5-sample local median whether or not that qid was drawn, so it reports *history* events, not *this-round* events. Drift was therefore recomputed from the round files against a **model-segmented** baseline (r396 switched jev-1.13.0 → 1.14.0), restricted to qids actually drawn in r421.

| qid | p | same-model n | mu | sd | dev | z | flag |
|-----|---|--------------|-----|-----|-----|---|------|
| q04 | 0.88 | 6 | 0.8850 | 0.0112 | -0.0050 | -0.45 | |
| q18 | 0.25 | 7 | 0.2471 | 0.0088 | +0.0029 | +0.32 | |
| q07 | 0.79 | 6 | 0.7667 | 0.0125 | +0.0233 | +1.87 | |
| q02 | 0.75 | 9 | 0.7356 | 0.0263 | +0.0144 | +0.55 | |
| q19 | 0.10 | 5 | 0.1040 | 0.0049 | -0.0040 | -0.82 | |

**No drawn qid exceeds |dev| > 0.05.** Per-qid bucketing: each qid judged against its OWN baseline, never one global threshold.

### The full-history flag on q02 is a CROSS-MODEL ARTIFACT, not drift

Computing against the full-history baseline instead flags q02 at dev **-0.0651** (z -2.04). Proof this is the r396 model switch:

- q02 under **jev-1.13.0**: n=76, mu=**0.8245**, min 0.79, max 0.86 — **76/76 draws >= 0.70**
- q02 under **jev-1.14.0**: n=10, mu=**0.7370**, min 0.69, max 0.77 — 9/10 draws >= 0.70
- r421's q02 = 0.75 sits **inside** the 1.14.0 distribution.

A baseline that spans r396 measures the model switch, not the canon. This is the same shape as the q02 step at r416 — **3rd instance of this pattern** (r416 q02 down; r419/r420 q12 up). The same-model baseline carries the verdict.

## Class-mix check (is 0.5540 ordinary?)

200k synthetic 5-of-22 draws using per-qid deduped 1.14.0-era means:
- E[mean_p] = 0.4009; **P(mean_p <= 0.5540) = 0.871** — an unremarkable draw
- last-20 mean_p: mu 0.4102, sd 0.1243, z = **+1.16**
- P(bedrock_hits == 3) = 0.139, P(>=3) = 0.160

mean_p and hit-count are a **class-mix readout only**, not a trend. The r418 (0.1480, 0/5) → r419 (0.5380, 3/5) → r420 (0.3580, 1/5) → r421 (0.5540, 3/5) sequence is a lottery over which 5 of 22 get drawn, not a signal.

## Cathedral health (7 bedrock qids: q01 q02 q03 q04 q05 q07 q08)

| qid | hit-rate | mu | min | max |
|-----|----------|-----|-----|-----|
| q01 | 100/100 = 100.00% | 0.8744 | 0.84 | 0.90 |
| q02 | 85/86 = 98.84% | 0.8143 | 0.69 | 0.86 |
| q03 | 96/96 = 100.00% | 0.8855 | 0.86 | 0.91 |
| q04 | 97/97 = 100.00% | 0.8885 | 0.87 | 0.91 |
| q05 | 91/91 = 100.00% | 0.8490 | 0.78 | 0.87 |
| q07 | 84/84 = 100.00% | 0.7554 | 0.71 | 0.79 |
| q08 | 80/80 = 100.00% | 0.8996 | 0.87 | 0.91 |

- **ALL-TIME: 633/634 = 99.84%** (up from 630/631 — the counter advanced by one hit + one non-hit draw)
- **1.14-ERA: 46/47 = 97.87%** (q02 88.9% → 9/10, the r416 model step, now **26 rounds confirmed**)
- No promotion, no demotion, no class change. q12 read 0.50 in r420 does not promote it (`spec_notebook` gate).

## Open item: q05 AMBER (carried from r419, still unresolved)

r419's q05 = 0.78 remains the **only** draw below 0.80 in 91 draws (all-time min, z = **-5.05**). It was flagged AMBER at r419 with an instruction to watch r420–r422. **r421 did not draw q05**, so the AMBER is still open — no new evidence, no resolution.

Same-model 1.14.0-era q05 draws: r392 0.82, r394 0.86, r400 0.83, r404 0.82, r408 0.83, r410 0.83, r413 0.82, **r419 0.78**. The 0.78 is a single-point excursion, not a trend (no mirror signal: q01/q04/q08 flat, and no speculative-qid movement toward canon). **AMBER, not a finding.** Next q05 draw decides.

## Environment

- 8th consecutive wipe in which the prompt named ephemeral `/workspace/research/` paths that did not exist. Workspace arrived empty except `.plugin-cache`.
- **NAS 100% (0 bytes available)** — cannot land the report in `/workspace/research/`. Durable copy = git. This is the 28th observation of the silent-zero trap class; avoided by not attempting the write at all.
- TLS: **healthy**. `SSL_CERT_FILE` was gateway-anchor-only again (13th recurrence) → rebuilt **289-cert** combined bundle. Live leaf `docs.typesafe.ai` notAfter **Dec 10 2026 = VALID**. A hand-made body of the wrong shape returned **HTTP 405 Method not allowed** — a body/method fault, NOT an auth or network wall (routing is fine).
- Script md5 `3a255fa4…` = the repo-ROOT variant, unchanged (NOT the `continuous/` variant `95b552ea…`).
- Ran `python3 jev_continuous_probe.py 1` — explicit positional count, one round. Did not launch 200 and kill.
- Round counter resumed correctly: files->420, history->420, start=421.

## Method notes carried forward

1. **Baseline must be segmented by oracle model.** Any drift claim spanning r396 measures the model switch. Report both numbers; the same-model one carries the verdict.
2. **`history.jsonl` contains 13 duplicate rounds** (424 lines → 412 unique). De-duplicate by round number before any baseline computation.
3. **`drift_check()` reports history events, not this round's.** Recompute per-qid dev vs full-history mean/sigma restricted to drawn qids; `|dev|` FIRST, sigma second.
4. **`|dev| > 0.05` is the primary threshold; z is a trap.** The largest z is often the smallest real movement (q07 here: z +1.87 on a 0.0233 dev).
5. **mean_p is a class-mix readout, never a health verdict.** Health lives in the cathedral qids and the buckets.
