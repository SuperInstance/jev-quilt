# JEV Hourly Report — R-226 (round 386)

**Run:** 2026-10-23T10:04Z · 113th wipe · 1 round, status `ok`, 0.143 s
**Instrument:** `jev_continuous_probe.py` md5 `bda7ccb3d3af4d1c2c7e961e2dcf174a`
— **3rd consecutive round on this version** (r224, r225, r226). Baseline is same-instrument and valid.
**Model:** jev-1.14.0

## Headline
| metric | value |
|---|---|
| mean_p | **0.4840** |
| verdicts | 5 (5/27 qids sampled) |
| bedrock hits p>=0.70 | **2/5** |
| drift > 0.05 | **1 — q12 +0.1519** |
| drift verdict | **NOT canon movement** (see below) |

## Verdicts
| qid | p | kind | baseline mean | dev | z |
|---|---|---|---|---|---|
| q04 | 0.88 | bedrock | 0.8887 (n=182) | −0.0087 | −0.99 |
| q17 | 0.70 | review | 0.7024 (n=160) | −0.0024 | −0.17 |
| q21 | 0.09 | speculative | 0.0904 (n=185) | −0.0004 | −0.11 |
| q12 | 0.52 | speculative | 0.3681 (n=180) | **+0.1519** | +4.71 |
| q14 | 0.23 | adversarial | 0.1924 (n=161) | +0.0376 | +3.27 |

**Bedrock canon p>=0.70:** q04 (0.88), q17 (0.70 — exactly at bar, counts as hit).

## Drift analysis — q12 is the ceiling, not a slope
q12's +0.1519 is the largest aggregate deviation in the series, and it clears the 0.05
bar hard. But the **baseline distribution says this is a one-draw touch of the ceiling,
not advancement**:

- Baseline n=180, mean 0.3681, sd 0.0323, **range 0.30–0.52**
- Today's 0.52 is the **historical maximum**, 99.4th percentile — **zero** prior draws above it
- Decile histogram is bimodal and frozen: 0.3 ×64, 0.4 ×115, 0.5 ×**1** (this one)
- **Half-vs-half delta: +0.0012** (first half 0.3674 vs last half 0.3687) → dead flat

This is the 8th recurrence of the σ≈0 / ceiling-graze trap. q04 and q17 fired z within ±1
on deviations ≤0.009 — a stable, boring round. The only loud z is q12, and the loud z is
the ceiling, not a slope. **No canon advanced. No promotion gate touched.**

q14 (adversarial, z +3.27 on dev 0.0376) is under the 0.05 bar — a σ≈0 artifact, base sd
0.0115. Noted, not reported as drift.

## Environment
- **11th consecutive** wipe naming ephemeral `/workspace/research/` paths — absent again.
  Rebuilt to `/tmp/jev_probe` from `SuperInstance/jev-quilt @ 7124392`.
- **NAS 100% (600G/600G) on an empty workspace**, 13th recurrence. Workspace report
  cannot be staged; this file's durable copy is the git commit below.

## Two real defects found and fixed this round
1. **`SESSION_DIR` mismatch — the harness was writing r001 into a phantom directory.**
   The script hardcodes `SESSION_DIR = /tmp/jev_probe/jev_sessions` (line 49) but the real
   385-round corpus lives in `repo/jev_sessions/`. First attempt globbed the empty hardcoded
   dir, derived `round_idx = 1`, and **silently collided with an existing r001**. Fixed by
   repointing `P.SESSION_DIR` at the repo dir before `run_round()`. Any prior wipe whose
   harness didn't repoint has been reporting round numbers against a phantom corpus.
2. **The 385-round corpus lives in TWO history files, and neither is the "real" one.**
   `jev_sessions/history.jsonl` = 387 records; `research/jev_sessions/history.jsonl` =
   **399 records** (max round 395, **13 duplicate round numbers**). The repo-root
   `history.jsonl` is a 2-line stub that parses exactly like catastrophic data loss.
   Baseline here merges both. **This should be reconciled before the next drift call.**

Carried forward: `sys.argv` round-count path is gone; `rounds` is a hardcoded
`while time.time() - started < 55`. `/tmp/one_round.py` harness (with the SESSION_DIR
repoint) is the only reliable one-round path — 0.14 s, no overshoot.
