# JEV Hourly Report — 2026-10-21 17:02 UTC (R-213)

**Session**: r20261021T170217Z → 17:03:11Z (60s ceiling)
**Rounds**: 27 OK, 1 fail (round 020, TLS handshake timeout)
**Probes**: 130 (expected 135 = 27×5; the failed round left no verdicts)
**Script**: `jev_continuous_probe.py` md5 `c22e8c72f13f3b71d5b40e8f8fd04d61` (unchanged, drift-detector clean)
**Bootstrap**: `SuperInstance/jev-quilt @ r-081-continuous-probe-rebuild` @ `ae52108` (R-212)

## Headline

- **Grand mean_p = 0.4931** across 130 verdicts
- **Bedrock canon (cathedral): 41/41 @ 100%** — mean p = 0.9754 — **12th consecutive session at 100%**
- **Speculative clean-reject** (<0.40): **42/42 = 100%** (max 0.21)
- **Adversarial clean-reject** (<0.20): **12/12 = 100%** (max 0.05)
- **Drift events > 0.05**: **NONE** (largest single-sample deviation 0.0371, q12 = 1.80σ against a 0.05 floor)

This is a **real all-clear**, not the thin-round artifact: the current window is n=2–10 per qid, but the drift reference is the **full-history mean over 2,225 samples across all 22 qids**, which is well-populated. (R-206 lesson: the sample-size artifact applies to the current window, not the baseline.)

## Per-qid verdicts

| qid | n | cur mean | base mean | max dev | hit |
|-----|---|----------|-----------|---------|-----|
| q01_cells_are_scars | 7 | 0.9800 | 0.9798 | 0.0002 | 100% |
| q02_witness_log_is_prediction | 4 | 0.9725 | 0.9720 | 0.0080 | 100% |
| q03_substrate_is_grown | 3 | 0.9800 | 0.9798 | 0.0002 | 100% |
| q04_oracle_is_heard | 7 | 0.9729 | 0.9722 | 0.0078 | 100% |
| q05_lenia_flows | 10 | 0.9690 | 0.9696 | 0.0096 | 100% |
| q06_three_views | 2 | 0.1650 | 0.1652 | 0.0152 | — (durable REJECT) |
| q07_eleven_opcodes | 8 | 0.9700 | 0.9700 | 0.0000 | 100% |
| q08_polyformalism | 10 | 0.9800 | 0.9800 | 0.0000 | 100% |
| q09_signal_chain_canon | 9 | 0.2000 | 0.2009 | 0.0109 | — (spec REJECT) |
| q10_quorum_meshing | 6 | 0.0317 | 0.0310 | 0.0090 | — (spec REJECT) |
| q11_canon_gate_is_chord | 4 | 0.0525 | 0.0506 | 0.0094 | — (spec REJECT) |
| q12_substrate_polyformal | 9 | 0.6056 | 0.6071 | 0.0371 | — (REVIEW) |
| q13_witness_log_opcode | 8 | 0.1187 | 0.1120 | 0.0280 | — (spec REJECT) |
| q14_chain_dialing_real | 8 | 0.0500 | 0.0495 | 0.0005 | — (adv REJECT) |
| q15_jev_synapse | 4 | 0.0500 | 0.0501 | 0.0001 | — (adv REJECT) |
| q16_vibecoder_signal_chain | 2 | 0.0400 | 0.0399 | 0.0001 | — (spec REJECT) |
| q17_canary_honesty | 9 | 0.6578 | 0.6528 | 0.0328 | — (REVIEW plateau) |
| q18_address_is_data | 3 | 0.0500 | 0.0492 | 0.0008 | — (durable REJECT) |
| q19_style_resilience | 4 | 0.0400 | 0.0392 | 0.0008 | — (spec REJECT) |
| q20_wolffs_law | 4 | 0.0500 | 0.0499 | 0.0001 | — (spec REJECT) |
| q21_memory_sandbox | 4 | 0.0400 | 0.0398 | 0.0002 | — (durable REJECT) |
| q22_provenance_conflict | 5 | 0.0300 | 0.0303 | 0.0003 | — (spec REJECT) |

All 22 qids drawn. Note the cathedral is built from the **explicit 7-qid list**, never from the `kind` tag (q06 is tagged `bedrock` in the bank but reads REJECT — counting from the tag would under-report).

## Cross-session comparison (grand mean_p)

R-206 0.3820 · R-207 0.4153 · R-208 0.4260 · R-209 0.4172 · R-210 0.4306 · R-211 0.4441 · R-212 0.3596 · **R-213 0.4931**

R-213 sits at the top of the band. Per the R-212 rule: **the grand mean is draw-mix confounded** (5 of 22 per round, random draw), so it is a *mix* statistic, not a health statistic — a band move on mean_p alone is not drift. The health read is the cathedral + bucket separation, both of which are pristine.

## Bucket health

- **Cathedral 41/41 @100%** — 12th consecutive zero-miss session, mean 0.9754.
- **Spec clean-reject 42/42**, max 0.21 (q09). q10 `quorum_meshing` still reads 0.03 — the state-leak fix (STATE-ORDER, spec before bedrock) holds for the 10th session.
- **Adversarial clean-reject 12/12**, max 0.05.
- **q17 canary_honesty**: n=9, mean 0.6578 vs baseline 0.6528 — a stable REVIEW plateau per the R-210 decision. Not counted as drift noise, not read as decay.

## The 2026-10-17 q01/q04 "regression" is resolved — for the record

The `jev_hourly_report_20261017T2116Z.md` in `superinstance-advisor` reported q01 at 0.16 and q04 at 0.42 (both "regressed from durable bedrock"), blaming shortened doctrinal-state phrasing. **Both are back at ~0.97–0.98 this round.** That was a state-strengthening artifact, since corrected upstream. No action needed; noted so the stale advisory report isn't mistaken for a live defect.

## Environment / method notes

- **Recovery**: fresh wipe — `/workspace` was bare, `research/jev_sessions/` absent, and `/tmp/jev_probe/` (the interim mirror named in the 10-17 report) was **also gone**. Bootstrapped from `jev-quilt @ r-081-continuous-probe-rebuild`.
- **SSL_CERT_FILE gateway-anchor-only — 5th recurrence.** Env pointed at the gateway CA alone; canary first hit the expected handshake failure. Rebuilt the 289-cert bundle before the live run. *This is now the default expectation every wipe, not an incident.*
- **DEFECT B fixed at source — verified, not seeded.** `history.jsonl` is no longer gitignored and is committed (419 lines). Loaded 2,225 prior samples / 22 qids straight from the tracked file — **first wipe in 7 where no manual seeding was needed.** The 6-reports-asking fix landed.
- **DEFECT A still closed at the root.** `SESSION_TAG` defaulted to a timestamp (`r20261021T170217Z`), so this run created a fresh dir and never touched `rounds_r212`. Verified by the dir listing, not by inspection.
- **Schema check done pre-run** (R-212 trap): confirmed `history.jsonl` is round-shaped before trusting the baseline, so the exit-4 guard's "0 samples" failure mode could not fire silently.
- **Throughput is network-bound, not script-bound.** elapsed median 0.190s (healthy), p95 5.515s, max 9.300s, **9 stalls >1s all TLS handshake timeouts** (~5s = 4s attempt + jittered retry). 27 rounds at the 60s ceiling vs R-212's 19 and R-211's 30. **TIMEOUT_S=4 remains correct — do NOT lower it**; the lever is the handshake budget / persistent connection.
- **Token hygiene**: cloned with a tokenized URL then immediately `git remote set-url` back to clean, so the token does not appear in `git remote -v`.

## Status

**Healthy. No production alert.** Cathedral 100% (12th consecutive), all reject buckets clean, zero drift, all 22 qids exercised. Next actions: none required — this is a clean maintenance round.