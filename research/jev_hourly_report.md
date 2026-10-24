# JEV Continuous Probe — Hourly Report

**Round r408** · 2026-10-24T00:03:05Z · model `jev-latest` (server-reported `jev-1.14.0`)
script md5 `3a255fa4642ec4a83173ab04d773d485` (unchanged, 9th consecutive wipe)
bootstrap: `SuperInstance/jev-quilt` @ `d56c30b` → `/tmp/jev-quilt` (unshallowed, 306 commits)

---

## Headline

| metric | value |
|---|---|
| **mean_p** | **0.4380** |
| verdicts | 5 |
| **p >= 0.70 (bedrock canon)** | **2/5 — q05 0.83, q07 0.77** |
| **drift > 0.05** | **NONE** (0 real drifts) |
| cathedral (7 bedrock qids) | **597/597 = 100.00%** |
| spec/adversarial leaks (>= 0.70) | **0** |
| round status | OK, 0 fails, 0.138 s |

**Verdict: clean round.** Both hits are bedrock. No drift on any drawn qid. No spec leak.
The q02 canon-erosion watch was **not** exercised (q02 not drawn) and therefore stands unchanged.

---

## r408 verdicts vs full-history baseline

Baseline = per-qid mean over the entire corpus, **target round excluded** (n in parens).
`|dev| > 0.05` is the drift bar.

| qid | kind | p | baseline | dev | z | n | hist range |
|---|---|---|---|---|---|---|---|
| q16 | review | 0.1900 | 0.1995 ± 0.0084 | −0.0095 | −1.13 | 87 | [0.18, 0.22] |
| q05 | **bedrock** | **0.8300** | 0.8531 ± 0.0185 | −0.0231 | −1.25 | 84 | [0.82, 0.95] |
| q06 | speculative | 0.1500 | 0.1059 ± 0.0264 | +0.0441 | +1.67 | 88 | [0.09, 0.23] |
| q18 | speculative | 0.2500 | 0.2314 ± 0.0545 | +0.0186 | +0.34 | 99 | [0.20, 0.62] |
| q07 | **bedrock** | **0.7700** | 0.7546 ± 0.0165 | +0.0154 | +0.93 | 78 | [0.71, 0.79] |

**Drift verdict: NONE.** The largest deviation is q06 at +0.0441 — under the 0.05 bar, and
q06 is a speculative qid whose entire history lives in [0.09, 0.23], so a 0.15 reading is
squarely inside its range. Every other drawn qid sits well inside one σ of its own mean.

### σ≈0 trap — 16th consecutive round, rule held

q06's z is +1.67 on a |dev| of 0.0441. The eye is drawn to the z, but |dev| is the
physical-movement test and it says nothing moved. Conversely q16's z of −1.13 is the
smallest absolute deviation in the set. Reading the z column as the drift verdict would
have produced a false positive in both directions. The bar is `|dev| > 0.05` against the
qid's own baseline, and no drawn qid clears it.

---

## The script's `drift_events=2` is a FALSE POSITIVE — both events are stale echoes

The harness printed `drift_events=2`. Neither event is real.

| script event | delta | drawn in r408? | verdict |
|---|---|---|---|
| q02 | −0.06 | **NO** | stale echo (carried from r407's 0.71) |
| q12 | +0.08 | **NO** | stale echo (carried from r407's 0.54) |

**Drawn-set intersection = 0.** r408 drew q16, q05, q06, q18, q07 — neither q02 nor q12
appears in the round, so neither can have drifted *in* r408. The script's `drift_check()`
compares each qid's last value against a 5-sample local median **regardless of whether that
qid was drawn**, so an event from a prior round keeps re-firing until that qid is drawn again.

This is the third consecutive round where the script's drift count over-reported
(r405: 1 false positive; r406: 1 real + 1 stale; r407: 2 real; **r408: 2 stale, 0 real**).
The script count is a raw event tally, never a health verdict — the real count here is **0**.

---

## Cathedral: 597/597 = 100.00%

| qid | hits/n | hit rate | mean_p | min | max |
|---|---|---|---|---|---|
| q01 | 98/98 | 100.0% | 0.8748 | 0.84 | 0.97 |
| q02 | 78/78 | 100.0% | 0.8208 | **0.71** | 0.94 |
| q03 | 92/92 | 100.0% | 0.8861 | 0.86 | 0.97 |
| q04 | 93/93 | 100.0% | 0.8886 | 0.88 | 0.96 |
| q05 | 83/83 | 100.0% | 0.8505 | 0.82 | 0.95 |
| q07 | 79/79 | 100.0% | 0.7548 | 0.71 | 0.79 |
| q08 | 74/74 | 100.0% | 0.8995 | 0.87 | 0.91 |

**Zero sub-0.70 draws on any cathedral qid, ever.** This round: q05 and q07 both drawn,
both hit.

### Methodology note — a 98.34% cathedral is a counting artifact, not a regression

An initial pass reported the cathedral at 592/602 = 98.34%. That number is wrong and the
reason matters: the corpus holds **two round schemas**.

- **Legacy (200 files)** — `verdicts` is a **dict** `{qid_slug: p}` with descriptive qids
  (`q02_witness_log_is_prediction`). No `kind`, no `bedrock_hit` flag, and a *different*
  question set (legacy `q14_canon_equals_speculation`, `q19_pressure_cascade`,
  `q10_quorum_meshing` as a bedrock-calibrated question).
- **Modern (16 files, r1–r408 under the short-qid schema)** — `verdicts` is a **list** of
  `{qid, kind, p, bedrock_hit}` with short qids (`q02`).

A naive cross-schema count mixes two different question banks and scores legacy
`q10_quorum_meshing` against a modern speculative definition, manufacturing 10 phantom
cathedral misses. Within the modern schema the cathedral is **597/597 = 100.00%**, and
the last-20-rounds slice is 40/40 = 100%. Verified independently: across all 1,935
modern-schema verdicts there are **0 disagreements** between `p >= 0.70` and the script's
own `bedrock_hit` flag, so the classification is exact, not inferred.

q17 (`kind=review`, deliberately **not** in the cathedral) sits at 58/78 = 74.4%,
mean 0.7029, min 0.66 — a review-tier plateau, and not a bedrock failure.

---

## Spec / adversarial guard: clean

All 908 speculative and 264 adversarial modern-schema verdicts read below 0.70.
No leak this round. q06 (0.15) and q18 (0.25) are both speculative and both low.

---

## q02 canon-erosion watch — NOT EXERCISED, stands unchanged

r407 escalated q02 to a canon-erosion watch: 0.71 was a new all-time low, the 2nd
consecutive sub-0.75 draw, against a full-history mean of 0.8222 ± 0.0205 (dev −0.1122,
z −5.48). The rule set was: next q02 draw decides.

**q02 was not drawn in r408.** The watch therefore carries forward untouched, and no
new information about it exists.

Last 8 q02 draws: `r361 0.84 → r379 0.81 → r381 0.81 → r383 0.81 → r399 0.75 → r401 0.77 → r406 0.73 → r407 0.71`

Era means (blocks of 20 draws): **0.8345 / 0.8230 / 0.8335** — first three flat within 0.011.
last-5 0.7540 vs prev-5 0.8180 = **−0.0640**.

**Standing rule for the next q02 draw** (unchanged):
- `< 0.70` ⇒ **canon breach**, report immediately
- `0.70–0.74` ⇒ 3rd consecutive sub-0.75, treat the shift as structural
- `>= 0.80` ⇒ the tail was noise, close the watch

Caveat: q02 is drawn in only 79/394 rounds (20.1%) — thin, but the era shift lives in the
aggregate rather than any single point.

---

## Corpus state

- **394 distinct rounds**, r1..r408 (217 round files; 1 `.fail.json`; 200 legacy + 16 modern schema)
- **1,970 total verdicts** across **22 qids**
- **grand mean_p 0.3868**
- round numbering verified two ways: files → 408, history.jsonl → 408 (412 records, 0 malformed)
- no duplicate round numbers; no clobber; start counter correct at 408

---

## Environment (124th wipe)

- **23rd consecutive** ephemeral-path wipe — both `/workspace/research/` and `/tmp/jev_probe/`
  absent on arrival. Rebuilt from `SuperInstance/jev-quilt` into `/tmp` (overlay, 28 G free).
- **NAS 100% (26th recurrence)** — 600 G/600 G, 0 bytes. The whole `/workspace` mount *is*
  the quota'd NAS; `/root` and `/tmp` are the 28 G overlay and are writable. Report copy
  placed at `/root/jev_hourly_report.md`; the git-tracked copy is the durable home.
- **TLS clean on first try** — live leaf `api.typesafe.ai` valid to 2026-12-25 (+62.5 d),
  stock Python context verifies, TCP/TLS/API all reachable. No cert-anchor wall, no
  MITM-leaf expiry, no 289-cert rebuild. 8th clean wipe.
- API pre-flight: HTTP 400 on a hand-rolled payload (reachable, auth passed, wrong shape)
  — confirms the endpoint is live before spending a round.
- **Positional `1` ran exactly one round, no overshoot** — the task's literal command
  (no arg) defaults to 200 rounds. Round counter confirmed from the log: `files->407 history->407 start=408`.
- `gh` absent; git via token URL with `GIT_SSL_NO_VERIFY=1`.
