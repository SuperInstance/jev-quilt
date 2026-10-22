# JEV Continuous Probe — Hourly Report

**Run:** 2026-10-22T14:02Z (4th run of the day, post-wipe)
**Rounds:** r396–r575 (180 rounds, 0 fails)
**Model:** `jev-1.14.0` · **Script md5:** `bda7ccb3d3af4d1c2c7e961e2dcf174a` (identical to prior 2 runs ⇒ comparable)

## Headline

| Metric | Value |
|---|---|
| **grand_mean_p** | **0.4240** |
| total verdicts | 900 |
| bedrock hits | 340 / 900 (37.8%) |
| real drift > 0.05 | **none** |
| script-reported drift events | 1 — **false positive** (q17) |
| fails | 0 |

**mean_p vs prior runs** (same script md5): 0.3829 (2nd run) → 0.4023 (3rd run) → **0.4240** (this run).
Upward trend across the three runs, +0.041 total. Consistent with q02 continuing its recovery (see below).

## Bedrock canon — questions at p ≥ 0.70

**7/7 canonical bedrock questions hold.**

| qid | mean_p | rounds ≥0.70 | rate | status |
|---|---|---|---|---|
| q08 | 0.8965 | 118/118 | 100% | canon |
| q03 | 0.8852 | 139/139 | 100% | canon |
| q04 | 0.8859 | 135/135 | 100% | canon |
| q01 | 0.8698 | 139/139 | 100% | canon |
| q05 | 0.8391 | 128/128 | 100% | canon |
| q07 | 0.7613 | 118/118 | 100% | canon |
| q02 | 0.7881 | 114/122 | 93.4% | canon |
| q17 | 0.7066 | 90/125 | 72.0% | review — above threshold |

q02 continues recovering: hit rate 86.7% (3rd run) → **93.4%** (this run), mean 0.7282 → **0.7881**. The REAL q02 drift flagged in the 2nd run has now fully settled.

q17 (`review` kind) sits just above threshold at 0.7066 / 72% and tracks q02.

Everything else stays correctly low: speculative questions q06 .1125, q09 .0827, q10 .0627, q20 .1003, q21 .0915, q22 .1249; adversarial q15 .0263, q19 .1052. No speculative claim has crept upward — the promotion gate still correctly separates canon from speculation.

## Drift analysis

**No real drift.** Verified two independent ways.

1. **Series test** (last 20 vs prior 60, all 22 questions, |dev| > 0.05): **zero flags.**
2. **Thirds trend** on the bedrock 7: all flat within ±0.004 except q02, which is **monotonic-up** (+0.0158) — recovery, not decay.

The script reported 1 event: **q17, recent_p 0.75 vs prior_median 0.69, delta +0.06.**

**Verdict: FALSE POSITIVE.** q17's series runs 0.7175 → 0.7175 → 0.7044 across thirds (**−0.0131**), last-20 vs prior-60 **−0.0131**, whole-run stdev 0.0270. The flag claims *rising*; the series is actually *mildly falling* — the sign flips because q17 straddles the 0.70 boundary and one sample out of 48 decides the direction. Same failure mode as the q12 flag in the 2nd run.

`drift_check(window=5)` compares a **single last sample** against the prior-5 median. At 180 rounds that is a one-sample deviation test, which will fire on any question sitting near its threshold. **Always re-verify by hand against the series before acting.**

## Environment / method notes (this wipe)

- **4th wipe today.** `/workspace` empty except `.plugin-cache`; NAS at **100% (600G/600G, 0 avail)** ⇒ cannot create `/workspace/research/` or write any report file there. All work in `/tmp`; report delivered inline.
- **Round-counter shadowing trap, 4th confirmed instance.** Script hardcodes `SESSION_DIR=/tmp/jev_probe/jev_sessions` (line 49) and derives the start round from the highest `continuous_r*.json` **file** (lines 345–347). Clone's highest file was **r383** while `history.jsonl` held round **395** — a naive run would have re-shadowed 384–395 permanently. Fixed by seeding a synthetic `continuous_r395.json` anchor from the last history row. Verified afterwards: 565 rows, 565 distinct, **0 dups**, resumed cleanly at r396.
- **API healthy.** `POST https://api.typesafe.ai/v1/systemone` → **HTTP 400 "Invalid request"** on a dummy payload = server rejecting bad input ⇒ DNS + TLS + auth all good. TLS wall down again (3rd consecutive run).
- Copy into `/tmp` verified with `find -size +0c` (204 non-empty session files) — the `cp -a` 0-byte truncation trap does not apply to `/tmp`.
- Verdict records key on **`qid`**, not `q`; `kind` is per-verdict (bedrock/speculative/adversarial/review). Each round samples **5 of 22** questions, so per-question n ranges 31–154 across the run.

## Carry forward

- Cross-check **both** the highest session file **and** `history.jsonl` before every run; seed a synthetic anchor when they disagree. The file counter lies; the jsonl is the truth.
- The script's drift check is a one-sample test — treat its flags as prompts to investigate, not findings.
- q02 recovery is now corroborated across two runs (86.7% → 93.4%); re-check next run to confirm it has not regressed.
