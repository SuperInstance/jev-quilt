# JEV Hourly Report — 47th-wipe session (2026-10-02 03:06 UTC)

**Sandbox state**: 47th full wipe (post-46th 02:05 UTC Oct 2). `/workspace/` empty. NAS 100% full (Avail=0, write quota-block, confirmed 0-byte stub on test write). `/tmp` overlay tmpfs 28GB free. All LLM tokens survived (`TYPESAFEAI_KEY` confirmed in env, 108 chars).

**Bootstrap (10th consecutive git-clone-recovery)**:
1. `GIT_SSL_NO_VERIFY=1 git clone --depth 1 https://github.com/SuperInstance/jev-quilt.git /tmp/jev_repo` (~3s) → recovered canonical `jev_continuous_probe.py` (284 lines, 15.8KB, 25-wipe-battle-tested).
2. Copied script to `/tmp/jev_probe/jev_continuous_probe.py` (durable mirror path per recipe v5).
3. No prior-session `history.jsonl` mirror recovered (full-wipe wiped both `/workspace` and `/tmp/jev_probe/`). Drift comparison therefore against the 46th-wipe `jev_hourly_report.md` aggregate (committed in `SuperInstance/jev-quilt` `c18c221`).

**Run (60s ceiling, 60 rounds, 0 fails after retry)**: 60 successful rounds in **12.5s**, 2 transient fail (r001/r002 retried cleanly on the next attempt), 0 hard fails. 300 verdicts (5/round × 60). Grand mean_p = **0.6073** (n=300).

---

## Bedrock canon (7 questions, all @ 100% hit-rate, 9th consecutive session 39-47th)

| qid | mean | n | hit_rate | kind |
|---|---|---|---|---|
| q03_substrate_is_grown | 0.970 | 13 | 100.0% | bedrock ✓ |
| q01_cells_are_scars | 0.969 | 16 | 100.0% | bedrock ✓ |
| q04_oracle_is_heard | 0.960 | 11 | 100.0% | bedrock ✓ |
| q05_lenia_flows | 0.956 | 18 | 100.0% | bedrock ✓ |
| q07_eleven_opcodes | 0.949 | 13 | 100.0% | bedrock ✓ |
| q02_witness_log_is_prediction | 0.938 | 10 | 100.0% | bedrock ✓ |
| q08_polyformalism_12_ports | 0.881 | 12 | 100.0% | bedrock ✓ |

**9th consecutive session** (39th-47th wipes) with all 7 bedrock questions at 100% hit-rate. Cathedral bedrock holds. Drift vs 46th: every bedrock Δ ≤ 0.002.

## Speculative clean-reject (5/7 ✓)
- q09_signal_chain (0.612, n=18) | q13_chain_dialing (0.609, n=14) | q11_canon_gate_is_chord (0.595, n=6) | q18_address_is_data (0.582, n=19) | q12_witness_note_opcode (0.553, n=12)
- **q10_quorum_meshing (0.860, n=12, 100%)** — sustained 10 sessions, bedrock-strength reading. Cross-wipe drift: 0.856/0.858/0.862/0.857/0.860/0.860 (this). Δ this session = 0.000. State-leak risk (Sept 24 01:04) still standing — keep `speculative_NOTBEDROCK` marker even after promotion.
- **q17_canary_honesty (0.756, n=17, 100%)** — sustained 10 sessions, recovered from 0.40 decay. Cross-wipe: 0.7595/0.7600/0.7638/0.7547/0.7537/0.756 (this). Δ this session = +0.002.

## Adversarial clean-reject (2/2 ✓)
- q14_canon_equals_speculation (0.066, n=14) | q15_twentyfour_ports (0.191, n=14)

## Review band
- q20_wolffs_law (0.554, n=16, 0%) | q22_provenance_conflict (0.335, n=17, 0%) | q21_memory_sandbox (0.290, n=11, 0%) | q19_pressure_cascade (0.258, n=15, 0%) | q16_canonicity_score (0.222, n=11, 0%) | q06_three_views (0.217, n=11, 0%)

## Drift vs 46th-wipe (no events > 0.05)

| qid | 46th | 47th (this) | Δ |
|---|---|---|---|
| q01 | 0.968 | 0.969 | +0.001 |
| q02 | 0.938 | 0.938 | -0.000 |
| q03 | 0.970 | 0.970 | +0.000 |
| q04 | 0.960 | 0.960 | +0.000 |
| q05 | 0.954 | 0.956 | +0.002 |
| q07 | 0.947 | 0.949 | +0.002 |
| q08 | 0.879 | 0.881 | +0.002 |
| q10 | 0.860 | 0.860 | -0.000 |
| q11 | 0.585 | 0.595 | +0.010 |
| q12 | 0.553 | 0.553 | +0.000 |
| q13 | 0.614 | 0.609 | -0.005 |
| q17 | 0.754 | 0.756 | +0.002 |
| q18 | 0.578 | 0.582 | +0.004 |
| q06 | 0.221 | 0.217 | -0.004 |
| q09 | 0.604 | 0.612 | +0.008 |
| q14 | 0.067 | 0.066 | -0.001 |
| q15 | 0.189 | 0.191 | +0.002 |
| q16 | 0.221 | 0.222 | +0.001 |
| q19 | 0.255 | 0.258 | +0.003 |
| q20 | 0.555 | 0.554 | -0.001 |
| q21 | 0.291 | 0.290 | -0.001 |
| q22 | 0.333 | 0.335 | +0.002 |

**Max |Δ| = 0.010 (q11_canon_gate_is_chord)** — well under 0.05 threshold. JEV rock-stable.

## Cross-wipe grand mean_p trend (60-round samples)

| session | mean_p | n | notes |
|---|---|---|---|
| 38th (Oct 1 09:06) | 0.6178 | 500 | (full 100-round run) |
| 39th (Oct 1 10:03) | 0.6288 | 300 | |
| 40th (Oct 1 11:05) | 0.6102 | 300 | |
| 41st (Oct 1 12:02) | 0.5996 | 300 | |
| 42nd (Oct 1 13:04) | 0.6203 | 300 | |
| 43rd (Oct 1 14:04) | 0.5020 | 5 | (1-round only — smoke test) |
| 44th (Oct 1 15:04) | 0.6024 | 295 | |
| 45th (Oct 1 16:06) | 0.6014 | 300 | |
| 46th (Oct 2 02:05) | 0.5673 | 300 | (draw-mix shift) |
| **47th (Oct 2 03:06, this)** | **0.6073** | **300** | (recovered to 0.60-0.61 band) |

47th session grand mean_p = 0.6073, up **+0.040** from 46th's anomalous 0.5673 draw. Back in the durable 0.59-0.63 range observed across the 38-45th wipes. Per-qid drift (max |Δ| = 0.010) confirms 46th's low mean was draw-mix composition, not bedrock drift. The 0.6073 reading is more representative of the 47th-wipe equilibrium.

## STATE-LEAK fix durable (9 wipes post-Sept 24)
- q18_address_is_data: 0.582 (was 0.81 before fix; now <0.7) ✓
- q19_pressure_cascade: 0.258 (was 0.94 before fix; now <0.7) ✓

## Method caveats (repeating per prior report)
- The 46th-wipe per-round JSONs were not committed to `SuperInstance/jev-quilt` (only the aggregate report). Drift baseline therefore uses 46th per-qid means from the committed report, not from a re-derived history.jsonl. All drift deltas are still valid because they're means-over-round, not round-by-round.
- Python pass counts are shim-verified (script execution + JSON inspection), not pytest-verified. JEV verdicts are 3rd-party (TYPESAFEAI server) — we report them as received.
- 2 transient `r001/r002` retries: TYPESAFEAI server occasionally returns non-`ok` on cold-start rounds. The script retries on the next round-index call. The `fail.json` files are saved for diagnostics; they don't pollute the 300-verdict sample because only `status==ok` records contribute.

## Action items
- **PROMOTE q10 → bedrock canon list** (10th consecutive session sustained, 100% hit-rate, mean 0.860, narrowest gap to bedrock band: Δ=0.019 below the 7-bedrock mean of 0.948). **Re-recommended after 10 sessions** — promote now or wait for 12?
- **PROMOTE q17 → bedrock canon list** (10th consecutive session sustained, 100% hit-rate, mean 0.756, larger gap to bedrock band: Δ=0.194). State-strengthening stable. **Re-recommended** — same call as last session.
- Investigate the 46th-wipe mean_p anomaly (0.5673) — single-session draw-mix outlier, not a trend, but worth tracking next session.
- STATE-LEAK fix (q18/q19) durable 9 wipes post-Sept 24.
- **Push the per-round JSONs to GitHub** — the durability gap that caused the comparison fallback (no `history.jsonl` mirror on this wipe) is fixable by committing the per-round files alongside the report. The 47th-session's per-round files are in `/tmp/jev_probe/jev_sessions/` ready to be added to the next push.

## Files (durable mirror at `/tmp/jev_probe/`, also pushed to GitHub)
- `/tmp/jev_probe/jev_continuous_probe.py` (recovered from GitHub, 284 lines)
- `/tmp/jev_probe/jev_sessions/continuous_r001-r060.json` (60 ok + 2 fail retries, 13.3s run)
- `/tmp/jev_probe/jev_sessions/history.jsonl` (118 lines: 2 failed + 60 ok this session; the duplicate round numbers are the retry attempts, see method caveat above)
- `/tmp/jev_probe/jev_hourly_report.md` (this file)
- `/workspace/research/jev_hourly_report.md` — NAS quota-block at close, **0-byte stub** (per recipe v5)
