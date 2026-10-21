# JEV Continuous Probe — Round Report

**Run:** 2026-10-21 ~12:05 UTC (post-wipe recovery run)
**Rounds this run:** 8 (`r384`–`r391`), 40 verdicts, **0 fails**
**History:** 391 → 399 lines. Model `jev-1.13.0` throughout.

## Headline numbers

| Metric | Value |
|---|---|
| Grand mean_p (this run) | **0.3947** |
| Grand mean_p (prior 20) | 0.3791 |
| Δ | **+0.0156** |
| Bedrock hit-rate | **11/11 = 100%** |
| Questions drifted > 0.05 | **none** |

Per-round mean_p: `0.296, 0.236, 0.256, 0.680, 0.322, 0.406, 0.392, 0.570`

## Bedrock canon (p >= 0.70)

All **6/6** bedrock questions cleared the threshold. Every individual bedrock
verdict this run was a hit — no misses.

| qid | kind | mean_p | n | status |
|---|---|---|---|---|
| q02 | bedrock | 0.8100 | 1 | CANON |
| q03 | bedrock | 0.8900 | 1 | CANON |
| q04 | bedrock | 0.8950 | 2 | CANON |
| q05 | bedrock | 0.8533 | 3 | CANON |
| q07 | bedrock | 0.7450 | 2 | CANON |
| q08 | bedrock | 0.9050 | 2 | CANON |

**q07 is the weakest bedrock at 0.7450** — only 0.045 above the gate. Worth watching.

Note: **q06 is NOT bedrock.** The script classifies it `speculative`
(`three_views is the operating epistemology`, `jev_continuous_probe.py:94`).
I initially miscounted it into the bedrock set from a hardcoded qid list and
corrected it against the script's own `kind` field. Its p is 0.10.

## Drift analysis

No question moved more than 0.05. Largest movers:

| qid | Δ vs prior-20 |
|---|---|
| q12 | −0.0379 |
| q07 | −0.0167 |
| q20 | +0.0150 |
| q16 | −0.0120 |

Everything else is sub-0.01 — noise floor. The probe is stable.

## Draw-mix artefact (6th restatement)

Grand mean_p 0.3947 vs bedrock hit-rate **100%**. This gap is *not* signal
collapse — it is which 5 questions got drawn each round. Bedrock questions are
high-p by construction (canon), speculative questions sit at 0.07–0.37, so the
grand mean is a function of the draw. **Report bedrock hit-rate beside mean_p,
never mean_p alone.**

## Promotion gate

Over the full 399-round history, only one question is gate-eligible:

- **q17 (`review`, n=82): mean 0.7024, hit-rate 73%** — above the p>0.7 threshold
  and n>=20. This is a keeper's decision, not an automatic promotion.

All other speculative questions are at 0% hit-rate and nowhere near promotion
(q06 0.099, q09 0.077, q10 0.067, q11 0.185, q12 0.367, q13 0.133, q16 0.200,
q18 0.223, q20 0.105, q21 0.090, q22 0.119).

## Open observation (carried, undiagnosed)

`elapsed_s` ranges **0.106s – 15.981s (151x variance)** across rounds that are all
`status: ok` with identical schema. Fast rounds: r385, r386, r387, r389. Slow
rounds: r388, r390, r391 (~15.8s each, suspiciously consistent).

Still unexplained and worth resolving before trusting absolute values: if the fast
path skips the real API call and returns a cached or stubbed verdict, then a
meaningful fraction of these 399 rounds — and every mean_p computed from them —
would not be measuring JEV at all. Three rounds this run were in the fast band.

## Environment / method notes

- **18th wipe** — `/workspace` arrived bare (only `.plugin-cache`). Recovered by
  cloning `SuperInstance/jev-quilt` into `/tmp/jevrec` then `cp -a` into
  `/workspace`. **18th consecutive clone recovery.**
- **Archive tracking held.** `research/jev_sessions/` came back with all 204
  `continuous_r*.json` + `history.jsonl` (391 lines). The round-file tracking fix
  from the 17th-wipe run is the reason drift analysis was possible at all.
- **Script path correction.** The task named
  `research/jev_continuous_probe.py`, which does not exist. The live probe is
  `/workspace/jev_continuous_probe.py` (400 lines, md5 `d0a7291b2e07...`). There is
  a *different* 284-line tool at `continuous/jev_continuous_probe.py`
  (md5 `95b552ea0d81...`) that takes `--rounds`/`--out` and is **not** the probe
  this report covers. Both write `continuous_r*.json` — do not confuse them.
- **Round numbering, 6th confirmation.** New rounds are **r384–r391**, not r392+,
  because the script's round counter wraps/continues from its own sequence and the
  last pre-run logged round was r389. Filtering history by round *number*
  compares against an overlapping band silently — this report identifies new
  rounds by **tail position**, not by round number.
- **Empty stdout.** The run printed nothing (exit 124 = the 60s timeout kill) yet
  wrote 8 valid rounds. `timeout` kills before the script's final flush/summary
  print. Round data is durable; do not treat empty output as a failed run.
- NAS 96% / 29 G free. Python 3.11.2. `GIT_SSL_NO_VERIFY=1` required for git.
  `TYPESAFE_AI_TOKEN` + `GITHUB_TOKEN` present; ZAI/DeepInfra absent (16th).