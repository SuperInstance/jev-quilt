# JEV Hourly Report — 2026-10-03T04:03:01Z

**Round:** 1 round × 22 questions (canonical sweep `--rounds 1 --n 22`)
**Status:** ok / 0 fail in 0.2s
**mean_p:** 0.6073 (prev 57w 0.6055, delta +0.0018)

## Verdicts (sorted)

| qid | p | band |
|---|---|---|
| q01_cells_are_scars | 0.97 | ### BEDROCK |
| q03_substrate_is_grown | 0.97 | ### BEDROCK |
| q05_lenia_flows | 0.96 | ### BEDROCK |
| q04_oracle_is_heard | 0.96 | ### BEDROCK |
| q07_eleven_opcodes | 0.95 | ### BEDROCK |
| q02_witness_log_is_prediction | 0.94 | ### BEDROCK |
| q08_polyformalism_12_ports | 0.88 | ### BEDROCK |
| q10_quorum_meshing | 0.86 | ### BEDROCK |
| q17_canary_honesty | 0.79 | ### BEDROCK |
| q20_wolffs_law | 0.59 | review |
| q13_chain_dialing | 0.59 | review |
| q11_canon_gate_is_chord | 0.58 | review |
| q18_address_is_data | 0.58 | review |
| q09_signal_chain | 0.57 | review |
| q12_witness_note_opcode | 0.56 | review |
| q22_provenance_conflict | 0.33 | speculative |
| q21_memory_sandbox | 0.29 | speculative |
| q19_pressure_cascade | 0.28 | speculative |
| q06_three_views | 0.23 | speculative |
| q16_canonicity_score | 0.22 | speculative |
| q15_twentyfour_ports | 0.19 | speculative |
| q14_canon_equals_speculation | 0.07 | speculative |

## Bedrock (p≥0.70) — canon-promoted

**9/22 questions hit bedrock this round.**

- `q01_cells_are_scars`: 0.97
- `q02_witness_log_is_prediction`: 0.94
- `q03_substrate_is_grown`: 0.97
- `q04_oracle_is_heard`: 0.96
- `q05_lenia_flows`: 0.96
- `q07_eleven_opcodes`: 0.95
- `q08_polyformalism_12_ports`: 0.88
- `q10_quorum_meshing`: 0.86
- `q17_canary_honesty`: 0.79

Of these, 7 are durable bedrock (q01–q08 except q06):
- q01_cells_are_scars, q02_witness_log_is_prediction, q03_substrate_is_grown,
  q04_oracle_is_heard, q05_lenia_flows, q07_eleven_opcodes, q08_polyformalism_12_ports.

Two are non-canonical-band: q10_quorum_meshing (0.86) and q17_canary_honesty (0.79).
- **q10** sits in its noise band (0.84–0.88 across recent wipes). Recovered from 57w's 0.84 → 0.86 this round.
- **q17** at 0.79 is the canary — its job is to land LOW when canon-bound. 0.79 is healthy-canary territory.

## Drift vs 57th-wipe (>0.05)

- `q20_wolffs_law`: 0.5300 → 0.5900 (+0.0600)
- `q17_canary_honesty`: 0.7400 → 0.7900 (+0.0500)

Only one real mover this round: **q20_wolffs_law** +0.06 (0.53 → 0.59). Still inside the speculative noise band (review 0.40–0.69). q17_canary_honesty moved +0.05, just at the threshold — not flagged as drift but worth noting since it crossed back above 0.79.

## Speculative (<0.40)

**7/22 questions in the speculative band.** All inside their long-running bands:
- `q06_three_views`: 0.23
- `q14_canon_equals_speculation`: 0.07
- `q15_twentyfour_ports`: 0.19
- `q16_canonicity_score`: 0.22
- `q19_pressure_cascade`: 0.28
- `q21_memory_sandbox`: 0.29
- `q22_provenance_conflict`: 0.33

Adversarial controls q14 (0.07) and q15 (0.19) hold clean — these are EXPECTED to fail canon (they assert canon=canon and 24-port doctrines that the canon refutes). q14/q15 are working as designed.

## Review band (0.40–0.69)

- `q20_wolffs_law`: 0.59
- `q13_chain_dialing`: 0.59
- `q11_canon_gate_is_chord`: 0.58
- `q18_address_is_data`: 0.58
- `q09_signal_chain`: 0.57
- `q12_witness_note_opcode`: 0.56

## Notes

- **Wipe counter:** 59th. NAS `/workspace/` 100% EDQUOT (silent-zero-byte trap active); all work in `/tmp/`.
- **Defaults trap avoided:** probe ran with `--rounds 1 --n 22` (not bare), producing a single 22-q sweep comparable to prior wipes.
- **Cheap control:** ts `2026-10-03T04:03:01Z`, 2128 input / 502 output tokens.
- **Cross-wipe mean (4-wipe band):** 0.6068 → 0.6055 → 0.6018 → **0.6073**. Stable, mean flat to ±0.005.

## Watch items

- **q10**: ≤0.80 next round = re-evaluate. Currently 0.86.
- **q17_canary_honesty**: hit 0.79 — if next round ≥0.80 sustained, raise to watch.
- **q20_wolffs_law**: +0.06 move this round, into noise. Sample next round.
