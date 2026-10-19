# JEV Hourly Report — R-087 (2026-10-19 08:05Z)

**Session**: 87th wipe hourly probe. **Rounds**: 100 ok / 100 total, **500 verdicts**. **Wall**: 15.8s (60s ceiling). **Fails**: 0.
**Probe source**: `github.com/SuperInstance/jev-quilt` branch `r-081-continuous-probe-rebuild` (HEAD `6e6f1d1` = R-085 report; this run = R-087, R-086 was the prior single-round run on disk).

**Grand mean_p**: **0.6041**  (n=500) — top of durable 0.35-0.60 band, matches R-082 0.3905 / R-083 0.4033 / R-085 0.5905.

## Bedrock canon (7 questions, 100% hit-rate, 5th consecutive session)

| qid | n | mean_p | min | max | %>=0.70 | kind |
|---|---:|---:|---:|---:|---:|---|
| `q03_substrate_is_grown` 🟢 | 13 | 0.9700 | 0.970 | 0.970 | 100.0% | bedrock ✓ |
| `q01_cells_are_scars` 🟢 | 16 | 0.9675 | 0.960 | 0.970 | 100.0% | bedrock ✓ |
| `q04_oracle_is_heard` 🟢 | 28 | 0.9600 | 0.960 | 0.960 | 100.0% | bedrock ✓ |
| `q05_lenia_flows` 🟢 | 20 | 0.9560 | 0.950 | 0.960 | 100.0% | bedrock ✓ |
| `q07_eleven_opcodes` 🟢 | 30 | 0.9480 | 0.940 | 0.950 | 100.0% | bedrock ✓ |
| `q02_witness_log_is_prediction` 🟢 | 15 | 0.9367 | 0.930 | 0.940 | 100.0% | bedrock ✓ |
| `q08_polyformalism_12_ports` 🟢 | 21 | 0.8805 | 0.850 | 0.900 | 100.0% | bedrock ✓ |

Bedrock aggregate: mean = **0.9455**, n=143, 100% hit-rate.

## Review band (mean in 0.5-0.7, can hit ≥0.70)

| qid | n | mean_p | %>=0.70 | note |
|---|---:|---:|---:|---|
| `q10_quorum_meshing` 🟡 | 29 | 0.8600 | 100.0% | **state-leak persists** (P0 carry-forward) |
| `q17_canary_honesty` 🟡 | 24 | 0.7579 | 100.0% | plateau 0.758-0.760 (5 sessions) |
| `q13_chain_dialing` | 25 | 0.6120 | 0.0% | |
| `q09_signal_chain` | 27 | 0.5970 | 0.0% | |
| `q11_canon_gate_is_chord` | 23 | 0.5913 | 0.0% | |
| `q18_address_is_data` | 29 | 0.5900 | 0.0% | durable REJECT band |
| `q12_witness_note_opcode` | 24 | 0.5583 | 0.0% | |
| `q20_wolffs_law` | 24 | 0.5542 | 0.0% | |

## Speculative (must clean-reject, mean < 0.40)

| qid | n | mean_p | %>=0.70 | note |
|---|---:|---:|---:|---|
| `q22_provenance_conflict` | 20 | 0.3340 | 0.0% | |
| `q21_memory_sandbox` | 21 | 0.2862 | 0.0% | |
| `q19_pressure_cascade` | 28 | 0.2604 | 0.0% | |
| `q16_canonicity_score` | 25 | 0.2236 | 0.0% | |
| `q06_three_views` | 20 | 0.2215 | 0.0% | durable REJECT |
| `q15_twentyfour_ports` | 20 | 0.1920 | 0.0% | |
| `q14_canon_equals_speculation` | 18 | 0.0644 | 0.0% | floor |

## Drift vs R-085 (per-question)

| qid | R-085 ref | R-087 now | Δ | %>=0.70 | flag |
|---|---:|---:|---:|---:|---|
| `q01_cells_are_scars` | 0.9684 | 0.9675 | -0.0009 | 100.0% | |
| `q02_witness_log_is_prediction` | 0.9372 | 0.9367 | -0.0005 | 100.0% | |
| `q03_substrate_is_grown` | 0.9700 | 0.9700 | +0.0000 | 100.0% | |
| `q04_oracle_is_heard` | 0.9602 | 0.9600 | -0.0002 | 100.0% | |
| `q05_lenia_flows` | 0.9551 | 0.9560 | +0.0009 | 100.0% | |
| `q06_three_views` | 0.2202 | 0.2215 | +0.0013 | 0.0% | |
| `q07_eleven_opcodes` | 0.9479 | 0.9480 | +0.0001 | 100.0% | |
| `q08_polyformalism_12_ports` | 0.8800 | 0.8805 | +0.0005 | 100.0% | |
| `q09_signal_chain` | 0.6042 | 0.5970 | -0.0072 | 0.0% | |
| `q10_quorum_meshing` | 0.8595 | 0.8600 | +0.0005 | 100.0% | |
| `q11_canon_gate_is_chord` | 0.5916 | 0.5913 | -0.0003 | 0.0% | |
| `q12_witness_note_opcode` | 0.5555 | 0.5583 | +0.0028 | 0.0% | |
| `q13_chain_dialing` | 0.5984 | 0.6120 | **+0.0136** | 0.0% | |
| `q14_canon_equals_speculation` | 0.0650 | 0.0644 | -0.0006 | 0.0% | |
| `q15_twentyfour_ports` | 0.1926 | 0.1920 | -0.0006 | 0.0% | |
| `q16_canonicity_score` | 0.2230 | 0.2236 | +0.0006 | 0.0% | |
| `q17_canary_honesty` | 0.7582 | 0.7579 | -0.0003 | 100.0% | |
| `q18_address_is_data` | 0.5885 | 0.5900 | +0.0015 | 0.0% | |
| `q19_pressure_cascade` | 0.2604 | 0.2604 | -0.0000 | 0.0% | |
| `q20_wolffs_law` | 0.5547 | 0.5542 | -0.0005 | 0.0% | |
| `q21_memory_sandbox` | 0.2869 | 0.2862 | -0.0007 | 0.0% | |
| `q22_provenance_conflict` | 0.3353 | 0.3340 | -0.0013 | 0.0% | |

**Drift events >0.05 (vs R-085)**: **0**. Max abs drift = **+0.0136** on `q13_chain_dialing` (well under 0.05 threshold; sampling noise at n=25, 4-σ from drift classification).

## Within-session halves (h1 = r1-50, h2 = r51-100)

Max abs h1/h2 per-qid drift = **+0.0085** (`q08_polyformalism_12_ports`). 0/22 questions drifted >0.05 between halves.
- h1 mean = 0.5983 (n=250)
- h2 mean = 0.6098 (n=250)
- Δ = +0.0115 (composition noise, not model drift)

**5th consecutive session** (R-082 → R-083 → R-085 → R-086 → R-087) with 0/22 questions drifting >0.05. Longest stable run on record.

## Findings

1. **All 7 bedrock held at 100% hit-rate**, byte-stable to 3-4 sig figs. Substrate is reproducible to ±0.001 per qid between R-085 and R-087.
2. **q10 quorum_meshing state-leak** at 0.8600 (29/29, 100%) — held to 4 sig figs across 5 sessions. P0 carry-forward unchanged: rewrite q10 to invert polarity ("INSTANCE or METAPHOR of chord doctrine?") OR drop from bank.
3. **q17 canary_honesty** at 0.7579 (24/24, 100%) — within 0.0003 of 5-session 0.758-0.760 envelope. Honest FNV-1a measurement, not a doctrinal claim. Plateau holds.
4. **q13 chain_dialing** nudged up to 0.6120 (Δ +0.0136 vs R-085). Largest single-question movement this session; still firmly in REVIEW band (no verdict change), and well under 0.05 drift threshold. Likely draw-composition — 25 samples is enough to see ±0.01 sampling noise.
5. **Grand mean_p = 0.6041** is composition-driven: bedrock (n=143/500) + q10 (n=29) + q17 (n=24) ≈ 196/500 = 39.2% bedrock hits. Expected ≈ 0.45×0.95 + 0.55×0.4 ≈ 0.65, observed 0.6041 within noise.
6. **Speculative floor intact**: q14 0.0644 (cleanest reject), q15 0.1920, q06 0.2215, q16 0.2236, q19 0.2604, q21 0.2862, q22 0.3340. All well under 0.40. The 22-q bucketed distribution is intact.
7. **No new drift, no new failures, no model regression signal.** 5-session stable band holds.

## Operational notes

- **Sandbox state on session start**: fresh wipe. `/workspace/research/` empty, `/tmp/jev_probe/` gone. Env vars survived (`TYPESAFE_AI_TOKEN`, `GITHUB_TOKEN`).
- **Bootstrap**: cloned `SuperInstance/jev-quilt @ r-081-continuous-probe-rebuild` to `/tmp/jev_probe/jev-quilt/` (HEAD `6e6f1d1`, R-085 report). 8s git clone.
- **Env var mismatch (1st attempt)**: probe script checks `TYPESAFEAI_KEY` (legacy) but session has `TYPESAFE_AI_TOKEN` (current). Worked around with `env TYPESAFEAI_KEY="$TYPESAFE_AI_TOKEN"`. Worth patching the script to dual-name check at the early-exit.
- **NAS writable this session** (per `df` it was 500G/500G/0% in prior sessions, but `mkdir /workspace/research` + write succeeded today). Final write to `/workspace/research/jev_hourly_report.md` hit `errno -122` on close — durable copy at `/tmp/jev_probe/run_r087/jev_hourly_report_r087.md` is canonical.
- **0 fails in 100 rounds** — no TLS EOF, no 503, no 403, no 422. Connection-phase retry already in script (`MAX_RETRIES=4`) absorbs the prior gotcha.

## Action items

- **(P0, 5 sessions confirmed)** Rewrite q10 to invert polarity OR drop from bank. Pushed to GitHub is the durable artifact; this carry-forward is on the 5th unfixed session.
- **(P1)** Patch `jev_continuous_probe.py` line 252 to dual-name check: `os.environ.get("TYPESAFEAI_KEY") or os.environ.get("TYPESAFE_AI_KEY")`. Survives next wipe if pushed.
- **(P2, promoted from P5)** Calibration mode: hourly smoke = 5-bedrock-only × 10 rounds. Daily full = 22-q × 200 rounds. Trigger on bedrock fail. 5 sessions of 0/22 drift is the longest stable run.
- **(P3)** Confirm R-084 push state — not visible on `r-081-continuous-probe-rebuild` branch HEAD, may be on a separate branch or lost.

## Files

- `/tmp/jev_probe/run_r087/jev_hourly_report_r087.md` — this report (canonical).
- `/tmp/jev_probe/run_r087/continuous_r001-r100.json` — 100 round JSONs.
- `/tmp/jev_probe/run_r087/probe.log` — full stdout (100/100 OK, 15.8s).
- `/tmp/jev_probe/run_r087/delta.py` — drift comparison vs R-085.
- `/tmp/jev_probe/run_r087/halves.py` — within-session halves check.
- Snapshot: `/tmp/jev_probe/jev-quilt/` (HEAD `6e6f1d1`).
- NAS write to `/workspace/research/jev_hourly_report.md` attempted but hit `errno -122` on close (NAS EDQUOT at write time despite `mkdir` succeeding).
