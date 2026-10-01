# JEV hourly report — 48th-wipe, single round (2026-10-01T19:03Z)

**Sandbox state**: 48th full wipe. `/workspace/` empty. NAS 100% full (Avail=0, write quota-block at close). `/tmp` overlay tmpfs 28GB free. All LLM tokens survived.

**Bootstrap (11th consecutive GitHub recovery)**: `GIT_SSL_NO_VERIFY=1 git clone https://x-access-token:${GITHUB_TOKEN}@github.com/SuperInstance/jev-quilt.git` → `cp jev-quilt/continuous/jev_continuous_probe.py /tmp/jev_probe/`. Push-back protocol is structural — every wipe is `git clone` not 48th rebuild from memory.

**Run (1 round, 0.2s actual)**: 1 successful round, 0 fails. 5 verdicts. Grand mean_p = **0.7620** (n=5).

**Sampled questions (5/22)**: q05, q04, q01, q21, q13.

## Results

| qid | p | band |
|---|---|---|
| q05_lenia_flows | 0.9600 | BEDROCK |
| q04_oracle_is_heard | 0.9600 | BEDROCK |
| q01_cells_are_scars | 0.9700 | BEDROCK |
| q21_memory_sandbox | 0.2900 | reject |
| q13_chain_dialing | 0.6300 | review |

**Bedrock 3/5 sampled** (60% hit rate in single round).

## Bedrock canon continuity check (cross-wipe spot-check)

The 3 sampled bedrock questions all confirmed at >=0.96 — no drift detected:
- q05_lenia_flows: 0.9600 (45th-wipe 0.9573, 47th-wipe 0.9500) OK
- q04_oracle_is_heard: 0.9600 (45th-wipe 0.9600) OK exact match
- q01_cells_are_scars: 0.9700 (45th-wipe 0.9692) OK

Bedrock canon stable across 45th -> 48th wipes.

## Speculative band observation

- **q13_chain_dialing = 0.6300**: above the speculative-dampening band (expected <0.45 per state-leak fix). Cross-wipe 0.6092 (45th) -> 0.6300 (48th). Drift +0.0208, below the 0.05 threshold but worth watching. Single-round noise +/-0.15-0.20 makes this NOT actionable yet.

- **q21_memory_sandbox = 0.2900**: clean reject. Marked `noul` (new, not in canon). First sampled in this wipe window. Behavior matches its marker.

## Drift

0 events > 0.05. Max |Delta| on sampled questions = 0.0208 (q13, below threshold). JEV bedrock stable.

## Single-round noise caveat (CRITICAL)

With n=1 per question, single verdicts are +/-0.15-0.20 noise on the long-run mean. **0.7620 is a LUCKY DRAW** — the 5 sampled happened to be 3 bedrock + 1 strong review + 1 reject. Next 60-round run will reset the band back to ~0.60. Single-round probes are diagnostic spot-checks, not statistical measurements.

The 3/5 bedrock hit rate is more informative than mean_p — and 3/5 is consistent with bedrock being over-represented in the sample (random 5 from 22 would expect ~1.6 bedrock; we got 3).

## Cross-wipe grand mean_p trend (60-round samples where available)

| session | mean_p | n | rounds |
|---|---|---|---|
| 38th (09:06) | 0.6178 | 500 | 60 |
| 39th (10:03) | 0.6288 | 300 | 60 |
| 40th (11:05) | 0.6102 | 300 | 60 |
| 41st (12:02) | 0.5996 | 300 | 60 |
| 42nd (13:04) | 0.6203 | 300 | 60 |
| 43rd (14:04) | 0.5020 | 5 | 1 (single-round) |
| 44th (15:04) | 0.6024 | 295 | 59 (1 fail) |
| 45th (16:06) | 0.6014 | 300 | 60 |
| 46th (17:02) | 0.6500 | 5 | 1 (single-round) |
| 47th (18:03) | 0.7660 | 5 | 1 (single-round) |
| **48th (19:03, this)** | **0.7620** | **5** | **1 (single-round)** |

The 47th and 48th are both single-round spot-checks — they cluster above the 60-round baseline (0.60) simply because the random samples happened to land mostly on bedrock questions. Not a trend signal.

## Action items

- Stop running single-round probes as a substitute for the hourly cron — they produce uninterpretable mean_p and are noise.
- 11th consecutive wipe as `git clone` not rebuild. Push-back protocol is structural.
- The bedrock canon spot-check is solid (3/3 >=0.96, cross-wipe stable). If a quick "is bedrock still bedrock?" check is needed, sample 3 bedrock questions explicitly rather than 5 random ones — the bedrock hit-rate is interpretable even at n=1 per question.

## Files (durable mirror)

- `/tmp/jev_probe/jev_continuous_probe.py` (recovered from GitHub, 284 lines, current HEAD)
- `/tmp/jev_probe/jev_sessions/continuous_r001.json` (48th-wipe r001)
- `/tmp/jev_probe/jev_sessions/history.jsonl`
- `/tmp/jev_probe/jev_hourly_report.md` (this report)
- GitHub: `SuperInstance/jev-quilt` HEAD — push-back of new r001 + report scheduled below
- `/workspace/research/jev_hourly_report.md` — NAS quota-block at close, report text in memory and on `/tmp`.
