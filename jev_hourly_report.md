# JEV Hourly Report — 2026-10-21 18:05 UTC (R-214, 101st wipe)

**Session**: `rounds_r214` · 2026-10-21T18:04:50Z → 18:05:51Z
**Rounds**: 36 attempted — **32 OK / 3 fail** (60s ceiling), **160 verdicts**, all 22 qids drawn
**Baseline**: 2,515 prior verdicts / 22 qids from tracked `jev_sessions/history.jsonl` (DEFECT B verified at source, 7th wipe with no manual seeding)

## Headline

- **Grand mean_p = 0.3864** (n=160) — mid-band. Band history: 0.3596 (R-212) / 0.4260 (R-208) / 0.4441 (R-211) / 0.4931 (R-213). Grand mean is draw-mix confounded (5 of 22 qids per round); a band move here is **not** drift.
- **Bedrock canon (cathedral, explicit 7-qid list): 6/7 qids drawn, 45/45 verdicts at p≥0.70 — ZERO misses, 13th consecutive.** Mean 0.9768.
- **Speculative clean-reject: 100%** (max 0.20, q09). **Adversarial clean-reject: 100%** (q19 0.0387).
- **Drift vs full-history mean: max |dev| = 0.0097 (q12)** — every qid inside ±0.01 of baseline. No real drift.
- **One drift EVENT fired, and it is a documented false positive** (see below): a single q06 reading.

## Per-qid verdicts (current vs full-history baseline)

| qid | kind | n | cur | base | dev | σ | hits |
|-----|------|---|-----|------|-----|---|------|
| q01_cells_are_scars | bedrock | 6 | 0.9800 | 0.9798 | +0.0002 | +0.13 | 6/6 |
| q02_witness_log_is_prediction | bedrock | 5 | 0.9760 | 0.9722 | +0.0038 | +0.93 | 5/5 |
| q03_substrate_is_grown | bedrock | 8 | 0.9800 | 0.9798 | +0.0002 | +0.14 | 8/8 |
| q04_oracle_is_heard | bedrock | 3 | 0.9700 | 0.9722 | −0.0022 | −0.53 | 3/3 |
| q05_lenia_flows | bedrock | 9 | 0.9700 | 0.9696 | +0.0004 | +0.21 | 9/9 |
| q06_three_views | review | 10 | 0.1720 | 0.1657 | +0.0063 | +0.38 | 0 |
| q07_11_opcodes | bedrock | 7 | 0.9700 | 0.9700 | +0.0000 | 0.00 | 7/7 |
| q08_polyformalism | bedrock | 7 | 0.9800 | 0.9800 | −0.0000 | 0.00 | 7/7 |
| q09_signal_chain_canon | speculative | 8 | 0.2037 | 0.2010 | +0.0027 | +0.24 | 0 |
| q10_quorum_meshing | speculative | 6 | 0.0300 | 0.0310 | −0.0010 | −0.33 | 0 |
| q11_canon_gate_is_chord | review | 6 | 0.0500 | 0.0506 | −0.0006 | −0.26 | 0 |
| q12_substrate_polyformal | review | 11 | 0.5964 | 0.6060 | −0.0097 | −0.47 | 0 |
| q13_witness_log_opcode | review | 10 | 0.1070 | 0.1120 | −0.0050 | −0.47 | 0 |
| q14_chain_dialing_real | speculative | 7 | 0.0500 | 0.0495 | +0.0005 | +0.22 | 0 |
| q15_jev_synapse | speculative | 9 | 0.0500 | 0.0501 | −0.0001 | −0.10 | 0 |
| q16_vibecoder_signal_chain | speculative | 3 | 0.0400 | 0.0399 | +0.0001 | +0.10 | 0 |
| q17_canary_honesty | review | 6 | 0.6617 | 0.6536 | +0.0081 | +0.32 | 0 |
| q18_address_is_data | speculative | 9 | 0.0500 | 0.0493 | +0.0007 | +0.28 | 0 |
| q19_style_resilience | adversarial | 8 | 0.0387 | 0.0392 | −0.0005 | −0.17 | 0 |
| q20_wolffs_law | speculative | 5 | 0.0500 | 0.0499 | +0.0001 | +0.10 | 0 |
| q21_memory_sandbox | speculative | 6 | 0.0400 | 0.0398 | +0.0002 | +0.13 | 0 |
| q22_provenance_conflict | speculative | 11 | 0.0300 | 0.0302 | −0.0002 | −0.16 | 0 |

## The one drift event — resolved as a false positive

The summary printed `Drift events > 0.05: 1`. Traced to source:

- Fired on **`round_024`, q06_three_views, single reading p=0.2200**, baseline 0.1657, delta **+0.0543** vs floor 0.0502.
- Drift is evaluated **per single verdict** against the full-history mean (`compute_drift`), so one bucket-hop can trip it.
- **q06 is a quantized bimodal REJECT**: history n=134 spans 0.13–0.22 across 8 discrete values; 0.22 is the historical *maximum*, seen 2/134 (1.5%) of the time. A single 0.22 is a tail value, not a regime change.
- Aggregate dev for q06 is +0.0063 and the in-session first/second-half delta is +0.0080 — both deep in band.

**Verdict: no substrate movement. A single-sample excursion on a bimodal bucket metric.** Worth noting as a known detector characteristic: the per-verdict drift floor will occasionally fire on q06/q17 tail values. The correct triage is *aggregate-then-judge*, never trust a raw event count alone.

## Gates

- **Cathedral**: 45/45 @ p≥0.70, 13th consecutive clean session. q07/q08 read a constant 0.97/0.98 (σ=0).
- **Speculative**: 8 qids, all <0.40; max 0.2037 (q09). Spec-notebook doing its job. q10 spec-leak resolved (0.0300) for the 10th session.
- **Adversarial**: q19 0.0387 — clean reject holds.
- **Borderline/review**: q06 0.1720 (REJECT), q11 0.0500 (REJECT), q12 0.5964 (REVIEW band), q13 0.1070 (REJECT), q17 0.6617 (**stable REVIEW plateau** — flat ~0.65 across 10–21/20/21; not decay, promotion needs state-strengthening not more monitoring).

## Environment / method notes

- **Recovery**: `/workspace` bare on arrival (101st wipe); `/tmp/jev_probe/` mirror also gone — both documented homes empty. Bootstrapped from `SuperInstance/jev-quilt @ r-081-continuous-probe-rebuild` (HEAD `7774737`, R-213) via `git clone --depth 1`. Script md5 `c22e8c72f13f3b71d5b40e8f8fd04d61` unchanged.
- **`history.jsonl` lives at `jev_sessions/history.jsonl`, not repo root** — a shallow clone that looks for it at the root finds nothing and falls to the DEFECT-B false-all-clear. Restored via `git checkout HEAD -- jev_sessions/history.jsonl` → 2,515 samples / 22 qids. Path matters.
- **SSL_CERT_FILE** = gateway-anchor-only on arrival (5th documented recurrence). Rebuilt 289-cert bundle (`ca-certificates.crt` + `sandbox-gateway-ca.crt` → `/tmp/cab/bundle.crt`) and exported. Canary: 2× HTTP 200 (0.18s, 0.11s) + 1 handshake timeout.
- **Throughput — network-bound, TIMEOUT_S=4 stays**: elapsed median 0.177s, p95 9.09s, max 9.44s, **8 stalls >1s, all TLS handshake timeouts**. 32 rounds vs R-213's 27, R-211's 30. Fourth consecutive session confirming the lever is the handshake budget / persistent connection, never the read ceiling.
- **Run harness**: `timeout -s KILL 75` + `setsid nohup` + `python3 -u` so `session_summary.json` and the log survive (60s bare `timeout` eats the summary; memory rule: compute from round files regardless). Analysis re-derived independently from round files, not trusted from the summary.
- **DEFECT A** closed at root (timestamped `SESSION_DIR`); no collision, guard not tripped. **DEFECT C** per-verdict `isinstance` guard clean (0 malformed).

## Bottom line

Cathedral 13th consecutive clean, spec/adv 100% clean, every qid within ±0.01 of baseline. The single flagged drift event is a q06 tail value, resolved as a false positive. **No production alert.**