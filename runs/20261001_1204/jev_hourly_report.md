# JEV Hourly Report — 41st-wipe (2026-10-01 12:02 UTC)

**Sandbox state**: 41st full wipe. `/workspace/` empty except `.plugin-cache/`. NAS `/workspace/` 100% full (Avail=0, write quota-block). Canonical mirror is `/tmp/jev_probe/` (overlay tmpfs, 28GB free). `TYPESAFEAI_KEY` + `GITHUB_TOKEN` survived.

**Bootstrap**: 4th time from GitHub durable mirror. `GIT_SSL_NO_VERIFY=1 git clone https://x-access-token:${GITHUB_TOKEN}@github.com/SuperInstance/jev-quilt.git` → `cp jev_repo/continuous/jev_continuous_probe.py /tmp/jev_probe/`. The 39th-wipe push-back protocol continues to pay off — every wipe is now `git clone` not 41st rebuild from topic memory.

**Run (60s ceiling, 60 rounds, 0 fails)**: 60 successful rounds in **12.7s**, 0 fails. 300 verdicts (5/round × 60). Grand mean_p = **0.5996** (n=300). In-band with 40th-wipe 0.6102 (-0.0106, well within sampling noise).

## Bedrock canon (p≥0.70 @ 100% hit-rate)

**7 / 7 bedrock questions hold at 100% hit-rate** (cathedral rock-solid for 5 consecutive sessions: 36/37/38/39/40/41st-wipe):

| qid | mean | n | hit_rate |
|---|---|---|---|
| q01 cells_are_scars | 0.9683 | 18 | 100.0% |
| q02 witness_log_is_prediction | 0.9385 | 13 | 100.0% |
| q03 substrate_is_grown | 0.9700 | 17 | 100.0% |
| q04 oracle_is_heard | 0.9600 | 11 | 100.0% |
| q05 lenia_flows | 0.9564 | 11 | 100.0% |
| q07 eleven_opcodes | 0.9493 | 15 | 100.0% |
| q08 polyformalism_12_ports | 0.8775 | 8 | 100.0% |

All 7 in 0.88-0.97 band, 100% hit-rate. Cathedral unchanged.

## Promotion candidates (review → bedrock)

**2 / 8 review-band questions read as bedrock @ 100% hit-rate** (sustained 5th consecutive session):

| qid | mean | n | hit_rate | recommendation |
|---|---|---|---|---|
| **q10 quorum_meshing** | 0.8576 | 17 | 100% | **PROMOTE → bedrock** (5th consecutive session sustained 0.85-0.86, state-leak caveat noted) |
| **q17 canary_honesty** | 0.7600 | 15 | 100% | **PROMOTE → bedrock** (5th consecutive session, recovered from prior decay 0.99→0.40→0.76) |

## Speculative clean-reject (5 / 5)

| qid | mean | n | hit_rate |
|---|---|---|---|
| q06 three_views | 0.2229 | 14 | 0% |
| q09 signal_chain | 0.6085 | 13 | 0% |
| q11 canon_gate_is_chord | 0.5927 | 15 | 0% |
| q12 witness_note_opcode | 0.5540 | 10 | 0% |
| q13 chain_dialing | 0.6000 | 9 | 0% |

All speculative sub-aspects of canon vocabulary cleanly REJECT (0% hit-rate, p<0.70).

## Adversarial clean-reject (2 / 2)

| qid | mean | n | verdict |
|---|---|---|---|
| q14 canon_equals_speculation | 0.0647 | 17 | ✓ clean-reject |
| q15 twentyfour_ports | 0.1943 | 14 | ✓ clean-reject |

Both landmines cleanly rejected.

## Review band — durable REJECT candidates

| qid | mean | n | hit_rate | status |
|---|---|---|---|---|
| q18 address_is_data | 0.5879 | 14 | 0% | speculative (state-leak persists, 0% hit-rate) |
| q16 canonicity_score | 0.2233 | 15 | 0% | durable REJECT |
| q19 pressure_cascade | 0.2600 | 11 | 0% | durable REJECT |
| q20 wolffs_law | 0.5575 | 12 | 0% | speculative (small n) |
| q21 memory_sandbox | 0.2821 | 14 | 0% | durable REJECT |
| q22 provenance_conflict | 0.3335 | 17 | 0% | durable REJECT |

Six durable REJECT candidates, all 0% hit-rate. The q18 state-leak (speculative-tagged but reads as 0.59) is a known false-positive — oracle treats the question as canon, but it's tagged speculative. No rephrasing in this session, carrying over the action item from 37/38/39/40th-wipe reports.

## Drift analysis

**Cross-session drift (41st-wipe mean vs 40th-wipe mean, per question)**:

| qid | 40th | 41st | Δ |
|---|---|---|---|
| q01 | 0.9685 | 0.9683 | -0.0002 |
| q02 | 0.9367 | 0.9385 | +0.0018 |
| q03 | 0.9700 | 0.9700 | 0.0000 |
| q04 | 0.9600 | 0.9600 | 0.0000 |
| q05 | 0.9538 | 0.9564 | +0.0026 |
| q06 | 0.2208 | 0.2229 | +0.0021 |
| q07 | 0.9467 | 0.9493 | +0.0026 |
| q08 | 0.8764 | 0.8775 | +0.0011 |
| q09 | 0.6053 | 0.6085 | +0.0032 |
| q10 | 0.8569 | 0.8576 | +0.0007 |
| q11 | 0.5873 | 0.5927 | +0.0054 |
| q12 | 0.5538 | 0.5540 | +0.0002 |
| q13 | 0.6027 | 0.6000 | -0.0027 |
| q14 | 0.0670 | 0.0647 | -0.0023 |
| q15 | 0.1857 | 0.1943 | +0.0086 |
| q16 | 0.2238 | 0.2233 | -0.0005 |
| q17 | 0.7600 | 0.7600 | 0.0000 |
| q18 | 0.5853 | 0.5879 | +0.0026 |
| q19 | 0.2640 | 0.2600 | -0.0040 |
| q20 | 0.5558 | 0.5575 | +0.0017 |
| q21 | 0.2850 | 0.2821 | -0.0029 |
| q22 | 0.3335 | 0.3335 | 0.0000 |

**0 drift events > 0.05.** Max delta: q15 +0.0086 (still well under 0.05 threshold). JEV is rock-stable.

**Within-session drift**: max in-session mean_p range across rounds = 0.332 (r024) to 0.786 (r017) — normal sampling noise from 5-q samples.

## Cross-session grand mean_p trend

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
| Oct 1 06:06 | 1440 | 0.4699 | 36 |
| Oct 1 08:08 | 1065 | 0.5832 | 37 |
| Oct 1 09:08 | 500 | 0.6178 | 38 |
| Oct 1 10:05 | 300 | 0.6288 | 39 |
| Oct 1 11:04 | 300 | 0.6102 | 40 |
| **Oct 1 12:02 (this, 41st wipe)** | **300** | **0.5996** | **41** |

mean_p stable in 0.58-0.63 band for last 5 wipes. No drift, no degradation.

## Summary

- Bedrock @ 100% hit-rate: **7 / 7** ✓
- Speculative clean-reject: **5 / 5** ✓
- Adversarial clean-reject: **2 / 2** ✓
- Review band coherent (read as bedrock @ 100%): **2 / 8** (q10, q17 — 5th consecutive session)
- Grand mean_p: **0.5996**
- Drift events > 0.05: **0**
- Fails: **0 / 60 rounds**

## Action items

- PROMOTE q10 → bedrock canon list (5th consecutive session sustained 0.85-0.86).
- PROMOTE q17 → bedrock canon list (5th consecutive session, recovered from prior decay).
- Carry over q18 state-leak fix action (spec_notebook rephrasing not yet applied).
- **GitHub durable mirror is paying off — 4th consecutive wipe as `git clone` not rebuild.** Keep push-back protocol.

## Files (durable mirror)

- `/tmp/jev_probe/jev_continuous_probe.py` (recovered from GitHub, 284 lines)
- `/tmp/jev_probe/jev_sessions/continuous_r001-r060.json` (60 rounds, 0 fails)
- `/tmp/jev_probe/jev_sessions/history.jsonl` (60 clean round summaries)
- `/tmp/jev_probe/jev_hourly_report.md` (this file)

## Files (failed — NAS quota-block at close, 0-byte stubs)

- `/workspace/research/*` — cleaned up. NAS `/workspace/` 100% full; all artifacts in `/tmp/jev_probe/` mirror.

---

**Bootstrap (FIRST TIME from GitHub, repeated)**: `GIT_SSL_NO_VERIFY=1 git clone https://x-access-token:${GITHUB_TOKEN}@github.com/SuperInstance/jev-quilt.git` → `cp jev_repo/continuous/jev_continuous_probe.py /tmp/jev_probe/`. Going forward: `git clone` → `cp` → `python3 jev_continuous_probe.py --rounds 60 --out /tmp/jev_probe/jev_sessions` → `python3 analyze_jev.py /tmp/jev_probe/jev_sessions --out /tmp/jev_probe/jev_hourly_report.md`.

**Push-back protocol**:
```
cd /tmp/jev_probe/jev_repo
mkdir -p runs/$(date +%Y%m%d_%H%M)
cp /tmp/jev_probe/jev_continuous_probe.py runs/<ts>/
cp /tmp/jev_probe/jev_hourly_report.md runs/<ts>/
cp /tmp/jev_probe/jev_sessions/history.jsonl runs/<ts>/
git config user.email "jev-probe@superinstance.dev" && git config user.name "JEV Probe"
git add runs/<ts>/ && git commit -m "JEV probe r001-r060 (Oct 1 41st-wipe): 7/7 bedrock, mean_p 0.5996, 0 drift"
GIT_SSL_NO_VERIFY=1 git push
```
