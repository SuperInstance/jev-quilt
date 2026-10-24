# JEV continuous probe — round 417 (2026-10-24T11:0xZ)

**Verdict: HEALTHY. mean_p 0.4180 is exactly what the class mix predicts, not a collapse. 2/2 bedrock drawn hit p>=0.70. The script's `drift_events=1` is a PHANTOM (8th reproduction). Two real drawn-qid deviations, both benign. q02's decline is a model-version artifact, now 21 rounds old and stable.**

- **Round:** 417 (single round; positional count `1`)
- **Model:** `jev-1.14.0` (21st consecutive round on this model; 1.14.0 live since r396)
- **Script md5:** `3a255fa4642ec4a83173ab04d773d485` (unchanged from r416 — comparable)
- **mean_p:** **0.4180**
- **bedrock hits:** **2/5** verdicts at p>=0.70 (both bedrock qids drawn HIT)
- **fails:** 0 · elapsed 0.178 s · exit 0 · history.jsonl 420→421 lines, round 417 recorded once
- **Baseline:** 407 unique rounds / 22 qids / 2,035 samples (asserted non-empty)

---

## 1. The round's verdicts

| qid | kind | p | p>=0.70 | baseline mu | dev |
|-----|------|---|---------|-------------|-----|
| q14 | adversarial | 0.25 | no | 0.1942 | **+0.0558** (z=+4.06) |
| q20 | speculative | 0.08 | no | 0.1041 | −0.0241 (z=−2.27) |
| **q08** | **bedrock** | **0.91** | **YES** | 0.8994 | +0.0106 (z=+1.21) |
| q21 | speculative | 0.10 | no | 0.0905 | +0.0095 (z=+2.39) |
| **q02** | **bedrock** | **0.75** | **YES** | 0.8159 | **−0.0659** (z=−2.09) |

**mean_p = 0.4180 = (0.25 + 0.08 + 0.91 + 0.10 + 0.75) / 5**

## 2. Questions hitting p>=0.70 (bedrock canon)

**2 of 5 — q08 (0.91) and q02 (0.75).** Both bedrock qids that were drawn hit; **no non-bedrock qid crossed 0.70** (no speculative promotion candidate, no adversarial leak).

All-time bedrock hit-rates (from the 407-round baseline):

| qid | kind | n | mu | all-time hit-rate | this round |
|-----|------|---|-----|------------------|-----------|
| q01 | bedrock | 101 | 0.8745 | 101/101 = 100% | not drawn |
| q02 | bedrock | 83 | 0.8159 | 82/83 = 98.8% | **0.75 HIT** |
| q03 | bedrock | 96 | 0.8855 | 96/96 = 100% | not drawn |
| q04 | bedrock | 94 | 0.8886 | 94/94 = 100% | not drawn |
| q05 | bedrock | 88 | 0.8498 | 88/88 = 100% | not drawn |
| q07 | bedrock | 81 | 0.7551 | 81/81 = 100% | not drawn |
| q08 | bedrock | 81 | 0.8994 | 81/81 = 100% | **0.91 HIT** |

*(`review` class is separate: q17 mu 0.7027, 61/83 = 73.5% at threshold — a plateau that sits ON the line by design; q16 mu 0.1993, 0/94.)*

**7 of 7 bedrock qids at 100% all-time hit-rate except q02 at 98.8%** — the same single q02 miss from r416 (0.69) remains the only bedrock sub-threshold draw in the entire corpus.

## 3. mean_p 0.4180 is a CLASS-MIX NUMBER, NOT A HEALTH SIGNAL

This is the third round in a row where `mean_p` alone would have cried wolf. Recomputing properly:

- Per-kind baseline mu: bedrock **0.8548**, review 0.4353, speculative 0.1474, adversarial 0.1002
- r417's mix (1 adversarial, 2 speculative, 2 bedrock) ⇒ **expected mean_p = 0.4209**
- **Observed 0.4180 — within 0.003 of expectation.**
- Monte Carlo (uniform class-mix bootstrap, n=20,000): **P(mean_p >= 0.418) = 0.391** ⇒ completely ordinary, near the median draw.
- The last-20 window mean is **0.4343** and **366 of 388 historical 20-round windows sit BELOW it** ⇒ the corpus is in its *upper* band, not declining.

**⇒ mean_p 0.4180 is a perfectly normal draw. It is not a collapse, and it is not a recovery either. Read the cathedral (bedrock), not the grand mean.**

## 4. Drift

### 4.1 The script's `drift_events=1` is a PHANTOM (8th reproduction)

The script's `drift_check()` compares every qid's last value to a local 5-sample median **whether or not that qid was drawn this round**:

```
drift_events=1 -> q12: recent_p=0.56 prior_median=0.50 delta=+0.06
q12 DRAWN THIS ROUND = False
```

**q12 was not drawn.** This is the same defect as r410, r414, r416 and four earlier rounds. A qid that was not sampled cannot have drifted *this round*. Always intersect drift with the drawn qid set.

### 4.2 Real drift, restricted to qids DRAWN this round

Recomputed as `p_this − full_history_mean` for the 5 drawn qids only (baseline = 407 unique rounds, 2,035 samples, asserted non-empty):

| qid | p | baseline mu | sd | dev | z | verdict |
|-----|---|-------------|----|-----|---|---------|
| q14 | 0.25 | 0.1942 | 0.0138 | +0.0558 | +4.06 | >0.05 — reported, benign |
| q02 | 0.75 | 0.8159 | 0.0315 | −0.0659 | −2.09 | >0.05 — reported, explained below |
| q20 | 0.08 | 0.1041 | 0.0106 | −0.0241 | −2.27 | within band |
| q08 | 0.91 | 0.8994 | 0.0088 | +0.0106 | +1.21 | within band |
| q21 | 0.10 | 0.0905 | 0.0040 | +0.0095 | +2.39 | within band |

**Two drawn qids exceed |dev| > 0.05.** Both are explainable and neither indicates canon movement:

**q14 (+0.0558)** — 0.25 is a **TIE with r413's all-time max**, not a new maximum (baseline max 0.25, reached once before). Last 20 draws average 0.198 vs all-time 0.194 — a hair of upward creep in an adversarial qid that is *supposed* to read low and has never come close to 0.70. z is large only because q14's σ is tiny (0.0138); the absolute movement is 0.056 on a 0.19 baseline. **Benign, but it is the first adversarial qid to touch its ceiling — worth a second look if it repeats.**

**q02 (−0.0659)** — carried forward from r416, and now **resolved**: see §5.

## 5. q02: version artifact, not canon drift

r416 left q02 open with a "real signal vs model artifact" question. r417 answers it.

**Stratifying by model version:**

| qid | jev-1.13.0 | jev-1.14.0 |
|-----|-----------|-----------|
| q02 | n=75, **mu 0.8247**, sd 0.0148 | n=8, **mu 0.7337**, sd 0.0274 |
| q08 | n=78, mu 0.8996 | n=3, mu 0.8933 |
| q03 | n=89, mu 0.8860 | n=7, mu 0.8800 |

q02 stepped down **−0.0909** at the 1.13→1.14 boundary while q03/q04/q08 stayed flat (≤0.006) — q02 is uniquely sensitive to the model bump. **The version boundary explains the level shift.**

**Is there a residual trend *within* 1.14.0?** All 9 draws on the new model:

```
r399 0.75   r401 0.77   r406 0.73   r407 0.71   r411 0.77
r412 0.71   r414 0.74   r416 0.69   r417 0.75
```

- Spearman rho within 1.14.0 **with r417 included = −0.346** (down from −0.566 at n=8, i.e. the new mid-pack draw *flattens* the trend)
- r417's 0.75 ranks **6/9 ascending — dead mid-pack** among 1.14.0 draws
- Across all q02 draws ever, 0.75 is at the **6th percentile** (min 0.69, max 0.86)

**⇒ q02 is NOT in free-fall.** r416's 0.69 was the single floor value; r417's 0.75 is a typical 1.14.0 draw, the within-version slope relaxed, and the all-time miss record is unchanged (82/83, still only r416). The residual within-1.13.0 decline reported in r416 (rho=−0.271, p=0.016) predates the model switch and cannot be extrapolated across it. **No promotion, no alarm: this is a re-baselined q02, and the correct baseline for it is mu=0.734 (n=9), not the blended 0.8159.**

## 6. Promotion gate — nothing promoted

No speculative qid crossed 0.70 this round, and the `spec_notebook` guard (n>=20, hit-rate>=0.7, explicit doctrinal-state phrasing) is unchanged. q12 remains the highest speculative reading in the corpus (mu 0.374, max 0.56) — still well under the bar, and still not drawn this round.

## 7. Corpus health

- 407 unique baseline rounds, 22/22 qids with history, 2,035 samples — all baselines asserted non-empty (no `nan` all-clear)
- last-40-rounds bedrock hit rate: **73/200 = 36.5%** (≈ the 5-of-22-draw expectation of 1.43 bedrock/draw × 40 rounds = 57 bedrock draws; 73 is in the expected band)
- 20-round windows: n=388, mean 0.3818, range 0.3039–0.4615; current window 0.4343 sits in the top decile
- 8 duplicate round records in history.jsonl (r384–r391, the pre-r229 counter defect) — de-duplicated for all baseline math; r417 is recorded exactly once

## 8. Method notes carried forward

- **A "one round" ask must be launched with an explicit positional count.** `timeout 60 python3 jev_continuous_probe.py` with no arg defaults to **200** rounds inside a 55 s wall; killing after launch races the writer. `python3 jev_continuous_probe.py 1` returns in 0.178 s with exactly one round flushed.
- **`drift_check()` reports HISTORY events, not this round's events** (8th repro). Always recompute restricted to drawn qids.
- **|dev| first, sigma second.** q14's z=+4.06 is the largest z in the round, but its |dev| is 0.056 on a 0.19 baseline — a tie with a prior max. The largest z is often the smallest real movement.
- **Judge every qid against its OWN baseline.** A single global threshold mislabels plateau qids (q12 ~0.37, q16 ~0.20, q17 ~0.70 by design).
- **Never read mean_p without the class mix.** 5 uniform draws from 8 bedrock / 9 spec / 3 adv / 2 review ⇒ a low mean is the default ~75% of the time. Here the expectation was 0.4209 and we got 0.4180.
- **Re-baseline per-qid stats per model version.** The blended q02 mu of 0.8159 describes no live model.

## 9. Environment

- **112th wipe.** `/workspace` arrived empty (only `.plugin-cache`); `/workspace/research/` absent ⇒ recovered by cloning `SuperInstance/jev-quilt` to `/tmp` and `git fetch --unshallow` (408 unique rounds, 22 qids).
- **NAS at 100% (0 avail)** ⇒ `/workspace/research/jev_hourly_report.md` **cannot be landed**; a `cp` there yields "Disk quota exceeded" and leaves a **0-byte stub that appears in `ls`** (silent-zero trap, 24th observation). **Durable copy = git.** This report is committed to `research/jev_hourly_report.md` in the repo; the NAS path remains unwritable.
- **TLS healthy, no wall.** Live leaf `notAfter 2026-12-25`; `SSL_CERT_FILE` was the gateway-anchor-only bundle ⇒ rebuilt the **289-cert** combined bundle at `/tmp/bundle.pem`, which made Python urllib verify cleanly.
- API healthy: 1 round in 0.178 s, 0 fails, HTTP 422/403 never seen. `TYPESAFE_AI_TOKEN` present, `TYPESAFEAI_KEY` unset (script accepts either).

## 10. Bottom line

**The probe is healthy and the round is unremarkable.** mean_p 0.4180 is within 0.003 of its class-mix expectation (MC percentile 0.39), both bedrock qids drawn hit p>=0.70, no non-bedrock crossed the threshold, and 7 of 7 bedrock qids remain at 98.8–100% all-time hit-rate. The script's lone drift event is a phantom on an undrawn qid. The two genuine drawn-qid deviations are benign: q14 ties its all-time max on an adversarial qid that has never been near 0.70, and q02's apparent drop is fully accounted for by the jev-1.13.0 → jev-1.14.0 calibration step — its new draw is mid-pack among 1.14.0 values and *flattened* the within-version slope. Nothing to promote, nothing to alarm about, one adversarial qid worth a second look if it repeats.
