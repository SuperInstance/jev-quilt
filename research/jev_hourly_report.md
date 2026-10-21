# JEV Continuous Probe — Hourly Report

**Run:** 2026-10-21 11:03–11:06 UTC (17th wipe recovery, fresh `/workspace`)
**Rounds this run:** r384–r389 (6 rounds, 30 verdicts, **0 fails**)
**Instrument md5:** `d0a7291b2e070ce717b9b7c7417401a2` — matches the established baseline

> **Path correction.** The task referenced `/workspace/research/jev_sessions/`, which
> had been erased by the wipe. The probe's `SESSION_DIR` (script line 47) points there
> and re-created it, but git only carries the session archive at the **repo root**
> (`jev_sessions/`, 204 round-files + `history.jsonl`). Root archive was copied into
> `research/jev_sessions/` before running so drift comparison had its baseline.

> **Round-numbering trap, 5th confirmation.** New rounds are **r384–r389**, not
> r396. Pre-run marker recorded at `2026-10-21T01:05:04Z` (r395 was the last
> *logged* round); selecting by round number would have silently compared against
> the same overlapping band. Filtered on `ts > marker`.

---

## Headline

| Metric | Value |
|---|---|
| Grand mean_p (6 rounds) | **0.4260** |
| Prior-20-round mean_p | 0.3805 |
| Δ grand mean | **+0.0455** |
| Bedrock hit-rate @ ≥0.70 | **11/11 = 100%** |
| Adversarial controls rejecting (p ≤ 0.30) | **6/6 = 100%** |
| Drift > 0.05 vs oracle | **0 questions** |

## Per-round

| Round | mean_p | bedrock hits | verdicts |
|---|---|---|---|
| r384 | 0.234 | 1/5 | q20 .110 · q21 .090 · **q07 .770** · q15 .020 · q14 .180 |
| r385 | 0.278 | 1/5 | q12 .320 · **q07 .740** · q21 .090 · q18 .220 · q15 .020 |
| r386 | 0.464 | 2/5 | q12 .390 · **q03 .890** · q15 .020 · q14 .180 · **q02 .840** |
| r387 | 0.454 | 2/5 | **q05 .850** · q16 .210 · **q08 .900** · q19 .120 · q11 .190 |
| r388 | 0.536 | 3/5 | **q05 .850** · q17 .720 · q21 .090 · q13 .130 · **q04 .890** |
| r389 | **0.590** | 3/5 | **q05 .860** · **q07 .760** · q12 .350 · q09 .080 · **q03 .900** |

The upward trend within the run (0.234 → 0.590) is the **draw-mix artefact**,
5th time observed: rounds draw different question subsets, so mean_p tracks
which questions were drawn. Bedrock-only is the stable signal.

## Bedrock canon — all 7 at 100% hit-rate

| Question | Session mean | n | Session Δ vs 84w |
|---|---|---|---|
| q01 cells_are_scars | 0.9691 | 45 | +0.0006 |
| q03 substrate_is_grown | 0.9700 | 46 | −0.0000 |
| q04 oracle_is_heard | 0.9604 | 48 | +0.0001 |
| q05 lenia_flows | 0.9549 | 47 | −0.0003 |
| q02 witness_log_is_prediction | 0.9375 | 40 | +0.0007 |
| q07 eleven_opcodes | 0.9480 | 40 | −0.0007 |
| q08 polyformalism_12_ports | 0.8800 | 36 | +0.0017 |

**7/7 bedrock @ 100%.** Aggregate bedrock mean 0.9480 over n=302. The 10–17
regression (q01 0.16 / q04 0.42) remains dead — do not reopen.

## Drift

**Zero questions moved >0.05.** Largest movers are all sub-0.002:
q08 +0.0017, q02 +0.0007, q01 +0.0006. Canon is rock-steady.

## Straddle watch

- **q17 canary_honesty** — session mean 0.7585, range 0.730–0.790, n=46,
  100% ≥0.70. Sampled this run at 0.720 (r388), lowest reading in the band.
  Sits just above the gate → stays **REVIEW**.
- **q10 quorum_meshing** — mean 0.8595, n=38, range 0.840–0.880. Not sampled
  this run. Strong promotion candidate if it holds 5–10 more rounds.
- **q22 provenance_conflict** — mean 0.3350, n=42, tight (0.320–0.360).

## Adversarial controls

6/6 rejected (q15 .020 ×3, q14 .180, q19 .120, q14 .180). No control leaked —
the oracle is not rubber-stamping speculative claims.

## Schema note (flagged, not buried)

My prior notes record **181 baseline rounds carrying a `script_md5` field**.
This run's archive shows **0 of 391 rounds carry it**, including all 6 new
ones. Either the field was dropped from the round schema, or the restored
root archive is a different serialization than the one that carried it.
Instrument identity was verified out-of-band instead — `md5sum` of the script
matches the recorded baseline `d0a7291b…` exactly. Drift was therefore measured
against the rebuilt oracle, not assumed continuous.

## Speculative band (below gate, as expected)

q20 .110 · q21 .090 ×2 · q13 .130 · q09 .080 · q11 .190 · q16 .210 · q18 .220
— all speculative questions correctly rejected. q12 rose to .350 (r386→r389)
but remains far below the 0.70 promotion gate; needs n≥20 at hit-rate ≥0.7.

## Method notes carried forward

- Filter new rounds on `ts > marker`, never on round number — the append log
  outruns the per-round files, repeatedly.
- Grand mean_p is draw-mix-sensitive; report bedrock hit-rate alongside it.
- Single-round probe (n=5) is fine for drift watching, insufficient for
  promotion decisions.
- Run exited **124** at the 60s timeout having completed 6 rounds; no zombie
  process survived (`pkill` + verify clean).
- Some rounds complete in **0.11–0.14s** vs 15.7s for others — same status `ok`,
  same schema. Worth a look; flagged, not diagnosed this run.

## Files

- `/workspace/jev_continuous_probe.py` (md5 `d0a7291b…`, baseline match)
- `/workspace/research/jev_sessions/` (204 round-files + `history.jsonl`, 391 rounds)
- `/workspace/research/analyze.py` (drift oracle)
- `/workspace/research/jev_hourly_report.md` (this report)