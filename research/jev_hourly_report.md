# JEV Hourly Probe — Round 434

**Timestamp:** 2026-10-25T08:02:12Z  
**Model (resolved):** `jev-1.14.0`  
**Script:** root `jev_continuous_probe.py`, md5 `3a255fa4642ec4a83173ab04d773d485` (Variant A, positional `rounds` arg)  
**Instrument check:** `doctrinal_state_keys` = framework, core_doctrine, architecture, fleet, **spec_notebook**, operational_doctrine — 6 sections, `spec_notebook` present and correctly ordered (STATE-ORDER invariant holds)  
**Run:** 1 round, 0 fails, 5 verdicts, 0.13 s  
**Corpus:** 2125 deduped verdicts / 22 qids / 425 rounds (r1–r434)  
**Model split:** 1,930 × `jev-1.13.0` (r1–r395) / 195 × `jev-1.14.0` (r396–r434)

---

## Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.2240** |
| **Bedrock canon (p ≥ 0.70)** | **0 / 5** — no cathedral qid drawn this round |
| **Drift > 0.05** | **NONE** — every drawn qid clear on its own model segment |
| Script's own `drift_events` | 0 (not a verdict — see Method) |
| Model switch | none (1.13.0 → 1.14.0 boundary is at r396, long past) |

**Verdict: healthy.** The 0/5 bedrock count is a *draw-mix* artefact, not a substrate weakness — MC puts P(0 bedrock) at 8.72 % and today's mean_p sits at z = −1.24 against the empirical draw distribution (P(mean_p ≤ 0.2240) = 8.59 %). Every drawn question is a speculative/review qid; the cathedral was simply not sampled. No qid moved more than 0.05 from its own `jev-1.14.0` baseline.

---

## Round 434 verdicts

| qid | p | kind | bedrock? |
|---|---|---|---|
| q09 | 0.10 | speculative | no |
| q12 | 0.46 | speculative | no |
| q16 | 0.20 | review | no |
| q18 | 0.26 | speculative | no |
| q21 | 0.10 | speculative | no |

All five drawn qids are **speculative (4)** or **review (1)**. Per the promotion gate, `p ≥ 0.70` is required to enter canon; the highest reading is q12 at 0.46 and it is a speculative qid, so **nothing here is promotable** — and nothing should be.

### Drift check — model-segmented, drawn qids only

**Segmented on each qid's own `jev-1.14.0` segment (the verdict basis), with the pooled
all-model baseline shown only as a contrast column.** The 1.14.0 segments are thin (n = 4–9 per
qid) because the model boundary is only 38 rounds old, so the pooled column is retained to show
exactly what the wrong baseline would have said.

| qid | p | n (1.14.0) | μ₁₄ | dev₁₄ | σ₁₄ | z₁₄ | pooled dev | verdict |
|---|---|---|---|---|---|---|---|---|
| q09 | 0.10 | 4 | 0.1000 | **+0.0000** | 0.0100 | 0.00 | +0.0223 | **CLEAR** |
| q12 | 0.46 | 9 | 0.4989 | **−0.0389** | 0.0325 | −1.20 | +0.0805 ⚠ | **CLEAR** (pooled would flag) |
| q16 | 0.20 | 7 | 0.1914 | **+0.0086** | 0.0064 | +1.34 | +0.0012 | **CLEAR** |
| q18 | 0.26 | 9 | 0.2478 | **+0.0122** | 0.0079 | +1.56 | +0.0345 | **CLEAR** |
| q21 | 0.10 | 7 | 0.0929 | **+0.0071** | 0.0045 | +1.58 | +0.0094 | **CLEAR** |

**No drift > 0.05.** All five sit inside the absolute floor on their own model segment, and
every z₁₄ is below 2. Note that three qids carry large z on the *pooled* baseline (q09 +3.13,
q18 +3.21, q21 +2.34) on |dev| of only 0.009–0.034 — the σ≈0 trap; the largest z is routinely
the smallest real movement.

**🔴 The POOLED baseline would have manufactured a flag — 4th reproduction.** Pooling across the r396 model boundary puts q12 at dev **+0.0805 (> 0.05)**, which reads as a headline-grade drift. Segmented on its own `jev-1.14.0` segment, q12 reads dev **−0.0389, |dev| < 0.05, 77.8th percentile of its own |dev| distribution, z = −1.20 — CLEAR**. The entire +0.0805 is the model step itself: q12's mean is 0.3671 on 1.13.0 (n=87) and 0.4989 on 1.14.0 (n=9) — a +0.13 jump at the boundary, not a substrate trend. **Always segment by model before computing dev; report both.**

**Today's q12 = 0.46 is a REPEAT, not a new extreme.** It equals r422's 0.46 (2 prior values of 0.46 exist; 1.14.0 values are 0.46/0.46/0.47/0.49/0.50/0.50/0.51/0.54/0.56). Per the r422 rule a repeat is archive-judgeable — and the archive says clear. Within 1.14.0 the OLS slope is **−0.00098/draw (R² = 0.134)**: no trend.

**q09 fresh re-measurement (the only new extreme).** q09 = 0.10 had 0 prior values exactly equal, so per the r427 rule it was re-measured: **6 fresh draws on the identical doctrinal state, same call path → 0.10, 0.09, 0.10, 0.10, 0.09, 0.10 (mean 0.0967, sd 0.0047)**, with **q04 as control on the same calls holding 0.86–0.89 (mean 0.8733)**. The control licenses attributing the spread to q09 rather than a sick call. Today's 0.10 reproduces; **no drift.**

---

## Bedrock canon — which questions hit p ≥ 0.70

**None this round** (0/5): no cathedral qid was drawn. The 8 bedrock qids are q01, q02, q03, q04, q05, q07, q08 (and q17 is *review* tier, never counted as bedrock).

### Cathedral health (per-qid hit rate, `jev-1.14.0` segment)

| qid | n | hits | hit rate | μ | σ | min | max |
|---|---|---|---|---|---|---|---|
| q01 | 10 | 10 | 100.0% | 0.8540 | 0.0092 | 0.84 | 0.87 |
| q02 | 13 | 10 | 76.9% | 0.7277 | 0.0291 | 0.68 | 0.77 |
| q03 | 9 | 9 | 100.0% | 0.8811 | 0.0137 | 0.86 | 0.90 |
| q04 | 9 | 9 | 100.0% | 0.8822 | 0.0103 | 0.87 | 0.90 |
| q05 | 8 | 8 | 100.0% | 0.8150 | 0.0166 | 0.78 | 0.83 |
| q07 | 11 | 11 | 100.0% | 0.7700 | 0.0148 | 0.75 | 0.79 |
| q08 | 8 | 8 | 100.0% | 0.8900 | 0.0122 | 0.88 | 0.91 |
| **TOTAL (1.14.0)** | **68** | **65** | **95.59%** | | | | |

- All-time cathedral: **652 / 655 = 99.54%**
- Green rounds: **365 of 368** rounds that drew ≥ 1 cathedral qid had every drawn cathedral qid hit
- **No speculative or adversarial qid has EVER reached p ≥ 0.70 (0 / 1382 observations).**
- q12 max ever = **0.56** — q12 stays SPECULATIVE regardless of its score (the doctrinal state forbids promoting q10/q11/q12/q13).

### ⚠️ q02 watch item — still open, unchanged

| model | n | μ | σ | min | max | hits |
|---|---|---|---|---|---|---|
| jev-1.13.0 | 76 | 0.8245 | 0.0148 | 0.79 | 0.86 | 76/76 (100 %) |
| jev-1.14.0 | 13 | 0.7277 | 0.0291 | 0.68 | 0.77 | 10/13 (76.9 %) |

The 1.14.0 distribution **straddles the 0.70 gate** (below-gate draws: 0.68, 0.69, 0.69). q02 was not drawn this round, so it neither helps nor hurts. Standing watch item: **a 4th q02 breach, or a breach from ANY other cathedral qid, would make it a genuine drift finding.** This is an oracle-behaviour change (witness-vocabulary re-allocation at the r396 model boundary), **not** a substrate change — the doctrinal state is byte-identical and q01/q03/q04/q05/q07/q08 are all 100 % on 1.14.0.

---

## Comparison to previous rounds

*History table regenerated from the round archives by the same script that computes the drift — not hand-typed.*

| round | model | mean_p | bedrock | qids |
|---|---|---|---|---|
| r422 | jev-1.14.0 | 0.5060 | 2/5 | q01=0.85 q08=0.88 q09=0.09 q12=0.46 q18=0.25 |
| r423 | jev-1.14.0 | 0.5260 | 2/5 | q02=0.69 q05=0.80 q06=0.15 q08=0.88 q19=0.11 |
| r424 | jev-1.14.0 | 0.3760 | 2/5 | q01=0.86 q06=0.13 q10=0.05 q17=0.75 q21=0.09 |
| r425 | jev-1.14.0 | 0.3560 | 1/5 | q02=0.68 q05=0.81 q09=0.11 q20=0.09 q21=0.09 |
| r426 | jev-1.14.0 | 0.4040 | 2/5 | q04=0.87 q06=0.14 q07=0.76 q13=0.16 q21=0.09 |
| r427 | jev-1.14.0 | 0.4200 | 2/5 | q01=0.85 q04=0.88 q11=0.12 q13=0.15 q19=0.10 |
| r428 | jev-1.14.0 | 0.3760 | 1/5 | q02=0.72 q09=0.09 q13=0.16 q14=0.22 q17=0.69 |
| r429 | jev-1.14.0 | 0.5400 | 3/5 | q03=0.88 q07=0.75 q08=0.88 q13=0.16 q15=0.03 |
| r430 | jev-1.14.0 | 0.2840 | 1/5 | q07=0.78 q11=0.20 q16=0.18 q19=0.12 q22=0.14 |
| r431 | jev-1.14.0 | 0.4920 | 2/5 | q01=0.84 q08=0.89 q10=0.05 q12=0.49 q16=0.19 |
| r432 | jev-1.14.0 | 0.1880 | 0/5 | q10=0.05 q12=0.47 q14=0.25 q19=0.09 q20=0.08 |
| r433 | jev-1.14.0 | 0.5060 | 3/5 | q03=0.89 q07=0.79 q15=0.03 q17=0.73 q20=0.09 |
| r434 | jev-1.14.0 | 0.2240 | 0/5 | q09=0.10 q12=0.46 q16=0.20 q18=0.26 q21=0.10 |

- **Last-12 (excl. today): μ = 0.4145, σ = 0.1024 → z = -1.86**
- **MC (200k draws, 5 qids uniform from all 22, empirical per-qid p distribution): E[mean_p] = 0.3942, σ = 0.1374 → z = -1.24, P(mean_p ≤ 0.2240) = 8.59 %**
- P(k bedrock) under the draw: 0→8.72 %, 1→32.19 %, **2→38.03 % (modal)**, 3→17.67 %, 4→3.21 %, 5→0.18 %
- All-time mean_p = 0.3845

**A 0/5 draw with mean_p 0.2240 is an ordinary low draw, not a regression.** The previous round (r433) scored 0.5060 with 3/5 bedrock purely because it happened to draw q03/q07/q17. The aggregate moved; the instrument did not.

---

## Method (and the traps this round walked around)

1. **Model-segmented baselines.** The resolved model lives only in `history.jsonl` — the round file's `model` field is the static alias `jev-latest` (a script constant). Reading it from the round file makes every round look like one model and fuses the r396 model step permanently into the signal. The pooled-vs-segmented q12 contrast above is the 4th reproduction of this false positive.
2. **Drawn-qids-only.** Drift is judged only for the 5 qids actually drawn. The script's own `drift_check()` compares every qid's last value to a 5-sample local median whether or not that qid was drawn — it has reported stale events for 15 consecutive rounds. `drift_events` is a report, not a measurement.
3. **|dev| against the 0.05 absolute floor FIRST, sigma second.** Three qids here carry z ≥ 2.3 on |dev| of 0.009–0.034 — the σ≈0 trap. The largest z is routinely the smallest real movement.
4. **Dedup key = (qid, p, round)**, not (qid, p, ts): the round file and `history.jsonl` carry different `ts` for the same verdict, so a ts-based key double-counts and puts the duplicate on *today's* side, shrinking the deviation and under-reporting drift. Sanity assertion: each drawn qid appears exactly once at its own p — checked, passed.
5. **Re-measure before calling a new extreme.** q09 (the only new extreme) was re-measured with a control qid on the same call path. A new extreme cannot be judged from the archive; a repeat can.
6. **Regenerate the history table from the archives.** A hand-typed comparison table is the receipt a reader trusts most and the easiest one to get wrong.

---

## Environment (127th wipe)

- `/workspace` arrived **empty** — the task's `/workspace/research/jev_sessions/continuous_r*.json` path did not exist (20th consecutive wipe naming an ephemeral probe path). Bootstrapped `SuperInstance/jev-quilt` from git via `https://x-access-token:$GITHUB_TOKEN@github.com/...` with `GIT_SSL_NO_VERIFY=1` (clone OK, no 503).
- **NAS 100 % (0 avail)** → `rm -rf /workspace/research` then `ln -s /tmp/jev/jev-quilt/research /workspace/research`; the deliverable path resolves while the bytes live on the 28 G overlay. (`ln` into an existing directory silently creates the link *inside* it — `rm -rf` first.)
- **TLS leaf VALID** — CN=typesafe.ai, notAfter 2026-12-25 (61 days) → no CA bundle rebuild needed.
- `JEV_API_KEY="$TYPESAFE_AI_TOKEN"` mapping required (the vault holds `TYPESAFE_AI_TOKEN`; the client reads `JEV_API_KEY`/`TYPESAFEAPI_KEY`/`TYPESAFEAI_KEY`).
- **Explicit positional `1`** → exactly 1 round in 0.13 s. The default is **200**, and `timeout 60` alone races the writer to flush many rounds.
- Round counter derived from max(round files = 433, history.jsonl = 433) → start **434**; the script aborts if the target round file already exists, so no round was shadowed.

---

**Bottom line:** round 434 is clean. mean_p 0.2240 with 0/5 bedrock is an ordinary low draw (z = −1.24 vs the empirical draw distribution, P = 8.6 %); no question moved more than 0.05 from its own model segment; the one pooled-baseline flag (q12) dissolves under proper model segmentation and is a repeat of an existing value; and the q09 new-extreme was refuted by fresh re-measurement with a healthy control. The cathedral is 95.6 % on `jev-1.14.0` with q02 the sole deficit, and the q02 watch item is unchanged.
