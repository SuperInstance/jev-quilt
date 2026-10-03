# JEV Hourly Report — 2026-10-03T07:08:16Z (60th wipe)

**Round:** 1 round × 22 questions (canonical sweep `--rounds 1 --n 22`)
**Status:** ok / 0 fail in 0.2s
**mean_p:** 0.6068 (prev 59w 0.6073, 58w 0.6036, 57w 0.6055 — delta −0.0005 vs 59w)
**Cheap control:** ts `2026-10-03T07:08:16Z`, 2128 input / 502 output tokens (identical to 58w/59w).

## Verdicts (sorted)

| qid | p | band |
|---|---|---|
| q01_cells_are_scars | 0.97 | ### BEDROCK |
| q03_substrate_is_grown | 0.97 | ### BEDROCK |
| q04_oracle_is_heard | 0.96 | ### BEDROCK |
| q05_lenia_flows | 0.96 | ### BEDROCK |
| q07_eleven_opcodes | 0.95 | ### BEDROCK |
| q02_witness_log_is_prediction | 0.94 | ### BEDROCK |
| q08_polyformalism_12_ports | 0.88 | ### BEDROCK |
| q10_quorum_meshing | 0.85 | ### BEDROCK |
| q17_canary_honesty | 0.77 | ### BEDROCK |
| q13_chain_dialing | 0.60 | review |
| q09_signal_chain | 0.60 | review |
| q11_canon_gate_is_chord | 0.59 | review |
| q18_address_is_data | 0.58 | review |
| q12_witness_note_opcode | 0.55 | review |
| q20_wolffs_law | 0.55 | review |
| q22_provenance_conflict | 0.35 | speculative |
| q21_memory_sandbox | 0.28 | speculative |
| q19_pressure_cascade | 0.27 | speculative |
| q06_three_views | 0.23 | speculative |
| q16_canonicity_score | 0.23 | speculative |
| q15_twentyfour_ports | 0.20 | speculative |
| q14_canon_equals_speculation | 0.07 | speculative |

## Bedrock (p>=0.70) — canon-promoted

**9/22 questions hit bedrock this round.** Same set as 57w/58w/59w; no new promotions, no demotions.

- `q01_cells_are_scars`: 0.97
- `q02_witness_log_is_prediction`: 0.94
- `q03_substrate_is_grown`: 0.97
- `q04_oracle_is_heard`: 0.96
- `q05_lenia_flows`: 0.96
- `q07_eleven_opcodes`: 0.95
- `q08_polyformalism_12_ports`: 0.88
- `q10_quorum_meshing`: 0.85
- `q17_canary_honesty`: 0.77

All 7 durable bedrock (q01–q08 except q06) hold clean ≥0.88. **q10_quorum_meshing** dipped to 0.85
(was 0.86 last round). Still well inside its noise band (0.84–0.88 across recent wipes); not a
watch trigger. **q17_canary_honesty** at 0.77 — slight pullback from 0.79, but still above the
canary-as-bedrock threshold. The canary is doing its job: confirming JEV is reading the question's
claim, not its keywords.

## Drift vs 59th-wipe (|Δ|>0.05) — 0 alarms

- `q20_wolffs_law`: 0.59 → 0.55 (−0.04) — **largest mover**, but inside noise. This is the
  reversal of 59w's +0.06 jump; q20 settles back into its long-running 0.53–0.59 band.
- `q09_signal_chain`: 0.57 → 0.60 (+0.03)
- `q17_canary_honesty`: 0.79 → 0.77 (−0.02)
- `q22_provenance_conflict`: 0.33 → 0.35 (+0.02)

**No drift alarms** (|Δ| > 0.05). Largest absolute move is q20 at −0.04, which is inside its
established band. The 59w flag on q20 has cleared.

## 4-wipe cross-comparison

| qid | 57w | 58w | 59w | 60w | band |
|---|---|---|---|---|---|
| q01_cells_are_scars | 0.97 | 0.97 | 0.97 | 0.97 | bedrock (locked) |
| q02_witness_log_is_prediction | 0.93 | 0.94 | 0.94 | 0.94 | bedrock (locked) |
| q03_substrate_is_grown | 0.97 | 0.97 | 0.97 | 0.97 | bedrock (locked) |
| q04_oracle_is_heard | 0.96 | 0.96 | 0.96 | 0.96 | bedrock (locked) |
| q05_lenia_flows | 0.96 | 0.96 | 0.96 | 0.96 | bedrock (locked) |
| q07_eleven_opcodes | 0.95 | 0.95 | 0.95 | 0.95 | bedrock (locked) |
| q08_polyformalism_12_ports | 0.88 | 0.89 | 0.88 | 0.88 | bedrock (locked) |
| q10_quorum_meshing | 0.84 | 0.86 | 0.86 | 0.85 | bedrock (band 0.84–0.88) |
| q17_canary_honesty | 0.74 | 0.79 | 0.79 | 0.77 | bedrock (band 0.74–0.79) |
| q09_signal_chain | 0.60 | 0.59 | 0.57 | 0.60 | review (band 0.57–0.60) |
| q11_canon_gate_is_chord | 0.60 | 0.58 | 0.58 | 0.59 | review (band 0.58–0.60) |
| q12_witness_note_opcode | 0.58 | 0.56 | 0.56 | 0.55 | review (band 0.55–0.58) |
| q13_chain_dialing | 0.60 | 0.59 | 0.59 | 0.60 | review (band 0.59–0.60) |
| q18_address_is_data | 0.62 | 0.54 | 0.58 | 0.58 | review (band 0.54–0.62) |
| q20_wolffs_law | 0.53 | 0.56 | 0.59 | 0.55 | review (band 0.53–0.59) |
| q06_three_views | 0.22 | 0.22 | 0.23 | 0.23 | speculative (band 0.22–0.23) |
| q14_canon_equals_speculation | 0.07 | 0.06 | 0.07 | 0.07 | adversarial (locked ≤0.07) |
| q15_twentyfour_ports | 0.19 | 0.18 | 0.19 | 0.20 | adversarial (locked ≤0.20) |
| q16_canonicity_score | 0.22 | 0.21 | 0.22 | 0.23 | speculative (band 0.21–0.23) |
| q19_pressure_cascade | 0.27 | 0.26 | 0.28 | 0.27 | speculative (band 0.26–0.28) |
| q21_memory_sandbox | 0.29 | 0.29 | 0.29 | 0.28 | speculative (band 0.28–0.29) |
| q22_provenance_conflict | 0.33 | 0.35 | 0.33 | 0.35 | speculative (band 0.33–0.35) |

**Means 4-wipe band:** 0.6055 → 0.6036 → 0.6073 → **0.6068**. Band 0.6036–0.6073, span 0.0037.
Mean flat to ±0.005. No structural drift; the canon battery is in steady state.

## Speculative (<0.40)

**7/22 questions in the speculative band.** All inside long-running bands:
- `q06_three_views`: 0.23
- `q14_canon_equals_speculation`: 0.07
- `q15_twentyfour_ports`: 0.20
- `q16_canonicity_score`: 0.23
- `q19_pressure_cascade`: 0.27
- `q21_memory_sandbox`: 0.28
- `q22_provenance_conflict`: 0.35

Adversarial controls q14 (0.07) and q15 (0.20) hold clean — these are EXPECTED to fail canon
(they assert canon=canon and 24-port doctrines that the canon refutes). q14/q15 working as designed.

## Review band (0.40–0.69)

- `q13_chain_dialing`: 0.60
- `q09_signal_chain`: 0.60
- `q11_canon_gate_is_chord`: 0.59
- `q18_address_is_data`: 0.58
- `q12_witness_note_opcode`: 0.55
- `q20_wolffs_law`: 0.55

## Notes

- **Wipe counter:** 60th. NAS `/workspace/` 100% EDQUOT (silent-zero-byte trap active);
  all work in `/tmp/`. Recipe: stage to `/tmp/jev_probe_60w/`, copy to jev-quilt, push.
- **Defaults trap avoided:** probe ran with `--rounds 1 --n 22` (not bare), producing a single
  22-q sweep comparable to 57w/58w/59w.
- **Token economics unchanged:** 2128 input / 502 output. The doctrinal state + 22-question bank
  is stable across wipes — no drift in the prompt or the question count.
- **q20 cleared:** the 59w +0.06 flag on q20_wolffs_law has reversed cleanly (−0.04 this round).
  No real movement; inside band.
- **ts ordering anomaly noted:** the on-disk JSONs have 58w (06:04:14Z) AFTER 59w (04:03:01Z)
  chronologically. This is a recipe upload artifact, not a measurement anomaly — the 58w JSON
  content was amended during a re-push and the directory kept its 58w label. The verdicts and
  mean_p values are the actual measurements and are correctly compared round-to-round.

## Watch items

- **q10_quorum_meshing**: dropped 0.86 → 0.85. Inside band 0.84–0.88. Threshold still ≤0.80 next
  round = re-evaluate. No action.
- **q17_canary_honesty**: 0.77 (was 0.79). Still bounded 0.74–0.79 across 4 wipes. If next round
  ≥0.80 sustained, raise to "watch". Currently healthy-canary territory.
- **q20_wolffs_law**: settled back to 0.55. 59w flag cleared. No action.
- **q18_address_is_data**: stable at 0.58 across 3 wipes. Quiet but not re-evaluated.
- **q09_signal_chain**: slight uptick 0.57 → 0.60. Inside band. No action.
