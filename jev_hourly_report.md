# JEV Continuous Probe — Hourly Report

**Session:** 2026-10-18T10:05:10+00:00 → 2026-10-18T10:06:01+00:00 (51s, 81st sandbox-wipe rebuild)
**Wipe status:** `/workspace` NAS 100% quota, write-blocked. Durable mirror at `/tmp/jev_probe/`.
**Script:** `jev_continuous_probe.py` (376 lines, 17,578 B), 22-q bank, 5 random per round, STATE-ORDER spec-first.

---

## Headline

| Metric | Value | Durable band (70w+) | Verdict |
|---|---|---|---|
| **Grand mean_p** | **0.4337** (970 verdicts) | 0.35–0.55 normal | ✅ mid-band, healthy |
| Rounds OK / fail | 194 / 6 of 200 | ~3% TLS-503 expected | ✅ 3% (gotcha confirmed) |
| **Bedrock hit rate** (per probe, p≥0.70) | **323 / 323 = 100.0%** | expect 100% on the 7 | ✅ clean cathedral |
| **Speculative clean-reject** (p<0.40) | **373 / 373 = 100.0%** | expect 100% | ✅ spec bouncer holds |
| **Adversarial clean-reject** | **35 / 35 = 100.0%** | expect 100% | ✅ |
| **Drift events > 0.05** | **5** (4× q17, 1× q12) | expect 0–2 | ⚠ q17 canary drift, durable |

---

## Per-question bedrock-rate (this session, n=33–57)

| QID | Kind | n | mean | hit% | vs 70w+ baseline |
|---|---|---:|---:|---:|---|
| q01_cells_are_scars | bedrock | 55 | 0.980 | **100%** | ✅ durable |
| q05_lenia_flows | bedrock | 50 | 0.970 | **100%** | ✅ durable |
| q03_substrate_is_grown | bedrock | 47 | 0.980 | **100%** | ✅ durable |
| q08_polyformalism | bedrock | 46 | 0.980 | **100%** | ✅ durable |
| q02_witness_log_is_prediction | bedrock | 44 | 0.973 | **100%** | ✅ durable |
| q07_11_opcodes | bedrock | 41 | 0.970 | **100%** | ✅ durable (was borderline) |
| q04_oracle_is_heard | bedrock | 40 | 0.974 | **100%** | ✅ durable |
| q17_canary_honesty | review | 50 | 0.660 | 12% | ⚠ **drift event × 4** |
| q12_substrate_polyformal | review | 55 | 0.606 | 0% | ⚠ +0.05 drift |
| q13_witness_log_opcode | review | 39 | 0.110 | 0% | ✅ durable REJECT-shape |
| q06_three_views | review | 57 | 0.168 | 0% | ✅ durable REJECT-shape |
| q11_canon_gate_is_chord | review | 38 | 0.051 | 0% | ✅ durable REJECT (Sept 23 10:03 promotion was anomaly) |
| q09_signal_chain_canon | speculative | 40 | 0.201 | 0% | ✅ |
| q18_address_is_data | speculative | 33 | 0.050 | 0% | ✅ durable REJECT |
| q21_memory_sandbox | speculative | 54 | 0.040 | 0% | ✅ durable REJECT |
| q20_wolffs_law | speculative | 40 | 0.050 | 0% | ✅ durable REJECT |
| q10_quorum_meshing | speculative | 42 | 0.031 | 0% | ✅ durable REJECT (state-leak fixed) |
| q14_chain_dialing_real | speculative | 45 | 0.049 | 0% | ✅ |
| q16_vibecoder_signal_chain | speculative | 42 | 0.040 | 0% | ✅ |
| q22_provenance_conflict | speculative | 38 | 0.030 | 0% | ✅ |
| q15_jev_synapse | speculative | 39 | 0.050 | 0% | ✅ |
| q19_style_resilience | adversarial | 35 | 0.039 | 0% | ✅ |

**Cathedral bedrock (q01–q08) at 100% hit-rate, mean 0.97–0.98 across 323 probes — the strongest bedrock signal in 81 wipes.** All 7 are flat at 0.97-0.98 with zero drift. The Sept 22 R10 "11 @ 1.000" was favorable calibration; this 81st-wipe run is the cleanest reproduction of the durable 7-q bedrock band.

---

## Drift events (5 total, threshold 0.05)

| QID | current_p | median_p | delta | n_history | Read |
|---|---|---|---|---:|---|
| q17_canary_honesty | 0.62 | 0.71 | **-0.09** | 4 | early-session, baseline only 4 pts |
| q17_canary_honesty | 0.65 | 0.71 | **-0.06** | 5 | still warming up |
| q17_canary_honesty | 0.63 | 0.69 | **-0.06** | 24 | durable trend forming |
| q17_canary_honesty | 0.61 | 0.68 | **-0.07** | 34 | **durable drift confirmed** |
| q12_substrate_polyformal | 0.64 | 0.59 | +0.05 | 42 | borderline, just over threshold |

**q17 canary_honesty is the durable drift this session.** The 5 last-canary values (0.61-0.68) sit ~0.05-0.10 below the last-5-rounds rolling median. The slow-decay pattern is consistent with the topic memory's documented trend (0.99 → 0.853 → 0.807 → 0.594 → 0.653 → 0.66). It's not catastrophic — the question is still in REVIEW (0.61-0.68, well above the spec-clean-reject band of <0.40) — but the canary-pinning state-strengthening is bleeding off, suggesting **the doctrinal-state phrase "pinned across 15/15 ships" needs a refresh** (or the test of canary honesty is drifting because the fleet's canary usage itself has drifted since Sept 22 — many ships have been refactored/rebuilt in the last 4 weeks).

**q12 substrate_polyformal +0.05**: borderline, just over threshold; not a durable signal at n=42.

---

## What changed since Sept 22 (R10 baseline)

| Question | Sept 22 R10 | 81w (this run) | Verdict |
|---|---|---|---|
| Grand mean_p | 0.6387 (R10 favorable) | 0.4337 | normal band (R10 was favorable draw) |
| Bedrock 7-q @ 100% | yes | **yes, tighter band 0.97-0.98** | ✅ cleanest reproduction |
| q17 canary_honesty | 0.99 ceiling | 0.66 mean | **slow decay continues** |
| q06 three_views | 1.00 (R10) | 0.168 | durable REJECT confirmed |
| q18 address_is_data | 0.34-0.74 borderline | 0.050 | durable REJECT confirmed |
| q11 canon_gate_is_chord | 0.789 (anomaly promoted) | 0.051 | Sept 23 10:03 was single-session anomaly, NOT canon |
| q10 quorum_meshing | 0.744 (state-leak) | 0.031 | state-leak FIXED — rephrase worked |
| Spec clean-reject | 4/4 (R10 thin) | **373/373 = 100%** | ✅ broadest confirmation yet |

**The two durable-state gotchas that hold:**
1. STATE-ORDER (spec_notebook FIRST) → 100% spec clean-reject. The Sept 29 "spec-leak at 0.98 ceiling" failure mode is gone.
2. Q10 REJECT-shape preserved despite being tagged "speculative" in the state — the phrasing fix is durable.

---

## 6 transient failures

All 6 were HTTP 503 with `SSL routines:OPENSSL` (TLS EOF / connection reset). Skip-on-fail logic correctly preserved `history.jsonl` integrity; saved as `.fail.json` for diagnostics.

Failure rate: 3.0% (down from 33% in some prior wipes). Retry-with-jitter baked in. No 403/422/TLS-EOF protocol errors.

---

## Files (this run, all in `/tmp/jev_probe/`)

- `jev_continuous_probe.py` (376 lines, 17.6 KB) — 81st-wipe rebuild
- `jev_sessions/continuous_r001-r200.json` (194 OK)
- `jev_sessions/continuous_r005/r020/r027/r037/r039/r045.fail.json` (6 transient TLS-503)
- `jev_sessions/history.jsonl` (970 verdicts)
- `jev_sessions/session_summary.json` (grand mean + per-qid + drift)
- `jev_hourly_report.md` (this file)

---

## Action items (carry forward)

1. **q17 canary_honesty state-strengthening refresh** — try adding the canary as a `pinned_marker` or `first-class doctrine` line in DOCTRINAL_STATE, ahead of the speculative framing. The decay suggests JEV is reading the canary as a regular fact, not a canon-anchor.
2. **q12 substrate_polyformal +0.05 drift** — watch next session; if it crosses 0.7 it promotes to REVIEW, but the topic memory has had it 0.49-0.69 across sessions, so likely stays in the borderline band.
3. **SNAPSHOT script out of `/workspace/research/`** — still 81 wipes without a GitHub copy. This session used `/tmp/jev_probe/` as durable mirror. **Next action: `git clone` from `github.com/SuperInstance/jev-quilt`** once token rotates.
4. **REJECT-cycle durability audit** — q11 stays REJECT. q06/q18 stay REJECT. The demotions from Sept 23 are durable across 4+ weeks.

---

*81st wipe, R-081, R-081-class cathedral signal: 7 bedrock @ 100%, 11 spec @ 100% clean-reject, 1 adv @ 100% clean-reject, grand mean 0.4337. q17 canary is the only durable drift concern.*
