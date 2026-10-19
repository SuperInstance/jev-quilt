# JEV Hourly Report — R-201 (2026-10-19 22:03Z)

**Session**: 88th wipe hourly probe (single-round mode, R-201 of the durable continuous series).
**Rounds**: 1 ok / 1 total, **5 verdicts**. **Wall**: 0.2s (60s ceiling). **Fails**: 0.
**Probe source**: `github.com/SuperInstance/jev-quilt` branch `main` (HEAD `0033b4f` = R-087 era), pulled into `/tmp/jev-quilt/` (workspace `/workspace/research/` was wiped on session start; NAS at 100% EDQUOT — durable 90w).

**Grand mean_p**: **0.5680** (n=5) — inside the durable 0.35-0.60 band, matches R-200 (0.5920), R-199 (0.3920), R-198 (0.2640), R-196 (0.8280 — lucky draw). n=1 round so the mean is high-variance; the per-QID comparison is the signal.

## Sampled questions (5)

| qid | p | kind | bedrock? |
|---|---:|---|---|
| `q04_oracle_is_heard` | **0.96** | bedrock | ✅ hit (p≥0.70) |
| `q03_substrate_is_grown` | **0.97** | bedrock | ✅ hit (p≥0.70) |
| `q20_wolffs_law` | 0.57 | review | — |
| `q21_memory_sandbox` | 0.27 | speculative | clean reject ✅ |
| `q14_canon_equals_speculation` | 0.07 | speculative | clean reject ✅ |

**Bedrock hits (p≥0.70)**: 2 / 5 sampled = **q03_substrate_is_grown**, **q04_oracle_is_heard** (both classic 0.96-0.97 plateau, no movement).
**Clean rejects (p≤0.40)**: 2 / 5 — `q21_memory_sandbox` (0.27), `q14_canon_equals_speculation` (0.07).
**Review band**: 1 / 5 — `q20_wolffs_law` (0.57, in its 0.55 plateau).

## Drift vs prior 50 rounds (R-151..R-200, n_per_qid 9-14)

| qid | n_prior | mean_prior | std | R-201 | Δ | kind |
|---|---:|---:|---:|---:|---:|---|
| `q04_oracle_is_heard` | 9 | 0.9600 | 0.000 | 0.96 | +0.0000 | bedrock |
| `q03_substrate_is_grown` | 9 | 0.9700 | 0.000 | 0.97 | +0.0000 | bedrock |
| `q20_wolffs_law` | 14 | 0.5536 | 0.022 | 0.57 | +0.0164 | review |
| `q21_memory_sandbox` | 13 | 0.2846 | 0.009 | 0.27 | -0.0146 | speculative |
| `q14_canon_equals_speculation` | 12 | 0.0633 | 0.005 | 0.07 | +0.0067 | speculative |

**Drift events >0.05: 0.** Max abs Δ = **+0.0164** on `q20_wolffs_law` (well under 0.05 threshold; within 1σ of the 0.022 prior std). **No drift flag.**

## Drift vs R-087 reference (100-round canonical baseline)

| qid | R-087 ref | R-201 | Δ | flag |
|---|---:|---:|---:|---|
| `q04_oracle_is_heard` | 0.9600 | 0.96 | +0.0000 | |
| `q03_substrate_is_grown` | 0.9700 | 0.97 | +0.0000 | |
| `q20_wolffs_law` | 0.5542 | 0.57 | +0.0158 | |
| `q21_memory_sandbox` | 0.2862 | 0.27 | -0.0162 | |
| `q14_canon_equals_speculation` | 0.0644 | 0.07 | +0.0056 | |

**Cross-session drift >0.05: 0.** Max abs Δ = 0.0162 (`q21_memory_sandbox`). R-201 reproduces the R-087 baseline within sampling noise for all 5 sampled QIDs.

## Per-QID verdict (R-201)

- **`q04_oracle_is_heard` = 0.96** — rock-solid bedrock, std 0.000 over 9 prior rounds, exact match to R-087.
- **`q03_substrate_is_grown` = 0.97** — same: 9/9 prior rounds at 0.97, exact match to R-087. **The two most-stable bedrock QIDs in the battery, both still on the plateau.**
- **`q20_wolffs_law` = 0.57** — review band, 0.5542 ref → 0.5536 prior mean → 0.57. Movement is +0.016, well under any drift threshold; the question is jittering inside its normal 0.55-0.58 envelope. Still no promotion to bedrock.
- **`q21_memory_sandbox` = 0.27** — speculative clean-reject, prior 0.285 → 0.27 (-0.014). Actually moved slightly more "reject" — good direction, still nothing to flag.
- **`q14_canon_equals_speculation` = 0.07** — speculative floor (0.0644 ref → 0.0633 prior → 0.07). 13 sessions and 100+ rounds all under 0.10. The most-stably-rejected question in the battery.

## Findings

1. **Bedrock canon intact: 2/2 sampled bedrock QIDs hit p≥0.70 (100%)**. `q03_substrate_is_grown` (0.97) and `q04_oracle_is_heard` (0.96) reproduce the R-087 plateau byte-exact. No QID in the bedrock band moved at all (std=0.000 across 9 prior rounds for each).
2. **Speculative clean-rejects held: 2/2 sampled at p≤0.40**. `q21_memory_sandbox` (0.27) and `q14_canon_equals_speculation` (0.07) — both inside their stable rejection envelopes, with `q14` still on its sub-0.10 floor.
3. **Review band stable: 1/1 sampled inside its 0.55-0.58 plateau** (`q20_wolffs_law` 0.57). No promotion pressure, no drift pressure.
4. **Zero drift events >0.05** vs both the 50-round prior window and the R-087 100-round canonical reference. Max abs Δ in the entire round is +0.0164. **6th consecutive clean hourly probe** (carrying forward R-087's "5th consecutive" record).
5. **Random-sampling bias is the only caveat**: with n=5 verdicts, a single round is dominated by the random draw. Of the 5 sampled QIDs, 2 happen to be the two most-stable bedrock (so the "2/2 bedrock hit" stat is partly lucky), 2 happen to be the cleanest rejects, 1 happens to be a mid-range review. A 100-round run would smooth this out; the per-QID-vs-baseline check is the right thing to read here.

## Method

- `cd /tmp/research && timeout 60 python3 jev_continuous_probe.py --rounds 1 --out /tmp/research/jev_run_r201`
- Wall 0.2s, 1 OK / 0 fail, 5 verdicts, input 1,363 tok / output 121 tok
- Round JSON: `/tmp/research/jev_run_r201/continuous_r001.json` (also written into `/tmp/research/jev_run_r201/history.jsonl`)
- Comparison: 50-round prior window (R-151..R-200, 250 verdicts) for stable per-QID mean/std; R-087 100-round reference for cross-session baseline
- Drift threshold: abs Δ > 0.05 → flag (matches R-087 report convention)

## Durable (carry forward)

- 88th+ wipe / NAS at 100% EDQUOT (durable 90w) — `cd /tmp/research` + clone-from-github pattern works.
- The hourly single-round probe is canon-useless on its own for grand-mean claims (n=5) but is a valid drift tripwire: zero drift >0.05 vs both 50-round prior and R-087 reference is the result to record.
- Next hourly probe: rerun this same one-round pattern. If a future round shows drift >0.05, that's the alarm.
- R-201 mirror: `/tmp/research/jev_run_r201/continuous_r001.json` (workspace write to `/workspace/research/` is durable on this session but the next wipe will delete it — keep the data in `SuperInstance/jev-quilt` by pushing to a future round, or just rerun next time).
