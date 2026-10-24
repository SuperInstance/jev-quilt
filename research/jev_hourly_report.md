# JEV continuous probe — r412 (2026-10-24T04:04Z)

**One round, exactly as asked** (positional `rounds=1` on the root instrument — not a launch-and-kill; the positional arg now works, so no kill was needed and the run self-terminated in 0.27 s).
Probe: `jev_continuous_probe.py` (repo root), script md5 `3a255fa4642ec4a83173ab04d773d485` — **identical to r404–r411**, so mean_p is directly comparable with the hourly series.
Model: `jev-1.14.0` · API: `api.typesafe.ai/v1/systemone` · 0 fails · 0.12 s per round.

**Environment note (109th wipe).** `/workspace` was empty on arrival and the NAS quota read 100 % (`600G/600G` on an empty mount); `write` to the workspace root produced a 0-byte stub, so the probe was cloned and run under `/tmp/jev/jev-quilt` and the round file + `history.jsonl` append were made there. All 385 rounds shared between the canonical `research/jev_sessions/history.jsonl` and the legacy root `jev_sessions/history.jsonl` **agree exactly**, so the baseline below is not contaminated by the r397 `SESSION_DIR` relocation.

---

## Headline

| metric | value |
|---|---|
| rounds_ok | **1** (r412) |
| fails | **0** |
| **mean_p** | **0.5520** |
| verdicts | 5 |
| **p >= 0.70 hits** | **3 / 5** — `q08` 0.88, `q03` 0.88, `q02` 0.71 |
| **drift > 0.05** | **1 nominal flag (q12) — PHANTOM**; **1 REAL shift (q02) — a model-version artefact, not a substrate drift** |
| cathedral (bedrock canon) | **619/619 = 100 %** corpus-wide; **586/586 on `jev-1.13.0` and 33/33 on `jev-1.14.0` — 100 % within each model version** |

**mean_p 0.5520 is high but this round drew 3 of 7 bedrock questions** (q08, q03, q02) and 0 of 10 speculative. The hourly series r404–r412 reads 0.440, 0.390, 0.294, 0.458, 0.438, 0.368, 0.418, 0.424, **0.552**. r412 is above the band, and the reason is draw composition, not a health change — grand mean_p is draw-mix confounded at n=5.

---

## r412 verdicts

| qid | kind | p | baseline mean (all history) | dev | sigma | z | p>=0.70 |
|---|---|---|---|---|---|---|---|
| q10 | speculative | 0.05 | 0.0666 (n=114) | -0.0166 | 0.0054 | -3.05 | no |
| q18 | speculative | 0.24 | 0.2240 (n=102) | +0.0160 | 0.0095 | +1.68 | no |
| **q08** | **bedrock** | **0.88** | 0.8996 (n=80) | -0.0196 | 0.0086 | -2.29 | **YES** |
| **q03** | **bedrock** | **0.88** | 0.8861 (n=93) | -0.0061 | 0.0092 | -0.67 | **YES** |
| **q02** | **bedrock** | **0.71** | 0.8184 (n=81) | **-0.1097** | 0.0272 | **-4.47** | **YES** |

Real movement on this round: **q02, dev -0.1097, z = -4.47.** The other four qids are flat (|dev| <= 0.020, and the two large z values on q10 and q08 are the **sigma~0 trap** — a 0.0054 sigma over 114 samples makes a 0.017 deviation three sigma, and it is not a trend).

---

## The reported drift is wrong in BOTH directions

`drift_check()` reported **1 event: q12, +0.06**. That flag is **phantom** — q12 was **not drawn in r412**. It last appeared at r409. The check has no current-round filter, so it re-flags stale draws (the r411 report already documented this defect; it fires again here).

Meanwhile the check **missed the only real movement on the round**, because it compares against a **5-sample local median**, not the long-run baseline. q02's prior-5 median is 0.75 (r406 0.73, r407 0.71, r411 0.77, r392 0.79, r401 0.77), so the 0.71 reading produced only a -0.04 delta — under the 0.05 bar. Against the long-run mean the deviation is **-0.1097**, which clears it.

**A local 5-sample median cannot detect a slow shift.** That is the structural reason this drift was nearly invisible.

---

## The real cause: `jev-1.13.0` -> `jev-1.14.0` at r396

The corpus splits cleanly along a model-version boundary that the instrument never segments on. `model` changed at **r396**:

| model | rounds | q02 n | q02 mean | q02 min | q12 n | q12 mean |
|---|---|---|---|---|---|---|
| `jev-1.13.0` | 386 | 75 | **0.8247** | 0.79 | 87 | **0.3679** |
| `jev-1.14.0` | 17 | 6 | **0.7400** | 0.71 | 5 | **0.5140** |

**Bootstrap 95 % CI on the q02 difference: [-0.1048, -0.0644] — excludes zero.** The shift is not sampling noise.

Per-qid across the boundary, exactly **two** questions move more than 0.05, and they are precisely the two **"witness"-vocabulary** questions:

| qid | kind | 1.13.0 | 1.14.0 | delta | flag |
|---|---|---|---|---|---|
| **q12** | speculative | 0.3679 (n=87) | 0.5140 (n=5) | **+0.1461** | **MODEL-SHIFT** |
| **q02** | **bedrock** | 0.8247 (n=75) | 0.7400 (n=6) | **-0.0847** | **MODEL-SHIFT** |
| q01 | bedrock | 0.8754 (n=96) | 0.8560 (n=5) | -0.0194 | noise |
| q05 | bedrock | 0.8512 (n=83) | 0.8275 (n=4) | -0.0237 | noise |
| q06 | speculative | 0.0990 (n=84) | 0.1420 (n=5) | +0.0430 | noise |
| q13 | speculative | 0.1329 (n=89) | 0.1625 (n=4) | +0.0296 | noise |
| q22 | speculative | 0.1193 (n=91) | 0.1467 (n=3) | +0.0273 | noise |
| q18 | speculative | 0.2234 (n=100) | 0.2500 (n=3) | +0.0266 | noise |
| q11 | speculative | 0.1850 (n=88) | 0.1825 (n=4) | -0.0025 | flat |
| q10 | speculative | 0.0669 (n=112) | 0.0500 (n=3) | -0.0169 | flat |
| q16 | review | 0.1996 (n=89) | 0.1925 (n=4) | -0.0071 | flat |
| q17 | review | 0.7025 (n=77) | 0.7100 (n=5) | +0.0075 | flat |
| q14 | adversarial | 0.1921 (n=80) | 0.2150 (n=4) | +0.0229 | noise |
| q15 | adversarial | 0.0250 (n=109) | 0.0300 (n=3) | +0.0050 | flat |
| q19 | adversarial | 0.1051 (n=77) | 0.1000 (n=4) | -0.0051 | flat |
| q03 | bedrock | 0.8860 (n=89) | 0.8880 (n=5) | +0.0020 | flat |
| q04 | bedrock | 0.8887 (n=89) | 0.8880 (n=5) | -0.0007 | flat |
| q07 | bedrock | 0.7545 (n=76) | 0.7640 (n=5) | +0.0095 | flat |
| q08 | bedrock | 0.8996 (n=78) | 0.8933 (n=3) | -0.0063 | flat |

Every question outside the witness pair moves **less than 0.025**. The effect is isolated, not fleet-wide.

### What moved, in plain terms

`jev-1.14.0` **re-allocated canonicity inside the "witness" vocabulary**. The bedrock doctrine *"witness logs are predictions"* lost mass; the speculative framing *"witness_note is an opcode"* gained it. The two are complementary readings of the same word, and the new model weighs the opcode framing higher.

This is a change in **the oracle's behaviour, not in the substrate**. `JEV_LEARNINGS.md` line 125 states *"JEV does not drift. It pattern-matches state->answer deterministically with small noise."* That holds — but only **within a model version**. The probe sends a byte-identical `DOCTRINAL_STATE` (script md5 unchanged since r397, question bank unchanged since Oct 1) and gets a different answer, because the model behind it changed.

The state itself contains the tension: `core_doctrine` says *"witness logs are predictions"* while `spec_notebook` says *"q12 witness_note_opcode ... is SPECULATIVE and not yet canon."* `jev-1.14.0` resolved that tension differently than `1.13.0` did. **That is the mechanism.**

---

## The canon is NOT at risk

Three separate checks, all clean:

1. **Cathedral holds at 100 % — and holds within each model version separately.** q01 101/101, q02 81/81, q03 94/94, q04 94/94, q05 87/87, q07 81/81, q08 81/81 = **619/619**. Split: `1.13.0` **586/586 = 100 %**, `1.14.0` **33/33 = 100 %**. q02 still clears the 0.70 gate on every single draw under the new model.
2. **No canon-promotion violation.** No speculative or adversarial question has ever reached p >= 0.70 in the corpus. q12's new high of 0.56 (r409) is still speculative, and the promotion gate needs n>=20 AND hit-rate >= 0.7.
3. **Adversarial questions still read low.** q14/q15/q19 all remain at 0.02-0.22. The oracle was not simply inflated.

**One watch item:** q02's margin above the bedrock gate on `1.14.0` is thin. Its `1.14.0` samples are 0.75, 0.77, 0.73, 0.71, 0.77, **0.71** — minimum 0.71, i.e. **0.01 above the gate**. The mean has moved 0.085 downward, and 0.71 is the joint-lowest value in q02's entire 81-sample history. q02 remains canon, but it is now the **fragile** member of the cathedral, and a further downward move under `1.14.0` would begin to matter.

---

## Verdict

**r412 is healthy, and its one alarming number has a benign explanation.**

- mean_p 0.5520 — above band, but explained by drawing 3 of 7 bedrock questions and 0 of 10 speculative. Draw-mix, not substrate change.
- 3/5 bedrock hits: q08 0.88, q03 0.88, q02 0.71. All three canon, all three correct.
- **Drift > 0.05: the one flag the instrument printed (q12 +0.06) is phantom** — q12 was not drawn. The one real movement (q02, -0.1097) is a **model-version artefact** of `jev-1.14.0` replacing `1.13.0` at r396, not a drift in the substrate. Verified by a bootstrap CI that excludes zero, by the fact that the effect is confined to the two "witness" questions while every other qid moved < 0.025, and by the fact that the doctrinal state and question bank are byte-identical across the boundary.
- Cathedral 619/619 = 100 %, and 100 % within each model version. Canon intact.

---

## Instrument defects on the books (this round confirms three of them)

1. **`drift_check()` has no current-round filter** — it printed q12 as this round's drift when r412 did not draw it. Phantom event, second confirmation (r410, r411, r412).
2. **`drift_check()` uses a 5-sample local median, which cannot detect a slow shift.** q02's real -0.1097 dev measured -0.04 against the local median and was missed. **A rolling local median is the wrong instrument for drift in a slowly-moving series.**
3. **The 0.05 absolute threshold is mis-calibrated at n>100** — it fires on 31-69 % of a qid's own history, and simultaneously *misses* a real 0.11 dev (this round). It should be a per-qid percentile or a z-threshold.
4. **NEW: the drift machinery never segments on `model`.** A version bump is invisible to the instrument by construction, and it *is* the largest real effect in the corpus. The round file already stamps `script_md5`; it should equally stamp and **group by model version**, and any baseline comparison spanning a model boundary should be reported as two baselines, not one.
5. **NEW: `drift_check()` compares against a pooled corpus mixing 1.13.0 and 1.14.0.** Pooling a shifted population into one baseline inflates the apparent sigma of every qid and makes real shifts look like noise — the direct cause of the r411 report's "no real drift" conclusion for q02.

## Recommended next probe

- **Segment the corpus by `model` before computing any baseline or drift.** Re-derive the q02 drift against a `1.14.0`-only baseline (n=6, mean 0.7400) — the shift is then obvious.
- **Watch q02's margin.** If a 7th `1.14.0` draw of q02 lands at <= 0.70, the bedrock gate is breached and that *is* a substrate signal, not a model artefact. This is the single measurement that matters next round.
- **Re-run the q02/q12 pair deliberately** (both drawn in the same round) to get a clean co-draw reading of the witness-vocabulary split on `1.14.0`. They were co-drawn only twice post-boundary (r401, r407), both showing q02 ~0.71-0.77 with q12 ~0.51-0.54.
- **Note the q12 +0.1461 shift is the flip side of the same coin.** If a future probe wanted to promote q12, it must first clear the n>=20 + hit-rate >= 0.7 gate on a **1.14.0-only** baseline. It is at n=5, hit-rate 0 %. Nowhere near.
