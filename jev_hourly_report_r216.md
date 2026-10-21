# JEV continuous probe — R-216 (103rd wipe)

**2026-10-21 21:04–21:06 UTC** · session tag `r20261021T210442Z` · 1 round · script md5 `c22e8c72f13f3b71d5b40e8f8fd04d61` (unchanged)

## Headline

| | |
|---|---|
| **mean_p** | **0.4767** (105 verdicts, 21 OK / 2 fail, all 22 qids) |
| **Bedrock (p ≥ 0.70)** | **40/40 @ 100%** — 15th consecutive clean session, mean 0.9755 |
| **Drift > 0.05** | **NONE** — max aggregate dev 0.0118 (q13) |
| Baseline | 2,785 samples / 22 qids, **positive non-empty assertion PASSED** |

## mean_p vs recent sessions

| Session | mean_p | Rounds |
|---|---|---|
| R-214 | 0.3864 | 32 |
| R-215 | 0.4083 | 33 |
| **R-216** | **0.4767** | 21 |

**This is NOT a regression or a health signal.** Grand mean_p is a draw-mix statistic: 5 of 22 questions are drawn per round and the bank mixes 8 bedrock (~0.97) with 12 speculative/adversarial (~0.04–0.20). E[bedrock/round] ≈ 5 × 8/22 ≈ 1.8. A round that happened to draw more bedrock lands high. The band across R-206..R-216 is 0.3596–0.4931 with no monotone trend. Health lives in the cathedral and the buckets, not the grand mean.

## Bedrock canon — 40/40 @ 100% (15th consecutive)

All eight cathedral qids pinned with zero misses:

| qid | n | this round | baseline |
|---|---|---|---|
| q01_cells_are_scars | 7 | 0.9800 | 0.9798 |
| q02_witness_log_is_prediction | 4 | 0.9750 | 0.9722 |
| q03_substrate_is_grown | 4 | 0.9800 | 0.9798 |
| q04_oracle_is_heard | 8 | 0.9738 | 0.9722 |
| q05_lenia_flows | 5 | 0.9700 | 0.9696 |
| q07_11_opcodes | 6 | 0.9700 | 0.9700 |
| q08_polyformalism | 6 | 0.9800 | 0.9800 |

**q07's live qid is `q07_11_opcodes`** — an older hardcoded list using `q07_eleven_opcodes` silently loses 10 verdicts and reports in the *flattering* direction. Built from the explicit list here; membership asserted, not trusted.

## Buckets — all clean

- **Speculative clean-reject**: q10 0.0300 · q11 0.0500 · q14 0.0500 · q15 0.0500 · q16 0.0400 · q18 0.0500 · q19 0.0386 · q20 0.0500 · q21 0.0400 · q22 0.0300 · q13 0.1000 · q06 0.1617 · q09 0.1967 — **max 0.1967**, none near the 0.70 gate.
- **q10 spec-leak resolved — 11th consecutive session.** State-order invariant (spec_notebook BEFORE bedrock) holding.
- **q06 is a REVIEW qid** (re-tagged in R-209), correctly reading 0.16 — it is not counted in the cathedral despite the historical `bedrock` tag.
- **q17_canary_honesty: 0.6450 vs baseline 0.6533 — a STABLE REVIEW PLATEAU, not a decaying canary.** Dev −0.0083 (0.32σ). Flat ~0.65 since R-209. Not reported as drift.

## Drift analysis — per-qid AGGREGATE (R-214 DEFECT D rule)

Every qid compared against the **full-history mean**, not a local median, and judged on aggregate deviation rather than raw event count:

**max |aggregate dev| = 0.0118 (q13_witness_log_opcode, −1.11σ). Nothing exceeds the 0.05 floor.**

This is a **real all-clear, not the thin-round artifact.** Current window n=1–8 per qid, but the baseline is n=108–152 per qid — the sample-size caveat applies to the *current* window, not the reference, so a thin round against a fat corpus is still a sound measurement. The exit-4 empty-baseline guard was pre-checked and did not fire.

Note the two-guard rule in action: q02 (0.69σ), q05 (0.20σ), q13 (−1.11σ) sit at or above 1σ but do not fire, because the σ-scaled floor never binds above 0.05 for tight distributions. σ and the 0.05 floor are separate guards and both are needed.

## Environment (this wipe)

- **102nd→103rd wipe**: `/workspace` bare on arrival AND `/tmp/jev_probe/` gone — both documented mirror homes empty again. Bootstrapped from `jev-quilt @ r-081-continuous-probe-rebuild` HEAD `5fb4fd5` (R-215), ~8s, then `git remote set-url` to strip the tokenized remote.
- **SSL_CERT_FILE gateway-anchor-only — 6th recurrence.** Default expectation every wipe. Rebuilt 289-cert bundle before the first call.
- **Canary reproduced the network pathology**: 1 OK (0.14s) + 1 TLS handshake-TO (8.10s) + 1 HTTP 503 (0.21s).
- **Throughput network-bound, 5th consecutive session — TIMEOUT_S=4 stays.** 21 OK + 2 fail (both handshake-TO). Never lower the read ceiling; the lever is the handshake budget or a persistent connection.
- **DEFECT A structurally impossible**: `rounds_r20261021T210442Z/` is timestamp-tagged, not a per-session hardcode. The `timeout -s KILL 75` ceiling let the run finish inside budget; analysis was re-derived from round files regardless, never from `session_summary.json`.
- **DEFECT B stayed fixed** — `load_history()` read 2,785 samples straight from the tracked file, no manual seeding for the 11th consecutive wipe.
- **Mirror verified by byte read-back** (NAS at 100%; 184,512 B history, 24 round files) — zero-byte writes were checked for explicitly.