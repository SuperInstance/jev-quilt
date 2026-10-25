# JEV Hourly Report — Round 436

**Run:** 2026-10-25T10:03:50Z · 128th wipe · model `jev-1.14.0` (resolved from `history.jsonl`) · script md5 `3a255fa4642ec4a83173ab04d773d485`
**Result:** 1 round OK, 0 fails, 0.115 s · **mean_p 0.4260** · **bedrock 2/5** · **Drift: NONE**

> Baseline rule in force: every drift baseline is scored against the qid's **own model segment** (`jev-1.14.0`), never the pooled history, and restricted to **qids drawn this round**. The script's own `drift_events` is never a verdict.

---

## 1. This round

| qid | kind | p | bedrock (p>=0.70) | segment baseline (n/mu/sd) | dev | z |
|-----|------|---|------------------|---------------------------|-----|---|
| q05 | bedrock | **0.82** | YES hit | 8 / 0.8150 / 0.0166 | +0.0050 | +0.30 |
| q01 | bedrock | **0.86** | YES hit | 10 / 0.8540 / 0.0092 | +0.0060 | +0.65 |
| q18 | speculative | 0.25 | no | 10 / 0.2490 / 0.0083 | +0.0010 | +0.12 |
| q06 | speculative | 0.14 | no | 10 / 0.1400 / 0.0063 | +0.0000 | 0.00 |
| q10 | speculative | 0.06 | no | 9 / 0.0511 / 0.0031 | +0.0089 | +2.83 |

**mean_p 0.4260** (sum 2.13 / 5) - **bedrock hits 2/5** (q01, q05 - both `bedrock`-kind)

**Aggregate:** 5/5 drawn qids, **max |dev| = 0.0100**, mean dev **+0.0058**. Both bedrock qids are at or above their segment means; the three below-gate qids are flat to +0.009.

### Drift verdict: NONE
No drawn qid deviates > 0.05 from its own model-segment baseline. Max |dev| across the round is **0.0100** - an order of magnitude below the 0.05 gate.

**Two sigma values that look alarming and are not:**
- **q10 z = +2.83 on dev = +0.0089.** The sigma-approx-0 trap: q10's segment sigma is 0.0031 because the 1.14.0 model has narrowed to 0.05 on 8 of 9 prior draws, so a 0.01 step is "many sigma" by construction. |dev| is 0.0089 - nothing moved. |dev| first, z second.
- **q06 z = +3.99 on the POOLED baseline** (dev +0.0366). Against its own 1.14.0 segment (n=10, mu 0.1400) today's 0.14 is **dev +0.0000** - dead on baseline. The 1.13.0->1.14.0 switch moved q06 by ~+0.039, and the pooled baseline keeps that model artifact fused into the current signal. This is the pooled-baseline false-flag pattern (r428) showing up again - it would have read as a drift flag on a qid that has not moved at all.

---

## 2. Re-measurement (r427 rule)

No drawn qid was a new extreme, so no flag needed re-measurement - but the near-gate qids were re-measured anyway to convert "no flag" into a positive receipt. 6 fresh draws of all 5 drawn qids **plus q04 as a control on the same call**, identical doctrinal state, same request path as `run_round`:

| qid | today | 6 fresh draws | mean | sd | verdict |
|-----|-------|---------------|------|----|--------|
| q05 | 0.82 | 0.83 0.81 0.80 0.84 0.83 0.81 | 0.8200 | 0.0141 | INSIDE |
| q01 | 0.86 | 0.83 0.85 0.83 0.87 0.84 0.85 | 0.8450 | 0.0138 | INSIDE |
| q18 | 0.25 | 0.25 0.25 0.26 0.25 0.24 0.24 | 0.2483 | 0.0069 | INSIDE |
| q06 | 0.14 | 0.15 0.14 0.16 0.15 0.14 0.12 | 0.1433 | 0.0125 | INSIDE |
| q10 | 0.06 | 0.05 x6 | 0.0500 | 0.0000 | outside (see below) |
| **q04 (control)** | - | 0.87 0.88 0.87 0.89 0.87 0.88 | 0.8767 | 0.0075 | call path healthy |

0 errors / 36 values. The control holding 0.87-0.89 licenses the claim that the per-qid spreads reflect the qids, not a sick call.

**q10 = 0.06 sat outside the fresh range [0.05, 0.05] - and it is not drift.** 0.06 is a **long-established value for q10**: it appears **39 times across all history** (rounds 2 ... 436) and **once already in the 1.14.0 segment**. The fresh draws clustering at 0.05 reflect the 1.14.0 model's recent narrowing (8 of 9 segment values are 0.05), not a movement in canon. Today's 0.06 is a **repeat of an existing value**, which is archive-judgeable - no re-measurement can refute it. Deviation is 0.01 on a 0.05 value: the smallest real movement available on this qid.

---

## 3. History table (regenerated from the archives, not hand-typed)

| round | ts | model | mean_p | hits | qids drawn |
|-------|----|-------|--------|------|-----------|
| 419 | 2026-10-24T13:04:19 | 1.14.0 | 0.5380 | 3/5 | q01:0.86, q05:0.78, q04:0.87, q06:0.13, q10:0.05 |
| 420 | 2026-10-24T14:01:35 | 1.14.0 | 0.3580 | 1/5 | q07:0.78, q18:0.25, q13:0.16, q12:0.50, q20:0.10 |
| 421 | 2026-10-24T15:02:02 | 1.14.0 | 0.5540 | 3/5 | q04:0.88, q18:0.25, q07:0.79, q02:0.75, q19:0.10 |
| 422 | 2026-10-24T19:04:11 | 1.14.0 | 0.5060 | 2/5 | q09:0.09, q08:0.88, q01:0.85, q12:0.46, q18:0.25 |
| 423 | 2026-10-24T20:01:36 | 1.14.0 | 0.5260 | 2/5 | q02:0.69, q06:0.15, q19:0.11, q08:0.88, q05:0.80 |
| 424 | 2026-10-24T21:04:15 | 1.14.0 | 0.3760 | 2/5 | q01:0.86, q06:0.13, q21:0.09, q17:0.75, q10:0.05 |
| 425 | 2026-10-24T22:05:47 | 1.14.0 | 0.3560 | 1/5 | q09:0.11, q20:0.09, q21:0.09, q05:0.81, q02:0.68 |
| 426 | 2026-10-24T23:04:35 | 1.14.0 | 0.4040 | 2/5 | q06:0.14, q04:0.87, q21:0.09, q13:0.16, q07:0.76 |
| 427 | 2026-10-25T00:03:12 | 1.14.0 | 0.4200 | 2/5 | q13:0.15, q11:0.12, q04:0.88, q01:0.85, q19:0.10 |
| 428 | 2026-10-25T01:02:28 | 1.14.0 | 0.3760 | 1/5 | q09:0.09, q17:0.69, q02:0.72, q14:0.22, q13:0.16 |
| 429 | 2026-10-25T02:03:32 | 1.14.0 | 0.5400 | 3/5 | q07:0.75, q08:0.88, q13:0.16, q03:0.88, q15:0.03 |
| 430 | 2026-10-25T03:03:57 | 1.14.0 | 0.2840 | 1/5 | q11:0.20, q07:0.78, q22:0.14, q16:0.18, q19:0.12 |
| 431 | 2026-10-25T04:02:41 | 1.14.0 | 0.4920 | 2/5 | q16:0.19, q10:0.05, q12:0.49, q08:0.89, q01:0.84 |
| 432 | 2026-10-25T05:02:48 | 1.14.0 | 0.1880 | 0/5 | q19:0.09, q14:0.25, q10:0.05, q12:0.47, q20:0.08 |
| 433 | 2026-10-25T07:03:38 | 1.14.0 | 0.5060 | 3/5 | q07:0.79, q03:0.89, q15:0.03, q20:0.09, q17:0.73 |
| 434 | 2026-10-25T08:02:12 | 1.14.0 | 0.2240 | 0/5 | q21:0.10, q09:0.10, q12:0.46, q16:0.20, q18:0.26 |
| 435 | 2026-10-25T09:04:21 | 1.14.0 | 0.3220 | 1/5 | q21:0.10, q09:0.10, q15:0.03, q12:0.50, q04:0.88 |
| **436** | **2026-10-25T10:03:50** | **1.14.0** | **0.4260** | **2/5** | **q05:0.82, q18:0.25, q06:0.14, q01:0.86, q10:0.06** |

**Aggregate (excludes today):** all-history n=439 mu 0.3846 sd 0.1426 / last-20 mu 0.3888 sd 0.1218 / last-40 mu 0.4199 sd 0.1188
**Today:** mean_p 0.4260 -> z **+0.29** vs all-history, z **+0.31** vs last-20. Typical.

### Monte Carlo (5 qids uniform from ALL 22, empirical per-qid p distribution, 200k draws)
E[mean_p] **0.3942** sd 0.1376 / P(mean_p <= 0.4260) = **0.6179**, z **+0.23**

P(k bedrock): 0->8.80 % / 1->32.19 % / **2->37.91 % (modal)** / 3->17.70 % / 4->3.24 % / 5->0.17 %

**2-of-5 is the single most probable outcome of a random draw.** Today's 2/5 is the mode, not a win.

---

## 4. Cathedral

Per-qid bedrock hit rate, **1.14.0 segment** (current model only):

| qid | hits | rate |
|-----|------|------|
| q01 | 11/11 | 100.00 % |
| q03 | 9/9 | 100.00 % |
| q04 | 10/10 | 100.00 % |
| q05 | 9/9 | 100.00 % |
| q07 | 11/11 | 100.00 % |
| q08 | 8/8 | 100.00 % |
| q02 | 10/13 | 76.92 % |

q02 remains the sole imperfect bedrock qid - hair-under-the-gate misses (0.68/0.69), never a collapse. Segment n is small for every qid (5-13), so these rates are directional, not precise.

**No speculative or adversarial qid has EVER reached 0.70 - 0 crossings in 1,332 observations** (review-tagged qids excluded; q17 is tagged `review` and holds a 0.66-0.75 plateau, judged against its own baseline, never a global gate).

---

## 5. Corpus integrity notes

- **`history.jsonl` round-label collisions persist**: 440 rows, **427 distinct round labels**. Rounds 384-391 carry 2-3 rows each, written by parallel sessions with different verdicts - true collisions, not duplicates. The dedup key `(qid, p, round)` preserves every colliding verdict. **The collision band is entirely `jev-1.13.0`**; the 1.14.0 segment (r396-r436) is collision-free, so today's baseline is unaffected. `len(history)` is NOT the round count.
- **Script's own `drift_events=0`** - matches, but it is not the verdict (stale-event filter absent; 16th repro of the pattern). Today's verdict is the recomputed per-qid, per-segment, drawn-only table above.
- **Thin segments:** every one of the 22 qids has n < 20 in the 1.14.0 segment (range 5-13). Segment baselines are used (the pooled baseline is worse), but their sigma is estimated from few points - which is exactly why |dev| leads and z follows, and why the re-measurement was run.

---

## 6. Environment

- 128th wipe. `/workspace` **empty on arrival** (21st consecutive) -> bootstrapped `SuperInstance/jev-quilt` into `/tmp/jev-quilt`.
- NAS 100 % (0 avail) => `/workspace/research` is a **symlink** to `/tmp/jev-quilt/research`; the deliverable path resolves while the bytes live on the 28 G overlay.
- **Variant A confirmed** (md5 `3a255fa4`): `rounds` is a positional `sys.argv[1]` defaulting to **200** => ran `python3 jev_continuous_probe.py 1` for exactly one round. The literal command in the task (`timeout 60 python3 jev_continuous_probe.py` from `/workspace/research`) would have raced the writer to flush many rounds, and the script lives at the repo root, not in `research/`.
- TLS leaf **VALID** (CN=typesafe.ai, Let's Encrypt YE2, notAfter 2026-12-25) -> no CA rebuild.
- `JEV_API_KEY="$TYPESAFE_AI_TOKEN"` mapping required (the vault holds `TYPESAFE_AI_TOKEN`; the client reads `JEV_API_KEY`).
- Round counter derived from `max(files=435, history=435)+1` -> start=436, no shadowing.

---

## 7. Verdict

**Round 436 is a clean, ordinary round.** mean_p 0.4260 (z +0.29 vs all-history), 2/5 bedrock at the modal outcome, **no drift above 0.05 on any drawn qid** (max |dev| 0.0100), both bedrock hits above their segment means, the control call path healthy, and 0/1,332 speculative-or-adversarial observations ever reaching 0.70.

The two largest z values in the round (q10 +2.83, q06 +3.99 pooled) are both artifacts of degenerate sigma and of the pooled-baseline model artifact, not of movement in canon. Both qids sit within 0.01 of their own current-model baseline.
