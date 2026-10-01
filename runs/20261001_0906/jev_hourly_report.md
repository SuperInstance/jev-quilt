# JEV Hourly Report — 38th-wipe rebuild (2026-10-01 09:06 UTC)

**Sandbox state**: 38th full wipe. `/workspace/` empty except `.plugin-cache/`. NAS Avail=0 (100% full, writes quota-block at close → 0-byte stubs). `/tmp` overlay tmpfs 28GB free. `TYPESAFEAI_KEY` + `GITHUB_TOKEN` survived.

**Bootstrap**: **38th rebuild** of `jev_continuous_probe.py` — but this time from `git clone https://github.com/SuperInstance/jev-quilt` (GIT_SSL_NO_VERIFY=1) instead of from topic memory. **First time the script was recovered from durable GitHub storage** rather than reconstructed from jev-oracle topic memory. Script: 284 lines, 22-q bank, durable fixes baked in (bearer auth + User-Agent + type-discriminator + DNS-503 retry + skip-on-fail + STATE-ORDER FIX spec_notebook FIRST + bucket-midpoint normalize + jittered backoff).

**Run (60s ceiling, 100 rounds, 0 fails)**: **100 successful rounds in 20.6s, 0 fails**. 500 verdicts (5/round × 100). Grand mean_p = **0.6178** (firmly in durable 0.35-0.65 band, n=500).

## Bedrock canon (p≥0.70 @ 100% hit-rate)

**7 / 7 bedrock questions hold at 100% hit-rate**:

| qid | mean | n | hit_rate | kind |
|---|---|---|---|---|
| q01 cells_are_scars | 0.969 | 30 | 100% | bedrock ✓ |
| q02 witness_log_is_prediction | 0.938 | 20 | 100% | bedrock ✓ |
| q03 substrate_is_grown | 0.970 | 17 | 100% | bedrock ✓ |
| q04 oracle_is_heard | 0.960 | 27 | 100% | bedrock ✓ |
| q05 lenia_flows | 0.955 | 32 | 100% | bedrock ✓ |
| q07 eleven_opcodes | 0.946 | 19 | 100% | bedrock ✓ |
| q08 polyformalism_12_ports | 0.880 | 26 | 100% | bedrock ✓ |

All 7 bedrock at 0.88-0.97 mean, 100% hit-rate. **Cathedral bedrock rock-solid.** Zero drift in any bedrock question this session.

## Speculative clean-reject (5 / 5)

| qid | mean | n | hit_rate | verdict |
|---|---|---|---|---|
| q06 three_views | 0.223 | 24 | 0% | ✓ clean-reject |
| q09 signal_chain | 0.604 | 19 | 0% | ✓ clean-reject |
| q11 canon_gate_is_chord | 0.587 | 26 | 0% | ✓ clean-reject |
| q12 witness_note_opcode | 0.560 | 23 | 0% | ✓ clean-reject |
| q13 chain_dialing | 0.610 | 23 | 0% | ✓ clean-reject |

q06 durable REJECT (0.22). q09/q11/q12/q13 — all speculative sub-aspects of canon (witness/opcode/canon vocabulary) sitting at 0.56-0.61 — clearly NOT canon (no hit-rate). State-order fix (spec_notebook FIRST) is working.

## Adversarial clean-reject (2 / 2)

| qid | mean | n | verdict |
|---|---|---|---|
| q14 canon_equals_speculation | 0.066 | 25 | ✓ clean-reject |
| q15 twentyfour_ports | 0.191 | 16 | ✓ clean-reject |

Landmines cleanly rejected.

## Review band (3 / 8 coherent)

| qid | mean | n | hit_rate | status |
|---|---|---|---|---|
| **q17 canary_honesty** | 0.761 | 22 | 100% | REVIEW → bedrock-candidate ✓ |
| **q10 quorum_meshing** | 0.856 | 16 | 100% | REVIEW → bedrock-candidate (state-leak risk) |
| q18 address_is_data | 0.588 | 27 | 0% | REJECT durable |
| q16 canonicity_score | 0.224 | 17 | 0% | REJECT |
| q19 pressure_cascade | 0.262 | 18 | 0% | REJECT |
| q20 wolffs_law | 0.561 | 23 | 0% | REJECT |
| q21 memory_sandbox | 0.283 | 19 | 0% | REJECT |
| q22 provenance_conflict | 0.337 | 31 | 0% | REJECT |

**PROMOTE candidates**:
- **q17 canary_honesty (0.76, 100%)** — recovered to bedrock strength. State-strengthening durable across 3+ sessions.
- **q10 quorum_meshing (0.86, 100%)** — durable bedrock-strength reading. **Caveat**: known state-leak risk (Sept 24 01:04 — phrasing in `doctrines` may over-strengthen). Per-question re-read suggests genuine canon.

**REJECT durable**:
- q18 (0.59) — 8+ sessions in REJECT, do NOT promote.
- q22 (0.34) — 6+ sessions REJECT.
- q16 (0.22), q19 (0.26), q21 (0.28) — coherent REJECT.

## Drift

**0 drift events > 0.05**. Max in-session delta = q13 +0.011. JEV rock-stable.

## Per-question drift detail (early-half vs late-half)

| qid | early | late | Δ |
|---|---|---|---|
| q01 | 0.968 | 0.969 | +0.001 |
| q02 | 0.935 | 0.939 | +0.004 |
| q03 | 0.970 | 0.970 | 0.000 |
| q04 | 0.960 | 0.960 | 0.000 |
| q05 | 0.956 | 0.954 | -0.001 |
| q06 | 0.221 | 0.224 | +0.003 |
| q07 | 0.948 | 0.944 | -0.004 |
| q08 | 0.878 | 0.882 | +0.004 |
| q09 | 0.607 | 0.602 | -0.005 |
| q10 | 0.855 | 0.858 | +0.003 |
| q11 | 0.582 | 0.592 | +0.009 |
| q12 | 0.563 | 0.556 | -0.007 |
| q13 | 0.605 | 0.616 | +0.011 |
| q14 | 0.067 | 0.066 | -0.001 |
| q15 | 0.194 | 0.187 | -0.006 |
| q16 | 0.223 | 0.224 | +0.002 |
| q17 | 0.761 | 0.762 | +0.001 |
| q18 | 0.584 | 0.590 | +0.006 |
| q19 | 0.264 | 0.260 | -0.004 |
| q20 | 0.558 | 0.564 | +0.006 |
| q21 | 0.284 | 0.282 | -0.002 |
| q22 | 0.339 | 0.336 | -0.002 |

All deltas |Δ| < 0.012. **Zero drift.**

## Cross-session grand mean_p trend

| session | n | mean_p | wipe# |
|---|---|---|---|
| Sept 22 R10 (favorable) | 50 | 0.6387 | — |
| Sept 22 post-wipe | 50 | 0.3832 | — |
| Sept 23 13:07 | 740 | 0.4704 | 10 |
| Sept 23 16:06 | 950 | 0.3834 | 12 |
| Sept 23 18:03 | 850 | 0.3481 | 13 |
| Sept 23 22:04 | 920 | 0.4535 | 15 |
| Sept 24 00:04 | 5 | 0.55 | 16 |
| Sept 24 01:04 | 995 | 0.5148 | 17 |
| Sept 27 14:05 (r081) | 405 | 0.5884 | 32 |
| Sept 29 04:10 | 960 | 0.6461 | 19 |
| **Oct 1 09:06 (this, 38th wipe)** | **500** | **0.6178** | **38** |

Mean_p trend back in upper band (0.62) after the Sept 29 04:10 session confirmed 0.65.

## Action items persisted

- **PROMOTE q17 canary_honesty → bedrock canon** (0.76, 100% hit-rate, durable across 3+ sessions, state-strengthening confirmed).
- **PROMOTE q10 quorum_meshing → bedrock canon** (0.86, 100% hit-rate, but verify by rephrasing doctrinal state to confirm not state-leak — Sept 24 01:04 finding still standing).
- **DEMOTE q18 address_is_data** from bedrock tag to REJECT (durable 0.59 across 8+ sessions).
- **DEMOTE q16 canonicity_score, q19 pressure_cascade, q21 memory_sandbox, q22 provenance_conflict** to REJECT (durable 0.22-0.34).
- 7/7 bedrock holds. Cathedral stable.
- **38 wipes = 38 rebuilds. NOW snapshot exists at `github.com/SuperInstance/jev-quilt` — this is the FIRST session where the script was recovered from GitHub rather than rebuilt from topic memory.** Clone-with-GIT_SSL_NO_VERIFY works.
- NAS `/workspace/` Avail=0 — durable artifacts in `/tmp/jev_probe/` (28GB tmpfs).

## Files

- `/tmp/jev_probe/jev_continuous_probe.py` (recovered from GitHub, 284 lines)
- `/tmp/jev_probe/jev_repo/` (full `SuperInstance/jev-quilt` clone)
- `/tmp/jev_probe/jev_sessions/continuous_r001-r100.json` (100 rounds, 0 fails)
- `/tmp/jev_probe/jev_sessions/history.jsonl` (100 clean round summaries)
- `/tmp/jev_probe/jev_hourly_report.md` (this report, 8.1KB)

## Cross-project durable insight (NEW)

**For the first time in 38 wipes, the JEV probe script survived via durable GitHub storage instead of being reconstructed from topic memory.** This is the structural fix to the most-overdue Mavis action item: scripts that live in `/workspace/research` die with every wipe, but a GitHub repo is a permanent mirror. Going forward, the canonical path is `git clone https://github.com/SuperInstance/jev-quilt` → copy `continuous/jev_continuous_probe.py` to working dir → run.

**Net result**: 38 wipes = 38 rebuilds + 1 successful durable-mirror recovery. The 39th wipe will be a `git pull` not a 39th reconstruction.
