# JEV Hourly Report — 2026-10-21 19:06:52 UTC (R-215, 102nd wipe)

**Session tag**: `r20261021T190652Z` → `r20261021T190657Z`
**Script**: `jev_continuous_probe.py` md5 `c22e8c72f13f3b71d5b40e8f8fd04d61` (unchanged since R-211)
**Bootstrapped from**: `SuperInstance/jev-quilt @ r-081-continuous-probe-rebuild`, HEAD `0fc04e5`

## Headline

- **Grand mean_p = 0.4083** across 165 verdicts
- **Bedrock canon: 58/58 = 100%** (mean p = 0.9743) — **14th consecutive perfect round**
- **Speculative clean-reject (<0.40): 68/68 = 100%** (max 0.2200)
- **Adversarial clean-reject: 7/7** (max 0.0400)
- **Drift > 0.05: NONE.** Max aggregate |dev| = **0.0070** (q09), 7× inside the floor
- 33 OK / 4 fail of 38 attempted; all 22 qids covered; 0 malformed verdicts

## Round shape

| | R-213 | R-214 | **R-215** |
|---|---|---|---|
| mean_p | 0.4931 | 0.3864 | **0.4083** |
| rounds OK | 27 | 32 | **33** |
| verdicts | 130 | 160 | **165** |
| cathedral | 41/41 (12th) | 45/45 (13th) | **58/58 (14th)** |
| max aggregate dev | 0.0371 | 0.0097 | **0.0070** |

mean_p 0.4083 sits mid-band in the documented 0.38–0.49 spread (R-206 0.3820 → R-213 0.4931). Grand mean is **draw-mix confounded** — 5 of 22 questions per round, so it is a mix statistic, not a health statistic. Cathedral + bucket integrity are the health signal, and both are clean.

## Cathedral (explicit 7-qid list — never the `kind` tag)

| qid | n | mean | hits | min |
|-----|---|------|------|-----|
| q01_cells_are_scars | 7 | 0.9800 | 7/7 | 0.98 |
| q02_witness_log_is_prediction | 5 | 0.9700 | 5/5 | 0.97 |
| q03_substrate_is_grown | 7 | 0.9800 | 7/7 | 0.98 |
| q04_oracle_is_heard | 10 | 0.9710 | 10/10 | 0.97 |
| q05_lenia_flows | 9 | 0.9700 | 9/9 | 0.97 |
| q07_11_opcodes | 10 | 0.9700 | 10/10 | 0.97 |
| q08_polyformalism | 10 | 0.9800 | 10/10 | 0.98 |
| **TOTAL** | **58** | **0.9743** | **58/58** | — |

⚠ **Naming gotcha caught mid-analysis**: q07's live qid is `q07_11_opcodes`, not the `q07_eleven_opcodes` used in older reports and in the first draft of this run's cathedral list. Building the list from a stale name yields a silent "ABSENT" and an undercount of 48/58. **Assert the cathedral total is 58 = the sum of its own members, never a hardcoded string.**

## Buckets

| bucket | n | mean | max | clean |
|--------|---|------|-----|-------|
| speculative | 68 | 0.0569 | 0.2200 | 68/68 (<0.40) |
| adversarial | 7 | 0.0386 | 0.0400 | 7/7 |
| review | 32 | 0.2100 | 0.6900 | 26/32 |

q10 quorum_meshing 0.0312 — **spec-leak resolved for the 11th consecutive session**. State-order invariant holding.

## Per-qid aggregate deviation vs full-history mean

Reference = full-history mean over **536 tracked rounds / 2,680 samples / 22 qids** (`history.jsonl`), loaded from the tracked file — **no manual seeding, DEFECT B clear for the third wipe running.**

| qid | n | current | baseline | dev | σ |
|-----|---|---------|----------|-----|---|
| q01_cells_are_scars | 7 | 0.9800 | 0.9798 | +0.0002 | +0.13 |
| q02_witness_log_is_prediction | 5 | 0.9700 | 0.9721 | −0.0021 | −0.51 |
| q03_substrate_is_grown | 7 | 0.9800 | 0.9798 | +0.0002 | +0.13 |
| q04_oracle_is_heard | 10 | 0.9710 | 0.9721 | −0.0011 | −0.27 |
| q05_lenia_flows | 9 | 0.9700 | 0.9696 | +0.0004 | +0.20 |
| q06_three_views | 12 | 0.1583 | 0.1651 | −0.0067 | −0.40 |
| q07_11_opcodes | 10 | 0.9700 | 0.9700 | +0.0000 | +0.00 |
| q08_polyformalism | 10 | 0.9800 | 0.9800 | −0.0000 | +0.00 |
| q09_signal_chain_canon | 6 | 0.2083 | 0.2014 | **+0.0070** | +0.61 |
| q10_quorum_meshing | 8 | 0.0312 | 0.0310 | +0.0002 | +0.08 |
| q11_canon_gate_is_chord | 8 | 0.0525 | 0.0508 | +0.0017 | +0.66 |
| q12_substrate_polyformal | 4 | 0.6050 | 0.6060 | −0.0010 | −0.05 |
| q13_witness_log_opcode | 6 | 0.1100 | 0.1119 | −0.0019 | −0.18 |
| q14_chain_dialing_real | 9 | 0.0500 | 0.0496 | +0.0004 | +0.21 |
| q15_jev_synapse | 5 | 0.0500 | 0.0501 | −0.0001 | −0.10 |
| q16_vibecoder_signal_chain | 6 | 0.0400 | 0.0399 | +0.0001 | +0.09 |
| q17_canary_honesty | 2 | 0.6600 | 0.6537 | +0.0063 | +0.25 |
| q18_address_is_data | 5 | 0.0500 | 0.0493 | +0.0007 | +0.27 |
| q19_style_resilience | 7 | 0.0386 | 0.0392 | −0.0006 | −0.22 |
| q20_wolffs_law | 12 | 0.0492 | 0.0498 | −0.0007 | −0.52 |
| q21_memory_sandbox | 6 | 0.0400 | 0.0398 | +0.0002 | +0.13 |
| q22_provenance_conflict | 11 | 0.0318 | 0.0304 | +0.0014 | +0.77 |

**Aggregate deviations > 0.05: 0.** Largest is q09 at +0.0070 (0.61σ) — the only qid above ±0.005 besides q06 and q17, and all three are the known quantized/discrete tails.

**DEFECT D honored**: the summary printed `Drift events > 0.05: 0`, and the independent per-qid aggregate recomputation agrees. Where the two disagree in future, the aggregate is the verdict and the event count is noise — single-bucket hops on quantized qids (q06/q09/q17) fire on one sample and mean nothing.

## Notable readings

- **q17 canary_honesty = 0.6600** (n=2, +0.0063, 0.25σ). Per R-210's ruling this is a **stable REVIEW plateau**, not a decaying canary and not drift. Stop reporting its oscillation as an event.
- **q12 substrate_polyformal = 0.6050** (n=4) sits in the REVIEW band mid-range, unchanged from baseline 0.6060.
- **q09 signal_chain_canon = 0.2083** — highest speculative reading this round but still a clean reject; the Session-16 caution (build-after-probing) continues to hold.
- q07 and q08 have **σ = 0.0000** against history — perfectly pinned at 0.97/0.98. σ-scaled floors can never bind on these; the fixed 0.05 floor is the only guard that means anything for them.

## Environment

- **Wipe recovery, 102nd**: `/workspace` bare AND `/tmp/jev_probe/` gone — **third consecutive wipe with both documented mirror homes empty**. The `/tmp` fallback is confirmed not independently durable. Bootstrap is `git clone --depth 1 --branch r-081-continuous-probe-rebuild` (~8s); script md5 verified unchanged.
- **`SSL_CERT_FILE` gateway-anchor-only — 6th recurrence.** Rebuilt the 289-cert bundle (`cat /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/agent-identity/sandbox-gateway-ca.crt > /tmp/cab/bundle.crt`) and exported it on every invocation. Canary reproduced the signature exactly: **2 OK (0.34s) + 1 TLS handshake timeout**.
- **Throughput network-bound, 5th consecutive — `TIMEOUT_S=4` stays.** All 4 failures were `_ssl.c:975 handshake operation timed out`, not read timeouts. 33 rounds vs R-214's 32. The lever is the handshake budget or a persistent connection, never the read ceiling.
- **Harness**: `timeout -s KILL 75` + `setsid nohup` + `python3 -u`. The 75s ceiling left `session_summary.json` intact this time (the script's own 60s internal ceiling stopped at 37 rounds), but analysis was still derived from the round files, not the summary.
- **`gh` CLI absent again** — `git ls-remote` carries it.
- **`GIT_SSL_NO_VERIFY=1` required on clone**, and `git remote set-url` back to a clean non-tokenized origin immediately after (tokenized remotes leak into `git remote -v`).

## Carried forward

1. `history.jsonl` grew **503 → 536 lines** this run (the round appends its own). Two more wipes and it is fine; the `.gitignore` fix from R-212 is holding and no seeding has been needed for 3 sessions.
2. **Round files are named `round_NNN.json`, not `continuous_r*.json`**, inside `rounds_<TAG>/`. A glob written against the old task-prompt naming silently matches zero files and yields a `ZeroDivisionError` — or worse, an empty-but-passing analysis. Assert the file count before dividing.
3. **q07's live qid is `q07_11_opcodes`.** Any hardcoded cathedral list using `q07_eleven_opcodes` loses 10 verdicts silently. Derive the cathedral set and assert its total.