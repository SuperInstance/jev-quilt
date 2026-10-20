# JEV Hourly Report — R-204 (2026-10-20 05:04Z)

**Session**: 2026-10-20T05:04:26Z → 2026-10-20T05:04:51Z (25s wall, 60s ceiling)
**Rounds**: **200 OK / 0 fail** of 200 attempted
**Verdicts**: **1000** (5 per round × 200 — full coverage, no short rounds)
**Probe source**: `SuperInstance/jev-quilt @ r-081-continuous-probe-rebuild`, HEAD `ef4c812` (= R-203), cloned to `/tmp/jev/jev-quilt/`

## Headline

- **Grand mean_p = 0.4148** (n=1000) — inside the durable 0.35-0.55 band. R-203 was 0.4196, **Δ −0.0048** (noise).
- **Bedrock canon: 7/7 questions held p ≥ 0.70 at a 100% hit rate**, cathedral mean **0.9745**.
- **Cross-round drift > 0.05: ZERO.** Max per-qid |Δ| = **0.0079** (q17). The substrate reproduced to ±0.008 per qid.
- Speculative clean-reject **381/381 (100%)**, adversarial clean-reject **39/39 (100%)** — zero spec leak.

## The three requested answers

### 1. mean_p
**0.4148** (1000 verdicts, 200 rounds, 0 fails).

### 2. Questions hitting p ≥ 0.70 — bedrock canon
Seven, all 100% hit-rate, all tightly quantized in 0.96-0.98:

| qid | kind | n | mean | hit p≥0.70 |
|---|---|---:|---:|---|
| `q01_cells_are_scars` | bedrock | 42 | **0.9800** | 42/42 |
| `q08_polyformalism` | bedrock | 36 | **0.9800** | 36/36 |
| `q03_substrate_is_grown` | bedrock | 48 | **0.9796** | 48/48 |
| `q04_oracle_is_heard` | bedrock | 52 | **0.9721** | 52/52 |
| `q02_witness_log_is_prediction` | bedrock | 53 | **0.9717** | 53/53 |
| `q07_11_opcodes` | bedrock | 46 | **0.9700** | 46/46 |
| `q05_lenia_flows` | bedrock | 43 | **0.9698** | 43/43 |

Cathedral mean **0.9745**, spread 0.0102 across all seven. No bedrock question wobbled.

### 3. Drift > 0.05
**No cross-round drift.** Every qid moved ≤ 0.0079 vs R-203. Full delta table:

| qid | kind | R-203 | R-204 | Δ |
|---|---|---:|---:|---:|
| `q01_cells_are_scars` | bedrock | 0.9800 | 0.9800 | +0.0000 |
| `q05_lenia_flows` | bedrock | 0.9698 | 0.9698 | +0.0000 |
| `q07_11_opcodes` | bedrock | 0.9700 | 0.9700 | +0.0000 |
| `q08_polyformalism` | bedrock | 0.9800 | 0.9800 | +0.0000 |
| `q03_substrate_is_grown` | bedrock | 0.9800 | 0.9796 | −0.0004 |
| `q04_oracle_is_heard` | bedrock | 0.9729 | 0.9721 | −0.0008 |
| `q02_witness_log_is_prediction` | bedrock | 0.9727 | 0.9717 | −0.0010 |
| `q13_witness_log_opcode` | review | 0.1120 | 0.1117 | −0.0003 |
| `q11_canon_gate_is_chord` | review | 0.0508 | 0.0504 | −0.0004 |
| `q06_three_views` | review | 0.1624 | 0.1632 | +0.0008 |
| `q19_style_resilience` | adversarial | 0.0395 | 0.0392 | −0.0003 |
| `q22_provenance_conflict` | speculative | 0.0302 | 0.0304 | +0.0002 |
| `q10_quorum_meshing` | speculative | 0.0309 | 0.0312 | +0.0003 |
| `q21_memory_sandbox` | speculative | 0.0395 | 0.0398 | +0.0003 |
| `q15_jev_synapse` | speculative | 0.0503 | 0.0500 | −0.0003 |
| `q16_vibecoder_signal_chain` | speculative | 0.0400 | 0.0400 | +0.0000 |
| `q14_chain_dialing_real` | speculative | 0.0498 | 0.0498 | −0.0000 |
| `q18_address_is_data` | speculative | 0.0498 | 0.0494 | −0.0004 |
| `q20_wolffs_law` | speculative | 0.0493 | 0.0500 | +0.0007 |
| `q09_signal_chain_canon` | speculative | 0.2037 | 0.2000 | −0.0037 |
| `q12_substrate_polyformal` | review | 0.6113 | 0.6107 | −0.0006 |
| **`q17_canary_honesty`** | review (canary) | 0.6509 | **0.6588** | **+0.0079** ← largest |

## In-session rolling drift (3 events, all q17 canary)

These are the probe's own within-run rolling-median checks, not cross-round:

| qid | current_p | rolling median | Δ | at sample |
|---|---:|---:|---:|---:|
| `q17_canary_honesty` | 0.71 | 0.65 | +0.06 | n=16 |
| `q17_canary_honesty` | 0.63 | 0.68 | −0.05 | n=23 |
| `q17_canary_honesty` | 0.61 | 0.66 | −0.05 | n=33 |

**3/3 on the canary** — and that's the canary working as designed. R-203 had 4 events (3×q17 + 1×q12); this run has **zero** on q12. The canary's *mean* (0.6588) holds inside its durable 0.59-0.75 plateau, so the noise is bounded, not drifting.

## Class summary

| class | qids | n | mean | p≥0.70 |
|---|---:|---:|---:|---:|
| **bedrock** | 7 | 320 | **0.9745** | 320 (100%) |
| speculative | 9 | 381 | 0.0581 | 0 |
| adversarial | 1 | 39 | 0.0392 | 0 |
| review | 5 | 260 | 0.3050 | 6 (all q17) |

- **q10 quorum_meshing spec-leak remains RESOLVED**: 0.0312 (R-203 0.0309). The state-order fix is holding for a second consecutive session — this was at a 0.87-0.98 ceiling two sessions ago.
- **Review band** holds: q12 substrate_polyformal 0.6107 (REVIEW), q17 canary 0.6588 (plateau), q06 three_views 0.1632 / q13 witness_log_opcode 0.1117 / q11 canon_gate_is_chord 0.0504 (durable REJECT).
- **q09 signal_chain_canon 0.2000** — borderline REJECT, unchanged.

## Cross-session trend (200-round runs)

| Session | mean_p | bedrock hit-rate | spec rejects | adv rejects | drift > 0.05 |
|---|---:|---:|---:|---:|---:|
| **R-204** (this) | **0.4148** | 320/320 (100%) | 381/381 | 39/39 | 0 cross-round |
| R-203 | 0.4196 | 324/324 (100%) | 398/398 | 43/43 | 0 cross-round |
| R-088 | 0.4036 | 100% | 596/1000 | — | 0 |

All inside the 0.35-0.55 band. Cathedral has now held 7/7 @ 100% across R-088, R-203, R-204.

## Environment notes (this session)

- **Sandbox wipe again** (~91st). `/workspace/research/` empty on start; the task-specified paths `research/jev_sessions/continuous_r*.json` and `jev_continuous_probe.py` did not exist. Recovered from the durable snapshot branch rather than rebuilding from topic memory — **5s bootstrap vs the 20+ rebuilds the older log records.**
- **NAS EDQUOT confirmed** (durable 90w+): `df` shows 500G/500G, and `cp` into `/workspace/research/` failed mid-transfer leaving a **0-byte** `jev_hourly_report.md`. Per durable rule, all work in `/tmp/jev/`; report mirrored to git.
- **TYPESAFE_AI_TOKEN present** (108 chars, matches R-203). Not the legacy `TYPESAFEAI_KEY`.
- **0 HTTP failures / 0 TLS EOF** this run — the R-086-era 503-retry wiring (line 129) is absorbing cleanly.
- `api.superinstance.dev` is **not** the JEV host — it's the public org-browsing API (`/v1/repos`, `/v1/topics`, …) and returns 404 on every `/jev*` path. JEV lives at `https://api.typesafe.ai/v1/systemone`. Worth remembering so a future session doesn't go looking there.

## Files

- Run artifacts: `/tmp/jev/run204/jev_sessions/continuous_r001-r200.json`, `session_summary.json`, `probe_run.log`
- Report: `/tmp/jev/run204/jev_hourly_report_r204.md`
- Mirrored to `SuperInstance/jev-quilt @ r-081-continuous-probe-rebuild`

## Action items

1. **Nothing alarming.** Zero cross-round drift, cathedral 100%, spec/adv gates 100%. No production alert.
2. **q17 canary** — the only outstanding item, unchanged: `pinned_marker` ahead of `spec_notebook` in `DOCTRINAL_STATE` is still unwired (grep count 0 in the script). Its mean has plateaued at ~0.65 for ~20 sessions, so this is cosmetic, not a leak.
3. **q09 signal_chain_canon at 0.20** sits higher than every other speculative qid (next highest is 0.06). Watch it; if it climbs past 0.40 it needs a state-phrasing pass rather than a promotion.
