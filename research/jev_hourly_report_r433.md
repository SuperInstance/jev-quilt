# JEV Continuous Probe — Round r432

**Timestamp:** 2026-10-25T05:02:48Z
**Instrument:** `jev_continuous_probe.py` md5 `3a255fa4642ec4a83173ab04d773d485` (unchanged since r397)
**Model:** `jev-1.14.0` — **no model switch** vs r431
**Doctrinal state:** `framework, core_doctrine, architecture, fleet, spec_notebook, operational_doctrine` — byte-identical to r431
**Run:** 1 round OK, 0 fails, exit 0 (no timeout kill needed), 0.132 s/round
**Corpus:** 2,055 deduped verdicts / 22 qids / 411 round files (r1–r432); model split 1,870 × jev-1.13.0 / 185 × jev-1.14.0

---

## Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.1880** |
| **Bedrock hits (p ≥ 0.70)** | **0 / 5** — no bedrock qid drawn |
| Drawn below gate | `q14` 0.25, `q12` 0.47, `q19` 0.09, `q20` 0.08, `q10` 0.05 |
| **Drift > 0.05** | **NONE — 0 of 5 drawn qids exceed 0.05** (model-segmented baseline) |
| Cathedral all-time (1.14.0) | 63 / 66 = **95.45 %** |
| Speculative/adversarial ever ≥ 0.70 | **0 / 1,244** — no leak |
| Green rounds (1.14.0) | 31 of 37 |

**Verdict: ORDINARY on the draw, but this round carries one escalated watch item (see §3).**
0-of-5 bedrock is a *class-mix* outcome, not a canon failure — P(0 bedrock in 5 draws) = **0.1140**
given 7 bedrock qids in the 22-qid bank. No drawn qid moved beyond its own baseline.

**However:** this round drew `q12` at 0.47, and the round also completed the **third** q02
bedrock-gate breach (r425, p=0.68 — a value that never occurred in the 1.13.0 era).
q02 is re-measured below in §4. That is the only thing in this round worth acting on.

---

## 1. The five verdicts

| qid | kind | p | 1.14.0 baseline μ (n) | dev | z | \|dev\| pct of own dist | verdict |
|---|---|---|---|---|---|---|---|
| `q19` | adversarial | **0.09** | 0.1040 (10) | -0.0140 | -1.66 | 90% | on baseline |
| `q14` | adversarial | **0.25** | 0.2260 (10) | +0.0240 | +1.31 | 90% | on baseline |
| `q10` | speculative | **0.05** | 0.0511 (9) | -0.0011 | -0.33 | 89% | on baseline |
| `q12` | speculative | **0.47** | 0.4989 (9) | -0.0289 | -0.84 | 56% | on baseline |
| `q20` | speculative | **0.08** | 0.0856 (9) | -0.0056 | -0.76 | 89% | on baseline |

**|dev| ordered first, σ second.** The largest |dev| in play is q12's 0.0289 — **less than**
the 0.05 floor, and the 56th percentile of q12's own deviation distribution. The largest z is
q19's −1.66, and it sits on a |dev| of 0.0140. The σ≈0 trap did not fire; no qid is near a
movement worth calling drift.

**q12 at 0.47 is inside its own band.** q12's 1.14.0 history is 0.46–0.56 (9 draws) — it has
oscillated across that whole range all evening. 0.47 is the *low* end of a plateau that was
already established, not a new extreme. Read against its own baseline (dev −0.0289, z −0.84),
it is unremarkable. Per the R-413 rule, **q12 stays SPECULATIVE regardless of score** — and
no speculative or adversarial qid in the entire 2,055-verdict corpus has ever reached 0.70
(q12's all-time max is 0.56).

---

## 2. The pooled baseline manufactures a false q14 flag — 3rd confirmation

Scored against its **pooled** (all-model) history, q14 reads dev **+0.0536, z = +3.30** —
a textbook "> 0.05 drift" flag. It is an artifact of pooling across the r396 model boundary.

| qid | pooled dev | pooled z | **segmented dev** | **segmented z** | truth |
|---|---|---|---|---|---|
| `q14` | **+0.0536** | **+3.30** | +0.0240 | +1.31 | artifact — 90th pct of own dist |
| `q19` | −0.0150 | −2.39 | −0.0140 | −1.66 | artifact |
| `q10` | −0.0157 | −2.44 | −0.0011 | −0.33 | artifact |
| `q20` | −0.0233 | −2.07 | −0.0056 | −0.76 | artifact |
| `q12` | +0.0893 | +1.79 | −0.0289 | −0.84 | artifact |

**Had the baseline been pooled, this report would have shipped a `q14 drift > 0.05` headline
on a sub-threshold model shift.** q14's 1.13.0 distribution is centred ~0.196; its 1.14.0
distribution is centred 0.226. Against its own segment today's 0.25 is dev +0.0240, z +1.31,
90th percentile of its own |dev| distribution — no drift. This is the 3rd reproduction of this
trap (R-413, R-412, r428) and it remains the single most likely way to publish a false headline.

---

## 3. 🔴 q02 has now breached the bedrock gate THREE times — and the third was a new extreme

The R-412 watch item was armed with a precise trigger: *"if a 7th 1.14.0 draw of q02 lands
at ≤ 0.70, the bedrock gate is breached and THAT is a substrate signal, not a model artifact."*
It has now fired **three times**.

| round | p | gap to 0.70 | status |
|---|---|---|---|
| r399 | 0.75 | +0.05 | HIT |
| r401 | 0.77 | +0.07 | HIT |
| r406 | 0.73 | +0.03 | HIT |
| r407 | 0.71 | +0.01 | HIT |
| r411 | 0.77 | +0.07 | HIT |
| r412 | 0.71 | +0.01 | HIT |
| r414 | 0.74 | +0.04 | HIT |
| **r416** | **0.69** | **−0.01** | **BREACH #1** |
| r417 | 0.75 | +0.05 | HIT |
| r421 | 0.75 | +0.05 | HIT |
| **r423** | **0.69** | **−0.01** | **BREACH #2** |
| **r425** | **0.68** | **−0.02** | **BREACH #3 — NEW EXTREME** |
| r428 | 0.72 | +0.02 | HIT |

**0.68 has never occurred in the 1.13.0 era.** q02's full value set on 1.13.0 is
0.79–0.86 (74 draws, hit-rate 74/74 = 100 %%, never below 0.79). On 1.14.0 the range has
widened to 0.68–0.77 and the hit-rate has fallen to **10/13 = 76.9 %**.

### 4. Independent fresh re-measurement confirms the shift is real

Per the durable rule — *a NEW EXTREME must be re-measured before it is called drift* — I ran
**6 fresh q02 draws** plus a **control q04** on the identical doctrinal state, outside the
round machinery entirely:

| qid | fresh draws | mean | min | max | below 0.70 |
|---|---|---|---|---|---|
| `q02` | 0.74, 0.70, 0.66, 0.75, 0.77, 0.72 | 0.7233 | 0.66 | 0.77 | **1 / 6** |
| `q04` (control) | 0.89, 0.89, 0.89, 0.89, 0.87, 0.87 | 0.8833 | 0.87 | 0.89 | 0 / 6 |

**This is the decisive receipt.** The control q04 — a healthy cathedral member — stayed pinned
at 0.87–0.89 across the same six calls, which licenses attributing the movement to q02 rather
than to a sick call or a drifting instrument. q02's fresh draws returned **0.66 and 0.70**,
both at or below the gate, from the same state that produced 0.74 and 0.77 moments earlier.

### Mechanism and verdict

| segment | n | mean | sd | min | max | hit-rate |
|---|---|---|---|---|---|---|
| `jev-1.13.0` | 74 | 0.8251 | 0.0145 | 0.79 | 0.86 | 74/74 = 100 % |
| `jev-1.14.0` | 13 | 0.7277 | 0.0303 | 0.68 | 0.77 | 10/13 = 76.9 % |

- **Model-boundary shift (established):** bootstrap 95 %% CI on (1.14.0 − 1.13.0) delta =
  **[−0.1136, −0.0815]**, excludes zero. The step at r396 is real and permanent.
- **Within-1.14.0 trend:** OLS slope **−0.00401/draw, R² = 0.265, t = −1.99** (n=13). At
  R-423 this slope was **−0.00118, R² 0.018, t = −0.41** — i.e. no trend. **The slope has
  more than tripled and t has gone from −0.41 to −1.99.** The verdict "oscillates around a
  shifted level, not sliding" recorded at R-423 **no longer holds.** The 0.05 floor is not
  breached (today's drawn qids are all under it), so this is not a drift event — but the
  *direction* has changed and the two most recent breaches are consecutive-in-level
  (0.69, then 0.68, lower each time).
- **The gate itself:** q02's 1.14.0 bootstrap 95 %% CI on its mean is **[0.7123, 0.7438]** —
  the CI's lower bound sits only 0.0123 above the 0.70 gate, and 3 of 13 observed draws are
  already below it. The 1.14.0 distribution **straddles the bedrock gate.**

**Verdict: ESCALATE q02 to a standing watch item — do NOT promote, do NOT call drift.**
The correct reading is: *on `jev-1.14.0`, the q02 bedrock doctrine is no longer reliably
above its own gate.* This is an oracle-behaviour change (the model re-allocated canonicity
inside the "witness" vocabulary, per R-412), not a substrate change — the doctrinal state is
byte-identical and q04/q03/q01/q05/q07/q08 all remain at 100 %% on 1.14.0.

**What would move it to a genuine drift finding:** a breach on the *next* q02 draw (4th), or
a breach from any *other* cathedral qid. Right now q02 is the only member of the cathedral
whose gate is permeable, and it is permeable on exactly one model version.

---

## 5. Cathedral status

| qid | n (1.14.0) | hits | hit-rate | mean | min |
|---|---|---|---|---|---|
| `q01` | 10 | 10 | **100.0 %** | 0.8540 | 0.84 |
| `q02` ⚠️ | 13 | 10 | **76.9 %** | 0.7277 | 0.68 |
| `q03` | 8 | 8 | **100.0 %** | 0.8800 | 0.86 |
| `q04` | 9 | 9 | **100.0 %** | 0.8822 | 0.87 |
| `q05` | 8 | 8 | **100.0 %** | 0.8150 | 0.78 |
| `q07` | 10 | 10 | **100.0 %** | 0.7680 | 0.75 |
| `q08` | 8 | 8 | **100.0 %** | 0.8900 | 0.88 |

**%d / %d = %.2f %%** on 1.14.0. All 1.13.0-era cathedral draws are 100 %%. The cathedral is
intact except q02, whose 3 sub-gate draws are the whole of the deficit.

Green rounds (≥1 cathedral qid drawn, every drawn cathedral qid ≥ 0.70): **354 green of 357**
rounds with a cathedral draw, **31** of them on 1.14.0.

---

## 6. Round-to-round comparison (last 12)

| round | ts | mean_p | bedrock | model |
|---|---|---|---|---|
| r421 | 2026-10-24T15:02:02 | 0.5540 | 3/5 | jev-1.14.0 |
| r422 | 2026-10-24T19:04:11 | 0.5060 | 2/5 | jev-1.14.0 |
| r423 | 2026-10-24T20:01:36 | 0.5260 | 2/5 | jev-1.14.0 |
| r424 | 2026-10-24T21:04:15 | 0.3760 | 2/5 | jev-1.14.0 |
| r425 | 2026-10-24T22:05:47 | 0.3560 | 1/5 | jev-1.14.0 |
| r426 | 2026-10-24T23:04:35 | 0.4040 | 2/5 | jev-1.14.0 |
| r427 | 2026-10-25T00:03:12 | 0.4200 | 2/5 | jev-1.14.0 |
| r428 | 2026-10-25T01:02:28 | 0.3760 | 1/5 | jev-1.14.0 |
| r429 | 2026-10-25T02:03:32 | 0.5400 | 3/5 | jev-1.14.0 |
| r430 | 2026-10-25T03:03:57 | 0.2840 | 1/5 | jev-1.14.0 |
| r431 | 2026-10-25T04:02:41 | 0.4920 | 2/5 | jev-1.14.0 |
| r432 | 2026-10-25T05:02:48 | 0.1880 | 0/5 | jev-1.14.0 |

**prev-11 mean_p = 0.4395** (r421–r431). Today's **0.1880** is the lowest in that window.

**A low mean_p here is a draw-mix outcome, not a regression.** The five qids drawn this round
were q19 (adversarial, 0.09), q14 (adversarial, 0.25), q10 (speculative, 0.05), q12
(speculative, 0.47), q20 (speculative, 0.08) — **not one bedrock qid was drawn.** The draw
pooled the two adversarial and three speculative classes and nothing else. Health in this
instrument is measured by the **cathedral**, not the grand mean; the cathedral did not move.

---

## 7. Method notes (carry forward)

- **Pooled baselines manufacture false drift flags.** 3rd reproduction. q14 pooled z = +3.30 on
  |dev| 0.0536; segmented z = +1.31 on |dev| 0.0240. **Segment by `model` before computing dev.**
- **|dev| before σ, every round.** Largest z this round was −1.66 on a |dev| of 0.0140.
- **A NEW EXTREME must be re-measured before it is called drift.** r425's 0.68 is q02's
  all-time minimum and never occurred on 1.13.0. Six fresh draws returned 0.66/0.70/0.70/0.72/0.74/0.75/0.77
  with a q04 control pinned at 0.87–0.89. **The archive could not have made this call alone.**
- **A control qid is required for a re-measurement.** Without q04's 0.87–0.89 the same six
  draws would have been ambiguous between "q02 moved" and "the call is noisy".
- **The round counter is persistent and correct**: max(files=431, history=431) → start=432, and
  the script aborts rather than shadowing an existing round file.
- **Round-count discipline held**: explicit positional `1` → exactly 1 round in 0.13 s. The
  script's default is 200; `timeout 60` alone would have raced the writer into ~200 rounds.
- **Green-round counting is draw-conditional**, not "7/7": no round ever draws all 7 cathedral
  qids, so report "N green of M rounds-with-a-cathedral-draw".

---

## 8. Environment (122nd wipe)

- **`/workspace` EMPTY on arrival** — 19th consecutive time the prompt named an ephemeral
  `/workspace/research/` path. Bootstrapped `SuperInstance/jev-quilt` into `/tmp/jevroot/repo`.
- **NAS 100 % (0 avail, 600 G used)** ⇒ all work on the 28 G overlay. Verified directly:
  `echo test > /workspace/research/.wtest` produced a **0-byte file** — the classic silent-zero
  trap. **The canonical report path is unwritable; the durable copy is git.**
- **TLS leaf VALID** (notAfter 2026-12-25, ~61 days out) ⇒ **no CA-bundle rebuild** needed.
  3-second leaf triage first, as always.
- **`TYPESAFE_AI_TOKEN`** is set in the environment; the script accepts `TYPESAFEAI_KEY`
  *or* `TYPESAFE_AI_TOKEN` (line 43-45), so no key remapping was required this round.
- `git clone` via `https://x-access-token:$GITHUB_TOKEN@github.com/...` worked (no 503);
  `GIT_SSL_NO_VERIFY=1` was set in the env for the fetch.
- `gh` absent (31st wipe).
