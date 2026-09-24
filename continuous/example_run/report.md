# JEV Hourly Report — example_run

Rounds: 80 ok | Verdicts: 400 | Grand mean_p: **0.5896**

## Bedrock canon (7 questions)
| qid | mean | n | hit_rate | kind |
|---|---|---|---|---|
| q01_cells_are_scars | 0.9673 | 15 | 100.0% | bedrock ✓ |
| q02_witness_log_is_prediction | 0.9362 | 13 | 100.0% | bedrock ✓ |
| q03_substrate_is_grown | 0.9700 | 20 | 100.0% | bedrock ✓ |
| q04_oracle_is_heard | 0.9600 | 12 | 100.0% | bedrock ✓ |
| q05_lenia_flows | 0.9565 | 17 | 100.0% | bedrock ✓ |
| q07_eleven_opcodes | 0.9471 | 17 | 100.0% | bedrock ✓ |
| q08_polyformalism_12_ports | 0.8789 | 18 | 100.0% | bedrock ✓ |

## Speculative (must clean-reject)
| qid | mean | n | hit_rate | verdict |
|---|---|---|---|---|
| q06_three_views | 0.2231 | 26 | 0.0% | ✓ clean-reject |
| q09_signal_chain | 0.6075 | 20 | 0.0% | ✓ clean-reject |
| q11_canon_gate_is_chord | 0.5919 | 26 | 0.0% | ✓ clean-reject |
| q12_witness_note_opcode | 0.5522 | 9 | 0.0% | ✓ clean-reject |
| q13_chain_dialing | 0.6020 | 20 | 0.0% | ✓ clean-reject |

## Adversarial (must clean-reject)
| qid | mean | n | verdict |
|---|---|---|---|
| q14_canon_equals_speculation | 0.0635 | 17 | ✓ clean-reject |
| q15_twentyfour_ports | 0.1918 | 17 | ✓ clean-reject |

## Review band (borderline)
| qid | mean | n | hit_rate |
|---|---|---|---|
| q17_canary_honesty | 0.7591 | 22 | 100.0% |
| q10_quorum_meshing | 0.8586 | 22 | 100.0% |
| q18_address_is_data | 0.5921 | 14 | 0.0% |
| q16_canonicity_score | 0.2250 | 18 | 0.0% |
| q19_pressure_cascade | 0.2572 | 18 | 0.0% |
| q20_wolffs_law | 0.5528 | 18 | 0.0% |
| q21_memory_sandbox | 0.2867 | 18 | 0.0% |
| q22_provenance_conflict | 0.3352 | 23 | 0.0% |

## Summary
- Bedrock @ 100% hit-rate: **7 / 7**
- Speculative clean-reject: **5 / 5**
- Adversarial clean-reject: **2 / 2**
- Review band coherent: **3 / 8**
- Grand mean_p: **0.5896**
