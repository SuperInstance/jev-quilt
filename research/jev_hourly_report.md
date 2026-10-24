# JEV Continuous Probe — Hourly Report (r424)

**Run:** 2026-10-24T21:04:15Z · **1 round** (explicit positional `1`) · 0 fails · 5 verdicts  
**Instrument:** root `jev_continuous_probe.py` md5 `3a255fa4642ec4a83173ab04d773d485` (LIVE — matches the stamp in every round file since r397)  
**Model served:** `jev-1.14.0` (alias `jev-latest`)  
**Corpus:** 2,015 deduped records / 22 qids / 403 rounds · model split 1,870 × `1.13.0` + 145 × `1.14.0`  
**Baselines:** model-segmented (per-`model`, current round excluded). Pooled baselines are shown only to demonstrate the cross-model artifact.

---

## 1. Headline numbers

| metric | value |
|---|---|
| **mean_p** | **0.3760** |
| **bedrock hits (p ≥ 0.70)** | **2 / 5** |
| bedrock qids drawn | `q01` 0.86, `q17` 0.75 |
| below-gate qids | `q06` 0.13, `q21` 0.09, `q10` 0.05 |
| **drift > 0.05** | **NONE** (max same-model \|dev\| = 0.0450, `q17`) |
| script `drift_events` | 2 → **1 phantom + 1 sub-threshold candidate** |
| cathedral (7-qid bedrock list) | 622/624 = **99.68%** all-time · 51/53 = 96.23% on 1.14.0 |
| green rounds | 348/403 all-time · 25/29 on 1.14.0 |

### Verdict

**A quiet round. The instrument did not move.** `mean_p` 0.3760 is *below* the draw-mix expectation (E = 0.4004, MC P(mean_p ≥ 0.3760) = **0.594**), 2 bedrock in 5 is the single most likely outcome (P = **0.389**), and no qid moved more than 0.05 against its own model's history. The script's `drift_events=2` is **not** a drift finding — one flag is a qid that was never drawn this round, and the other is a real-but-sub-threshold candidate.

---

## 2. Verdicts in this round

| qid | kind | p | ≥0.70 | same-model mu | sd | n | dev | z | pctile of \|dev\| |
|---|---|---|---|---|---|---|---|---|---|---|
| `q01` | bedrock | **0.86** | **YES** | 0.8557 | 0.0090 | 7 | +0.0043 | +0.47 | 43% |
| `q17` | review | **0.75** | **YES** | 0.7050 | 0.0138 | 6 | +0.0450 | +3.25 | 100% |
| `q06` | speculative | **0.13** | no | 0.1413 | 0.0060 | 8 | -0.0113 | -1.88 | 100% |
| `q21` | speculative | **0.09** | no | 0.0950 | 0.0050 | 4 | -0.0050 | -1.00 | 100% |
| `q10` | speculative | **0.05** | no | 0.0517 | 0.0037 | 6 | -0.0017 | -0.45 | 83% |

---

## 3. Drift analysis — the two script flags, resolved

The script's `drift_check()` (lines 317–335) has three known defects, all still **unpatched**: (1) no current-round filter, (2) 5-sample local median instead of the full-history mean, (3) no model-version segmentation. Reproducing it verbatim over all 403 rounds gives exactly the 2 events it reported:

```
q02  recent_p 0.69  prior_median 0.74  delta -0.05
q17  recent_p 0.75  prior_median 0.70  delta +0.05
```

**`q02` — PHANTOM (11th reproduction of this defect).** `q02` was **not drawn in r424** (drawn: q01, q06, q10, q17, q21). The flag is an artifact of the local-median window. And it is a *stale* one on top of that: the `recent_p 0.69` it compares against is r423's draw, whose true same-model deviation is **-0.0427, z = -1.54** (r423's own analysis). Under the 0.05 floor. **Not drift.**

**`q17` — REAL CANDIDATE, BUT SUB-THRESHOLD. NO DRIFT.** `q17` *was* drawn, so this flag deserves a real look:

- 1.14.0 baseline: mu = 0.7114, sd = 0.0203, n = 7 → **dev = +0.0386, z = +1.90**, i.e. **under the 0.05 floor**.
- The script's own +0.05 came from comparing against a *local median* (0.70) instead of the model-segmented mean (0.7114).
- 0.75 **is** the new all-time max for q17 on 1.14.0 (prior max 0.72 in the 1.14.0 series), and it sits at the 100th percentile of q17's own |dev| distribution. That is a *candidate*, not a verdict — with n = 7, a single new max is exactly what a 0.05-floor event looks like when the floor is barely breached.
- **No trend:** OLS on the 1.14.0 series → slope **+0.00286/draw, R² = 0.079, t = 0.63 (df 5)** — not remotely significant. The 1.13.0 series (n = 74) is flat and centred at 0.7027.
- Bootstrap 95% CI on the 1.14.0 mean: **[0.6971, 0.7271]** — 0.75 sits above it, but the CI is built on 7 samples, which is not a basis for promotion.
- P(draw ≥ 0.75 | 1.14.0 history) = 0.143 — a once-in-seven draw, well within the ordinary range.

**=> `q17` is a WATCH item, not drift. Its 0.75 is the first sign of a possible upward move in the 1.14.0 era, and the second consecutive reason to keep watching it — but by every gate we use (\|dev\| vs 0.05, z, own-distribution percentile, OLS trend), it is not a drift event.** `q17` is also `review`-tier, **not** bedrock, so a q17 hit never counts as canon.

### Pooled baselines would have manufactured a false flag

| qid | segmented dev (correct) | pooled dev (cross-model artifact) |
|---|---|---|
| `q01` | +0.0043 (z +0.47) | -0.0142 (z -1.43) |
| `q17` | +0.0450 (z +3.25) | +0.0471 (z +3.29) |
| `q06` | -0.0113 (z -1.88) | +0.0272 (z +2.09) |
| `q21` | -0.0050 (z -1.00) | -0.0006 (z -0.16) |
| `q10` | -0.0017 (z -0.45) | -0.0161 (z -2.69) |

Pooling across the r396 `1.13.0 → 1.14.0` boundary inflates apparent sigma and manufactures supra-threshold z-scores out of sub-threshold model shifts (R-413's q14 case: pooled z = +4.07 vs segmented z = +1.46). No pooled value in this table crosses 0.05 either, but the discipline holds regardless.

---

## 4. `mean_p` 0.3760 = ordinary draw mix

| check | value |
|---|---|
| E[mean_p] over a random 5-question draw (per-qid 1.14.0 means) | 0.4004 |
| MC P(mean_p ≥ 0.3760) | **0.594** |
| MC P(exactly 2 bedrock-class draws) | **0.389** |
| bedrock-count distribution P(0/1/2/3/4/5) | 0.076 / 0.304 / **0.389** / 0.192 / 0.037 / 0.002 |

Today's 0.3760 is **below** the expectation and 2-bedrock is the **modal** outcome. The aggregate is unremarkable; the instrument is stable. (Last 12 rounds for context: 0.454, 0.280, 0.386, 0.240, 0.418, 0.148, 0.538, 0.358, 0.554, 0.506, 0.526, **0.376**.)

---

## 5. Bedrock canon — the 7-qid cathedral

The cathedral is built from the **explicit 7-qid bedrock list** read out of the question bank — `q01, q02, q03, q04, q05, q07, q08` — never from a `kind` tag (q06 carries a `bedrock` tag in older notes but reads REJECT; q17 is `review` and its hit today does **not** count as canon).

| scope | hits | rate |
|---|---|---|
| all-time | 622/624 | **99.68%** |
| `jev-1.14.0` era | 51/53 | 96.23% |
| green rounds (≥1 cathedral qid drawn, all hit) | 348/403 all-time · 25/29 on 1.14.0 | |

### Per-qid on 1.14.0

| qid | n | hit-rate | min | max | note |
|---|---|---|---|---|---|
| `q01` | 8 | 100.0% | 0.84 | 0.87 |  |
| `q02` | 11 | 81.8% | 0.69 | 0.77 | **FRAGILE** — 2 sub-0.70 draws (r416, r423), both exactly 0.69 |
| `q03` | 7 | 100.0% | 0.86 | 0.90 |  |
| `q04` | 7 | 100.0% | 0.87 | 0.90 |  |
| `q05` | 7 | 100.0% | 0.78 | 0.83 |  |
| `q07` | 7 | 100.0% | 0.75 | 0.79 |  |
| `q08` | 6 | 100.0% | 0.88 | 0.91 |  |

**`q02` watch item — STILL OPEN, NOT RE-ESCALATED.** R-412 set the trip condition: *a 7th 1.14.0 draw of q02 at ≤ 0.70 breaches the bedrock gate and that is a substrate signal, not a model artefact.* That fired at r416 (0.69) and again at r423 (0.69). **q02 was not drawn in r424**, so there is no new evidence either way. Its 1.14.0 series now stands at 11 draws, hit-rate **9/11 = 81.8%**, with exactly two sub-gate draws, both at 0.69 — a *repeat* value, not a new low. r416's own analysis established that 0.69 is not a novel reading and that there is no within-1.14.0 trend (OLS slope -0.00118/draw, R² 0.018, t = -0.41): q02 **oscillates around a shifted level, not sliding**. The r396 model step remains the mechanism. **No promotion, no demotion.**

**`q05` AMBER (opened r419) — STILL OPEN, NO NEW EVIDENCE.** q05's 1.14.0 series is 0.78, 0.80, 0.82, 0.82, 0.83, 0.83, 0.83 — 0.78 remains the only sub-0.80 reading in the 1.14.0 era and the only sub-0.80 in 87 draws overall. It was not re-drawn here. Not re-escalated.

**`q17` hit at 0.75 does not enter the cathedral** — q17 is `review`-tier. Counting it would be the exact error the method rules forbid.

---

## 6. No promotion, no demotion

- **No speculative or adversarial qid has EVER reached p ≥ 0.70 in the entire 2,015-record corpus.** The corpus max for any speculative qid is `q12` at 0.56 (and q12 was not drawn in r424).
- `q10` read **0.05** today (speculative, spec-notebook framed) — it stays suppressed, and its 15th resolution of the historical q10 state-leak (0.0300 leak resolved at R-221) remains intact.
- `q06` 0.13 and `q21` 0.09 — both speculative, both correctly below the gate.
- The r396 model boundary still splits q02 (bedrock, -0.085) and q12 (speculative, +0.146) in opposite directions; that is oracle behaviour inside the "witness" vocabulary, not a substrate change, and it is unchanged today.

---

## 7. Environment & method receipts

| item | status |
|---|---|
| `/workspace` | **EMPTY** — 15th consecutive time the task prompt named ephemeral `/workspace/research/` paths that did not exist. All work done in `/tmp/jevroot/` (overlay). |
| NAS | 600G/600G, **100%** → the canonical `/workspace/research/jev_hourly_report.md` path is unwritable (the `write` tool leaves a 0-byte stub and `cp` exits 1 `Disk quota exceeded`). Durable copy is **git**. |
| TLS leaf | **VALID** — `CN=typesafe.ai`, notAfter 2026-12-25, leaf delta +0.96d. **No CA-bundle rebuild needed** (3-second `openssl s_client` triage run first). |
| credential | `TYPESAFE_AI_TOKEN` read directly by the client (`TYPESAFEAI_KEY` || `TYPESAFE_AI_TOKEN`) — no `JEV_API_KEY` mapping needed. |
| "one round" | Launched with an **explicit positional `1`** → exactly 1 round in 0.101 s, exit 0, 0 fails. (The default `main(None)` runs to the 55 s ceiling ≈ 200 rounds.) |
| script identity | Root script md5 `3a255fa4…` == the md5 stamped in r424 and every round file since r397. The `continuous/` variant (md5 `95b552ea…`, flat 15-key state) was **not** run — its p-values are not comparable. |
| `q07` qid | Live qid is `q07_11_opcodes` in older notes; the round files use short form `q01`…`q22` throughout. The first corpus build mis-mapped short→full qids and produced n=0 baselines; corrected by reading the qids straight out of the round files. |
| corpus | 232 round files → 2,015 records, deduped on exact `(qid, p, ts)` (no collisions this round: raw == deduped). |
| push verification | `git ls-remote` + `git cat-file -p origin/main:<path>` (git protocol, no REST quota). |

---

## 8. What to watch next

1. **q17** — the 0.75 is a new 1.14.0-era max with a positive but insignificant OLS slope. If the next 1.14.0 draw of q17 lands ≥ 0.75 again, that is a *consecutive rung at the tail* (the third drift-discriminator question) and the plateau would be genuinely shifting. One high draw is a candidate, not a signal.
2. **q02** — watch item open, needs a draw. A third sub-0.70 (i.e. a 0.69 or lower) would move it from "oscillating around a shifted level" toward "sliding" and would be a genuine substrate signal.
3. **q05** — AMBER, still open, needs a draw.

*Generated by the JEV continuous probe, r424. All p-values are raw JEV `noul` scores. Baselines are model-segmented; the current round is excluded from every baseline.*
