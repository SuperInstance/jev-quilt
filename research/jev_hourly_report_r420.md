# JEV Continuous Probe — Round 420 (2026-10-24T14:05Z)

**Script** `jev_continuous_probe.py` md5 `3a255fa4642ec4a83173ab04d773d485` (repo-root variant, unchanged) · **model** `jev-1.14.0` · **status** OK · 5/5 verdicts

---

## 1. Headline

| | |
|---|---|
| **mean_p** | **0.3580** |
| **bedrock hits (p ≥ 0.70)** | **1 / 5** — q07 (0.78) |
| **drift > 0.05 (full-history baseline)** | **1 — q12, dev +0.1246 (+2.69σ)** |
| **drift > 0.05 (same-model 1.14.0 baseline)** | **NONE** (max \|dev\| = 0.0143) |
| **script `drift_events`** | **0** |

**Verdict: an ordinary draw. The single full-history drift flag on q12 is an artifact of comparing across the jev-1.13.0 → jev-1.14.0 model switch, not a movement inside the live model era.**

---

## 2. The round

| qid | kind | p | p ≥ 0.70 |
|---|---|---|---|

| q07 | bedrock | 0.78 | **HIT** |
| q18 | speculative | 0.25 | — |
| q13 | speculative | 0.16 | — |
| q12 | speculative | 0.50 | — |
| q20 | speculative | 0.10 | — |

Only one bedrock question was drawn (q07, 1 of 8 bedrock in the 22-question bank). The other four were speculative.

---

## 3. Is mean_p 0.3580 a signal? — NO, it is class mix

mean_p mixes 8 bedrock (≈0.75–0.90) with 12 speculative + 2 adversarial (≈0.02–0.25). A 5-of-22 draw makes the grand mean a **lottery**, not a health metric.

- **MC bootstrap** (200,000 synthetic rounds, 5 qids sampled from 22, per-qid means from the deduped corpus): **P(mean_p ≤ 0.3580) = 0.385** — an entirely unremarkable draw.
- MC expectation for this class-mix: **0.3941**; observed 0.3580 ⇒ **z = −0.42** against the last-20-round distribution (mu 0.4102, sd 0.1243).
- **P(bedrock_drawn = 1) = 0.362** — r420's 1/5 hit count is the *expected* rate, not a shortfall.
- r418 (0.1480, 0/5) and r419 (0.5380, 3/5) are the same lottery, 60 minutes apart. **Never read mean_p alone.**

---

## 4. Drift — the one real flag, and why it is a cross-model artifact

### 4.1 Against the FULL-HISTORY baseline (all 411 deduped rounds)

| qid | kind | p | baseline mu | sd | dev | z | n |
|---|---|---|---|---|---|---|---|

| q07 | bedrock | 0.78 | 0.7549 | 0.0164 | +0.0251 | +1.53 | 83 |
| q18 | speculative | 0.25 | 0.2250 | 0.0103 | +0.0250 | +2.42 | 108 |
| q13 | speculative | 0.16 | 0.1349 | 0.0092 | +0.0251 | +2.73 | 94 |
| q12 | speculative | 0.50 | 0.3765 | 0.0470 | +0.1235 **← FLAG** | +2.63 | 93 |
| q20 | speculative | 0.10 | 0.1038 | 0.0112 | -0.0038 | -0.34 | 89 |

**q12 = 0.50, dev +0.1246 (+2.69σ), only qid over the 0.05 bar.**

But the baseline for q12 is dominated by the *old* model:

| model | rounds | q12 n | q12 mu | q12 max | q12 ≥ 0.48 |
|---|---|---|---|---|---|
| jev-1.13.0 | r1–r395 | 87 | 0.3671 | **0.44** | **0 / 87** |
| jev-1.14.0 | r396–r420 | 7 | 0.5117 | 0.56 | 7 / 7 |

**Under jev-1.13.0, q12 never once reached 0.48 in 87 draws.** Under 1.14.0 it has never been below 0.46. The step is a **model change, not a drift** — the same shape as the q02 step already documented at r416.

### 4.2 Against the SAME-MODEL (1.14.0) baseline — the correct comparison

| qid | kind | p | n(1.14) | mu14 | sd14 | dev | z |
|---|---|---|---|---|---|---|---|

| q07 | bedrock | 0.78 | 6 | 0.7667 | 0.0125 | +0.0133 | +1.07 |
| q18 | speculative | 0.25 | 7 | 0.2471 | 0.0088 | +0.0029 | +0.32 |
| q13 | speculative | 0.16 | 6 | 0.1617 | 0.0037 | -0.0017 | -0.45 |
| q12 | speculative | 0.50 | 6 | 0.5117 | 0.0318 | -0.0117 | -0.37 |
| q20 | speculative | 0.10 | 7 | 0.0857 | 0.0073 | +0.0143 | +1.96 |

**No qid exceeds |dev| = 0.05 against the live model.** Max |dev| = 0.0143 (q20), max |z| = +1.96 (q20) on n=7 — inside noise for a 7-sample baseline.

### 4.3 The script's own drift check

`drift_events = 0` this round. Note the standing defect: `drift_check()` scans the **entire history for every qid regardless of whether it was drawn**, and compares the last value to a 5-sample local median. It has produced **10 phantom events** (r410–r419) by re-firing q12's stale r409 sample. It was silent this round only because r420 *happened* to draw q12, replacing the stale sample.

⇒ **Standing rule (unchanged): recompute drift yourself — per-qid, restricted to qids DRAWN THIS ROUND, and judge each qid against a baseline of the SAME model era.** |dev| first, σ second. A z-score computed against a near-degenerate σ is not a finding.

---

## 5. Cathedral (bedrock canon) — unchanged, 99.84%

| qid | n (all-time) | hits | hit rate | mean_p | min_p |
|---|---|---|---|---|---|

| q01 | 100 | 100 | **100.0%** | 0.8744 | 0.84 |
| q02 | 85 | 84 | **98.8%** | 0.8151 | 0.69 |
| q03 | 96 | 96 | **100.0%** | 0.8855 | 0.86 |
| q04 | 96 | 96 | **100.0%** | 0.8885 | 0.87 |
| q05 | 91 | 91 | **100.0%** | 0.8490 | 0.78 ← r419 all-time min |
| q07 | 83 | 83 | **100.0%** | 0.7549 | 0.71 |
| q08 | 80 | 80 | **100.0%** | 0.8996 | 0.87 |
| **TOTAL** | **631** | **630** | **99.84%** | | |

**All-time: 630/631 = 99.84%.** Six of seven bedrock questions at a 100% all-time hit rate; q02 remains the only non-perfect one (98.8%, from the r416 model step). **No promotion, no demotion, no qid changed class.** q10/q11/q12/q13 remain speculative per `spec_notebook` regardless of score — q12's 0.50 does not promote it.

### 5.1 The live model era (jev-1.14.0, r396–r420) — 43/44 = 97.73%

| qid | n | hits | hit rate | mu | min | max |
|---|---|---|---|---|---|---|

| q01 | 6 | 6 | 100.0% | 0.8567 | 0.84 | 0.87 |
| q02 | 9 | 8 | 88.9% | 0.7356 | 0.69 | 0.77 |
| q03 | 7 | 7 | 100.0% | 0.8800 | 0.86 | 0.90 |
| q04 | 6 | 6 | 100.0% | 0.8850 | 0.87 | 0.90 |
| q05 | 6 | 6 | 100.0% | 0.8183 | 0.78 | 0.83 |
| q07 | 6 | 6 | 100.0% | 0.7667 | 0.75 | 0.78 |
| q08 | 4 | 4 | 100.0% | 0.8975 | 0.88 | 0.91 |
| **TOTAL** | **44** | **43** | **97.73%** | | | |

**q02 is the only 1.14-era bedrock below 100%** (88.9%, 8/9, min 0.69) — the same r416 model step, now with 25 rounds of confirmation. It is a *model-level* shift, not a canon change: q02 still reads 0.73–0.77, well above the 0.70 bar on 8 of 9 draws.

---

## 6. Comparison to previous rounds (r411–r420)

| round | mean_p | hits | model | verdicts |
|---|---|---|---|---|

| r411 | 0.4240 | 2/5 | jev-1.14.0 | q19=0.10 q14=0.21 q02=0.77* q16=0.19 q01=0.85* |
| r412 | 0.5520 | 3/5 | jev-1.14.0 | q10=0.05 q18=0.24 q08=0.88* q03=0.88* q02=0.71* |
| r413 | 0.4540 | 2/5 | jev-1.14.0 | q03=0.86* q18=0.23 q14=0.25 q05=0.82* q19=0.11 |
| r414 | 0.2800 | 1/5 | jev-1.14.0 | q18=0.25 q16=0.20 q02=0.74* q13=0.16 q10=0.05 |
| r415 | 0.3860 | 1/5 | jev-1.14.0 | q03=0.86* q17=0.68 q18=0.25 q09=0.11 q15=0.03 |
| r416 | 0.2400 | 0/5 | jev-1.14.0 | q21=0.09 q22=0.14 q10=0.06 q14=0.22 q02=0.69 |
| r417 | 0.4180 | 2/5 | jev-1.14.0 | q14=0.25 q20=0.08 q08=0.91* q21=0.10 q02=0.75* |
| r418 | 0.1480 | 0/5 | jev-1.14.0 | q06=0.14 q14=0.21 q19=0.11 q11=0.19 q20=0.09 |
| r419 | 0.5380 | 3/5 | jev-1.14.0 | q01=0.86* q05=0.78* q04=0.87* q06=0.13 q10=0.05 |
| r420 | 0.3580 | 1/5 | jev-1.14.0 | q07=0.78* q18=0.25 q13=0.16 q12=0.50 q20=0.10 |

`*` = bedrock hit. r420 is unremarkable in this window: mean_p 0.3580 sits between r415 (0.3860) and r414 (0.2800); the 1.14-era range over the last 10 rounds is 0.1480–0.5380.

**Class-mix note:** r418 drew 0 bedrock (mean_p 0.1480), r419 drew 3 (0.5380), r420 drew 1 (0.3580). A monotonic "recovery" narrative across r418→r420 would be reading the lottery, not the oracle.

---

## 7. Method notes (durable, carried forward)

1. **mean_p is a class-mix number — never read it alone.** Class-conditional expectation + MC bootstrap first. r420's 0.3580 has P = 0.385 under the mix; it is an ordinary draw.
2. **"N bedrock hits" is vacuous when bedrock_drawn is low.** r420 drew 1 bedrock of 5; P(bedrock_drawn == 1) = 0.362. Hit count only means something alongside the mix.
3. **Judge drift against the SAME-MODEL baseline.** The jev-1.13.0 → jev-1.14.0 switch (r396) moved q12 by +0.14σ-worth of distribution (0.3671 → 0.5117, 0/87 vs 7/7 above 0.48) and q02 down by ~0.09. **Any drift claim spanning the switch is measuring the switch.**
4. **de-duplicate `history.jsonl` by round number before baseline math** — this file carries **13 duplicate rounds** (424 lines → 411 unique). Every baseline in this report is computed post-dedup.
5. **A threshold verdict is not a finding.** q12's 0.50 is *below* the 0.70 canon bar, *above* its own 1.14-era mean, and *below* its own 1.14-era max (0.56 at r409). It trips neither a promotion nor a regression rule.
6. **Bucket each qid against its OWN baseline** — a single global threshold mislabels plateau qids (q12, q16 read 0.16–0.25 by design).
7. **`drift_check()` has produced 10 phantom events** (r410–r419) by scanning non-drawn qids. The standing cheap fix remains: **pass the drawn qid set into the function.**

---

## 8. Environment (115th wipe)

- **`/workspace` arrived EMPTY** (only `.plugin-cache`) — the user's stated path `/workspace/research/jev_sessions/continuous_r*.json` did not exist. Repo re-cloned to the overlay; corpus re-derived from `research/jev_sessions/` (LIVE tree, 228 round files) + `history.jsonl` (423 lines).
- **NAS at 100% (0 avail, 600 G used).** A direct write into `/workspace/research/` **returned exit 0 and produced a 0-byte file** — the 27th observation of the silent-zero trap. ⇒ **`/workspace/research/jev_hourly_report.md` is UNWRITABLE; the durable copy is git** (`research/jev_hourly_report_r420.md`).
- **Repo root is the live script** (`jev_continuous_probe.py`, md5 `3a255fa4…`), not the `continuous/` variant (md5 `95b552ea…`).
- **`SSL_CERT_FILE` = gateway-anchor-only (12th recurrence)** ⇒ rebuilt a **289-cert** bundle at `/tmp/combined-ca.crt`; TLS leaf `docs.typesafe.ai` **notAfter Dec 10 2026 = VALID**. Python urllib verifies clean against the rebuilt bundle.
- **API healthy:** `POST https://api.typesafe.ai/v1/systemone` → **HTTP 200**, `model: jev-1.14.0`. A hand-made body of the wrong shape returns **HTTP 400 "Invalid request."** — that is a body-shape fault, not an auth or network wall (and matches the durable note: 400 ≠ broken, 422 = healthy-but-wrong-shape, 401 = reachable-but-no-creds).
- `TYPESAFE_AI_TOKEN` set, `TYPESAFEAI_KEY` unset (script accepts either).
- `gh` absent (23rd). Clone/push need `GIT_SSL_NO_VERIFY=1`; push to the explicit token URL and verify with `git fetch` + `git rev-parse FETCH_HEAD:<path>`.
- **Work in `/tmp/<repo>`** (overlay, 28 G free) — the overlay is NOT subject to the NAS EDQUOT trap.
- **Run discipline:** `python3 -u jev_continuous_probe.py 1` — the positional arg defaults to **200**, and killing after launch races the writer to flush ~154 rounds. One round, one explicit count.

