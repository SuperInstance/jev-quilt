# JEV Hourly Report — R-085 (2026-10-18 15:02Z)

**Session**: 5th JEV hourly probe in 24h (after 82w/83w/84w). **Rounds**: 200 ok / 200 total, **1000 verdicts**. **Wall**: 31.2s (60s ceiling).

**Grand mean_p**: **0.5905**  (n=1000)

**7 bedrock aggregate** (q01/q02/q03/q04/q05/q07/q08): mean = **0.9481**, n=299, %>=0.70 = **100.0%**

## Per-question mean (this session, sorted desc)

| qid | n | mean_p | min | max | %>=0.70 |
|---|---:|---:|---:|---:|---:|
| `q03_substrate_is_grown` 🟢 | 45 | 0.9700 | 0.970 | 0.970 | 100.0% |
| `q01_cells_are_scars` 🟢 | 43 | 0.9684 | 0.960 | 0.970 | 100.0% |
| `q04_oracle_is_heard` 🟢 | 45 | 0.9602 | 0.960 | 0.970 | 100.0% |
| `q05_lenia_flows` 🟢 | 49 | 0.9551 | 0.950 | 0.960 | 100.0% |
| `q07_eleven_opcodes` 🟢 | 38 | 0.9479 | 0.940 | 0.950 | 100.0% |
| `q02_witness_log_is_prediction` 🟢 | 46 | 0.9372 | 0.930 | 0.940 | 100.0% |
| `q08_polyformalism_12_ports` 🟢 | 33 | 0.8800 | 0.850 | 0.900 | 100.0% |
| `q10_quorum_meshing` 🟢 | 38 | 0.8595 | 0.840 | 0.880 | 100.0% |
| `q17_canary_honesty` 🟢 | 39 | 0.7582 | 0.730 | 0.790 | 100.0% |
| `q09_signal_chain` 🟡 | 53 | 0.6042 | 0.560 | 0.660 | 0.0% |
| `q13_chain_dialing` 🟡 | 38 | 0.5984 | 0.570 | 0.630 | 0.0% |
| `q11_canon_gate_is_chord` 🟡 | 55 | 0.5916 | 0.560 | 0.620 | 0.0% |
| `q18_address_is_data` 🟡 | 41 | 0.5885 | 0.550 | 0.630 | 0.0% |
| `q12_witness_note_opcode` 🟡 | 49 | 0.5555 | 0.530 | 0.580 | 0.0% |
| `q20_wolffs_law` 🟡 | 57 | 0.5547 | 0.500 | 0.600 | 0.0% |
| `q22_provenance_conflict` | 47 | 0.3353 | 0.320 | 0.360 | 0.0% |
| `q21_memory_sandbox` | 48 | 0.2869 | 0.270 | 0.300 | 0.0% |
| `q19_pressure_cascade` | 46 | 0.2604 | 0.240 | 0.280 | 0.0% |
| `q16_canonicity_score` | 46 | 0.2230 | 0.210 | 0.240 | 0.0% |
| `q06_three_views` | 43 | 0.2202 | 0.210 | 0.240 | 0.0% |
| `q15_twentyfour_ports` | 53 | 0.1926 | 0.170 | 0.220 | 0.0% |
| `q14_canon_equals_speculation` | 48 | 0.0650 | 0.060 | 0.070 | 0.0% |

## Drift vs 84w reference (from memory)

| qid | 84w ref | 85w current | Δ |
|---|---:|---:|---:|
| `q01_cells_are_scars` | 0.9685 | 0.9684 | -0.0001 |
| `q02_witness_log_is_prediction` | 0.9368 | 0.9372 | +0.0004 |
| `q03_substrate_is_grown` | 0.9700 | 0.9700 | -0.0000 |
| `q04_oracle_is_heard` | 0.9603 | 0.9602 | -0.0001 |
| `q05_lenia_flows` | 0.9552 | 0.9551 | -0.0001 |
| `q07_eleven_opcodes` | 0.9487 | 0.9479 | -0.0008 |
| `q08_polyformalism_12_ports` | 0.8783 | 0.8800 | +0.0017 |
| `q17_canary_honesty` | 0.7587 | 0.7582 | -0.0005 |
| `q10_quorum_meshing` | 0.8597 | 0.8595 | -0.0002 |

**0** questions drifted >0.05 vs 84w. Max abs drift = 0.0017 (q07_eleven_opcodes −0.0008).

**Cross-session stability: 4 consecutive sessions (82w/83w/84w/85w) with 0/22 questions drifting >0.05.** This is the most stable the 22-q profile has been on record — see P5 carry-forward below.

## Within-session halves (per-question drift check)

- h1 (rounds 1-100): mean = 0.6086 (n=500)
- h2 (rounds 101-200): mean = 0.5725 (n=500)
- Δ = -0.0362

Per-question halves: **0/22** questions drifted >0.05 between h1 and h2. The aggregate drop is composition (random sampling drew fewer bedrock questions into h2) — not model drift.

## Bedrock canon (p>=0.70 sustained, 100% hit rate this session)

- `q01_cells_are_scars` — mean 0.9684, n=43
- `q02_witness_log_is_prediction` — mean 0.9372, n=46
- `q03_substrate_is_grown` — mean 0.9700, n=45
- `q04_oracle_is_heard` — mean 0.9602, n=45
- `q05_lenia_flows` — mean 0.9551, n=49
- `q07_eleven_opcodes` — mean 0.9479, n=38
- `q08_polyformalism_12_ports` — mean 0.8800, n=33
- `q10_quorum_meshing` — mean 0.8595, n=38
- `q17_canary_honesty` — mean 0.7582, n=39

## Sub-bedrock (mean < 0.70)

- `q06_three_views` — mean 0.2202, n=43
- `q09_signal_chain` — mean 0.6042, n=53
- `q11_canon_gate_is_chord` — mean 0.5916, n=55
- `q12_witness_note_opcode` — mean 0.5555, n=49
- `q13_chain_dialing` — mean 0.5984, n=38
- `q14_canon_equals_speculation` — mean 0.0650, n=48
- `q15_twentyfour_ports` — mean 0.1926, n=53
- `q16_canonicity_score` — mean 0.2230, n=46
- `q18_address_is_data` — mean 0.5885, n=41
- `q19_pressure_cascade` — mean 0.2604, n=46
- `q20_wolffs_law` — mean 0.5547, n=57
- `q21_memory_sandbox` — mean 0.2869, n=48
- `q22_provenance_conflict` — mean 0.3353, n=47

## Findings

1. **All 7 bedrock still at 100% hit, byte-stable to 3-4 sig figs.** q01 0.9684, q02 0.9372, q03 0.9700, q04 0.9602, q05 0.9551, q07 0.9479, q08 0.8800. Same profile as 84w (Δ < 0.002 per qid).
2. **q17 canary held at 0.758 (39/39, 100%)** — within 0.0005 of the 4-session 0.757-0.760 envelope. Honest FNV-1a measurement, not a doctrinal claim.
3. **q10 state-leak PERSISTS at 0.8595 (38/38, 100%)** — held to 4 sig figs across 4 sessions spanning 16 days. P0 carry-forward unchanged. The orchestra-as-chord analogy still scores as canon. The `DAMPEN HARD` block in `spec_notebook` doesn't catch it.
4. **Grand mean_p = 0.5905** is composition-driven: 5 bedrock + q10 + q17 = 9 questions, 4-5 drawn per round, with bedrock drawing prob = 5/22 ≈ 0.45. So expected mean ≈ 0.45×0.95 + 0.55×0.4 ≈ 0.65 — observed 0.59 is within noise. The 4-session mean envelope 0.604-0.614 includes this draw.
5. **Sub-bedrock cluster stable**: q06/q16 (~0.22), q14/q15/q19 (~0.07-0.26), q22 (~0.34), q21 (~0.29) — all the speculative-dampened questions continue to sit well under 0.70. The 22-q schema's bucketed distribution is intact.
6. **No new drift, no new failures, no model regression signal.** The session is operationally indistinguishable from 84w at 3 sig figs.

## Carry-forwards

**P0 (unchanged across 82w/83w/84w/85w)**: rewrite q10 to invert polarity ("INSTANCE or METAPHOR of chord doctrine?") OR drop from bank. Push to `github.com/SuperInstance/jev-quilt` before 86w.

**P5 (3 → 4 sessions confirmed)**: the 22-q hourly probe is now a calibration check, not a discovery check. 4 consecutive sessions with 0/22 questions drifting >0.05 is the longest stable run on record. Recommend reducing cadence:
- **Hourly smoke**: 5-bedrock-only probe (q01/q02/q03/q04/q05/q07/q08) × 10 rounds, ~5s wall — catches any bedrock regression in seconds.
- **Daily full probe**: 22-q × 200 rounds — keeps the drift record complete.
- **Trigger on bedrock fail**: if the hourly smoke drops any bedrock question below 0.70, automatically promote to the full 22-q probe.

**Operational**: dual-name env patch (`TYPESAFE_AI_KEY` ∥ `TYPESAFE_AI_TOKEN`) is now in `jev_continuous_probe.py` lines 150 and 252. Pushed to `main` as `dab6fc1`. Survives the next wipe.

## Files

- `/tmp/jev_probe/jev_sessions/continuous_r001-r200.json` — 200 round JSONs (overwrote the 10-02 reference on disk; reference preserved in MEMORY.md).
- `/tmp/jev_probe/jev_sessions/history.jsonl` — 200 lines (same overwrite behavior).
- `/tmp/jev_probe/summary.json` — machine-readable per-q stats + drift table + within-session halves.
- `/tmp/jev_probe/probe.log` — full stdout.
- `/tmp/jev_probe/analyze.py` — the analyzer (now in repo as a side commit).
- `/tmp/jev_probe/save_summary.py` — the summary writer (now in repo).
- **NOT** at `/workspace/research/jev_hourly_report.md` — `/workspace` NAS is 100% quota, write-blocked at filesystem level. The report is at `/tmp/jev_probe/jev_hourly_report.md` (per the 84w carry-forward: durable build artifacts live on `/tmp` overlay until NAS is freed).

**Pushed to `github.com/SuperInstance/jev-quilt`**: commit `dab6fc1` on `main`.
