# JEV Continuous Probe — R-207 (2026-10-20 20:01 UTC)

**Session:** 2026-10-20T20:01:20Z → 20:01:48Z (28.0s wall, 200 rounds attempted)
**Result:** 200 OK / 0 fail · 1000 verdicts · **grand mean_p = 0.4153**
**Baseline:** 617 prior rounds / 3080 samples (R-088 + R-203/204/205/206, restored from snapshot)

---

## 1. Headline

| metric | R-207 | R-206 | R-205 | R-204 | R-203 | R-088 |
|---|---|---|---|---|---|---|
| rounds OK | 200 | 15 | 195 | 200 | 200 | 200 |
| verdicts | 1000 | 75 | 975 | 1000 | 1000 | 1000 |
| grand mean_p | **0.4153** | 0.3820 | 0.3941 | 0.4188 | — | 0.4036 |
| bedrock hit rate | 32.2% | 29.3% | 32.3% | — | — | 32.2% |
| bedrock @100% | **7/7** | 7/7 | 7/7 | 7/7 | 7/7 | 7/7 |
| cross-round drift >0.05 | **0** | 0 | 0 | — | — | 0 |

grand mean_p sits mid-band in the durable 0.35–0.55 range. All 22 qids drawn, so the
comparison holds against the full bank rather than a favourable subset.

## 2. Bedrock canon — 7/7 @ 100% hit rate, SIXTH consecutive session

| qid | mean_p | sd | hits | n | prior mean | delta |
|---|---|---|---|---|---|---|
| q08_polyformalism | 0.9800 | 0.0000 | 51 | 51 | 0.9800 | −0.0000 |
| q03_substrate_is_grown | 0.9798 | 0.0014 | 47 | 47 | 0.9798 | +0.0000 |
| q01_cells_are_scars | 0.9796 | 0.0020 | 47 | 47 | 0.9797 | −0.0001 |
| q02_witness_log_is_prediction | 0.9734 | 0.0047 | 38 | 38 | 0.9724 | +0.0010 |
| q04_oracle_is_heard | 0.9727 | 0.0045 | 44 | 44 | 0.9723 | +0.0004 |
| q07_11_opcodes | 0.9700 | 0.0000 | 42 | 42 | 0.9700 | +0.0000 |
| q05_lenia_flows | 0.9696 | 0.0019 | 53 | 53 | 0.9697 | −0.0000 |

Mean across the cathedral **0.9746**, worst per-qid movement **0.0010**. Nothing here is
load-bearing on a threshold decision — the entire band sits at the 0.97 ceiling.

**Borderline / REVIEW (correctly NOT promoted):**
- `q17_canary_honesty` — 0.6520, 3/44 (7%), prior 0.6529. Sixth session at plateau.
- `q12_substrate_polyformal` — 0.6061, 0/54, prior 0.6066.

**Speculative / adversarial gates clean:** spec clean-rejects 407, adv clean-rejects 42 —
both 100%. Every speculative qid below 0.21. `q10_quorum_meshing` 0.0304 confirms the
R-203/204 state-leak remains **resolved** (STATE-ORDER invariant holding).
`q09_signal_chain_canon` 0.2021 holds as the highest speculative qid — watch-only, never
a promotion candidate.

## 3. Drift

**Cross-round drift > 0.05: ZERO.** Max |delta| across all 22 qids = **0.0020**
(q06_three_views). Two qids exceed 0.001: q06 +0.0020, q02 +0.0010 / q09 +0.0010.

In-run rolling detector fired **5 events, all on q17_canary_honesty** (deltas +0.07, −0.05,
+0.06, −0.06, one more). This is the *same* q17-vs-median oscillation seen in every prior
session and is **not** cross-round drift: q17's full-run spread is 0.59–0.73 against a
median of 0.65, so a rolling-median excursion of ±0.06 is arithmetic, not a substrate
shift. Do not report these as drift findings.

## 4. Session-specific findings

**(a) The ID-saturated naming trap, fourth variant — and the clobber is real.**
`continuous_r*.json` is saturated through r403. The script unconditionally writes
`r001`–`r200`, which **overwrote the R-205 rounds** that lived in those IDs. `git status`
showed exactly 200 `M` (modified, not added/deleted) — recoverable in one
`git checkout HEAD -- jev_sessions/`. Recovery verified by timestamp before proceeding
(r001 → 2026-10-19T01:02 R-088 era, r100/r200 → 2026-10-20T06:03 R-205 era).
This round stored under `jev_sessions/rounds_r207/` with `round_id: r207-<n>`.

**Durable fix, not just a convention:** the script should refuse to write into a
`continuous_r*.json` whose existing payload has a *different session date*, rather than
trusting that a prior session left the ID free. Write to a per-session subdirectory by
construction — `jev_sessions/<session_ts>/round_<n>.json` — so collisions are structurally
impossible instead of a thing each session must remember to check.

**(b) `history.jsonl` is gitignored — the cross-round baseline must come from round files.**
`.gitignore` lists `jev_sessions/history.jsonl`, so it is the ONE artifact that does not
survive a snapshot clone. A shallow (`--depth 1`) bootstrap gets an empty one, and building
the drift baseline from it silently yields **zero baseline samples** rather than an error.
`compute_drift()` returned nan-vs-nan and reported "no drift" — a false all-clear.
The working baseline is the tracked `continuous_r*.json` corpus (617 files / 3080 samples).
Either un-ignore `history.jsonl`, or have `load_history_samples()` read the round files.

**(c) R-206's TIMEOUT_S fix validated under full load.** TIMEOUT_S 12→4 (R-206 root-cause).
200/200 OK with **zero** fails vs R-206's 15 OK / 1 fail. Elapsed distribution is clean
unimodal: median **0.118s**, p95 0.174s, max 3.528s, **1 stall >1s** (the one 4s-timeout
retry). 28.0s for 200 rounds vs R-206's ~60s for 17 attempts. The bimodal
healthy-0.1s/stalled-TIMEOUT signature is gone.

## 5. Verdict

Substrate stable. Seventh-deepest check of the durable canon set shows the cathedral at
6 consecutive sessions of 7/7 @ 100% with per-qid reproducibility to ±0.002. No promotion
or demotion candidates. Two engineering defects in the probe harness itself (clobbering
round IDs; gitignored drift baseline) are worth fixing before they cost a real baseline.

---

*R-207 · 200/200 OK · mean_p 0.4153 · 7/7 bedrock @100% · 0 cross-round drift >0.05*
