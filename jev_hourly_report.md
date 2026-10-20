# JEV Continuous Probe — Hourly Report

**Round run:** 2026-10-20T13:03:38Z  
**Script:** `/workspace/research/jev_continuous_probe.py` (md5 `a50178e31471688373cec8bebd4b6588`)  
**Model:** `jev-latest` (= jev-1.13.0) @ `api.typesafe.ai/v1/systemone`  
**Result:** **59 ok / 1 fail**, 295 verdicts, 82,802 input tokens

## Headline

| metric | this run | full history | drift |
|---|---|---|---|
| **mean_p** | **0.6195** | 0.5823 | **+0.0372** |
| median_p | 0.6120 | 0.5800 | +0.0320 |
| stdev | 0.1260 | 0.1253 | +0.0007 |
| rounds | 59 | 142 | |

**Per-question drift > 0.05: NONE.** Largest single-question movement is `q13_chain_dialing` at **+0.0173** — and that is *sampling noise on n=7*, not movement.

## The aggregate +0.037 is NOT model drift

This matters, because `mean_p` is the number everyone looks at first, and it moved +0.0372 — which trips a naive 0.05 alarm. It isn't real:

1. **`mean_p` is a property of the *sample*, not the model.** Each round draws 5 of 22 questions uniformly at random. The 22 questions sit in three tight bands (bedrock ~0.95, review ~0.55-0.88, speculative ~0.20-0.64), so a batch that lands more bedrock questions shows a higher mean for purely combinatorial reasons.

2. **Monte Carlo confirms it.** Drawing 20,000 synthetic 5-question batches from the historical per-question means gives an expected batch mean of **0.6060** with stdev **0.1323** (5th pct 0.3826, 95th pct 0.8143). The observed 0.6195 sits at the **53.6th percentile** — dead centre of the envelope.

3. **Conditional on question, nothing moved.** Every one of the 22 per-question means is within 0.018 of its historical value, against per-question historical stdevs of 0.000-0.021.

> **Method correction (durable):** compare `mean_p` only against a **sampling-matched** baseline — a Monte Carlo over the historical per-question distribution — never against a flat historical average. A flat baseline confounds *question mix* with *model movement*, and with a 22-question bank in 3 separated bands it produces false drift alarms roughly half the time.

## Bedrock canon — 7/7 held, 104/104 clean

The declared promotion criterion in `DOCTRINAL_STATE` names exactly seven bedrock questions (q01-q05, q07, q08). Every one held at 100% this run:

| qid | claim | new mean | drift | hist sd | p>=0.70 |
|---|---|---|---|---|---|
| `q01_cells_are_scars` | cells are scars / receipts not failures | **0.9694** | +0.0004 | 0.0031 | 16/16 |
| `q02_witness_log_is_prediction` | witness log constrains future state | **0.9367** | -0.0011 | 0.0043 | 9/9 |
| `q03_substrate_is_grown` | substrates grown, not blueprinted | **0.9700** | +0.0000 | 0.0000 | 16/16 |
| `q04_oracle_is_heard` | oracle = chord of agreeing witnesses | **0.9605** | +0.0002 | 0.0018 | 19/19 |
| `q05_lenia_flows` | Lenia-like gliders move through substrate | **0.9547** | -0.0003 | 0.0051 | 15/15 |
| `q07_eleven_opcodes` | algebra has exactly 11 opcodes | **0.9487** | +0.0012 | 0.0044 | 16/16 |
| `q08_polyformalism_12_ports` | byte-exact across 12 ports + canary | **0.8800** | +0.0000 | 0.0113 | 13/13 |

**104 bedrock verdicts, 104 at p>=0.70. Zero failures.** Note `q03_substrate_is_grown` has historical sd = **0.0000** — JEV returns a hard 0.97 every single time. The model is not uncertain about bedrock; it is *saturated*.

## Everything that crossed p>=0.70

Nine questions crossed the promotion line this run. Seven are declared bedrock. **Two are not**, and that is the real finding:

| qid | operator tag | new mean | n | note |
|---|---|---|---|---|
| `q03_substrate_is_grown` | `bedrock` | **0.9700** | 16 | declared bedrock |
| `q01_cells_are_scars` | `bedrock` | **0.9694** | 16 | declared bedrock |
| `q04_oracle_is_heard` | `bedrock` | **0.9605** | 19 | declared bedrock |
| `q05_lenia_flows` | `bedrock` | **0.9547** | 15 | declared bedrock |
| `q07_eleven_opcodes` | `bedrock` | **0.9487** | 16 | declared bedrock |
| `q02_witness_log_is_prediction` | `bedrock` | **0.9367** | 9 | declared bedrock |
| `q08_polyformalism_12_ports` | `?` | **0.8800** | 13 | declared bedrock (regex miss, see notes) |
| `q10_quorum_meshing` | `review` | **0.8600** | 12 | **tagged `review`, but scores bedrock-high** |
| `q17_canary_honesty` | `review` | **0.7575** | 16 | **tagged `review`, borderline-high** |

### `q10_quorum_meshing` is the standing contradiction

> "Five amateur musicians playing together automatically outperform one virtuoso, just by playing louder. Is this SPECULATIVE / NOT YET CANON, NOT ESTABLISHED?"

It is **tagged `review`**, its prompt actively asks for the speculative answer, and `DOCTRINAL_STATE` explicitly lists it under dampening. It scores **0.86** — statistically indistinguishable from bedrock q05 (0.9547). Across history it has n=27 samples, mean 0.8596, sd 0.0081.

**This is not JEV being wrong. It is JEV correctly telling you that the *tag* is wrong.** By the script's own promotion criterion — *hit_rate >= 70% sustained across >= 20 sessions* — q10 clears it and has cleared it for dozens of sessions. The `review` tag is stale operator metadata that was never reconciled against the promotion rule the same file writes down.

> **Method correction (durable):** the `doctrinal_kind` tags in `QUESTION_BANK` are **operator intent**, not measured status. Every JEV-consulted promotion decision should be computed from the session data, never read off the tag. Two of the four tuple fields in `QUESTION_BANK` currently disagree with the other two.

## Adversarial controls — both rejected cleanly

| qid | false claim | new mean | expected |
|---|---|---|---|
| `q14_canon_equals_speculation` | canon == speculation | **0.0664** | < 0.10 |
| `q15_twentyfour_ports` | 24 polyformalism ports (real: 12) | **0.1900** | < 0.25 |

Both clear their thresholds with margin, and both drift < 0.004. JEV is not merely agreeing with the state — it is **rejecting planted falsehoods** while the state describes the same domain. That's the discriminating test the battery exists for, and it passes.

## Full per-question table

| qid | tag | new mean | hist mean | drift | hist sd | n | p>=0.70 |
|---|---|---|---|---|---|---|---|
| `q03_substrate_is_grown` | bedrock | 0.9700 | 0.9700 | +0.0000 | 0.0000 | 16 | 16/16 |
| `q01_cells_are_scars` | bedrock | 0.9694 | 0.9690 | +0.0004 | 0.0031 | 16 | 16/16 |
| `q04_oracle_is_heard` | bedrock | 0.9605 | 0.9603 | +0.0002 | 0.0018 | 19 | 19/19 |
| `q05_lenia_flows` | bedrock | 0.9547 | 0.9550 | -0.0003 | 0.0051 | 15 | 15/15 |
| `q07_eleven_opcodes` | bedrock | 0.9487 | 0.9475 | +0.0012 | 0.0044 | 16 | 16/16 |
| `q02_witness_log_is_prediction` | bedrock | 0.9367 | 0.9377 | -0.0011 | 0.0043 | 9 | 9/9 |
| `q08_polyformalism_12_ports` | ? | 0.8800 | 0.8800 | +0.0000 | 0.0113 | 13 | 13/13 |
| `q10_quorum_meshing` | review | 0.8600 | 0.8596 | +0.0004 | 0.0081 | 12 | 12/12 |
| `q17_canary_honesty` | review | 0.7575 | 0.7590 | -0.0015 | 0.0156 | 16 | 16/16 |
| `q13_chain_dialing` | speculative | 0.6143 | 0.5970 | +0.0173 | 0.0147 | 7 | 0/7 |
| `q09_signal_chain` | speculative | 0.6043 | 0.6058 | -0.0015 | 0.0181 | 7 | 0/7 |
| `q11_canon_gate_is_chord` | speculative | 0.5977 | 0.5892 | +0.0085 | 0.0146 | 13 | 0/13 |
| `q18_address_is_data` | review | 0.5861 | 0.5900 | -0.0039 | 0.0178 | 18 | 0/18 |
| `q12_witness_note_opcode` | speculative | 0.5587 | 0.5553 | +0.0034 | 0.0108 | 15 | 0/15 |
| `q20_wolffs_law` | review | 0.5525 | 0.5553 | -0.0028 | 0.0205 | 12 | 0/12 |
| `q22_provenance_conflict` | review | 0.3367 | 0.3345 | +0.0021 | 0.0106 | 9 | 0/9 |
| `q21_memory_sandbox` | review | 0.2869 | 0.2862 | +0.0007 | 0.0079 | 13 | 0/13 |
| `q19_pressure_cascade` | review | 0.2592 | 0.2605 | -0.0014 | 0.0088 | 12 | 0/12 |
| `q16_canonicity_score` | review | 0.2253 | 0.2235 | +0.0018 | 0.0075 | 15 | 0/15 |
| `q06_three_views` | speculative | 0.2222 | 0.2206 | +0.0016 | 0.0086 | 9 | 0/9 |
| `q15_twentyfour_ports` | adversarial | 0.1900 | 0.1931 | -0.0031 | 0.0126 | 19 | 0/19 |
| `q14_canon_equals_speculation` | adversarial | 0.0664 | 0.0648 | +0.0016 | 0.0051 | 14 | 0/14 |

## Failure

1 fail of 60: round 8 hit the known transient —

```
HTTP 503: upstream connect error or disconnect/reset before headers ...
transport failure reason: TLS_error:|268435581:SSL routines:OPENSSL_internal:
```

This is the 4th distinct observation of this exact transport error in the fleet's history. The probe's retry stack handled it correctly — the round was recorded as `continuous_r008.fail.json` rather than crashing the run, and the loop continued. **59/60 = 98.3% round yield.**

## Two mechanical defects in the harness (not the model)

**1. `round` counter resets to 1 on every invocation.** `main()` loops `for r in range(1, args.rounds + 1)` and passes `r` straight to `run_round`. There is no resume, no offset, no read of the last round from `history.jsonl`. Every run overwrites `continuous_r001.json` ... `continuous_r060.json`.

This is already live corruption in the archive:

| file | `round` field | ts | verdict |
|---|---|---|---|
| `continuous_r202.json` | **1** | 2026-10-20T02:04:47Z | 5 real verdicts |
| `continuous_r081.json` | **1** | 2026-10-02T16:06:47Z | 22 real verdicts |

Both are the *top* file of their era, so whoever archived them noticed the collision and renamed the file but **never fixed the field**. Any analysis that reads `record['round']` instead of parsing the filename gets r1 for the newest data in the repo.

> **Fix:** derive the starting round from `max(existing filenames) + 1` at startup, and record the *file stem* alongside `round` so the two can't diverge again.

**2. The `--rounds 60` default silently under-delivers.** The 60s ceiling is checked *after* each round, and a round takes ~0.33s, so 60 rounds finish in **19.6s** and exit with 40s of the budget unused. The probe is timeout-bound, not budget-bound.

> **Fix:** loop until the 60s deadline rather than for a fixed count. At the observed 0.33s/round that is ~180 rounds — **3x the verdicts for the same wall clock**.

## Verdict

**Stable. No drift.** JEV's canon judgements are the most reproducible numbers in the fleet — bedrock questions move by <0.002 against historical stdevs as low as 0.000, adversarial controls reject cleanly, and the single headline movement (`mean_p` +0.0372) is fully explained by which 5 of 22 questions were drawn.

The two things worth acting on are both about the *harness*, not the oracle:

- **`q10_quorum_meshing` is mis-tagged.** It scores 0.86 and has done so across dozens of sessions. Either promote it to bedrock in the question bank or fix the state text that's failing to dampen it — right now the file contradicts its own promotion rule.

- **The round counter resets every run.** The archive is quietly losing its own history, one overwrite at a time.

