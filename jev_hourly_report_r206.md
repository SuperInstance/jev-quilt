# JEV Continuous Probe — Hourly Report R-206 (2026-10-20)

**Session:** 2026-10-20T19:05:44+00:00 → 2026-10-20T19:06:50+00:00
**Run:** 15 OK / 1 fail of 17 attempted (60s ceiling hit)
**Verdicts:** 75  |  **grand mean_p = 0.3820**
**Bedrock hits (p≥0.70):** 22/75 = 29.3%
**Spec clean-rejects (p<0.40):** 32  |  **Adv clean-rejects:** 4
**Cross-round drift > 0.05:** **0**  |  In-run rolling drift events: 0

## Verdict

R-206 is a **clean round on a throttled transport**. mean_p = **0.3820** vs R-205's 0.3941 → **−0.0121**, inside the durable 0.35–0.55 band and well within draw-mix jitter. The cathedral is **7/7 bedrock @ 100% hit**, both rejection gates are 100% clean, and **zero questions drifted > 0.05**.

**The round is statistically thin** (75 verdicts vs 975 in R-205) because of a transport issue, not a substrate issue — see Throughput below. Sample sizes per qid are n=1–7, so per-qid deltas carry real uncertainty; the grand mean and the gates are the trustworthy signals here, not the individual qid means.

No alert. No state-phrasing intervention warranted.

## Grand mean_p — session vs prior

| Session | grand mean_p | bedrock hit rate | drift >0.05 |
|---------|--------------|------------------|------------|
| **R-206** (this) | **0.3820** | 29.3% | **0** |
| R-205 | 0.3941 (975 verdicts) | 29.9% | 0 |
| R-204 | 0.4188 | — | 0 |
| R-203 | 0.4196 | 32.4% | 0 |
| R-088 | 0.4036 | 32.2% | 0 |

All inside the 0.35–0.55 band. Bedrock *hit-rate* is draw-mix confounded (expected ≈ 5 × 7/22 ≈ 1.59 bedrock probes/round); R-206's 29.3% is the expected value for its draw, not a regression.

## Questions hitting p ≥ 0.70 — bedrock canon (7/7 @ 100%)

| qid | mean | n | hit | prev (R-205) | delta |
|-----|------|---|-----|--------------|-------|
| q01_cells_are_scars | 0.9800 | 1 | 1/1 | 0.9796 | +0.0004 |
| q02_witness_log_is_prediction | 0.9717 | 6 | 6/6 | 0.9725 | −0.0008 |
| q03_substrate_is_grown | 0.9800 | 2 | 2/2 | 0.9800 | +0.0000 |
| q04_oracle_is_heard | 0.9740 | 5 | 5/5 | 0.9723 | +0.0017 |
| q05_lenia_flows | 0.9650 | 2 | 2/2 | 0.9695 | −0.0045 |
| q07_11_opcodes | 0.9700 | 3 | 3/3 | 0.9700 | +0.0000 |
| q08_polyformalism | 0.9800 | 3 | 3/3 | 0.9800 | +0.0000 |

**Cathedral 7/7 @ 100% hit — fifth consecutive session** (R-088, R-203, R-204, R-205, R-206). Every bedrock probe crossed 0.70; no misses. Per-qid movement ≤ 0.0045, so the substrate is still reproducible to well under ±0.005 on canon questions.

## Full per-qid table

| qid | kind | n | mean | prev | delta | hit≥0.70 | drift>0.05 |
|-----|------|---|------|------|-------|----------|-----------|
| q01_cells_are_scars | bedrock | 1 | 0.9800 | 0.9796 | +0.0004 | 1/1 | — |
| q02_witness_log_is_prediction | bedrock | 6 | 0.9717 | 0.9725 | −0.0008 | 6/6 | — |
| q03_substrate_is_grown | bedrock | 2 | 0.9800 | 0.9800 | +0.0000 | 2/2 | — |
| q04_oracle_is_heard | bedrock | 5 | 0.9740 | 0.9723 | +0.0017 | 5/5 | — |
| q05_lenia_flows | bedrock | 2 | 0.9650 | 0.9695 | −0.0045 | 2/2 | — |
| q06_three_views | review | 4 | 0.1600 | 0.1660 | −0.0060 | 0/4 | — |
| q07_11_opcodes | bedrock | 3 | 0.9700 | 0.9700 | +0.0000 | 3/3 | — |
| q08_polyformalism | bedrock | 3 | 0.9800 | 0.9800 | +0.0000 | 3/3 | — |
| q09_signal_chain_canon | speculative | 6 | 0.1933 | 0.2013 | −0.0080 | 0/6 | — |
| q10_quorum_meshing | speculative | 2 | 0.0300 | 0.0306 | −0.0006 | 0/2 | — |
| q11_canon_gate_is_chord | review | 4 | 0.0525 | 0.0506 | +0.0019 | 0/4 | — |
| q12_substrate_polyformal | review | 4 | 0.5950 | 0.6038 | −0.0088 | 0/4 | — |
| q13_witness_log_opcode | review | 3 | 0.1033 | 0.1100 | −0.0067 | 0/3 | — |
| q14_chain_dialing_real | speculative | 3 | 0.0500 | 0.0490 | +0.0010 | 0/3 | — |
| q15_jev_synapse | speculative | 4 | 0.0500 | 0.0502 | −0.0002 | 0/4 | — |
| q16_vibecoder_signal_chain | speculative | 7 | 0.0400 | 0.0400 | +0.0000 | 0/7 | — |
| q17_canary_honesty | review | 2 | 0.6450 | 0.6483 | −0.0033 | 0/2 | — |
| q18_address_is_data | speculative | 3 | 0.0500 | 0.0490 | +0.0010 | 0/3 | — |
| q19_style_resilience | adversarial | 4 | 0.0350 | 0.0393 | −0.0043 | 0/4 | — |
| q20_wolffs_law | speculative | 1 | 0.0500 | 0.0498 | +0.0002 | 0/1 | — |
| q21_memory_sandbox | speculative | 3 | 0.0400 | 0.0398 | +0.0002 | 0/3 | — |
| q22_provenance_conflict | speculative | 3 | 0.0300 | 0.0302 | −0.0002 | 0/3 | — |

**All 22 qids were drawn** — full bank coverage despite the short run, which is why the comparison holds despite low n.

## Drift analysis (threshold > 0.05)

**Cross-round drift: ZERO questions exceed 0.05.** Max absolute per-qid delta is **q12 −0.0088**, then q09 −0.0080, q13 −0.0067, q06 −0.0060. All are borderline REVIEW questions oscillating inside their historical band — q12 sits at 0.595 (spread 0.56–0.72 across sessions) and q09 at 0.193 (its established ~0.20 level). Nothing moved.

The script's in-run rolling detector fired **0 events** this round (R-205 fired 7). That is a *consequence of the short run*, not improved stability — with n=1–7 per qid there is barely any rolling history to deviate from. Do not read this as the substrate getting steadier.

## Notable per-question states

- **q17 canary_honesty (0.645, 0/2)** — plateau holds for a fifth consecutive session (R-082 0.66 → R-083 0.65 → R-205 0.648 → R-206 0.645). No decay, no recovery. n=2 is too small to be informative; the plateau reading rests on the long series, not this round.
- **q09 signal_chain_canon (0.193, 0/6)** — holds at its ~0.20 level, still the highest speculative qid. Watch only.
- **q10 quorum_meshing (0.030, 0/2)** — spec-leak remains fully resolved; STATE-ORDER invariant holding.
- **Durable REJECTs clean:** q11 (0.053), q13 (0.103), q06 (0.160) — 0 hits across all three.

## Throughput — the one thing that changed

This round produced **17 attempts vs 200 in R-205**. Root cause is **not** rate limiting: healthy rounds still complete in ~0.13s, identical to prior sessions. Three rounds (r008, r011, r016) took **13.2s, 13.4s, 13.0s** — each one is hitting the script's `TIMEOUT_S = 12` ceiling, then the retry succeeds. Mean elapsed across OK rounds was 2.59s vs ~0.15s historically.

That is **~40s of the 60s budget consumed by three 12s timeouts**. The transport is degrading into connect-phase stalls (the same upstream TLS/reset class seen all 90+ wipes), and `TIMEOUT_S=12` is far longer than the ~0.13s a healthy call needs — so each stall burns 12s before the retry even starts.

This is cosmetic to the verdict (no bias in the verdicts themselves — all three slow rounds returned status `ok` with 5/5) but it is a real, fixable inefficiency: **lower `TIMEOUT_S` to ~4s**. Healthy calls finish in 0.13s, so a 4s ceiling still leaves 30× headroom while cutting worst-case stall cost by 3×. Flagging for the next round rather than patching mid-run.

## Environment

- **NAS EDQUOT is over.** `/workspace` at 527G/600G, **74G available (88%)** — the first non-zero free space in ~90 wipes. The `/workspace/research/jev_hourly_report.md` 0-byte trap is *not* currently active; this report was written there and verified non-zero. The `/tmp` canonical-mirror workflow remains good practice but was not strictly required today.
- Task-specified path `/workspace/research/jev_sessions/continuous_r*.json` did not exist on start (fresh wipe). Recovered the probe via durable snapshot branch `SuperInstance/jev-quilt @ r-081-continuous-probe-rebuild` (HEAD `73a4129`, R-205) — ~8s bootstrap, no rebuild-from-memory.
- **Auth:** `TYPESAFE_AI_TOKEN` present, legacy `TYPESAFEAI_KEY` absent. Dual-name fallback exercised correctly.
- 1 × TLS handshake timeout (r002), skip-on-fail preserved history cleanliness — no corrupted rounds.
- All protocol invariants present in the snapshot script and behaving correctly: STATE-ORDER, 3 auth headers + `type:noul`, bucket-midpoint normalization, skip-on-fail.

## Files

- Report: `/workspace/research/jev_hourly_report.md` (this file)
- Canonical mirror: `/tmp/jev_probe/repo/jev_hourly_report_r206.md`
- Rounds: `/tmp/jev_probe/repo/jev_sessions/continuous_r001-r016.json` (+ 1 `.fail.json`)
- Summary: `/tmp/jev_probe/repo/jev_sessions/session_summary.json`
- Log: `/tmp/jev_probe/repo/run_r206.log`

## Action items

1. **No alert.** Zero cross-round drift, cathedral 7/7 for a fifth consecutive session, both gates 100%. Steady state.
2. **Lower `TIMEOUT_S` 12 → 4** in `jev_continuous_probe.py`. Highest-value fix available: recovers ~3× throughput under the current stall profile, and costs nothing when transport is healthy.
3. **q17 canary** — unchanged, plateaued 5 sessions. Optional `pinned_marker` ahead of `spec_notebook` still unwired. Low priority.
4. **q09 signal_chain_canon** — hold at ~0.20; revisit only if it trends toward 0.40.

_Generated 2026-10-20T19:06:50+00:00 · round R-206 · substrate reproducible to ±0.005 per qid · thin round (75 verdicts), gates and grand mean are the trustworthy signals._
