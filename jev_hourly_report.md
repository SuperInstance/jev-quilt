# JEV continuous probe — R-217 (104th wipe)

**Run:** 2026-10-22 00:04 UTC  |  **tag:** `r20261022T000200Z`  |  **bootstrap:** `jev-quilt @ r-081-continuous-probe-rebuild` HEAD `7d6e716`

**Verdict: HEALTHY. Cathedral 9/9 @100% — 16th consecutive. Zero aggregate drift.**

## Round summary

| metric | value | note |
|---|---|---|
| rounds attempted | 12 | 5 OK / 7 fail — all TLS handshake timeouts |
| verdicts | 25 | across 17 distinct qids |
| **grand mean_p** | **0.4608** | band R-206..R-217 = 0.3596–0.4931 — mid-pack, no trend |
| **cathedral bedrock** | **9/9 @100%** | mean 0.9733, zero misses — **16th consecutive** |
| **aggregate drift >0.05** | **NONE** | max \|dev\| 0.0246 (q06) |
| spec clean-rejects | 10/10 | p<0.40 |
| q10 spec-leak | resolved | 0.0300 vs base 0.0310 (−0.33σ) — 12th session |
| q17 canary | 0.6700 | vs base 0.6536 (+0.63σ) — stable REVIEW plateau, not decay |

## mean_p context — read the cathedral, not the grand mean

The grand mean is draw-mix confounded: each round draws 5 of 22 questions, and the 8 bedrock-side qids sit at ~0.97 while the 12 spec/adv qids sit at 0.03–0.20. E[bedrock/round] ≈ 1.8, so a *higher* mean means *more bedrock got drawn* — it is not a health statistic. **Health lives in the cathedral count and the spec/adv buckets.** This round's 0.4608 sits mid-band (R-212 0.3596 low → R-213 0.4931 high); no trend.

## Per-qid aggregate drift vs full-history mean

Judged per DEFECT D: **aggregate per-qid deviation against the full-history mean**, never the raw per-verdict event count from `session_summary.json`. Baseline = 2810 samples / 22 qids, non-empty assertion PASSED (no manual seeding — DEFECT B clear, 12th consecutive).

| qid | n | current | baseline | dev | σ | verdict |
|---|---|---|---|---|---|---|
| q02_witness_log_is_prediction | 2 | 0.9750 | 0.9722 | +0.0028 | +0.67 | ok |
| q03_substrate_is_grown | 1 | 0.9800 | 0.9798 | +0.0002 | +0.13 | ok |
| q04_oracle_is_heard | 1 | 0.9700 | 0.9722 | -0.0022 | -0.52 | ok |
| q05_lenia_flows | 1 | 0.9700 | 0.9696 | +0.0004 | +0.19 | ok |
| q06_three_views | 2 | 0.1400 | 0.1646 | -0.0246 | -1.48 | ok |
| q07_11_opcodes | 3 | 0.9700 | 0.9700 | +0.0000 | +1.12 | ok |
| q08_polyformalism | 1 | 0.9800 | 0.9800 | -0.0000 | -1.00 | ok |
| q10_quorum_meshing | 1 | 0.0300 | 0.0310 | -0.0010 | -0.33 | ok |
| q12_substrate_polyformal | 1 | 0.6300 | 0.6062 | +0.0238 | +1.19 | ok |
| q13_witness_log_opcode | 1 | 0.1200 | 0.1119 | +0.0081 | +0.76 | ok |
| q16_vibecoder_signal_chain | 3 | 0.0400 | 0.0399 | +0.0001 | +0.09 | ok |
| q17_canary_honesty | 2 | 0.6700 | 0.6536 | +0.0164 | +0.63 | ok |
| q18_address_is_data | 1 | 0.0500 | 0.0493 | +0.0007 | +0.26 | ok |
| q19_style_resilience | 1 | 0.0400 | 0.0391 | +0.0009 | +0.30 | ok |
| q20_wolffs_law | 1 | 0.0500 | 0.0498 | +0.0002 | +0.13 | ok |
| q21_memory_sandbox | 1 | 0.0400 | 0.0398 | +0.0002 | +0.13 | ok |
| q22_provenance_conflict | 2 | 0.0300 | 0.0304 | -0.0004 | -0.19 | ok |

Two-guard rule in force: the 0.05 absolute floor and the σ-scaled guard are **different** guards and both are needed. q06 sits at −1.48σ and q07 at +1.12σ yet neither fires, because the σ-scaled floor never exceeds 0.05 for these tight distributions.

## Environment & method

- **`SSL_CERT_FILE` gateway-anchor-only — 7th recurrence.** Export path pointed at the gateway anchor (147 certs), not the full set; rebuilt the 289-cert bundle (`ca-certificates.crt` + gateway anchor) before the first call. Canary: API reachable in 0.21 s.

- **Both documented mirror homes were empty again** — `/workspace` bare on arrival and `/tmp/jev_probe/` gone (3rd consecutive). *Neither ephemeral home is independently durable; the git snapshot is the only bootstrap that works.*

- **Network-bound, 6th consecutive session — `TIMEOUT_S=4` stays.** All 7 failures were TLS *handshake* timeouts (`URLError ... handshake operation timed out`). The lever is the handshake budget or a persistent connection, never the read ceiling.

- **Thin round is network, not regression.** 5 OK rounds is at the low end (R-211 30, R-213 27, R-214 32). Per the durable rule, the sample-size caveat applies to the *current* window, not the baseline — a thin round against a 2,785-sample corpus is still a sound all-clear.

- **Arg shape:** the script takes rounds as a **positional** `sys.argv[1]`, not `--rounds N`. A `--rounds` invocation dies with `ValueError` before spending a single API call — harmless but worth knowing.

- **Harness:** `setsid nohup timeout -s KILL 75 python3 -u` — the probe's own 60 s deadline sits inside it, and the tool's 30 s ceiling means the launch and the analysis must both be polled in short increments.

- `TYPESAFE_AI_TOKEN` set (`TYPESAFEAI_KEY`/`JEV_API_KEY` unset); `gh` **MISSING** this wipe (`git ls-remote` carries it).

- **Script md5 `c22e8c72f13f3b71d5b40e8f8fd04d61`, unchanged.** All 5 protocol invariants intact: timestamp-derived `SESSION_TAG` (DEFECT A structurally impossible), 3 auth headers, `type: noul` discriminator, bucket-index score normalization via `_bucket_midpoint`, TLS/503 retry with jitter.

