# JEV Continuous Probe — R-220 (2026-10-23T03:03Z)

**107th wipe. Round tag `r20261023T030500Z`. 12 attempted / 12 OK / 0 fail, 60 verdicts, 22/22 qids, 3 s.**

## Headline

| metric | value |
|---|---|
| **grand mean_p** | **0.5005** (top of the 0.3596-0.4931 band; see "why high mean is not drift") |
| **cathedral (bedrock canon)** | **25/25 @ 100%**, mean 0.9740 - **18th consecutive** |
| **qids hitting p >= 0.70** | **7 of 7 cathedral qids. No non-bedrock qid reached 0.70.** |
| **drift > 0.05 (per-qid aggregate)** | **NONE** - max abs(dev) 0.0420 (q12, +1.96 sigma) |
| spec clean-reject (< 0.40) | 22/22, max 0.1800 (q09) |
| adversarial clean-reject | 3/3 |
| q10 spec-leak | 0.0300 vs base 0.0309 - resolved, 14th consecutive |
| q17 canary | 0.6500 vs base 0.6527 (-0.10 sigma) - **stable REVIEW plateau** |

## Questions at p >= 0.70 (bedrock canon)

All seven cathedral members, every sample, zero misses:

| qid | n | p range | mean | base |
|---|---|---|---|---|
| q01_cells_are_scars | 3 | 0.980 | 0.9800 | 0.9798 |
| q02_witness_log_is_prediction | 4 | 0.970-0.980 | 0.9750 | 0.9723 |
| q03_substrate_is_grown | 2 | 0.980 | 0.9800 | 0.9798 |
| q04_oracle_is_heard | 3 | 0.970 | 0.9700 | 0.9720 |
| q05_lenia_flows | 2 | 0.970 | 0.9700 | 0.9696 |
| q07_11_opcodes | 4 | 0.960-0.970 | 0.9650 | 0.9697 |
| q08_polyformalism | 7 | 0.970-0.980 | 0.9771 | 0.9799 |

Cathedral built from the **explicit 7-qid list**, never from the `kind` tag (q06 carries a historical
`bedrock` tag but reads 0.19 and belongs outside it - tag-based counting would report 26/26 and be wrong).

Everything below the gate: q17 0.60-0.68 and q12 0.63-0.67 (both `review`, both below 0.70 as designed),
q06 0.19, then the speculative wall at 0.03-0.18.

## Drift

**NONE.** Baseline 2,955 prior samples / 22 qids, non-empty assertion PASSED (DEFECT B clear, 13th consecutive
session needing no manual seeding).

Ranked by per-qid aggregate deviation from the full-history mean:

```
q12_substrate_polyformal   0.6500 vs 0.6080   +0.0420  sigma=0.0214  +1.96s
q09_signal_chain_canon     0.1750 vs 0.2007   -0.0257  sigma=0.0117  -2.20s
q06_three_views            0.1900 vs 0.1645   +0.0255  sigma=0.0167  +1.52s
q13_witness_log_opcode     0.0900 vs 0.1115   -0.0215  sigma=0.0110  -1.96s
q20_wolffs_law             0.0633 vs 0.0505   +0.0129  sigma=0.0035  +3.69s
q15_jev_synapse            0.0400 vs 0.0497   -0.0097  sigma=0.0021  -4.64s
q07_11_opcodes             0.9650 vs 0.9697   -0.0047  sigma=0.0016  -2.95s
q17_canary_honesty         0.6500 vs 0.6527   -0.0027  sigma=0.0266  -0.10s
... all remaining 14 qids < 0.003
```

### DEFECT D, third confirmation - the summary's drift count was wrong again

`session_summary.json` reported **`Drift events > 0.05: 1`**. Recomputing per-qid aggregates from the
round files: the count is **0**. The raw count is inflated by single-verdict excursions on high-variance
qids - q12 read 0.6300 and 0.6700 (dev +0.0620 on one sample) and q17 read 0.6000 (-0.0527), each firing
individually while the qid *mean* moves less. Three distinct inflations now (R-214, R-216, R-220), each
with a different raw count and zero real drift: **never quote the summary's event count.**

### sigma is meaningless when sigma ~ 0 - guard before quoting a z-score

q15 shows **-4.64 sigma on a -0.0097 dev**. q20 shows +3.69 sigma on +0.0129. Neither is drift: both sit far
inside the 0.05 floor because their baselines are near-degenerate (sigma = 0.0021, 0.0035). This is the
R-219 finding confirmed on a second round - **report abs(dev) against the 0.05 floor first; a z against a
near-zero sigma is not evidence of anything.** Conversely q12's +1.96 sigma on the largest real deviation is
the only one worth watching, and +1.96 sigma is not a signal.

## Why mean_p 0.5005 is not a regression

The grand mean mixes 7 bedrock (~0.97) with 13 spec/review/adv (~0.04-0.68) on 5-of-22 draws, so
E[bedrock per round] ~ 5 x 7/22 ~ 1.6. This round drew **25/60 bedrock verdicts**, far above expectation -
the draw mix, not the model, produced the number.

Band across R-206 -> R-220: 0.3596 - 0.5005. No trend; this round is the top of the band and the cathedral
is intact. **Health lives in the cathedral and the buckets, never the grand mean.**

## Environment

- **107th wipe; both documented mirror homes empty again** (`/workspace/research/` bare, `/tmp/jev_probe/`
  gone) - 5th consecutive time the task prompt named ephemeral probe paths that did not exist.
  Bootstrapped from `jev-quilt @ r-081-continuous-probe-rebuild` HEAD `ae0990d`;
  `jev_continuous_probe.py` md5 `c22e8c72f13f3b71d5b40e8f8fd04d61` unchanged across the last 3 wipes.
- **TLS leaf triage ran first** (R-219's 3-second procedure): `notAfter Oct 24 03:03:31 2026 GMT`,
  **delta +1.00 d -> VALID**. Confirms the ~24 h rotation; R-218's "outage" remains a closed incident.
  `SSL_CERT_FILE` gateway-anchor-only **9th recurrence** -> rebuilt the 289-cert bundle.
- **New observation - a bare canary is not representative.** The pre-flight `/v1/models` probe returned
  **HTTP 503**, yet the probe itself ran **12/12 with zero stalls and zero retries**. 503 is the
  service's transient overload path (the retry logic already covers it), *not* a reason to skip a round.
  Don't gate on the canary alone; the 3-second leaf check is the meaningful triage.
- DEFECT A structurally impossible (timestamp-tagged `rounds_<TAG>/`, 12 files written, none clobbered).
- Round files, not `session_summary.json`, are the analysis substrate - the probe's 60 s deadline sits
  inside the harness and would eat the summary.
- NAS `/workspace` is at 100% quota (600G/600G, Avail 0), so the task-requested
  `/workspace/research/jev_hourly_report.md` cannot be written. Durable copies: this repo (git) and
  `/tmp`. Byte-verify every write before claiming delivery.

## Comparison to previous rounds

| round | mean_p | cathedral | agg drift | note |
|---|---|---|---|---|
| R-216 | 0.4767 | 40/40 (15th) | none | max 0.0118 (q13) |
| R-217 | 0.4608 | 9/9 (16th) | none | max 0.0246 (q06) |
| R-218 | undefined | - | - | 0/12, TLS leaf expired; no data |
| R-219 | 0.4547 | 21/21 (17th) | none | max 0.0363 (q17) |
| **R-220** | **0.5005** | **25/25 (18th)** | **none** | **max 0.0420 (q12)** |

Cathedral now 18 sessions consecutive at 100%. Zero aggregate drift in every session with data since
R-206. q17 remains a stable REVIEW plateau - its own aggregate moved -0.0027, i.e. it is flat, and should
stop being reported as oscillating.
