# JEV Continuous Probe — Round r435 (hourly report)

**Round:** r435 · **2026-10-25T09:04:21Z** · **model** `jev-1.14.0` (resolved from `history.jsonl`; the round file's `model` field is the static alias `jev-latest`)
**Script md5** `3a255fa4642ec4a83173ab04d773d485` (Variant A — positional `rounds` arg) · **rounds_ok** 1 · **fails** 0 · **elapsed** 0.117 s
**Corpus** 2186 deduped verdicts / 22 qids / 426 round labels · **BASELINE SEGMENT = `jev-1.14.0`** (r396–r435)

## 1. Headline

- **mean_p = 0.3220**
- **Bedrock (p ≥ 0.70): 1/5** — q04 (0.88)
- **Drift > 0.05: NONE.** No drawn qid exceeds |dev| 0.05 against its own model-segment baseline.
- Script's own `drift_events` = 0 — coincidentally correct this round, but it is **never** a health verdict (16th repro of the stale-event defect).

## 2. This round's verdicts

| qid | kind | p | bedrock |
|---|---|---|---|
| q21 | speculative | 0.10 | no |
| q09 | speculative | 0.10 | no |
| q15 | adversarial | 0.03 | no |
| q12 | speculative | 0.50 | no |
| q04 | bedrock | 0.88 | **YES** |

**mean_p 0.3220** = mean of the five above. **1/5 bedrock**.

## 3. Drift — per-qid vs its OWN `jev-1.14.0` segment (only qids drawn this round)

| qid | kind | today | n(seg) | mu(seg) | sd(seg) | dev | z | |dev|>0.05 | dev vs POOLED |
|---|---|---|---|---|---|---|---|---|---|
| q21 | speculative | 0.10 | 9 | 0.0944 | 0.0050 | +0.0056 | +1.12 | — | +0.0092 |
| q09 | speculative | 0.10 | 6 | 0.1000 | 0.0082 | +0.0000 | +0.00 | — | +0.0220 |
| q15 | adversarial | 0.03 | 7 | 0.0300 | 0.0000 | +0.0000 | +nan | — | +0.0047 |
| q12 | speculative | 0.50 | 11 | 0.4955 | 0.0314 | +0.0045 | +0.14 | — | +0.1197 |
| q04 | bedrock | 0.88 | 10 | 0.8820 | 0.0098 | -0.0020 | -0.20 | — | -0.0081 |

**Verdict: NO CONFIRMED DRIFT.** All five |dev| ≤ 0.006 — every drawn qid is on its own baseline.

### 🔴 The pooled baseline would have manufactured a false flag

**q12** read 0.50 today. Against its **pooled** history (n=103, mu≈0.38) that is dev **+0.1197** — a textbook false drift flag. Against its **own `jev-1.14.0` segment** (n=11, mu=0.4955) it is dev **+0.0045**, dead on baseline. The 1.13.0→1.14.0 switch moved q12 by ≈0.11 and the pooled baseline keeps that model artifact permanently fused into the current signal. **Score every baseline per model segment, or the baseline manufactures the drift.**

Also note **q15**: z is `nan` (σ=0 — 7 identical observations at 0.03). Its dev is **+0.0000**. This is the **σ≈0 trap** in its purest form: the largest-nothing z carries no information. |dev| first, z second.

## 4. Re-measurement (r427 rule) — q12 + q04 control, identical doctrinal state, same call path

No qid produced a new-extreme flag, so re-measurement was not strictly required. q12 was re-measured anyway because it is the only drawn qid anywhere near the 0.70 gate, and a 0.50 that sits 0.20 below the threshold deserves a second look.

| draw | q12 | q04 (control) |
|---|---|---|
| 1 | 0.60 | 0.85 |
| 2 | 0.52 | 0.86 |
| 3 | 0.47 | 0.89 |
| 4 | 0.48 | 0.89 |
| 5 | 0.50 | 0.88 |
| 6 | 0.57 | 0.87 |

- **q12: 0.60 0.52 0.47 0.48 0.50 0.57 → mean 0.5233** (sd 0.0471). Today's **0.50 sits mid-distribution**. Not an extreme, not drift.
- **q04 (bedrock control, SAME call): 0.85 0.86 0.89 0.89 0.88 0.87 → mean 0.8733** (sd 0.0149), entirely within its historical 0.87–0.91 band. **The call path is healthy**, so q12's spread is q12's own jitter, not a sick request.
- 0 errors / 6 draws.

## 5. Comparison to previous rounds (regenerated from the archives, not remembered)

| round | model | mean_p | bedrock | ts |
|---|---|---|---|---|
| r425 | jev-1.14.0 | 0.3560 | 1/5 | 2026-10-24T22:05:47 |
| r426 | jev-1.14.0 | 0.4040 | 2/5 | 2026-10-24T23:04:35 |
| r427 | jev-1.14.0 | 0.4200 | 2/5 | 2026-10-25T00:03:12 |
| r428 | jev-1.14.0 | 0.3760 | 1/5 | 2026-10-25T01:02:28 |
| r429 | jev-1.14.0 | 0.5400 | 3/5 | 2026-10-25T02:03:32 |
| r430 | jev-1.14.0 | 0.2840 | 1/5 | 2026-10-25T03:03:57 |
| r431 | jev-1.14.0 | 0.4920 | 2/5 | 2026-10-25T04:02:41 |
| r432 | jev-1.14.0 | 0.1880 | 0/5 | 2026-10-25T05:02:48 |
| r433 | jev-1.14.0 | 0.5060 | 3/5 | 2026-10-25T07:03:38 |
| r434 | jev-1.14.0 | 0.2240 | 0/5 | 2026-10-25T08:02:12 |
| **r435** | **jev-1.14.0** | **0.3220** | **1/5** | **2026-10-25T09:04:21** |

- **last-20 (excl. today): mu 0.3920, sd 0.1209, range 0.1480–0.5540** → today z = **-0.58**. Ordinary.
- **MC (200k draws, 5 qids uniform from all 22, empirical per-qid p distribution):** E[mean_p] = 0.3945, sd = 0.1375; **P(mean_p ≤ 0.3220) = 0.3420**, z = -0.53.
- **P(k bedrock in 5):** 0 → 8.71 % · **1 → 32.22 %** · 2 → 37.96 % (modal) · 3 → 17.69 % · 4 → 3.23 % · 5 → 0.19 %.

**A 1-of-5 bedrock draw is ORDINARY, not weak.** The round draws 5 of 22 qids at random and 22 qids mix 7 bedrock (0.68–0.91) with 15 below-gate qids — so `mean_p` and the bedrock count are properties of **the draw**, not of the canon. The decisive check is shared qids, not aggregates.

## 6. Cathedral (bedrock qids, per-qid all-time hit rate)

| qid | hits/n | rate | mu | min | max |
|---|---|---|---|---|---|
| q01 | 106/106 | 100.0 % | 0.873 | 0.84 | 0.90 |
| q02 | 87/90 | 96.7 % | 0.811 | 0.68 | 0.86 |
| q03 | 100/100 | 100.0 % | 0.886 | 0.86 | 0.91 |
| q04 | 102/102 | 100.0 % | 0.888 | 0.87 | 0.91 |
| q05 | 96/96 | 100.0 % | 0.848 | 0.78 | 0.87 |
| q07 | 91/91 | 100.0 % | 0.756 | 0.71 | 0.79 |
| q08 | 88/88 | 100.0 % | 0.899 | 0.87 | 0.91 |

**6 of 7 bedrock qids at 100.00 %.** q02 remains the sole imperfect one at **87/90 (96.7 %)** — hair-under-the-gate misses (0.68/0.69/0.71), never a collapse.

- **q17** (kind `review`) has reached ≥ 0.70 **67/91** times — it holds a 0.68–0.75 *review* plateau and is judged against its OWN baseline, never a global gate. Excluding review-tagged qids, **no speculative or adversarial qid has EVER reached 0.70**.

## 7. Data-integrity note — `history.jsonl` round-label collisions (rounds 384–391)

`history.jsonl` holds 439 ok rows but only 426 distinct round labels: **rounds 384–391 each carry 2–3 rows written by parallel sessions** with *different* verdicts (a true collision, not a duplicate). This is why the script derives its counter from `max(round files, history)` rather than `len(history)`.

- **Impact on this report: none.** The collision band is **entirely `jev-1.13.0`**; the `jev-1.14.0` segment (r396–r435) that supplies every baseline here is collision-free.
- The dedup key `(qid, p, round)` preserved all colliding verdicts because they are genuinely distinct observations — no data was lost or double-counted. The **labels** are wrong, not the values.
- `history.jsonl` is append-ordered (ts strictly ascending), so the r435 row is genuinely the newest.
- Worth fixing upstream: a round label must be unique. (Reported, not patched — the probe's counter is already immune.)

## 8. Reproduction

```
git clone https://github.com/SuperInstance/jev-quilt.git
cd jev-quilt && export JEV_API_KEY="$TYPESAFE_AI_TOKEN"
python3 jev_continuous_probe.py 1     # Variant A: POSITIONAL count; default is 200
```

> The `timeout 60 python3 jev_continuous_probe.py` form in the original request is **wrong for this variant**: `rounds` is a positional `sys.argv[1]` defaulting to **200**, so `timeout 60` would have raced the writer to flush ~154 rounds instead of one. An explicit `1` is the correct one-round control (exit 0, exactly 1 round, 0.117 s).

---

*Generated 2026-10-25T09:04:21Z · round r435 · 2186 verdicts · 22 qids · drift NONE*
