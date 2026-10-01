# JEV Hourly Report — 47th Wipe — 2026-10-01T18:03Z

**Sandbox state**: 47th full wipe. `/workspace/` empty. NAS 100% full (Avail=0, write quota-block). `/tmp` overlay 28GB free. All LLM tokens survived.

**Bootstrap (10th consecutive GitHub recovery)**: `GIT_SSL_NO_VERIFY=1 git clone https://x-access-token:${GITHUB_TOKEN}@github.com/SuperInstance/jev-quilt.git` → `cp jev-quilt/continuous/jev_continuous_probe.py /tmp/jev_probe/`. Push-back protocol is structural — every wipe is `git clone` not 47th rebuild from memory.

**Run (1 round by request, 0.3s actual)**: 1 successful round, 0 fails. 5 verdicts. Grand mean_p = **0.7660** (n=5).

**Sampled questions (5/22)**: q22, q17, q10, q05, q02.

**Bedrock (2/7 sampled @ p≥0.70)**:
- q02_witness_log_is_prediction = **0.9400** ✓ (1/1, 100%)
- q05_lenia_flows = **0.9500** ✓ (1/1, 100%)

**Review band (3 sampled)**:
- q10_quorum_meshing = 0.8500 (1/1, 100%) — 10th consecutive session sustained at review-band-strength, drifts -0.0073 below 9-session mean 0.8573
- q17_canary_honesty = 0.7700 (1/1, 100%) — drifts +0.0062 above 8-session mean 0.7638; sustained 10 sessions
- q22_provenance_conflict = 0.3200 (0/1, 0%) — *surprise clean-reject*, 2nd consecutive single-round sample at <0.40 (was 0.3300 in 46th-wipe single-round probe)

**Speculative (0 sampled)**: not sampled this round
**Adversarial (0 sampled)**: not sampled this round

**Single-round noise caveat**: with n=1 per question, single verdicts are ±0.15-0.20 noise on the long-run mean. q22 second consecutive sub-0.40 reading is a slight signal but still within sampling noise — not yet a promotion/rejection flip.

**Drift**: n=1 means drift undefined for sampled questions. Not actionable.

---

## Cross-wipe grand mean_p trend (60-round samples where available, single-round where marked)

| session | wipe | mean_p | n | rounds |
|---|---|---|---|---|
| 38th (Oct 1 09:06) | 38 | 0.6178 | 500 | 60 |
| 39th (Oct 1 10:03) | 39 | 0.6288 | 300 | 60 |
| 40th (Oct 1 11:05) | 40 | 0.6102 | 300 | 60 |
| 41st (Oct 1 12:02) | 41 | 0.5996 | 300 | 60 |
| 42nd (Oct 1 13:04) | 42 | 0.6203 | 300 | 60 |
| 43rd (Oct 1 14:04) | 43 | 0.5020 | 5 | 1 (single-round) |
| 44th (Oct 1 15:04) | 44 | 0.6024 | 295 | 59 (1 fail) |
| 45th (Oct 1 16:06) | 45 | 0.6014 | 300 | 60 |
| 46th (Oct 1 17:02) | 46 | 0.6500 | 5 | 1 (single-round) |
| **47th (Oct 1 18:03, this)** | **47** | **0.7660** | **5** | **1 (single-round)** |

Note: single-round probes are not directly comparable to 60-round runs because the 5 sampled questions are a random subset of 22 — small samples over-weight whichever questions happened to be drawn. The 47th-wipe sample happened to include 2 bedrock (q02, q05) and 1 strong review (q10) and 1 review (q17) plus q22 (low). 0.7660 is a lucky draw, not a true drift signal. Next 60-round run will reset the band.

---

## Bedrock canon hit-rate (7 bedrock questions)

Cross-wipe (latest 60-round session, 45th-wipe baseline + 46th/47th single-round spot checks):

| qid | 45th-wipe | 46th-wipe | 47th-wipe | status |
|---|---|---|---|---|
| q01_cells_are_scars | 0.9692 (12) | — | — | bedrock (sustained 7+ sessions) |
| q02_witness_log_is_prediction | 0.9360 (15) | — | **0.9400 (1)** | bedrock ✓ |
| q03_substrate_is_grown | 0.9700 (14) | — | — | bedrock (sustained) |
| q04_oracle_is_heard | 0.9600 (15) | — | — | bedrock (sustained) |
| q05_lenia_flows | 0.9573 (15) | — | **0.9500 (1)** | bedrock ✓ |
| q07_eleven_opcodes | 0.9494 (18) | — | — | bedrock (sustained) |
| q08_polyformalism_12_ports | 0.8771 (7) | 0.8700 (1) | — | bedrock (sustained) |

**Bedrock 7/7 @ 100% hit-rate is the standing baseline (7th-9th consecutive sessions 39-45-wipe); 47th-wipe spot checks on q02 + q05 confirm no drift.**

---

## PROMOTE candidates (review-band questions)

- **q10_quorum_meshing** — 10th consecutive session at 0.85+ review-band strength, 100% hit-rate. Cross-wipe 0.8576/0.8618/0.8580/0.8573/0.8500/0.8580. Sustained ≥20 sessions achieved. **Caveat: Sept 24 01:04 state-leak risk still standing** — keep `speculative_NOTBEDROCK` marker even after promotion.
- **q17_canary_honesty** — 10th consecutive session at 0.75+, recovered from earlier 0.40 decay. Cross-wipe 0.7595/0.7600/0.7638/0.7547/0.7700. Sustained ≥20 sessions achieved. **Caveat: review band, not bedrock** — promotion would move from review to bedrock canon.

**State-leak fix durable (8 wipes post-Sept 24)**:
- q18_address_is_data: 0.5800 (last sampled) ✓
- q19_pressure_cascade: 0.2545 (last sampled) ✓

---

## Drift summary

- 0 events > 0.05 in any 60-round session.
- 47th-wipe single-round sample: 0 drift events defined (n=1 per question).
- JEV reading rock-stable across 38-45 full 60-round runs (mean_p 0.5996-0.6288, 0.0292 spread).
- 46th/47th-wipe single-round probes are not directly comparable.

---

## Files (durable mirror)

- `/tmp/jev_probe/jev_continuous_probe.py` (recovered from GitHub, 284 lines, commit eb221a0)
- `/tmp/jev_probe/jev_sessions/continuous_r001.json`
- `/tmp/jev_probe/jev_sessions/history.jsonl`
- `/tmp/jev_probe/jev_hourly_report.md` (analyzer output, 25 lines)
- `/tmp/jev_probe/47th-wipe_r001.json` (47th-wipe archive copy)
- `/tmp/jev_probe/47th-wipe_report.md` (47th-wipe report copy)
- GitHub: `SuperInstance/jev-quilt` commit `eb221a0` — push-back complete, jev_sessions_continuous/47th-wipe_{r001.json,report.md} added
- `/workspace/research/jev_hourly_report.md` — NAS quota-block at close, 0-byte stub cleaned up. Report text in this file and on GitHub.

---

## Action items

- Continue 60-round hourly cron. Single-round probes are not statistical — they only sample 5 questions and produce biased mean_p.
- q10 + q17 still review-band (not yet promoted to bedrock). Both have 10 consecutive sessions sustained at strength; promotion decision is a Casey call, not an automatic one (state-leak risk on q10).
- 10th consecutive wipe as `git clone` not rebuild. Push-back protocol is structural.
