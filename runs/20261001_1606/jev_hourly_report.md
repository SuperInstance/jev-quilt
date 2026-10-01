# JEV Hourly Report — 45th-wipe session (2026-10-01 16:06 UTC)

**Sandbox state**: 45th full wipe. `/workspace/` empty except `.plugin-cache/`. NAS 100% full (Avail=0, write quota-block). `/tmp` overlay tmpfs 28GB free. All LLM tokens survived.

**Bootstrap**: `GIT_SSL_NO_VERIFY=1 git clone https://x-access-token:${GITHUB_TOKEN}@github.com/SuperInstance/jev-quilt.git` → script intact (284 lines). 8th consecutive git-clone recovery. Push-back protocol is structural.

**Run (60s ceiling, 60 rounds, 0 fails)**: 60 successful rounds in **15.5s**, 0 fails. 300 verdicts (5/round × 60). Grand mean_p = **0.6014** (n=300). In-band with 38-44th-wipe trend 0.5020-0.6288.

---

## Bedrock canon (7 questions, all @ 100% hit-rate, 7th consecutive session 39-45th)

| qid | mean | n | hit_rate | kind |
|---|---|---|---|---|
| q01_cells_are_scars | 0.9692 | 12 | 100.0% | bedrock ✓ |
| q02_witness_log_is_prediction | 0.9360 | 15 | 100.0% | bedrock ✓ |
| q03_substrate_is_grown | 0.9700 | 14 | 100.0% | bedrock ✓ |
| q04_oracle_is_heard | 0.9600 | 15 | 100.0% | bedrock ✓ |
| q05_lenia_flows | 0.9573 | 15 | 100.0% | bedrock ✓ |
| q07_eleven_opcodes | 0.9494 | 18 | 100.0% | bedrock ✓ |
| q08_polyformalism_12_ports | 0.8771 | 7 | 100.0% | bedrock ✓ |

## Speculative clean-reject (5/5 ✓)
- q06_three_views (0.2227, n=15) | q09_signal_chain (0.6024, n=17) | q11_canon_gate_is_chord (0.5890, n=10) | q12_witness_note_opcode (0.5593, n=15) | q13_chain_dialing (0.6092, n=12)

## Adversarial clean-reject (2/2 ✓)
- q14_canon_equals_speculation (0.0656, n=18) | q15_twentyfour_ports (0.1915, n=13)

## Review band
- **q10_quorum_meshing (0.8573, n=11, 100%)** — sustained 8 sessions, bedrock-strength reading. Cross-wipe: 0.856/0.858/0.862/0.857 (this). Caveat: Sept 24 01:04 state-leak risk still standing — keep speculative_NOTBEDROCK marker even after promotion.
- **q17_canary_honesty (0.7547, n=17, 100%)** — sustained 8 sessions, recovered from 0.40 decay. Cross-wipe: 0.7595/0.7600/0.7638/0.7547 (this).
- q18_address_is_data (0.5830, n=10, 0%) | q16_canonicity_score (0.2223, n=13, 0%) | q19_pressure_cascade (0.2545, n=11, 0%) | q20_wolffs_law (0.5557, n=14, 0%) | q21_memory_sandbox (0.2915, n=13, 0%) | q22_provenance_conflict (0.3327, n=15, 0%)

## Drift vs 44th-wipe (no events > 0.05)
| qid | 44th | 45th (this) | Δ |
|---|---|---|---|
| q01 | 0.9700 | 0.9692 | -0.0008 |
| q02 | 0.9375 | 0.9360 | -0.0015 |
| q03 | 0.9700 | 0.9700 | +0.0000 |
| q04 | 0.9607 | 0.9600 | -0.0007 |
| q05 | 0.9567 | 0.9573 | +0.0006 |
| q07 | 0.9506 | 0.9494 | -0.0012 |
| q08 | 0.8800 | 0.8771 | -0.0029 |
| q10 | 0.8580 | 0.8573 | -0.0007 |
| q17 | 0.7638 | 0.7547 | -0.0091 |
| q18 | 0.5864 | 0.5830 | -0.0034 |
| q19 | 0.2600 | 0.2545 | -0.0055 |

**Max |Δ| = 0.0091 (q17)** — well under 0.05 threshold. JEV rock-stable.

## STATE-LEAK fix durable (7 wipes post-Sept 24)
- q18_address_is_data: cross-wipe 0.5830 (was 0.81 before fix; now <0.7) ✓
- q19_pressure_cascade: cross-wipe 0.2545 (was 0.94 before fix; now <0.7) ✓

## Cross-wipe grand mean_p trend (60-round samples)
| session | mean_p | n |
|---|---|---|
| 38th (09:06) | 0.6178 | 500 |
| 39th (10:03) | 0.6288 | 300 |
| 40th (11:05) | 0.6102 | 300 |
| 41st (12:02) | 0.5996 | 300 |
| 42nd (13:04) | 0.6203 | 300 |
| 43rd (14:04) | 0.5020 | 5 (1-round only) |
| 44th (15:04) | 0.6024 | 295 |
| **45th (16:06, this)** | **0.6014** | **300** |

## Action items
- PROMOTE q10 → bedrock canon list (8th consecutive session sustained).
- PROMOTE q17 → bedrock canon list (8th consecutive session sustained).
- 8th consecutive wipe as `git clone` not rebuild. Push-back protocol is structural.
- Carry over q18/q19 state-leak fix status (durable, 7 wipes post-fix).

## Files (durable mirror)
- `/tmp/jev_probe/jev_continuous_probe.py` (recovered from GitHub, 284 lines)
- `/tmp/jev_probe/jev_sessions/continuous_r001-r060.json` (60 rounds, 0 fails)
- `/tmp/jev_probe/jev_sessions/history.jsonl`
- `/tmp/jev_probe/jev_hourly_report.md` (this file)
- `/workspace/research/jev_hourly_report.md` — NAS quota-block at close, 0-byte stub
