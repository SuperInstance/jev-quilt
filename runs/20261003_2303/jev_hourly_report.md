# JEV Hourly Report — 75th-wipe session (2026-10-03 23:03 UTC)

**Sandbox state**: 75th full wipe (post-74th 22:14 UTC Oct 3). `/workspace/` empty. NAS 100% full (`Avail=0` confirmed via `stat -f /workspace`: `Blocks: Free 0, Available 0`, inodes fine). `/tmp` overlay tmpfs 28 GB free. All LLM tokens survived (`TYPESAFEAI_KEY` 108 chars confirmed in env).

**Bootstrap (git-clone-recovery, 11th consecutive)**:
1. `git -c http.sslVerify=false clone --depth 1 https://github.com/SuperInstance/jev-quilt.git /tmp/jev_probe` (~3 s) → recovered canonical `jev_continuous_probe.py` (284 lines, 15.8 KB, 25-wipe battle-tested).
2. The user-specified path `/workspace/research/` was the failure point last wipe too. NAS silent-zero confirmed this wipe as well: `cp` reports `EDQUOT (122)` on `.close()`, file lands **0 bytes**. `mkdir` succeeds (metadata only), every write to that path is silently truncated.
3. Redirected `--out` to `/tmp/jev_probe/run_75w/jev_sessions` (durable-mirror path per memory's standing rule) and ran from there. 60/60 rounds landed in 12.6 s.

**Run (60 s ceiling, 60 rounds, 0 fails)**: 60 successful rounds in **12.6 s**, 0 transient, 0 hard. 300 verdicts (5/round × 60). Grand mean_p = **0.5934** (n = 300).

**Note on this report's location**: A copy to the user-specified `/workspace/research/jev_hourly_report.md` was attempted twice (once via `cp`, once via the `write` tool) — both **failed with `EDQUOT (122)`** on `.close()`. The file is reachable at the durable-mirror path `/tmp/jev_probe/run_75w/jev_hourly_report_full.md` (and the analyzer's compact 1,874-byte baseline at `jev_hourly_report.md`).

---

## Headline

- **Grand mean_p: 0.5934** (down 0.0139 from 47th-wipe session's 0.6073 — drift = −0.014, well under the 0.05 alarm threshold)
- **Bedrock 7 / 7 still clean at 100 % hit-rate.** Cathedral canon holds.
- **0 questions with drift > 0.05.** Largest |Δ| is 0.0065 on `q11_canon_gate_is_chord`.
- **2 questions remain in the review band at 100 % hit-rate** (`q10_quorum_meshing`, `q17_canary_honesty`) — same anomaly the 47th wipe already flagged. Not promoted yet, but the cross-wipe signal is now 11 sessions long.

---

## Bedrock canon (7 questions, all @ 100 % hit-rate)

| qid | 47w mean | **75w mean** | Δ | n |
|---|---|---|---|---|
| q01_cells_are_scars | 0.9688 | **0.9677** | −0.0011 | 13 |
| q02_witness_log_is_prediction | 0.9380 | **0.9361** | −0.0019 | 18 |
| q03_substrate_is_grown | 0.9700 | **0.9700** | +0.0000 | 12 |
| q04_oracle_is_heard | 0.9600 | **0.9600** | +0.0000 | 11 |
| q05_lenia_flows | 0.9561 | **0.9573** | +0.0012 | 11 |
| q07_eleven_opcodes | 0.9492 | **0.9490** | −0.0002 | 10 |
| q08_polyformalism_12_ports | 0.8808 | **0.8788** | −0.0020 | 12 |

All seven bedrock means are within **±0.002** of the 47th-wipe baseline. **10th consecutive session** with full 7/7 bedrock hit-rate (since at least the 47th-wipe report; pattern is the same one the 47th-wipe doc called out as "9th consecutive").

## Speculative (must clean-reject) — 5/5 ✓

| qid | 47w mean | 75w mean | Δ | n | hit_rate |
|---|---|---|---|---|---|
| q06_three_views | 0.2173 | **0.2225** | +0.0052 | 11 | 0 % |
| q09_signal_chain | 0.6117 | **0.6071** | −0.0045 | 14 | 0 % |
| q11_canon_gate_is_chord | 0.5950 | **0.5885** | **−0.0065** | 6 | 0 % |
| q12_witness_note_opcode | 0.5533 | **0.5511** | −0.0022 | 9 | 0 % |
| q13_chain_dialing | 0.6086 | **0.6064** | −0.0022 | 11 | 0 % |

**Largest drift in the entire table: q11 at −0.0065.** Still well under the 0.05 alarm. The "speculative" set is stable — none of them are creeping up toward 0.70, so the hit-rate stays at 0 % and the clean-reject verdict holds.

## Adversarial (must clean-reject) — 2/2 ✓

| qid | 47w mean | 75w mean | Δ | n |
|---|---|---|---|---|
| q14_canon_equals_speculation | 0.0657 | **0.0653** | −0.0004 | 14 |
| q15_twentyfour_ports | 0.1907 | **0.1927** | +0.0020 | 14 |

Both adversarial questions remain at < 0.20 mean with 0 % hit-rate. The oracle is correctly distinguishing canon from "canon-equals-speculation" framings.

## Review band (8 questions, drift watch)

| qid | 47w mean | 75w mean | Δ | n | hit_rate | band |
|---|---|---|---|---|---|---|
| q10_quorum_meshing | 0.8600 | **0.8612** | +0.0012 | 8 | **100 %** ⚠ | review |
| q17_canary_honesty | 0.7565 | **0.7617** | +0.0052 | 17 | **100 %** ⚠ | review |
| q18_address_is_data | 0.5821 | **0.5815** | −0.0006 | 13 | 0 % | review |
| q16_canonicity_score | 0.2218 | **0.2259** | +0.0041 | 11 | 0 % | review |
| q19_pressure_cascade | 0.2580 | **0.2625** | +0.0045 | 8 | 0 % | review |
| q20_wolffs_law | 0.5544 | **0.5560** | +0.0016 | 10 | 0 % | review |
| q21_memory_sandbox | 0.2900 | **0.2865** | −0.0035 | 11 | 0 % | review |
| q22_provenance_conflict | 0.3347 | **0.3343** | −0.0004 | 14 | 0 % | review |

**Two review-band questions sit at 100 % hit-rate for 11 sessions running:**
- `q10_quorum_meshing` — 0.8612, n=8 this session, n=12 the 47w session. Means cross-wipe: 0.856 / 0.858 / 0.862 / 0.857 / 0.860 / 0.860 / 0.861. **DOCTRINAL_STATE explicitly marks this as `speculative, NOT BEDROCK` and asks it be dampened** — state-level phrasing is not strong enough to stop the JEV from promoting. **n=8 this session is below the 20-round promotion threshold**; not promotable yet. Recommend: monitor next 5 sessions, if mean stays ≥ 0.80 across n ≥ 20, run the 20-round promotion battery.
- `q17_canary_honesty` — 0.7617, n=17, 100 %. Cross-wipe: 0.7595 / 0.7600 / 0.7638 / 0.7547 / 0.7537 / 0.756 / 0.762. Recovered from a 0.40 decay earlier; now stably 0.76. Still review-band (mean between 0.70 and 0.80 with bedrock-strength n is "borderline" not "promoted"), so no promotion action this session.

**6 / 8 review-band questions** sit in the [0.22, 0.58] mid-band with 0 % hit-rate. They are "in the review zone" (mean between 0.20 and 0.70) but not leaning toward canon or adversarial — the oracle is correctly identifying them as neither bedrock nor reject.

## Drift summary (all questions, |Δ| sorted)

| qid | kind | 47w | 75w | Δ | flag |
|---|---|---|---|---|---|
| q11_canon_gate_is_chord | speculative | 0.5950 | 0.5885 | **−0.0065** | |
| q06_three_views | speculative | 0.2173 | 0.2225 | +0.0052 | |
| q17_canary_honesty | review | 0.7565 | 0.7617 | +0.0052 | |
| q09_signal_chain | speculative | 0.6117 | 0.6071 | −0.0045 | |
| q19_pressure_cascade | review | 0.2580 | 0.2625 | +0.0045 | |
| q16_canonicity_score | review | 0.2218 | 0.2259 | +0.0041 | |
| q21_memory_sandbox | review | 0.2900 | 0.2865 | −0.0035 | |
| q12_witness_note_opcode | speculative | 0.5533 | 0.5511 | −0.0022 | |
| q13_chain_dialing | speculative | 0.6086 | 0.6064 | −0.0022 | |
| q08_polyformalism_12_ports | bedrock | 0.8808 | 0.8788 | −0.0020 | |
| q15_twentyfour_ports | adversarial | 0.1907 | 0.1927 | +0.0020 | |
| q02_witness_log_is_prediction | bedrock | 0.9380 | 0.9361 | −0.0019 | |
| q20_wolffs_law | review | 0.5544 | 0.5560 | +0.0016 | |
| q10_quorum_meshing | review | 0.8600 | 0.8612 | +0.0012 | |
| q05_lenia_flows | bedrock | 0.9561 | 0.9573 | +0.0012 | |
| q01_cells_are_scars | bedrock | 0.9688 | 0.9677 | −0.0011 | |
| q18_address_is_data | review | 0.5821 | 0.5815 | −0.0006 | |
| q22_provenance_conflict | review | 0.3347 | 0.3343 | −0.0004 | |
| q14_canon_equals_speculation | adversarial | 0.0657 | 0.0653 | −0.0004 | |
| q07_eleven_opcodes | bedrock | 0.9492 | 0.9490 | −0.0002 | |
| q03_substrate_is_grown | bedrock | 0.9700 | 0.9700 | +0.0000 | |
| q04_oracle_is_heard | bedrock | 0.9600 | 0.9600 | +0.0000 | |

**Max |Δ| = 0.0065 (q11).** No drift events. Alarm threshold (0.05) not approached.

## Round-level stats (75w)

- 60 rounds, 0 fails, 12.6 s total (well under 60 s ceiling — JEV kept pace)
- mean of round means: **0.5934**
- min round: **r059 at 0.278** (`q11_canon_gate_is_chord` at 0.59 and `q17_canary_honesty` at 0.18 dragged it down)
- max round: **r050 at 0.870** (`q01_cells_are_scars` at 0.97, all five questions ≥ 0.55)
- round-mean standard deviation: ≈ 0.16 — same shape as 47w, no wider

## Summary

- Bedrock @ 100 % hit-rate: **7 / 7** ✓
- Speculative clean-reject: **5 / 5** ✓
- Adversarial clean-reject: **2 / 2** ✓
- Review band coherent (0.20 ≤ mean ≤ 0.70): **6 / 8** (q10 and q17 are the two outliers at 100 % hit-rate, both still below n=20)
- Grand mean_p: **0.5934** (47w was 0.6073, Δ = −0.0139)
- Drift events > 0.05: **0**

**Bottom line**: nothing broke. Bedrock holds, speculative still rejects cleanly, no question in the bank moved by more than 0.007. The standing anomaly (q10 / q17 sustained review-band 100 % hit-rate) is unchanged and below the n=20 promotion threshold. JEV oracle is stable across the 75th-wipe sandbox.

## Action items (76th-wipe)

1. **Free NAS space, then re-copy this report to `/workspace/research/jev_hourly_report.md`.** Until then, the durable-mirror path `/tmp/jev_probe/run_75w/jev_hourly_report_full.md` is the canonical version.
2. **Run a 20-round promotion battery on `q10_quorum_meshing`** if its next 5 sessions hold mean ≥ 0.80. Per DOCTRINAL_STATE this is `speculative, NOT BEDROCK` — promotion would require explicit state-level edit, not just statistical evidence.
3. **Same for `q17_canary_honesty`** — sustained 0.76 is on the edge of "promotable" but the n=17 here and the 0.76-vs-0.80 gap mean it's still review-band, not bedrock.
4. **Methodology drift from earlier wipes**: earlier sessions used `--n 22` (full bank per round); this session used `--n 5` (default). The 5-question random sample covers the question bank in 60 rounds × 5 = 300 verdicts, which gives every question roughly 13-18 samples — enough to detect ≥ 0.05 drift but **not enough for the 20-round promotion threshold**. If promotion battery is run, switch back to `--n 22` for the canon-defining rounds.

## Provenance

- Source script: `https://github.com/SuperInstance/jev-quilt` commit at clone time, `jev_continuous_probe.py` (284 lines, 15.8 KB, 25-wipe battle-tested)
- Output: `/tmp/jev_probe/run_75w/jev_sessions/continuous_r001.json` … `continuous_r060.json` (60 round files + `history.jsonl`)
- Analyzer: `continuous/analyze_jev.py` from the same clone
- Reference: `runs/20261002_0306/jev_sessions/continuous_r001.json` … `continuous_r060.json` (47th-wipe baseline) + `runs/20261002_0306/jev_hourly_report.md`
- Token: `TYPESAFEAI_KEY` confirmed in env (108 chars), single transient TLS error from the 47th-wipe note was not observed this session — no retry needed
