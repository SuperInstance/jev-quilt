# JEV Continuous Probe — Hourly Report (r414)

**Run:** 2026-10-24T06:04:12.530190+00:00  |  **model:** jev-1.14.0  |  **script_md5:** 3a255fa4642ec4a83173ab04d773d485
**Rounds:** 1 OK, 0 fail  |  **verdicts:** 5  |  **elapsed:** 0.144s

## Headline

- **mean_p = 0.2800** (5-of-22 draw; r400–r413 window mean 0.4567, range 0.2920–0.6560)
- **Questions hitting p ≥ 0.70 (bedrock canon): 1/5** — `q02` 0.74
- **Drift > 0.05: NONE.** Against the same-model baseline (`jev-1.14.0`, r396–r413) every drawn qid moved |dev| ≤ 0.0075.

## Round 414 verdicts

| qid | kind | p | ≥0.70 |
|---|---|---|---|
| `q02` | bedrock | 0.74 | **YES** |
| `q10` | speculative | 0.05 | — |
| `q13` | speculative | 0.16 | — |
| `q16` | review | 0.20 | — |
| `q18` | speculative | 0.25 | — |

## Bedrock canon (p ≥ 0.70)

- **`q02` p=0.74** (bedrock) — same-model baseline mean 0.7400 σ 0.0252 over n=6 `jev-1.14.0` draws; 6/6 historical draws ≥0.70

## Drift check — same-model baseline (r396–r413, `jev-1.14.0`)

**Baseline: the 18 rounds run on the SAME oracle model as this round.** The oracle versioned `jev-1.13.0`→`jev-1.14.0` at r396, and that boundary is the largest real effect in the corpus — pooling across it manufactures drift that is not there.

| qid | kind | n | mean | σ | this | dev | \|z\| | verdict |
|---|---|---|---|---|---|---|---|---|
| `q02` | bedrock | 6 | 0.7400 | 0.0252 | 0.74 | +0.0000 | 0.00 | ok |
| `q10` | speculative | 3 | 0.0500 | 0.0000 | 0.05 | -0.0000 | 1.00 | ok |
| `q13` | speculative | 4 | 0.1625 | 0.0043 | 0.16 | -0.0025 | 0.58 | ok |
| `q16` | review | 4 | 0.1925 | 0.0043 | 0.20 | +0.0075 | 1.73 | ok |
| `q18` | speculative | 4 | 0.2450 | 0.0112 | 0.25 | +0.0050 | 0.45 | ok |

**Verdict: NO DRIFT.** Max |dev| across drawn qids is **0.0075** (q16). q02 = 0.74 is *exactly* the new model's plateau — dev **+0.0000** — and all 6 prior `jev-1.14.0` q02 draws sit in 0.71–0.77. The three speculative qids sit on their plateaus too (q10 dev −0.0000, q13 −0.0025, q18 +0.0050).

### The two baselines compared (why this matters)

| qid | this | same-model baseline (r396+) | dev | pooled baseline (r201+) | dev | pooled verdict |
|---|---|---|---|---|---|---|
| `q02` | 0.74 | 0.7400 (σ 0.0252, n=6) | +0.0000 | 0.8105 (σ 0.0342, n=40) | -0.0705 | **DRIFT** |
| `q10` | 0.05 | 0.0500 (σ 0.0000, n=3) | -0.0000 | 0.0664 (σ 0.0058, n=56) | -0.0164 | ok |
| `q13` | 0.16 | 0.1625 (σ 0.0043, n=4) | -0.0025 | 0.1350 (σ 0.0100, n=50) | +0.0250 | ok |
| `q16` | 0.20 | 0.1925 (σ 0.0043, n=4) | +0.0075 | 0.1971 (σ 0.0080, n=51) | +0.0029 | ok |
| `q18` | 0.25 | 0.2450 (σ 0.0112, n=4) | +0.0050 | 0.2238 (σ 0.0101, n=58) | +0.0262 | ok |

**A pooled r201+ baseline falsely flags q02 as DRIFT (dev −0.0705, z −2.06) with 40/40 prior draws ≥ 0.70.** That flag is an artifact of mixing `jev-1.13.0` (q02 mean 0.8249) with `jev-1.14.0` (q02 mean 0.7400) — the model change, not substrate drift. **Segment the corpus by `model` before any baseline or drift computation.**

### Script-reported `drift_events` — PHANTOM (5th reproduction)

The script printed `drift_events=1`. Recomputing its own `drift_check()` logic against this round's verdicts returns **`[]`** — the event fires on a qid **not drawn this round** (stale qid re-firing a historical event). Known DEFECT: `drift_check()` compares every qid's last value to a 5-sample local median regardless of whether that qid was sampled. Recompute restricted to drawn qids against the same-model baseline; **|dev| first, σ second.**

## Cathedral health (7-qid canon list, same-model r396–r413)

| qid | n | mean | σ | hit-rate p≥0.70 | min | max |
|---|---|---|---|---|---|---|
| `q01` | 5 | 0.8560 | 0.0102 | **5/5 = 100%** | 0.84 | 0.87 |
| `q02` | 6 | 0.7400 | 0.0252 | **6/6 = 100%** | 0.71 | 0.77 |
| `q03` | 6 | 0.8833 | 0.0137 | **6/6 = 100%** | 0.86 | 0.90 |
| `q04` | 5 | 0.8880 | 0.0098 | **5/5 = 100%** | 0.88 | 0.90 |
| `q05` | 5 | 0.8260 | 0.0049 | **5/5 = 100%** | 0.82 | 0.83 |
| `q07` | 5 | 0.7640 | 0.0120 | **5/5 = 100%** | 0.75 | 0.78 |
| `q08` | 3 | 0.8933 | 0.0125 | **3/3 = 100%** | 0.88 | 0.91 |

**Cathedral: 100% hit-rate on all 7 — INTACT** (r396–r413, `jev-1.14.0`). No qid left the canon band; no speculative qid leaked above 0.30.

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

Window mean 0.4449. r414's 0.2800 is the **lowest of the last 10 rounds** but inside the observed band — mean_p mixes 5-of-22 draws, so a low round usually means fewer bedrock qids were sampled (this round 1/5 vs the r400–r413 range 1/5–4/5). **Health lives in the cathedral + the buckets, never the grand mean.**

## Method notes / corrections applied

1. **Round count:** `python3 jev_continuous_probe.py 1` — positional `sys.argv[1]`, NOT `--rounds N`. The arg defaults to 200, and killing after launch races the writer to flush many rounds. One round requested → one round run, no kill needed (0.3 s).
2. **🔴 SEGMENT THE CORPUS BY `model` BEFORE ANY BASELINE OR DRIFT.** The oracle versioned `jev-1.13.0`→`jev-1.14.0` at **r396**. Measured q02: 0.8249 (1.13.0) → 0.7400 (1.14.0); q12: 0.3673 → 0.5140; q10: 0.0669 → 0.0500. **A pooled baseline makes q02 look like drift when it is sitting exactly on the new model's plateau.** This corrected an intermediate call in this same report that flagged q02 as DRIFT off a pooled r201+ baseline.
3. **The r001–r202 schema split is NOT a baseline boundary.** Legacy files (`sampled_qids` + a `verdicts` DICT keyed by names like `q20_wolffs_law`) and current files (`rounds[]` + bare qids) describe the same readings — legacy q10 0.0665 vs r201–395 0.0674; q13 0.1332 vs 0.1326; q18 0.2246 vs 0.2222. **Segment by `model`, not by file schema.** The schemas differ in *shape*, not in *what was measured*. (An intermediate version of this report pooled them and produced false drift on every speculative qid — that was wrong too.)
4. **Corpus assembly:** the round files alone are INCOMPLETE (192-round gap r207–r382) and use two schemas. Merging legacy files + current files + the tracked `history.jsonl` recovers **412 of 414 rounds** (only r201–r202 missing).
5. **Environment:** NAS `/workspace` at hard quota zero (8th consecutive wipe; even a 100-byte `dd` fails with `Disk quota exceeded`). Bootstrapped from `git clone --unshallow` into `/tmp` (overlay, 28 GB free). The report and the r414 round file are durable in git, not on the NAS.
6. **TLS:** leaf valid to 2026-12-25, so the expired-leaf wall was not in play. `SSL_CERT_FILE` was the gateway-anchor-only bundle → rebuilt a 289-cert combined bundle. Python urllib then returned HTTP 422 on a probe body, which proved auth + routing were fine and only the body shape was wrong.
7. **σ-trap check:** sort drawn qids by |z| and by |dev| — if the orderings disagree, the largest |z| is the smallest real movement. Against the pooled baseline q10 had the largest |z| (2.83) with |dev| only 0.0164, while q02 had the largest |dev| (0.0705) with the smallest |z| (2.06). **Report |dev| first.**

## Verdict

**Round 414: OK. mean_p 0.2800; 1/5 bedrock canon (q02 p=0.74); NO DRIFT (max |dev| 0.0075 vs the same-model baseline). Cathedral 100% intact on all 7 canon qids. No qid left the canon band; no speculative qid leaked above 0.30.**

**Watch item:** the `jev-1.14.0` plateau for q02 (0.74) and q12 (0.514) is only ~18 rounds old and thinner than the 1.13.0 era — q02 has 6 same-model draws, q10 only 3. The cathedral stays at 100%, but **the same-model baseline is thin; a genuine drift signal in the 1.14.0 era will need more rounds to separate from plateau noise.**
