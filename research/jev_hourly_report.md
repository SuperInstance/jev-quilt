# JEV Continuous Probe — Round 423 (2026-10-24T20:01:37Z)

**Instrument:** `jev_continuous_probe.py` (root, md5 `3a255fa4642ec4a83173ab04d773d485` — the live 6-section doctrinal state; the `continuous/` variant md5 `95b552ea…` is stale and was NOT used).
**Model served:** `jev-1.14.0` · **Round counter:** files→422, history→422 → r423 · **Command:** `python3 jev_continuous_probe.py 1` (explicit positional `1` — see "one round" note below)
**Result:** 1 round OK, 0 fails, 5 verdicts, elapsed 0.114 s.

---

## 1. Headline

| | |
|---|---|
| **mean_p** | **0.5260** (recomputed from verdicts; matches script summary) |
| **Bedrock hits (p >= 0.70)** | **2 / 5** — q08 0.88, q05 0.80 |
| **Drift > 0.05 (model-segmented)** | **NONE** — max abs dev among drawn qids = 0.0427 (q02), i.e. 85% of the floor |
| **Script's own `drift_events`** | 1 — **q02, delta -0.05 vs a 5-sample local median**. This is a **known-defective** signal, not a verdict (see section 4) |
| **Cathedral (7-qid explicit list)** | 621/623 all-time = 99.68% · **1.14.0-era 50/52 = 96.15%** |
| **Green rounds** | 347 of 402 distinct rounds (>=1 cathedral qid drawn and every drawn cathedral qid hit) |
| **Verdict** | **No drift. But q02's bedrock gate is breached for the second time — a WATCH-ITEM ESCALATION, not a promotion, not a demotion.** |

---

## 2. The round's five verdicts

| qid | kind | p | bedrock (p >= 0.70) |
|---|---|---|---|
| **q02** | bedrock | **0.69** | **BELOW GATE** |
| q05 | bedrock | 0.80 | YES |
| q08 | bedrock | 0.88 | YES |
| q06 | speculative | 0.15 | no |
| q19 | adversarial | 0.11 | no |

**Bedrock canon (p >= 0.70) hit by 2 of 5 drawn questions: q08 (0.88), q05 (0.80).**
q02 — a bedrock-tagged canon question — read **0.69**, i.e. **0.01 below the 0.70 gate**.

---

## 3. mean_p = 0.5260 is ORDINARY — pure draw mix

A 5-draw round's mean_p is dominated by *which* questions were sampled, not by substrate movement. Against the **1.14.0-era per-qid means** (the correct baseline for the model currently being served):

- E[mean_p] for a random 5-draw = **0.4002**
- Monte-Carlo (200,000 draws): **P(mean_p >= 0.526) = 0.194** -> **not unusual** (p ~ 0.19)
- P(exactly 2 bedrock in 5) = **0.387** (hypergeometric, K = 8/22 drawable bedrock) -> **2/5 is the modal outcome**
- last-20 round mean_p average = 0.4095; corpus grand mean_p = 0.3847 over 2,010 records
- E[bedrock hits per round] = 1.821

**The aggregate moved; the instrument did not.** Consistent with the R-222 finding that grand mean_p is draw-mix confounded.

---

## 4. Drift: NONE > 0.05 — and the script's `drift_events=1` is a known-defect artefact

The script's own summary reports `drift_events=1` -> `{'qid': 'q02', 'recent_p': 0.69, 'prior_median': 0.74, 'delta': -0.05}`. Recomputing properly against the **same-model (1.14.0) full-history baseline**:

| qid | today | mu (1.14.0) | sigma (1.14.0) | dev | z | abs dev >= 0.05 ? |
|---|---|---|---|---|---|---|
| q02 | 0.69 | 0.7327 | 0.0277 | **-0.0427** | -1.54 | **no** |
| q06 | 0.15 | 0.1413 | 0.0060 | +0.0087 | +1.46 | no |
| q19 | 0.11 | 0.1043 | 0.0049 | +0.0057 | +1.15 | no |
| q08 | 0.88 | 0.8917 | 0.0134 | -0.0117 | -0.87 | no |
| q05 | 0.80 | 0.8157 | 0.0176 | -0.0157 | -0.89 | no |

**Max abs dev = 0.0427 (q02) — below the 0.05 floor, and abs z < 2 on every drawn qid.** No drift.

Three independent reasons the script's flag is not a verdict, all of them previously catalogued defects in `drift_check()` (lines 317-335), **still unpatched**:

1. **5-sample local median instead of the full-history mean.** A rolling local median cannot detect a slow shift — and it also *inflates* apparent deltas when the local window happens to sit high.
2. **No model-version segmentation.** Pooling 1.13.0 and 1.14.0 inflates apparent sigma and manufactures supra-threshold z on sub-threshold shifts (R-413 measured a z = +4.07 on q14 that was entirely a pooling artefact). Segmented, q02's dev is -0.0427, z = -1.54.
3. **No current-round filter.** (Not triggered this round — q02 *was* drawn — but still unpatched; the phantom reproduced at r400, r402, r412, r413.)

**The sigma~0 trap also held:** the largest z today (q06, +1.46) sits on a dev of +0.0087. Judging abs dev against the 0.05 floor first, as always, is what keeps the eye on the right quantity.

---

## 5. THE REAL FINDING — q02's bedrock gate has now been breached TWICE

This is the R-412/R-413 watch item **firing as predicted**, and it is the substantive event of this round.

> R-412: *"q02's margin above the bedrock gate on 1.14.0 is **0.01**... If a 7th 1.14.0 draw of q02 lands at <= 0.70, the bedrock gate is breached and THAT is a substrate signal, not a model artefact."*

**q02's complete 1.14.0-era history (n = 11):**

| round | r399 | r401 | r406 | r407 | r411 | r412 | r414 | r416 | r417 | r421 | **r423** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| p | 0.75 | 0.77 | 0.73 | 0.71 | 0.77 | 0.71 | 0.74 | **0.69** | 0.75 | 0.75 | **0.69** |

- **Hit-rate on 1.14.0: 9/11 = 81.8%** (was 10/10 = 100% at R-413, and 6/6 at R-412)
- **1.13.0-era hit-rate: 74/74 = 100%** — q02 was *never* below 0.79 in its entire pre-boundary history
- Bootstrap 95% CI on the 1.14.0 mean: **[0.7164, 0.7491]** — the upper 0.75 end is where the distribution now lives
- Bootstrap 95% CI on (1.13.0 mean - 1.14.0 mean): **[0.0760, 0.1092]**, delta 0.0924 -> **excludes zero**

### Two important negative results (do not over-read this)

1. **0.69 is not a new value.** q02 hit **0.69 at r416 as well**. Today's draw *repeats* the previous low — it is the joint-minimum of the 1.14.0 sample, not a new extreme. The r416 breach was already recorded and already reported; this round **re-confirms** it rather than escalating the *level*.
2. **There is NO within-1.14.0 downward trend.** OLS on the 11 draws: slope **-0.00118 per draw, R2 = 0.018, t = -0.41 (df 9) — not significant.** First 6 draws mean 0.7383, last 6 mean 0.7233. The two 0.69s sit at r416 (6th) and r423 (11th) with no monotone descent. **q02 is oscillating around a shifted level, not sliding.**

### So what *is* the signal?

The signal is **not** a new drift; it is the **cumulative shape of the model step**. The 1.14.0 boundary (r396) moved q02 down by -0.0924 with a CI excluding zero, and the new distribution's **lower tail reaches 0.69, i.e. below the 0.70 bedrock gate.** With n = 11 and 2 breaches, the 1.14.0-era hit-rate has fallen to 9/11.

**Mechanism (per R-412): jev-1.14.0 re-allocated canonicity inside the "witness" vocabulary** — the bedrock doctrine ("witness logs are predictions") lost mass, the speculative "witness_note is an opcode" framing gained it. q02 and q12 are the two "witness"-vocabulary questions, and they split exactly on the model boundary (q02 -0.0847, q12 +0.1461 on the 1.13.0->1.14.0 step). q12 is still SPECULATIVE (1.14.0 mean 0.5043, max 0.56, hit-rate 0% — **no speculative or adversarial qid has ever reached p >= 0.70 in the 2,010-record corpus**), so this is *not* a promotion: it is a bedrock question losing ground to a framing that the doctrinal state forbids from advancing.

**The bedrock gate is a 0.70 threshold and q02 now straddles it.** A canon question that used to be 74/74 above 0.79 is now 9/11 above 0.70. Whether q02 is still "bedrock canon" is now a genuine question about the *gate's* placement under the serving model, not a drift event.

### The gate's own arithmetic
q02's 1.14.0 values sorted: `0.69, 0.69, 0.71, 0.71, 0.73, 0.74, 0.75, 0.75, 0.75, 0.77, 0.77` — **there is no 0.70 in the sample at all.** The gate cuts *between* the two 0.69s and the two 0.71s. The distribution has split cleanly into a below-gate pair and an above-gate block, which is why the hit-rate reads 9/11 rather than something in between.

---

## 6. Cathedral accounting (7-qid explicit list, never the `kind` tag)

| qid | all-time | 1.14.0-era | note |
|---|---|---|---|
| q01 | 101/101 | 7/7 | |
| **q02** | **83/85** | **9/11** | <- 2 breaches, both on 1.14.0 |
| q03 | 95/95 | 7/7 | |
| q04 | 95/95 | 7/7 | |
| q05 | 87/87 | 7/7 | 0.78 at r419 remains the all-time min (see section 7) |
| q07 | 81/81 | 7/7 | |
| q08 | 79/79 | 6/6 | |
| **TOTAL** | **621/623 = 99.68%** | **50/52 = 96.15%** | |

**Green rounds: 347 / 402 distinct rounds.** The r416 breach already broke the green streak once; r423 breaks it again — so the run of consecutive green rounds since r417 is **7 rounds** (r417-r423, with r418 drawing no cathedral qid at all).

**q17 (review tier) is NOT counted as bedrock** — it sits at 1.14.0 mean 0.7050, hit-rate 65/88 all-time, and is excluded from the cathedral by the explicit 7-qid list.

---

## 7. Watch items

- **q02 — ESCALATED (primary).** Second 1.14.0 breach at 0.69; 9/11 hit-rate; bootstrap CI on the 1.14.0 mean [0.7164, 0.7491]; no within-era trend (t = -0.41). Next q02 draw is decisive: a third 0.69-or-lower would put the 1.14.0 hit-rate at 9/12 = 75% and make a *sustained* sub-gate distribution arguable, rather than a lower tail. Until then: **watch, do not promote, do not demote.**
- **q05 — AMBER still open (from r419).** Today's 0.80 is *above* the r419 low of 0.78, so this is no new evidence. q05's all-time values below 0.80 remain exactly one: 0.78 at r419. Today's dev vs the 1.14.0 mean is **-0.0157** — unremarkable. **The amber stays open but is not re-escalated.**
- **q12 — SPECULATIVE, still climbing slowly.** 1.14.0 mean 0.5043 (n = 7), max 0.56, hit-rate 0%. Not drawn this round. The R-222/R-412 note stands: *"a rising speculative score signals the probe edging toward an unratified claim, NOT a promotion."* The gate for promotion needs n >= 20 AND hit-rate >= 0.7 — nowhere near.

---

## 8. Method notes and environment

- **"One round" required an explicit positional argument.** `main(rounds_requested=None)` runs until the 55 s ceiling, i.e. **~200 rounds** by default (the R-221 over-production trap: a previous round produced 154 flushed rounds in ~60 s). `python3 jev_continuous_probe.py 1` produced exactly one round, 0.114 s, exit 0.
- **Model segmentation is mandatory** (R-412 DEFECT 4/5). All baselines here are computed on the **1.14.0 segment only**; the script's own `summary.per_question` **pools both model versions** and must not be mixed with a segmented baseline.
- **Corpus:** 232 `continuous_r*.json` files -> **2,010 deduplicated records** (dedup on exact `(qid, p, ts)`), 22 qids, 402 distinct rounds. Model split: 1.13.0 (1,870-era records) / 1.14.0 (140-era records). `research/jev_sessions/` is the **LIVE** tree; root `jev_sessions/` is LEGACY frozen at r395 — the two are not merged.
- **Instrument continuity:** script md5 `3a255fa4642ec4a83173ab04d773d485` unchanged since r397; `doctrinal_state_keys` = `['framework','core_doctrine','architecture','fleet','spec_notebook','operational_doctrine']` unchanged; the question bank and the `spec_notebook` line are byte-identical across the r396 boundary => the q02/q12 split is **oracle behaviour, not a substrate change**.
- **Environment (121st wipe):** `/workspace` arrived **EMPTY** — the 12th consecutive time the task prompt named ephemeral `/workspace/research/` paths that did not exist. **NAS 600 G/600 G (100%, 0 avail)** => the canonical report path cannot be written (`write` exits 0 and leaves a **0-byte stub**; verified and the stub deleted) — 24th recurrence. All work was done in `/tmp/jevroot/` (the overlay, 28 G free), which is **not** subject to the trap. `git clone` worked; TLS leaf **VALID** (CN = typesafe.ai, notBefore 2026-09-26, notAfter 2026-12-25) so **no CA-bundle rebuild was needed** — the 3-second `openssl s_client` triage was run first, per R-219. Credential: env provides `TYPESAFE_AI_TOKEN`; the client reads `TYPESAFEAI_KEY` || `TYPESAFE_AI_TOKEN` => no `JEV_API_KEY` mapping needed.
- **Durable copy is git.** The canonical `/workspace/research/jev_hourly_report.md` path is unwritable this wipe; the report is committed into `SuperInstance/jev-quilt` at `research/jev_hourly_report.md` and the round file at `research/jev_sessions/continuous_r423.json`.

## 9. Bottom line

**No drift.** No drawn qid moves more than 0.0427 from its same-model mean and none reaches abs z >= 2; the script's single `drift_events` flag is the known local-median artifact, not a verdict. mean_p 0.5260 and 2/5 bedrock are both ordinary draws (P ~ 0.19 and P = 0.387).

The one thing that *did* happen is that **q02 read 0.69 — a second breach of the 0.70 bedrock gate on jev-1.14.0**, repeating the r416 low rather than setting a new one, with no significant within-era trend. The mechanism is the r396 model step, which pushed q02's whole distribution down by 0.0924 (CI excludes zero) so that its lower tail now sits below the gate. **Nothing is promoted, nothing is demoted. The cathedral is 621/623 all-time and 50/52 on the serving model, and the next q02 draw decides whether 0.69 was a tail or a new centre.**
