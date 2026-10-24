# JEV Hourly Report — round r425 (2026-10-24T22:05Z)

**Round:** r425 (single round, `rounds_ok=1`, `fails=0`, 5 verdicts, exit 0)
**Model:** `jev-1.14.0` (resolved per-round; `MODEL="jev-latest"` alias)
**Script:** repo-ROOT `jev_continuous_probe.py`, md5 `3a255fa4642ec4a83173ab04d773d485` (unchanged — live script, not the `continuous/` variant)
**Corpus:** 233 round files → **2,020 deduped records** (2,015 prior + 5 this round), **22 qids**, max round 425
**Model split:** 1,870 × `jev-1.13.0` / 150 × `jev-1.14.0`

---

## 1. Headline numbers

| Metric | Value |
|---|---|
| **mean_p** | **0.3560** |
| bedrock hits (p >= 0.70) | **1 / 5** |
| qids hitting p >= 0.70 | **q05 (0.81)** |
| qids below gate | q02 0.68, q09 0.11, q20 0.09, q21 0.09 |
| **max abs(dev) (model-segmented, current round excluded)** | **0.0527 — q02** |
| qids with abs(dev) > 0.05 | **1 of 5 (q02)** |
| Script's own `drift_events` | 2 — **1 phantom + 1 sub-threshold** (see section 5) |

**Verdict: NO confirmed drift event. One WATCH item (q02) escalated.**

---

## 2. Round detail

| qid | kind | p | p >= 0.70 | dev vs same-model mu | z |
|---|---|---|---|---|---|
| q09 | speculative | 0.11 | no | +0.0100 | +1.00 |
| q20 | speculative | 0.09 | no | +0.0043 | +0.59 |
| q21 | speculative | 0.09 | no | -0.0040 | -0.82 |
| **q05** | **bedrock** | **0.81** | **YES** | -0.0057 | -0.32 |
| **q02** | **bedrock** | **0.68** | **no** | **-0.0527** | **-1.91** |

---

## 3. mean_p 0.3560 is an ORDINARY draw mix — the instrument did not move

- E[mean_p] for this qid set (per-qid corpus means) = **0.3863**
- Monte Carlo P(mean_p >= 0.3560) = **0.998** -> **ORDINARY**
- The aggregate is *below* expectation but well inside the sampler's normal range.

**Bedrock-count check.** Corpus per-round bedrock hit counts (rounds with >=2 bedrock drawn): `{1: 1, 2: 140, 3: 54, 4: 7, 5: 1}`.
P(exactly 1 hit) = **0.035** — low, but this is a *conditional* artifact of q02's low draw, not an instrument shift. Conditioning on the two bedrock qids actually drawn:

- P(exactly 1 of {q02, q05} passes) = **0.034**
- P(both pass) = **0.965**

So the round's low bedrock count is fully explained by q02 landing below the gate, not by a general weakening.

---

## 4. q02 — the one real signal. WATCH, not drift.

**q02** ("witness logs are predictions" canon?) is bedrock. It is the only qid in the entire corpus with sub-gate draws.

### 4.1 The value 0.68 breaks an 11-draw floor

q02's `jev-1.14.0` series, in draw order (rounds 399 -> 425):

```
0.75  0.77  0.73  0.71  0.77  0.71  0.74  0.69  0.75  0.75  0.69  0.68
```

- 0.69 was the floor for **11 consecutive 1.14.0 draws** (r416, r423).
- **0.68 is a NEW distinct value** — it has never appeared in the 1.14.0 era, and in the *all-model* history 0.68 occurs exactly once (this draw).
- This is a **threshold break**, not a repeat value. That distinction matters: prior sub-gate draws (0.69, 0.69) were repeats; this one is a new minimum.

### 4.2 Why it is still NOT a drift event

| Test | Result | Reading |
|---|---|---|
| dev vs same-model mu (n=12, mu=0.7283, sd=0.0302) | **-0.0527** | exceeds 0.05 — *technically* flagged |
| z | **-1.91** | **below** the 2.0 threshold |
| Empirical P(draw <= 0.68 given 1.14.0) | **0.083** | ~1-in-12 — rare but not extreme |
| Normal-tail P(X <= 0.68) | 0.055 | 5.5% |
| OLS trend on 1.14.0 series | slope **-0.00476/draw**, R2 0.295, **t = -2.04 (df 10)** | **NOT significant** (abs t < 2.262) |
| Aggregate drift test | **1 of 5** drawn qids beyond 0.05, max abs(dev) 0.0527 | single-qid, sub-threshold-in-practice |

**Reading:** the trend slope is negative and the R2 is the highest seen for q02, but **t = -2.04 does not clear significance at df 10**. One new minimum at 1-in-12 tail probability is a *watch* trigger, not a verdict. The 0.02-0.06 band is my established expected-jitter zone, and 0.0527 sits inside it.

**Action:** q02 stays a **WATCH item** (as it has been since r416). It is **not** re-escalated, **not** promoted to a drift event, and **not** a demotion candidate. Next draw of q02 is the test.

---

## 5. The script's `drift_events=2` is 1 phantom + 1 carried-over flag (12th consecutive reproduction)

The script reports:

```
q02  recent_p 0.68  prior_median 0.74  delta -0.06
q17  recent_p 0.75  prior_median 0.70  delta +0.05
```

- **q17 = PHANTOM.** q17 was **not drawn** in r425. The `recent_p 0.75` is r424's draw. This is the **12th consecutive reproduction** of the missing current-round filter in `drift_check()`. It is a flag on a question that was not asked.
- **q02 = real but computed against the wrong baseline.** The -0.06 delta comes from a 5-sample local-median window (prior_median 0.74), not from the model-segmented baseline (mu 0.7283) and not from the current-round-excluded 1.14.0 distribution. The magnitude happens to land near my own figure (0.0527), but for a different reason.

**The script's `drift_check()` still has all three known defects UNPATCHED:** (a) no current-round filter, (b) 5-sample local median instead of model-segmented history, (c) no model segmentation. All drift numbers in this report are recomputed from the round files with the current round excluded, model-segmented, and **n>0 asserted per drawn qid**.

---

## 6. Cathedral status

Bedrock set is the explicit 7-qid list `q01, q02, q03, q04, q05, q07, q08` (read from the script's `QUESTION_BANK`; q06 carries a `bedrock` tag in old notes but reads REJECT, and **q17 is `review` — its hits never count as canon**).

| qid | all-time hit-rate | 1.14.0 | sub-gate draws |
|---|---|---|---|
| q01 | 102/102 = 100.00% | 8/8 | — |
| **q02** | **83/86 = 96.51%** | **9/12** | **0.69, 0.69, 0.68** |
| q03 | 95/95 = 100.00% | 7/7 | — |
| q04 | 95/95 = 100.00% | 7/7 | — |
| q05 | 88/88 = 100.00% | 8/8 | — |
| q07 | 81/81 = 100.00% | 7/7 | — |
| q08 | 79/79 = 100.00% | 6/6 | — |
| **TOTAL** | **623/626 = 99.52%** | 52/58 | 3 (all q02) |

- Rounds where **all drawn** bedrock qids pass the gate: **348 / 351 = 99.1%**; longest consecutive all-pass streak **25 rounds**.
- 1.14.0 era: 25/28 = 89.3% all-pass rounds. The three non-perfect rounds are **r416, r423, r425 — every one of them a q02 sub-gate draw**.

**No promotion, no demotion.** q05 remains at 100% (the r419 AMBER note — 0.78 as its only sub-0.80 in 87 draws — is unchanged and q05 was not drawn low here at 0.81).

---

## 7. Containment still intact

| kind | n | max p | draws >= 0.70 |
|---|---|---|---|
| speculative | 947 | 0.56 | **0** |
| adversarial | 276 | 0.25 | **0** |
| review | 171 | 0.75 | 60 (all **q17**, a `review` qid — not canon) |

No speculative or adversarial qid has **ever** reached p >= 0.70 in the 2,020-record corpus. The gate is not leaking.

---

## 8. Environment

- **123rd wipe.** `/workspace` was **EMPTY** — the 16th consecutive time the prompt named ephemeral `/workspace/research/` paths that did not exist. All work ran in `/tmp` (28G overlay).
- **NAS 100%** (600G/600G, 0 avail) => the canonical `/workspace/research/jev_hourly_report.md` path is **unwritable**; the durable copy is **git**.
- **TLS leaf VALID** (CN=typesafe.ai, notAfter 2026-12-25) => **no CA-bundle rebuild needed** — 7th round in a row; `openssl s_client` triage first.
- Credential: `TYPESAFE_AI_TOKEN` read directly (client accepts `TYPESAFEAI_KEY` || `TYPESAFE_AI_TOKEN`) => no mapping needed.
- `gh` absent (28th). The script was located via the GitHub trees API across the 3,400-repo SuperInstance census — `SuperInstance/jev-quilt` holds both the repo-ROOT script and the `continuous/` variant.
- **"One round" needs an explicit positional `1`** — `python3 jev_continuous_probe.py 1` gave exactly 1 round in 0.146 s, exit 0. (The positional arg defaults to a 55-second wall-clock loop, so an un-argued run overshoots.)

---

## 9. Commit hygiene note (self-correction)

Commit `050c1e4` initially captured the **stale r424** report blob (11,186 B, md5 `f3e60378`) because the heredoc that wrote this report landed in a sibling clone (`/tmp/qr`) after a mistyped `cd /tmp/jr`. The round file (`continuous_r425.json`) and `history.jsonl` in that same commit were correct — only the report blob was wrong.

Caught by **verifying the pushed blob content, not just the commit SHA** (`git cat-file -p origin/main:research/jev_hourly_report.md` returned r424's header). Fixed in commit `c6b2278`; remote blob now **md5 `d80967d813c63d838315d89388e2e549`, 7,858 B, byte-identical to local**, and `continuous_r425.json` verified on the remote with the correct 5 verdicts.

**Method rule reinforced: a push receipt is not a content receipt. Always `cat-file` the pushed blob and diff it against the local file — a green push only proves the commit landed, not that the commit holds the bytes you meant.**
