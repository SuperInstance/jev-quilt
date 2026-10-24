# JEV Continuous Probe — Hourly Report (r414)

**Run:** 2026-10-24T06:04:12.530190+00:00  |  **model:** jev-1.14.0  |  **script_md5:** 3a255fa4642ec4a83173ab04d773d485
**Rounds:** 1 OK, 0 fail  |  **verdicts:** 5  |  **elapsed:** 0.144s

## Headline

- **mean_p = 0.2800** (5-of-22 draw; window r400–r413 mean 0.4567, range 0.2920–0.6560)
- **Questions hitting p ≥ 0.70 (bedrock canon): 1/5** — `q02` 0.74
- **Drift > 0.05:** **1 flagged** — `q02` (dev −0.0705), see verdict below

## Round 414 verdicts

| qid | kind | p | ≥0.70 |
|---|---|---|---|
| `q02` | bedrock | 0.74 | **YES** |
| `q10` | speculative | 0.05 | — |
| `q13` | speculative | 0.16 | — |
| `q16` | review | 0.20 | — |
| `q18` | speculative | 0.25 | — |

## Bedrock canon (p ≥ 0.70)

- **`q02` p=0.74** (bedrock) — baseline mean 0.8105 σ 0.0342 over n=40 current-schema draws; 40/40 historical draws ≥0.70

## Drift check (drawn qids only, vs current-schema baseline r201–r413)

Baseline: **211 rounds** (r201–r413, current-schema), 22 qids. Legacy r1–r200 excluded — different instrument (pre-`spec_notebook` guard), its speculative readings are not comparable.

| qid | kind | n | mean | σ | this | dev | \|z\| | verdict |
|---|---|---|---|---|---|---|---|---|
| `q02` | bedrock | 40 | 0.8105 | 0.0342 | 0.74 | -0.0705 | 2.06 | **DRIFT** |
| `q10` | speculative | 56 | 0.0664 | 0.0058 | 0.05 | -0.0164 | 2.83 | ok |
| `q13` | speculative | 50 | 0.1350 | 0.0100 | 0.16 | +0.0250 | 2.49 | ok |
| `q16` | review | 51 | 0.1971 | 0.0080 | 0.20 | +0.0029 | 0.37 | ok |
| `q18` | speculative | 58 | 0.2238 | 0.0101 | 0.25 | +0.0262 | 2.58 | ok |

### Verdicts

**`q02` — dev −0.0705 (> 0.05), z = −2.06 → FLAGGED but within known range.**

- Historical range (current schema): min 0.71, max 0.86. This draw (0.74) is **inside** the observed range — 3/40 = 7.5% of prior draws were ≤ 0.74.
- **q02 remains a bedrock canon hit: 40/40 = 100%** hit-rate, unchanged. A lower draw is variance within a canon that has never once missed.
- The **σ-trap check reverses the ranking here**: q02 has the largest |dev| (0.0705) but the **smallest** |z| (2.06) of the four candidates — q10 (|z| 2.83), q18 (2.58), q13 (2.49) all have larger z but |dev| ≤ 0.026, i.e. they are *not* drift. q02's σ is 0.034, ~3× the others, so the same z-scores a smaller move.
- Verdict: **variance at the low edge of a stable 100%-canon channel, not substrate drift.** Worth watching if the next 2–3 q02 draws stay ≤ 0.74; a sustained break below 0.70 would be a real event.

**q10, q13, q16, q18 — no drift.** All |dev| ≤ 0.0262; q16 dev −0.0080 is the tightest. Their elevated z-scores are the σ≈0 trap (σ 0.006–0.010): the denominator is near-degenerate, so |z| inflates without meaningful movement.

### Script-reported `drift_events` — PHANTOM (5th reproduction)

The script printed `drift_events=1`. Recomputing its own `drift_check()` logic against this round's verdicts returns **`[]`** — the event fires on a qid **not drawn this round** (stale qid re-firing a historical event). Known DEFECT: `drift_check()` compares every qid's last value to a 5-sample local median regardless of whether that qid was sampled. Recompute restricted to drawn qids against the full-history mean; **|dev| first, σ second.**

## Cathedral health (7-qid canon list, r201–r413)

| qid | n | mean | σ | hit-rate p≥0.70 | min | max |
|---|---|---|---|---|---|---|
| `q01` | 50 | 0.8722 | 0.0103 | **50/50 = 100%** | 0.84 | 0.89 |
| `q02` | 40 | 0.8105 | 0.0342 | **40/40 = 100%** | 0.71 | 0.86 |
| `q03` | 50 | 0.8846 | 0.0096 | **50/50 = 100%** | 0.86 | 0.90 |
| `q04` | 49 | 0.8894 | 0.0096 | **49/49 = 100%** | 0.88 | 0.91 |
| `q05` | 45 | 0.8469 | 0.0135 | **45/45 = 100%** | 0.82 | 0.87 |
| `q07` | 52 | 0.7537 | 0.0154 | **52/52 = 100%** | 0.72 | 0.78 |
| `q08` | 46 | 0.8987 | 0.0101 | **46/46 = 100%** | 0.87 | 0.91 |

**Cathedral: 100% hit-rate on all 7 — INTACT** (r201–r413, 211 rounds).

## mean_p trend (r405–r414, recomputed from merged corpus)

| round | mean_p |
|---|---|
| r400 | 0.5580 |
| r401 | 0.6560 |
| r402 | 0.6520 |
| r403 | 0.2920 |
| r404 | 0.4400 |
| r405 | 0.3900 |
| r406 | 0.2940 |
| r407 | 0.4580 |
| r408 | 0.4380 |
| r409 | 0.3680 |
| r410 | 0.4180 |
| r411 | 0.4240 |
| r412 | 0.5520 |
| r413 | 0.4540 |
| r414 | 0.2800 |

Window mean 0.4449. r414's 0.2800 is the **lowest of the last 10 rounds** but inside the observed band — mean_p mixes 5-of-22 draws, so a low round usually means fewer bedrock qids were sampled (this round: 1/5 vs the r400–r413 range of 1/5–4/5). **Health lives in the cathedral + the buckets, never the grand mean.**

## Method notes / corrections applied

1. **Round count:** `python3 jev_continuous_probe.py 1` — positional `sys.argv[1]`, NOT `--rounds N`. The arg defaults to 200, and killing after launch races the writer to flush many rounds. One round requested → one round run, no kill needed.
2. **Environment:** NAS `/workspace` at hard quota zero (8th consecutive wipe; even a 100-byte `dd` fails with `Disk quota exceeded`). Bootstrapped from `git clone --unshallow` into `/tmp` (overlay, 28 GB free). The live `research/jev_sessions/` tree was recovered from git; the report and the r414 round file are durable in git, not on the NAS.
3. **TLS:** leaf valid to 2026-12-25, so the expired-leaf wall was not in play. `SSL_CERT_FILE` was the gateway-anchor-only bundle → rebuilt a 289-cert combined bundle. Python urllib then returned HTTP 422 on a probe body, which proved auth + routing were fine and only the body shape was wrong.
4. **Corpus assembly:** the round files alone are incomplete (192-round gap r207–r382) **and** use two schemas — r001–r202 legacy (`sampled_qids` + descriptive qid names like `q20_wolffs_law`) and r193+ current (`rounds[]` + bare qids). Merging both file schemas **plus** the tracked `history.jsonl` recovers **412 of 414 rounds** (only r201–r202 remain missing).
5. **Baseline window:** the legacy r1–r200 segment is a *different instrument* — its speculative qids read high (q10 mean 0.392, q13 0.364, q18 0.442) because it predates the `spec_notebook` state-leak guard. Pooling it with the current segment inflates σ to 0.17–0.39 and manufactures drift on every speculative qid. **The correct baseline is the current-schema segment (r201+).**
6. **Per-qid bucketing:** each qid is judged against its own baseline — a single global threshold mislabels plateau qids (q12, q16 read 0.20–0.23 by design).

## Verdict

**Round 414: OK. mean_p 0.2800; 1/5 bedrock canon (q02 p=0.74); 1 drift flag (q02, dev −0.0705) judged VARIANCE, not substrate drift. Cathedral 100% intact on all 7 canon qids. No qid left the canon band; no speculative qid leaked above 0.30.**

Next check: watch `q02` — if the following 2–3 draws remain ≤ 0.74, re-open the drift call; a sustained break below 0.70 is the trigger.
