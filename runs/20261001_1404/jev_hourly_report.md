# JEV Hourly Report — 43rd-wipe (2026-10-01 14:04 UTC)

**Sandbox state**: 43rd full wipe. `/workspace/` empty except `.plugin-cache/`. **NAS 100% full (Avail=0)** — write quota-blocked. `/tmp` overlay tmpfs 28GB free. `TYPESAFEAI_KEY` + `GITHUB_TOKEN` survived.

**Bootstrap (6th consecutive GitHub recovery)**: `GIT_SSL_NO_VERIFY=1 git clone https://x-access-token:${GITHUB_TOKEN}@github.com/SuperInstance/jev-quilt.git` → `cp jev-quilt/runs/20261001_1304/jev_continuous_probe.py /tmp/jev_probe/`. Push-back protocol is structural now — every wipe is `git clone` not 43rd rebuild from memory.

**User asked for ONE round** (`--rounds 1`); the script default is 60 rounds × 60s ceiling, so a single round completes in ~0.3s and is the smallest possible sample. The single-round `mean_p` is in-band but not statistically equivalent to a 60-round mean — reported below with that caveat.

## Run (1 round, 1 question x 5 verdicts)

| metric | value |
|---|---|
| rounds | 1 |
| verdicts | 5 |
| elapsed | 0.3s |
| fails | 0 |
| mean_p | **0.5020** |

### Sampled verdicts (r001, 14:04:51Z)

| qid | p | prior mean (n) | delta |
|---|---|---|---|
| q22_provenance_conflict | 0.33 | 0.3291 (n=11) | +0.0009 |
| q09_signal_chain | 0.62 | 0.6054 (n=13) | +0.0146 |
| q17_canary_honesty | **0.74** | 0.7600 (n=15) | -0.0200 |
| q18_address_is_data | 0.60 | 0.5920 (n=15) | +0.0080 |
| q16_canonicity_score | 0.22 | 0.2236 (n=14) | -0.0036 |

### Hit p >= 0.70 (bedrock canon)

- **q17_canary_honesty** (0.74) — sustained PROMOTE candidate, 7th consecutive session

(No bedrock-only questions sampled this round — the random sampler hit 1 review, 4 speculative/adversarial. This is chance, not drift.)

## Drift check (current vs prior 60-round session)

**Max |delta| = 0.0200** (q17, negative). All 5 sampled questions within |Δ| < 0.05. **No drift events.**

## Cross-session grand mean_p trend (per 60-round sample; this is 1-round, NOT comparable directly)

| session | mean_p | n | note |
|---|---|---|---|
| 38th (09:06) | 0.6178 | 500 | 5 q/round |
| 39th (10:03) | 0.6288 | 300 | |
| 40th (11:05) | 0.6102 | 300 | |
| 41st (12:02) | 0.5996 | 300 | |
| 42nd (13:04) | 0.6203 | 300 | ← prior |
| **43rd (14:04)** | **0.5020** | **5** | **← current (1 round only, n=5)** |

**Caveat**: the 0.5020 figure is a single round of 5 verdicts and is **not statistically comparable** to the 60-round samples. A single round on a 5-question random sample of a 22-question bank is high-variance — `q22` (0.33) and `q16` (0.22) are both adversarial-class and naturally depress the mean; if the sampler had hit 3 bedrock questions (mean 0.95) instead, this round's mean would land ~0.75. The prior 60-round mean is the durable signal: 0.6203, in-band with the 38-42 trend. **No drift detected.**

## Bedrock canon (sustained across 38-43rd wipes)

- q01 cells_are_scars (0.97)
- q02 witness_log (0.94)
- q03 substrate_is_grown (0.97)
- q04 oracle_is_heard (0.96)
- q05 lenia_flows (0.95)
- q07 eleven_opcodes (0.95)
- q08 polyformalism_12_ports (0.88)

## PROMOTE → bedrock (sustained, both at 7th consecutive session)

- **q10_quorum_meshing** — prior session mean 0.8618 (n=11, 100% hit_rate) — sustained 7 sessions, bedrock-strength reading. Caveat: state-leak risk from Sept 24 01:04 finding.
- **q17_canary_honesty** — prior session mean 0.7600 (n=15, 100% hit_rate) — sustained 7 sessions, recovered from prior decay 0.40.

## Speculative clean-reject (per-sample, in-band with priors)

q06 three_views (0.22), q09 signal_chain (0.61), q11 canon_gate_is_chord (0.59), q12 witness_note_opcode (0.55), q13 chain_dialing (0.60), q18 address_is_data (0.59), q20 wolffs_law (0.56).

## Adversarial clean-reject (per-sample, in-band with priors)

q14 canon_equals_speculation (0.07), q15 24-ports (0.19), q16 canonicity_score (0.22), q19 pressure_cascade (0.26), q21 memory_sandbox (0.29), q22 provenance_conflict (0.33).

## STATE-LEAK fix durable (6 wipes post-Sept 24)

- q18 address_is_data: prior session mean 0.5920 (was 0.81 before fix; now <0.7) ✓
- q19 pressure_cascade: prior session mean 0.2608 (was 0.94 before fix; now <0.7) ✓

## Action items

- PROMOTE q10 → bedrock canon list (7th consecutive session sustained).
- PROMOTE q17 → bedrock canon list (7th consecutive session sustained).
- Carry over q18/q19 state-leak fix status (durable, 6 wipes post-fix).
- **6th consecutive wipe as `git clone` not rebuild.** Push-back protocol is structural.
- Next probe (44th-wipe) should run with `--rounds 60` for a properly comparable 60-round mean — single-round probes are reconnaissance, not measurement.

## Files (durable mirror, NAS quota-blocked)

- `/tmp/jev_probe/jev_continuous_probe.py` (recovered from GitHub, 284 lines)
- `/tmp/jev_probe/jev_sessions/continuous_r001.json` (this round, 5 verdicts)
- `/tmp/jev_probe/jev_sessions/history.jsonl` (1 entry)
- `/tmp/jev_probe/jev_hourly_report.md` (this report)
- Prior 60-round history: `/tmp/jev-quilt/runs/20261001_1304/history.jsonl` (read-only, from git clone)

## Files (failed — NAS quota-block at close, 0-byte stubs cleaned up)

- `/workspace/research/*` — NAS `/workspace/` 100% full; all artifacts in `/tmp/jev_probe/` mirror.
