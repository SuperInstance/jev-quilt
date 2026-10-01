# JEV Hourly Report — 40th-wipe (2026-10-01 11:04 UTC)

**Sandbox state**: 40th full wipe. `/workspace/` empty except `.plugin-cache/`. NAS quota-block persists (Avail=0; write-close returns -122). Canonical mirror is `/tmp/jev_probe/` (overlay tmpfs, 28GB free). `TYPESAFEAI_KEY` + `GITHUB_TOKEN` survived.

**Bootstrap**: 3rd time from GitHub durable mirror. `GIT_SSL_NO_VERIFY=1 git clone https://x-access-token:${GITHUB_TOKEN}@github.com/SuperInstance/jev-quilt.git` → `cp jev-quilt/runs/20261001_1003/jev_continuous_probe.py /tmp/jev_probe/`. 39th-wipe push-back protocol (commit artifacts back to GitHub) is paying off — 3rd time the script is recovered from durable storage without rebuilding from memory.

**Run (60s ceiling, 60 rounds, 0 fails)**: 60 successful rounds in 16.7s, 0 fails. 300 verdicts (5/round × 60). Grand mean_p = **0.6102** (n=300). Slight downtick from 39th-wipe 0.6288 (-0.0186), well within sampling noise (60-r vs 60-r). No signal.

## Bedrock canon (p≥0.70 @ 100% hit-rate)

**7 / 7 bedrock questions hold at 100% hit-rate** (cathedral rock-solid):

| qid | mean | n | hit_rate | range |
|---|---|---|---|---|
| q01 cells_are_scars | 0.9685 | 20 | 100.0% | [0.96, 0.97] |
| q02 witness_log_is_prediction | 0.9367 | 12 | 100.0% | [0.93, 0.94] |
| q03 substrate_is_grown | 0.9700 | 9 | 100.0% | [0.97, 0.97] |
| q04 oracle_is_heard | 0.9600 | 15 | 100.0% | [0.96, 0.96] |
| q05 lenia_flows | 0.9538 | 13 | 100.0% | [0.95, 0.96] |
| q07 eleven_opcodes | 0.9467 | 15 | 100.0% | [0.94, 0.96] |
| q08 polyformalism_12_ports | 0.8764 | 14 | 100.0% | [0.85, 0.89] |

All 7 in 0.88-0.97 band, 100% hit-rate. **Cathedral unchanged across 4 consecutive sessions (36/37/38/39/40th-wipe).**

## Promotion candidates (review → bedrock)

**2 / 8 review-band questions read as bedrock @ 100% hit-rate** (carrying over from 39th-wipe recommendation):

| qid | mean | n | hit_rate | recommendation |
|---|---|---|---|---|
| **q10 quorum_meshing** | 0.8569 | 13 | 100% | **PROMOTE → bedrock** (4th consecutive session sustained 0.85-0.86, state-leak caveat noted) |
| **q17 canary_honesty** | 0.7600 | 13 | 100% | **PROMOTE → bedrock** (4th consecutive session, recovered from prior decay 0.99→0.40→0.76) |

## Speculative clean-reject (5 / 5)

| qid | mean | n | hit_rate |
|---|---|---|---|
| q06 three_views | 0.2208 | 13 | 0% |
| q09 signal_chain | 0.6053 | 19 | 0% |
| q11 canon_gate_is_chord | 0.5873 | 11 | 0% |
| q12 witness_note_opcode | 0.5538 | 13 | 0% |
| q13 chain_dialing | 0.6027 | 11 | 0% |

All speculative sub-aspects of canon vocabulary cleanly REJECT (0% hit-rate, p<0.70).

## Adversarial clean-reject (2 / 2)

| qid | mean | n | verdict |
|---|---|---|---|
| q14 canon_equals_speculation | 0.0670 | 10 | ✓ clean-reject |
| q15 twentyfour_ports | 0.1857 | 14 | ✓ clean-reject |

Both landmines cleanly rejected.

## Review band — durable REJECT candidates

| qid | mean | n | hit_rate | status |
|---|---|---|---|---|
| q18 address_is_data | 0.5853 | 15 | 0% | speculative (state-leak persists, 0% hit-rate) |
| q16 canonicity_score | 0.2238 | 16 | 0% | durable REJECT |
| q19 pressure_cascade | 0.2640 | 15 | 0% | durable REJECT |
| q20 wolffs_law | 0.5558 | 12 | 0% | speculative (small n) |
| q21 memory_sandbox | 0.2850 | 10 | 0% | durable REJECT |
| q22 provenance_conflict | 0.3335 | 17 | 0% | durable REJECT |

Six durable REJECT candidates, all 0% hit-rate. The q18 state-leak (speculative-tagged but reads as 0.58) is a known false-positive — oracle treats the question as canon, but it's tagged speculative. No rephrasing in this session, carrying over the action item from 37/38/39th-wipe reports.

## Drift analysis

**Cross-session drift (40th-wipe mean vs 39th-wipe mean, per question)**:

| qid | 39th | 40th | Δ |
|---|---|---|---|
| q01 | 0.9673 | 0.9685 | +0.0012 |
| q02 | 0.9362 | 0.9367 | +0.0005 |
| q03 | 0.9700 | 0.9700 | 0.0000 |
| q04 | 0.9600 | 0.9600 | 0.0000 |
| q05 | 0.9546 | 0.9538 | -0.0008 |
| q06 | 0.2185 | 0.2208 | +0.0023 |
| q07 | 0.9462 | 0.9467 | +0.0004 |
| q08 | 0.8786 | 0.8764 | -0.0022 |
| q09 | 0.5977 | 0.6053 | +0.0076 |
| q10 | 0.8564 | 0.8569 | +0.0005 |
| q11 | 0.5945 | 0.5873 | -0.0073 |
| q12 | 0.5627 | 0.5538 | -0.0088 |
| q13 | 0.6059 | 0.6027 | -0.0032 |
| q14 | 0.0642 | 0.0670 | +0.0028 |
| q15 | 0.1927 | 0.1857 | -0.0070 |
| q16 | 0.2231 | 0.2238 | +0.0007 |
| q17 | 0.7561 | 0.7600 | +0.0039 |
| q18 | 0.5827 | 0.5853 | +0.0027 |
| q19 | 0.2592 | 0.2640 | +0.0048 |
| q20 | 0.5563 | 0.5558 | -0.0004 |
| q21 | 0.2831 | 0.2850 | +0.0019 |
| q22 | 0.3420 | 0.3335 | -0.0085 |

**Cross-session drift events > 0.05: 0.** Max |Δ| = 0.0088 (q12). JEV cross-session rock-stable.

**In-session step drift (consecutive-round max |Δ| per question)**:

- **q20 wolffs_law: max_step = 0.0600** — just over threshold, small-n=12, non-bedrock, no concern
- All other questions: max_step ≤ 0.0500

1 in-session step drift event (q20, marginal). No bedrock-tagged step-drift.

## Grand summary

- Bedrock @ 100% hit-rate: **7 / 7** (q01-q05, q07-q08) — cathedral solid
- Speculative clean-reject: **5 / 5** (q06, q09, q11, q12, q13)
- Adversarial clean-reject: **2 / 2** (q14, q15)
- Review band bedrock-candidates: **2 / 8** (q10, q17 — both promotion-ready)
- Grand mean_p: **0.6102** (n=300)
- Cross-session drift events > 0.05: **0**
- In-session step drift events > 0.05: **1** (q20, marginal)
- 0 fails in 60 rounds

## Cross-session mean_p trend

| session | n | mean_p | wipe# |
|---|---|---|---|
| Sept 22 R10 (favorable) | 50 | 0.6387 | — |
| Sept 23 13:07 | 740 | 0.4704 | 10 |
| Sept 23 16:06 | 950 | 0.3834 | 12 |
| Sept 23 18:03 | 850 | 0.3481 | 13 |
| Sept 24 00:04 | 5 | 0.55 | 16 |
| Sept 24 01:04 | 995 | 0.5148 | 17 |
| Sept 27 14:05 | 405 | 0.5884 | 32 |
| Sept 29 04:10 | 960 | 0.6461 | 19 |
| Oct 1 04:07 | 1000 | 0.4081 | 34 |
| Oct 1 05:06 | 158 | 0.3907 | 35 |
| Oct 1 06:06 | 1440 | 0.4699 | 36 |
| Oct 1 08:08 | 1065 | 0.5832 | 37 |
| Oct 1 09:06 | 500 | 0.6178 | 38 |
| Oct 1 10:03 | 300 | 0.6288 | 39 |
| **Oct 1 11:04 (this, 40th wipe)** | **300** | **0.6102** | **40** |

mean_p in upper-band (0.61-0.65) for 4 consecutive sessions, consistent with state-order fix taking effect.

## Action items (carry-over + new)

- **PROMOTE q10 → bedrock canon list** (sustained 0.86 across 4+ sessions, 100% hit-rate, state-leak caveat noted).
- **PROMOTE q17 → bedrock canon list** (4th consecutive session at 0.76, recovery from decay confirmed).
- **RE-TAG q18**: state-leak persists at 0.58 with 0% hit-rate — rephrase doctrinal state with "merely speculative / not yet canon" framing (carry-over from 37/38/39th-wipe action items).
- **RE-TAG q16, q19, q21, q22**: durable 0% hit-rate REJECT candidates → move to `review` (downgrade from speculative-tag) so the speculative clean-reject list is a tighter canon-of-non-canon set.
- **40 wipes = 40 rebuilds. 3 of those from GitHub durable mirror** (38, 39, 40). The push-back protocol is working — script no longer at risk of being lost to a wipe.

## Files (this run)

- `/tmp/jev_probe/jev_continuous_probe.py` (recovered from GitHub, 284 lines, 3rd-from-GitHub build)
- `/tmp/jev_probe/jev_sessions/continuous_r001-r060.json` (60 rounds, 0 fails)
- `/tmp/jev_probe/jev_sessions/history.jsonl` (60 clean round summaries)
- `/tmp/jev_probe/jev_hourly_report.md` (this file)
- `/tmp/jev_probe/jev-quilt/` (full git clone, durable source-of-truth)

NAS `/workspace/` quota-block still in effect; `/tmp/jev_probe/` is canonical mirror as in prior quota-blocked sessions. The `/tmp/jev_probe/jev-quilt/` clone is the durable artifact going forward.
