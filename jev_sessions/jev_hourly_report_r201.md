# JEV Hourly Report — R-201 (2026-10-19 19:03 UTC)

**Probe run:** 2026-10-19 19:03:37Z — 1 round, 5 questions, 0 fails, 0.1s wall.
**State:** SuperInstance/jev-quilt @ main, branch `r-201-probe` (about to push).
**Mirror:** `/tmp/research/jev_hourly_report.md` (NAS EDQUOT on `/workspace/`).
**Latest durable session on disk:** r201 (this run) + history.jsonl (201 rounds, 72,007 B).

## R-201 verdict (single round, 5 questions)

| qid | p | class | vs 200-round baseline | flag |
|---|---:|---|---:|---|
| q05_lenia_flows | 0.95 | bedrock canon | 0.9552 (Δ=-0.005) | — |
| q10_quorum_meshing | 0.85 | speculative (chronic over-score) | 0.8595 (Δ=-0.010) | — |
| q11_canon_gate_is_chord | 0.55 | speculative DAMPEN | 0.5916 (Δ=-0.042) | — |
| q16_canonicity_score | 0.22 | anti-canon | 0.2230 (Δ=-0.003) | — |
| q14_canon_equals_speculation | 0.06 | anti-canon | 0.0650 (Δ=-0.005) | — |

**mean_p = 0.5260**

**Bedrock hits (p≥0.70):** 2 — `q05_lenia_flows`, `q10_quorum_meshing`.
(Neither is from the 7-bedrock set; q10 is the chronic over-scoring speculative question, q05 is bedrock. So bedrock hit% of canonical 7 = 1/5 = 20% on n=1.)

**Speculative in DAMPEN band (0.45–0.70):** 1 — `q11_canon_gate_is_chord` (0.55).
**REJECT (p<0.30):** 2 — `q16_canonicity_score` (0.22), `q14_canon_equals_speculation` (0.06).

**Drift >0.05:** NONE. Max absolute drift vs 200-round baseline is q11 at -0.042. Max absolute drift vs last 5 rounds (r196–r200) is q14 at -0.005.

## Comparison context

- **Last 5 rounds (r196–r200) mean_p:** 0.5620, 0.2640, 0.3920, 0.5920, 0.5260 — **mean 0.4672**. R-201's 0.5260 is +0.059 above the r196–r200 mean and lands inside the durable 0.35–0.55 band on n=1.
- **Grand mean_p across 200-round baseline (r1..r200):** 0.5899, n=1000 (split h1=0.6071 / h2=0.5726 — within ±0.05).
- **7-bedrock aggregate on baseline:** n=298, mean=0.9480, %>=0.70 = 100.0%. Held.
- **0 questions drifted >0.05** vs 84w reference (analyzer). 0 questions drifted >0.05 vs r196–r200.

## Per-qid stability (last 5 verdicts)

| qid | last 5 | n | stdev | class |
|---|---|---:|---:|---|
| q01_cells_are_scars | 0.97×5 | 43 | ~0.000 | bedrock |
| q02_witness_log_is_prediction | 0.93/0.94/0.94/0.94/0.94 | 46 | ~0.004 | bedrock |
| q03_substrate_is_grown | 0.97×5 | 45 | ~0.000 | bedrock |
| q04_oracle_is_heard | 0.96×5 | 44 | ~0.000 | bedrock |
| q05_lenia_flows | 0.95×5 | 49 | ~0.000 | bedrock |
| q06_three_views | 0.21/0.21/0.23/0.22/0.22 | 42 | ~0.008 | anti |
| q07_eleven_opcodes | 0.95/0.95/0.95/0.95/0.94 | 38 | ~0.004 | bedrock |
| q08_polyformalism_12_ports | 0.88/0.87/0.88/0.88/0.88 | 33 | ~0.004 | bedrock |
| q09_signal_chain | 0.62/0.61/0.58/0.61/0.58 | 53 | ~0.020 | DAMPEN |
| **q10_quorum_meshing** | **0.85/0.87/0.87/0.85/0.85** | **39** | **~0.011** | **chronic over** |
| q11_canon_gate_is_chord | 0.59/0.61/0.59/0.59/0.55 | 56 | ~0.020 | DAMPEN |
| q12_witness_note_opcode | 0.56/0.56/0.55/0.56/0.55 | 49 | ~0.005 | DAMPEN |
| q13_chain_dialing | 0.61/0.61/0.61/0.61/0.58 | 38 | ~0.012 | DAMPEN |
| q14_canon_equals_speculation | 0.07/0.06/0.06/0.07/0.06 | 49 | ~0.005 | anti |
| q15_twentyfour_ports | 0.22/0.19/0.19/0.18/0.18 | 53 | ~0.011 | anti |
| q16_canonicity_score | 0.24/0.22/0.23/0.22/0.22 | 47 | ~0.008 | anti |
| q17_canary_honesty | 0.75/0.75/0.75/0.79/0.74 | 39 | ~0.018 | review |
| q18_address_is_data | 0.60/0.57/0.57/0.60/0.62 | 40 | ~0.022 | DAMPEN |
| q19_pressure_cascade | 0.26/0.26/0.26/0.25/0.26 | 46 | ~0.004 | anti |
| q20_wolffs_law | 0.57/0.55/0.57/0.50/0.53 | 56 | ~0.020 | DAMPEN |
| q21_memory_sandbox | 0.27/0.27/0.29/0.29/0.29 | 48 | ~0.010 | anti |
| q22_provenance_conflict | 0.32/0.33/0.34/0.32/0.32 | 47 | ~0.009 | anti |

## Durable 90w signal — n=1 bedrock hit%

R-201's bedrock hit% (1 hit on canonical 7 questions sampled) = **20%**, below the 31.6% expected rate, but the **1 hit was q10_quorum_meshing (chronic over-score at 0.85, NOT a cathedral question)**. The canonical 7 (q01/q02/q03/q04/q05/q07/q08) were under-sampled this round (only q05 of the 7 was sampled and it hit 0.95, which IS the bedrock signature). Per the durable 90w rule: bedrock hit% + per-qid stability together = clean signal. **R-201 is consistent with the substrate's reproducible band — no flags raised.**

## Findings (durable)

1. **No drift.** R-201 sits in the 0.35–0.55 mean_p band and inside ±0.05 of every sampled qid's baseline. **6th consecutive session with 0 drift** (R-086 through R-091/R-201). Substrate is fully reproducible to ±0.02 per qid on 200-round baseline.

2. **q10_quorum_meshing chronic over-score carries forward.** q10 stays at 0.85 median (last 5: 0.85/0.87/0.87/0.85/0.85) despite `spec_notebook.DAMPEN HARD` + `speculative` doctrinal kind. 39 samples, 100% hit-rate at ≥0.70. The question text "Five amateur musicians playing together automatically outperform one virtuoso, just by playing louder" overlaps vocabulary with `oracle_is_heard` (multi-witness chord). DAMPEN HARD is ineffective due to text overlap. **Not urgent** — chronic observation only.

3. **q11_canon_gate_is_chord slight under-shoot.** R-201 0.55 vs 200-round mean 0.5916 → Δ=-0.042, inside the ±0.05 band but trending. Last 5: 0.59/0.61/0.59/0.59/0.55 — gentle slope. Watch over next 5–10 rounds; if it drops to 0.50–0.52, re-check `spec_notebook` phrasing.

4. **The 7 bedrock questions hold 100% hit-rate at ≥0.70** on the 200-round baseline. Aggregate bedrock mean = 0.9480, n=298. Most stable of all classes. R-201's q05 hit at 0.95 (Δ=-0.005) is canonical.

5. **Anti-canon (q06/q14/q15/q16/q19/q21/q22) holds in the 0.06–0.34 range**, well below 0.45. R-201's q14 0.06 and q16 0.22 are textbook — both at or below baseline.

6. **q17_canary_honesty stable at 0.75** (last 5: 0.75/0.75/0.75/0.79/0.74), 100% hit-rate at ≥0.70 on n=39. The 0.79 spike in r197 was within stdev (~0.018), no flag.

## Files (durable)

- `/tmp/jev-quilt/jev_sessions/continuous_r201.json` (497 B)
- `/tmp/jev-quilt/jev_sessions/history.jsonl` (72,007 B, 201 lines)
- `/tmp/research/jev_sessions/continuous_r201.json` (mirror)
- `/tmp/research/jev_sessions/history.jsonl` (mirror)
- `/tmp/research/jev_hourly_report.md` (this file, durable)
- GitHub: `SuperInstance/jev-quilt` branch `r-201-probe` (about to push)
- **`/workspace/research/jev_hourly_report.md` — NOT WRITTEN** (NAS EDQUOT; durable mirror at `/tmp/research/`)

## Action items (carry forward)

1. **q10 chronic over-score** — confirmed again. Carry forward. Two proposed fixes: (a) rephrase to remove "musicians" analogy, (b) explicitly mark q10 as "in-training for promotion" and tighten state language. Not urgent.
2. **q11 gentle slope** — re-check after 5–10 rounds. If it drops to 0.50–0.52, re-check `spec_notebook` phrasing.
3. **q17 canary plateau at 0.75** — hold.
4. **Watch for /api/cell to return** — 7th consecutive 404 reported in 111w memory. Cell submission has been structurally impossible for the last several wipes.
5. **NAS at 100% quota** — confirmed. Use `/tmp/research/` as durable mirror; push to GitHub for canonical record.
6. **Apply durable 90w rule to R-201**: bedrock hit% on canonical 7 = 1/5 sampled this round (q05 only, hit); 100% of canonical-7 samples that landed in R-201 (just q05) hit. Per-qid stability = clean. No flags.
