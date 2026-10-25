# JEV Continuous Probe — Round r428

**Timestamp:** 2026-10-25T01:02:28Z
**Instrument:** `jev_continuous_probe.py` md5 `3a255fa4642ec4a83173ab04d773d485` (unchanged since r397)
**Model:** `jev-1.14.0` (resolved from `history.jsonl`) — **no model switch** vs r427
**Doctrinal state:** `framework, core_doctrine, architecture, fleet, spec_notebook, operational_doctrine` — byte-identical to r427
**Run:** 1 round OK, 0 fails, exit 0 (no timeout kill needed), 0.17 s/round
**Corpus:** 2,151 verdicts / 22 qids / 432 rounds (history.jsonl, dedup key `(qid, p, round)`)

---

## Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.3760** |
| **Bedrock hits (p ≥ 0.70)** | **1 / 5** — `q02` 0.72 |
| Below gate (this round) | `q17` 0.69, `q14` 0.22, `q13` 0.16, `q09` 0.09 |
| **Drift > 0.05** | **NONE — 0 of 5 drawn qids exceed 0.05** (model-segmented baseline) |
| Cathedral all-time | 661 / 664 = **99.55 %** (6 of 7 bedrock qids at 100 %) |
| Speculative ever ≥ 0.70 | **0 / 1,301** — no leak (review qid q17 excluded) |

**Verdict: ORDINARY.** 1-of-5 is the second-most-likely draw (32.2 %); a low hit count is a
property of the class mix, not of the canon. No qid moved beyond its own baseline. Nothing to escalate.

---

## The five verdicts

| qid | kind | p | 1.14.0 baseline μ | dev | z | verdict |
|---|---|---|---|---|---|---|
| `q02` | bedrock | **0.72** | 0.7283 (n=12) | −0.0083 | −0.28 | on baseline — a bedrock hit |
| `q17` | review | 0.69 | 0.7114 (n=7) | −0.0214 | −1.06 | on its 0.68–0.75 plateau |
| `q14` | adversarial | 0.22 | 0.2238 (n=8) | −0.0038 | −0.22 | on baseline |
| `q13` | speculative | 0.16 | 0.1600 (n=8) | +0.0000 | +0.00 | exactly at baseline |
| `q09` | speculative | 0.09 | 0.1033 (n=3) | −0.0133 | −1.41 | on baseline |

**|dev| ordered first, σ second** — the σ≈0 trap did not fire this round (smallest σ in play is
q13's 0.0050, and its dev was exactly 0.0000). The largest z is q13's class-mate q09 at +1.80 on
a |dev| of 0.0126 — a large z on a tiny movement, exactly the pattern the |dev|-first rule exists
to catch.

---

## 🔴 The pooled baseline manufactures a false q02 flag — model-segment the baseline

If q02 is scored against its **pooled** history (n=89, μ=0.8117) today's 0.72 reads
**dev = −0.0917, z = −2.45, 94.4th percentile** — a textbook drift flag, and one that would
have been reported as canon degradation.

It is an artifact. `q02` was re-baselined by the 1.13.0 → 1.14.0 model switch (r396):

| segment | n | mean | sd | min | max |
|---|---|---|---|---|---|
| `jev-1.13.0` | 77 | 0.8247 | 0.0148 | 0.79 | 0.86 |
| `jev-1.14.0` | 12 | 0.7277 | 0.0291 | 0.68 | 0.77 |

Against its **own** segment, today's 0.72 sits at dev −0.0083, 8.3rd percentile of its own
deviation distribution — dead on baseline. **The 1.13.0→1.14.0 switch moved q02 by −0.097; the
pooled baseline keeps that model artifact permanently fused into the 1.14.0 signal.**

**Rule (extended): every drift baseline MUST be segmented by the resolved model.** The script's
own `drift_check()` does not segment, does not filter to qids drawn this round, and compares to a
5-sample local median. It reported `drift_events=1` for r428 — on `q11`, which **was not drawn**
this round. That is **the 15th consecutive reproduction** of the stale-event defect. The script's
`drift_events` is never a health verdict.

## 🔴 Re-measurement: q02 holds, control confirms the call was healthy

Per the r427 rule (a new extreme must be re-measured; a repeat can be judged from the archive —
and q02's 0.72 *does* repeat an existing value), q02 was re-measured **6× on the identical
doctrinal state, same call path** (`call_jev(DOCTRINAL_STATE, …)`), with `q04` as a control on
the **same call**:

| qid | fresh draws | mean | min | max |
|---|---|---|---|---|
| `q02` | 0.71, 0.73, 0.77, 0.74, 0.76, 0.76 | **0.7450** | 0.71 | 0.77 |
| `q04` *(control)* | 0.87, 0.88, 0.88, 0.87, 0.89, 0.89 | **0.8800** | 0.87 | 0.89 |

q02 never fell below 0.71 — **today's 0.72 is not the low of the q02 distribution**, and the
control's 0.87–0.89 band licenses the claim that the q02 spread reflects q02 and not a sick call.
No confirmed drift.

---

## History table (regenerated from the archives, not transcribed)

| round | mean_p | hits | bedrock qids | model |
|---|---|---|---|---|
| r416 | 0.2400 | 0/5 | — | 1.14.0 |
| r417 | 0.4180 | 2/5 | q08, q02 | 1.14.0 |
| r418 | 0.1480 | 0/5 | — | 1.14.0 |
| r419 | 0.5380 | 3/5 | q01, q05, q04 | 1.14.0 |
| r420 | 0.3580 | 1/5 | q07 | 1.14.0 |
| r421 | 0.5540 | 3/5 | q04, q07, q02 | 1.14.0 |
| r422 | 0.5060 | 2/5 | q08, q01 | 1.14.0 |
| r423 | 0.5260 | 2/5 | q08, q05 | 1.14.0 |
| r424 | 0.3760 | 2/5 | q01, q17 | 1.14.0 |
| r425 | 0.3560 | 1/5 | q05 | 1.14.0 |
| r426 | 0.4040 | 2/5 | q04, q07 | 1.14.0 |
| r427 | 0.4200 | 2/5 | q04, q01 | 1.14.0 |
| **r428** | **0.3760** | **1/5** | **q02** | **1.14.0** |

*(Every value in this table is computed by looping `history.jsonl` in the same script that
computes the drift — no hand-typed numbers.)*

## Class-mix Monte Carlo (200,000 draws, 5 qids uniform from all 22)

- E[mean_p] = 0.3941, σ = 0.1375
- **P(mean_p ≤ 0.3760) = 0.4160**, z = **−0.13**
- P(k bedrock): 0 → 8.78 %, **1 → 32.20 %**, **2 → 37.91 %** (modal), 3 → 17.77 %, 4 → 3.16 %, 5 → 0.18 %
- last-20 prior rounds (excl. today): μ = 0.4082, σ = 0.1016, z = −0.32

**1-of-5 is ORDINARY** — 32.2 % of draws land there, and the round's mean_p is 41.6 % likely or
lower under the class mix. No signal.

## Cathedral (per-qid bedrock hit rate — the only metric that reads as canon health)

| qid | all-time | 1.14.0 segment | mean | min | max |
|---|---|---|---|---|---|
| q01 | 105/105 = **100 %** | 9/9 | 0.8737 | 0.84 | 0.90 |
| q02 | 87/90 = 96.7 % | 10/13 | 0.8107 | 0.68 | 0.86 |
| q03 | 98/98 = **100 %** | 7/7 | 0.8857 | 0.86 | 0.91 |
| q04 | 101/101 = **100 %** | 9/9 | 0.8882 | 0.87 | 0.91 |
| q05 | 96/96 = **100 %** | 8/8 | 0.8483 | 0.78 | 0.87 |
| q07 | 88/88 = **100 %** | 8/8 | 0.7555 | 0.71 | 0.79 |
| q08 | 86/86 = **100 %** | 6/6 | 0.8992 | 0.87 | 0.91 |

**6 of 7 bedrock qids at 100 %.** `q02` remains the sole imperfect one (87/90 = 96.7 %) — a
hair-under-the-gate pattern (0.68 / 0.69 / 0.71 misses), never a collapse. Unchanged watch item.

**No speculative or adversarial qid has EVER reached 0.70** (0 / 1,301 observations). The one
non-bedrock qid that has crossed is `q17`, tagged *review* not bedrock — it holds a 0.68–0.75
plateau (66 of its 90 observations ≥ 0.70) against which today's 0.69 is unremarkable, and it is
judged against its own baseline, never a global gate. Adversarials remain dead low (q14 max
0.25, q15 max 0.03, q19 max 0.12).

---

## Method notes carried forward

1. **Model-segment every baseline.** The pooled baseline inflates q02's dev by 11× (−0.092 vs
   −0.008) and would have reported a drift that does not exist.
2. **The script's `drift_events` is not a verdict** — 15th consecutive stale-event repro (q11,
   not drawn this round). Recompute per-qid, per-drawn-qid, against the segmented baseline.
3. **|dev| first, σ second.** Largest z today was +1.80 on a |dev| of 0.0126.
4. **Dedup key must be `(qid, p, round)`** — round files and `history.jsonl` carry different `ts`
   for the same verdict, so a `(qid, p, ts)` key double-counts and *shrinks* the observed dev.
5. **Round count discipline:** passed the explicit positional `1`; exactly 1 round in 0.3 s,
   stopped on count, not on the 55 s clock. Counter derived from `max(files=427, history=427)`.
6. **`/workspace` was empty on arrival (19th consecutive)** — the corpus was rebuilt from
   `SuperInstance/jev-quilt`; `/workspace/research` is a symlink into the `/tmp` overlay because
   the NAS is at 100 % (0 bytes available). Durable copy = git.

## Files

- Round file: `research/jev_sessions/continuous_r428.json`
- Prior report archived (not deleted): `research/jev_hourly_report_r427.md`
- Current report: `research/jev_hourly_report.md`
