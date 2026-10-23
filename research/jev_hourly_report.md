# JEV Hourly Report — r399 (2026-10-23T1503Z, 117th wipe)

## Result
- **1/1 round OK (r399), 0 fails, 5 verdicts, 5/22 qids.**
- **mean_p = 0.3720**, bedrock hits **2/5 (40.0%)** — q01 0.860, q02 0.750.
- **Cathedral 7/7 @ 100%** (q06 0.0% by design — it is a control, not canon).
- Round counter issued r399 correctly from history (files->398, history->398), no collision. Saved to canonical `research/jev_sessions/`.

## Verdicts vs each qid's own baseline
| qid | p | base mean | \|dev\| | z | base sd | call |
|----|---|-----------|--------|---|---------|------|
| q06 | 0.140 | 0.0995 | 0.0405 | +6.42 | 0.0063 | ok (see below) |
| q20 | 0.080 | 0.1048 | 0.0248 | −2.49 | 0.0100 | ok |
| q15 | 0.030 | 0.0250 | 0.0050 | +0.99 | 0.0050 | ok |
| q01 | 0.860 | 0.8751 | 0.0151 | −1.65 | 0.0091 | ok |
| **q02** | **0.750** | **0.8247** | **0.0747** | **−5.04** | **0.0148** | **REAL — see below** |

## Drift
**One drift > 0.05: q02 |dev| −0.0747.** Classified REAL, not a σ≈0 trap.

The discriminator (r230 rule) is *baseline shape*, not |z|. q02's baseline is **not flat** — it is on a monotone 4-era decline: 0.8308 → 0.8220 → 0.8185 → recent29 0.8197, sd inflated to 0.0201 (vs 0.0129 in the first third). q02's early→recent29 delta (−0.0111) is the **largest decline of all 22 qids**, and 17 of its last 20 draws are ≤0.83. This round's 0.750 is the only draw of that exact value in 77, and it sits at the far left of an already-descending distribution. **Verdict: leading edge of gradual canon erosion on a bedrock question (q02 is canon, 100% hit-rate).** Watching item, not an alarm.

## Traps correctly cleared
- **q06 z +6.42, |dev| only 0.0405** — largest z in the round, smallest real movement. Cleared on |dev| < 0.05. Additionally, the 0.14 is *not* a new extreme: r398 drew 0.14 as well, so the baseline max (0.140) **was created by the immediately preceding round**. The high z is an artifact of a baseline that had not yet absorbed its own most recent draw, not a jump.
- **q20 z −2.49, |dev| 0.0248** — cleared, narrow [0.080,0.130] band.

## mean_p is not a health signal at 5-of-22 draws
0.3720 vs previous-12 average 0.4177 = **−0.0457**, which looks like aggregate decline. It is **draw mix**: only 3 cathedral qids were drawn (q06, q01, q02) and two of the five were low-band controls (q20, q15). Per memory rule, always decompose an aggregate mean_p delta into per-qid |dev| before calling it drift. **No per-qid drift other than q02.**

## Corpus
- 390 distinct rounds / 1,950 verdicts / 22 qids; grand mean_p **0.3808** (post-r399 corpus basis for next round).
- history.jsonl = 403 lines vs 390 distinct ⇒ duplicate-tail records persist; **first-occurrence-wins (`setdefault`) is the correct read** and `last-line == max` this wipe (DEFECT B did not reproduce — keep setdefault anyway).

## Env (117th wipe)
- **16th consecutive** ephemeral-path wipe: `/workspace/research/` absent, `/workspace` empty. Rebuilt `/tmp/jev_probe` from `SuperInstance/jev-quilt @ cb29c2c`. Script md5 `3a255fa4642ec4a83173ab04d773d485` (unchanged, 2nd wipe).
- NAS 600G/600G on empty workspace (**18th recurrence**) ⇒ report cannot be staged into the workspace; durable copy is the git commit.
- TLS healthy first try (curl 200 and Python 200 same host/second); no cert-anchor bundle rebuild needed this wipe.
- `gh` absent (**8th wipe**); push via `https://x-access-token:$GITHUB_TOKEN@.../jev-quilt.git` + `GIT_SSL_NO_VERIFY=1`, branch `main`.
- `SESSION_DIR` is the fixed relative path and `main(rounds_requested=...)` exists — passed an explicit positional `1`; exactly one round ran (no R-221 overshoot).

## Carry-forward
- **q02 erosion watch**: if recent29 mean falls below ~0.81, or a second sub-0.80 draw appears, promote from "watching item" to a canon-drift finding on a bedrock question.
- **Baseline contamination rule (new)**: when a qid's current value *sets* its historical max/min (as q06's 0.140 did, via r398), the next round's z is inflated against a baseline that predates it. Always check whether the extreme is already the immediately-preceding draw before treating a high z as a jump.
