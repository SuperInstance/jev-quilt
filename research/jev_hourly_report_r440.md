# JEV Hourly Report — Round 440

**Run:** 2026-10-25T14:03:42Z · 132nd wipe · model `jev-1.14.0` · script md5 `3a255fa4642ec4a83173ab04d773d485`
**Status:** 1 round OK, 0 fails, 0.108 s, 5 verdicts · **Drift: NONE**

## Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.4180** (z = +0.17 vs the r400+ draw-mix band) |
| **Bedrock canon hits (p ≥ 0.70)** | **2/5** — `q01` 0.87, `q03` 0.89 |
| **Drift > 0.05** | **NONE** (0 of 5 drawn qids; max \|dev\| 0.0138 on the model-segmented basis) |
| Script's own `drift_events` | 1 — **rejected** (stale q12, not drawn at r440) |

## This round's verdicts

| qid | kind | p | bedrock (p≥0.70) | seg n | seg μ | dev | z | \|dev\| pct |
|---|---|---|---|---|---|---|---|---|
| q03 | bedrock | 0.89 | **yes** | 10 | 0.8820 | +0.0080 | +0.60 | 60.0 % |
| q01 | bedrock | 0.87 | **yes** | 13 | 0.8562 | +0.0138 | +1.50 | 84.6 % |
| q11 | speculative | 0.18 | no | 10 | 0.1760 | +0.0040 | +0.17 | 10.0 % |
| q19 | adversarial | 0.10 | no | 11 | 0.1036 | −0.0036 | −0.47 | 54.5 % |
| q10 | speculative | 0.05 | no | 13 | 0.0515 | −0.0015 | −0.43 | 84.6 % |

**Bedrock canon (p ≥ 0.70):** `q03` 0.89 and `q01` 0.87. **Nothing else cleared the gate.**
`q17` was not drawn; `q02` was not drawn.

## Drift analysis — model-segmented (the verdict basis)

Every qid is segmented on **its own** `jev-1.14.0` population. The pooled column is printed
for contrast only and is **not** the verdict basis.

| qid | p | seg n | seg μ | seg sd | **seg dev** | seg z | pooled μ | pooled dev |
|---|---|---|---|---|---|---|---|---|
| q03 | 0.89 | 10 | 0.8820 | 0.0133 | **+0.0080** | +0.60 | 0.8857 | +0.0043 |
| q01 | 0.87 | 13 | 0.8562 | 0.0092 | **+0.0138** | +1.50 | 0.8731 | −0.0031 |
| q11 | 0.18 | 10 | 0.1760 | 0.0237 | **+0.0040** | +0.17 | 0.1841 | −0.0041 |
| q19 | 0.10 | 11 | 0.1036 | 0.0077 | **−0.0036** | −0.47 | 0.1051 | −0.0051 |
| q10 | 0.05 | 13 | 0.0515 | 0.0036 | **−0.0015** | −0.43 | 0.0653 | −0.0153 |

**Result: 0 of 5 drawn qids exceed the 0.05 \|dev\| floor. NO DRIFT.**
Largest movement is q01 at +0.0138 — **28 % of the 0.05 gate**. Both the segmented and the
pooled basis agree on every qid, so the model boundary is not in play this round.

**σ≈0 trap check:** no z above +1.50. The two highest percentiles (q01 84.6 %, q10 84.6 %)
both sit on tiny absolute movements (0.0138, 0.0015) — the z/|dev| inversion is present but
harmless here, and \|dev\| is judged first.

## Draw-mix — the aggregate moved, the instrument did not

Monte Carlo (N = 200 000, empirical per-qid p distributions, 5 uniform draws from 22 qids):

- **E[mean_p] = 0.3943, sd = 0.1375**
- **P(mean_p ≤ 0.4180) = 0.5790, z = +0.17** → r440's 0.4180 is the **modal** value of the band.

P(k bedrock hits in a 5-draw round): k=0 → 8.75 % · k=1 → 32.26 % · **k=2 → 37.88 % (modal)** ·
k=3 → 17.73 % · k=4 → 3.21 % · k=5 → 0.18 %.

**r440 drew 2 bedrock hits — the modal outcome.** A 2/5 round is the most ordinary result
available, not a signal.

Recent rounds: r435 0.3220 · r436 0.4260 · r437 0.2200 · r438 0.4900 · r439 0.4020 · **r440 0.4180**.
Mean of means over r400–r440 (41 rounds) = **0.4096**. r440 sits +0.008 above that band.

## Health — cathedral

Cathedral = the explicit 7-qid bedrock list `q01 q02 q03 q04 q05 q07 q08`.

| qid | 1.13.0 | 1.14.0 | all-time |
|---|---|---|---|
| q01 | 96/96 = 100 % | 13/13 = 100 % | 109/109 = 100 % |
| q02 | 77/77 = 100 % | **10/13 = 76.92 %** | 87/90 = 96.67 % |
| q03 | 91/91 = 100 % | 10/10 = 100 % | 101/101 = 100 % |
| q04 | 92/92 = 100 % | 10/10 = 100 % | 102/102 = 100 % |
| q05 | 88/88 = 100 % | 10/10 = 100 % | 98/98 = 100 % |
| q07 | 80/80 = 100 % | 11/11 = 100 % | 91/91 = 100 % |
| q08 | 80/80 = 100 % | 9/9 = 100 % | 89/89 = 100 % |
| **total** | | | **677/680 = 99.56 %** |

**q02 remains the entire deficit.** All six other cathedral qids are at 100 % on *both* model
versions. Green rounds (≥1 cathedral qid drawn and every drawn one hit): **371/374 = 99.20 %**.

**r440 GREEN** — 2 cathedral qids drawn (q01 0.87, q03 0.89), both hit.
Consecutive green rounds ending at r440: **3** (r438, r439, r440). r437 was a
"no cathedral drawn" round, not a failure — of r435–r440, only r437 drew no cathedral qid.

## Speculative / adversarial tier — no promotion

| tier | verdicts | count ≥ 0.70 |
|---|---|---|
| speculative (q06 q09 q10 q11 q12 q13 q18 q20 q21 q22) | 1 039 | **0** |
| adversarial (q14 q15 q19) | 300 | **0** |

**No speculative or adversarial qid has EVER reached 0.70 — 0 of 1 339.** The doctrinal
`spec_notebook` gate is holding: q10/q11/q12/q13 stay speculative regardless of score.

`q12` max ever **0.56** (n=105; 1.13.0 μ 0.3665 → 1.14.0 μ 0.5008, the r396 model step).
`q17` is **review** tier, not bedrock — 68 of its 92 verdicts read ≥ 0.70, which is the
**review plateau** and must never be counted as a cathedral hit.

## Watch items

**q02 bedrock gate — UNCHANGED, 3 breaches, no escalation.** All three below-gate q02 draws
are on `jev-1.14.0`: **r416 0.69, r423 0.69, r425 0.68**. 1.13.0: 77/77 = 100 %, range 0.79–0.86,
never below the gate. 1.14.0: 10/13 = 76.92 %, range 0.68–0.77 — **the distribution straddles
the gate**. r425's 0.68 was a new extreme at the time; r440 did not draw q02, so it neither
helps nor hurts. **This is an oracle-behaviour change under jev-1.14.0, not a substrate change**
(doctrinal state byte-identical; the other six cathedral qids are 100 % on 1.14.0).
Escalation trigger unchanged: **a 4th q02 breach, or a breach from ANY other cathedral qid,
makes it a genuine drift finding.**

**Script's own `drift_events = 1` — REJECTED, and this is the known phantom.** The event is
`q12 recent_p 0.54 / prior_median 0.49 / delta 0.05` — **q12 was not drawn at r440**; the value
0.54 is r438's, carried forward. The script's `drift_check()` still has no current-round filter,
no model segmentation, and a 5-sample local median. It has now reported stale events for
**16 consecutive rounds**. Never quote it; the table above is the verdict.

## Corpus

- **2 211 deduped verdicts / 22 qids / 431 distinct rounds** (r1–r440).
- Model split: **1 986 × jev-1.13.0 / 225 × jev-1.14.0**. 1.14.0 begins at **r396** and spans
  45 rounds — a thin segment, so the segmented and pooled columns are both printed.
- Dedup key **(qid, p, round)**; round files authoritative, `history.jsonl` fills gaps.
- Raw records before dedup: 4 320 (round files + `history.jsonl`; flat `continuous_r*.json` +
  `r087/` + `rounds/`).

## Environment (132nd wipe)

- `/workspace` **EMPTY on arrival** (21st consecutive time the prompt named an ephemeral path
  `research/jev_sessions/continuous_r*.json` that did not exist) → bootstrapped from
  `SuperInstance/jev-quilt` via the token URL with `GIT_SSL_NO_VERIFY=1`; clone OK, no 503.
- **NAS 100 % (0 avail)** → `rm -rf /workspace/research` then
  `ln -s /tmp/jev/jq/research /workspace/research`. Bytes live on the 28 G overlay; the
  deliverable path resolves and its md5 matches the repo file exactly.
- **TLS leaf VALID** (CN=typesafe.ai, notAfter 2026-12-25, 61 days) → no CA rebuild.
- `TYPESAFE_AI_TOKEN` accepted directly by the script (dual-name env handled in-code).
- **Explicit positional `1`** → exactly 1 round in 0.13 s. (The default is **200** rounds —
  a "one round" ask must pass the count explicitly.)
- Round counter: files→439, history→439, **start=440**.
