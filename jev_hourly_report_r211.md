# JEV Hourly Report — R-211 (2026-10-21 15:05 UTC, 98th wipe)

**Session**: `rounds_r211/` (32 rounds on disk: 30 OK / 2 fail, 150 verdicts)
**Run**: 60s ceiling hit, `JEV_SESSION_TAG=r211`
**Baseline**: 4,100 prior verdicts across 22/22 qids (rebuilt from tracked corpus)

## Headline

- **Grand mean_p = 0.4441** (R-210 0.4306, R-209 0.4172, R-208 0.4260, R-207 0.4153, R-206 0.3820) — mid-band, +0.0135 vs R-210
- **Bedrock canon (cathedral): 49/49 draws @ p≥0.70 — ZERO misses. 10th consecutive session.** Cathedral mean p = **0.9767**
- **Speculative clean-reject: 61/61** (100%, max 0.2200)
- **Adversarial clean-reject: 7/7** (100%, max 0.0400)
- **Drift events > threshold: 0.** Max per-qid deviation from full-history mean = **0.0469** (q12), the tightest margin set in the series

## Bedrock canon (explicit 7-qid list — never counted from the `kind` tag)

| qid | n | mean p | base mean | maxdev |
|-----|---|--------|-----------|--------|
| q01_cells_are_scars | 3 | 0.9800 | 0.9797 | 0.0003 |
| q02_witness_log_is_prediction | 9 | 0.9744 | 0.9727 | 0.0073 |
| q03_substrate_is_grown | 11 | 0.9800 | 0.9798 | 0.0002 |
| q04_oracle_is_heard | 7 | 0.9757 | 0.9724 | 0.0076 |
| q05_lenia_flows | 6 | 0.9700 | 0.9697 | 0.0003 |
| q07_11_opcodes | 7 | 0.9700 | 0.9700 | 0.0000 |
| q08_polyformalism | 13 | 0.9800 | 0.9800 | 0.0000 |

## Drift — closest to the line (threshold = max(0.05, 2σ), judged vs FULL-HISTORY mean)

| qid | cur mean | base | maxdev | σ | margin to fire |
|-----|----------|------|--------|---|----------------|
| q12_substrate_polyformal | 0.5957 | 0.6069 | 0.0469 | 2.22σ | **1.07x** |
| q06_three_views | 0.1900 | 0.1656 | 0.0344 | 2.01σ | 1.45x |
| q17_canary_honesty | 0.6500 | 0.6524 | 0.0324 | 1.15σ | 1.74x |
| q09_signal_chain_canon | 0.2050 | 0.2015 | 0.0185 | 1.55σ | 2.71x |

**Zero drift > 0.05 fired.** Note this is a genuine all-clear, not a thin-round artifact: n ranges 2–13 per qid against a 175–219-sample baseline per qid, so the reference estimator is well-populated (unlike R-206's n=1–7 case).

Two qids sit close enough to watch next round: **q12** (1.07x margin — a single 0.05 swing fires it) and **q06** (1.45x). Both are the known high-variance REVIEW-band questions, and both remain far from any promotion threshold (q12 ≈0.60, q06 ≈0.19).

## Environment

- **Fresh wipe (98th).** `/workspace` bare on arrival; the task-named path `/workspace/research/jev_sessions/continuous_r*.json` did not exist. Bootstrapped from `jev-quilt @ r-081-continuous-probe-rebuild` (~8s) per the snapshot workflow.
- **EDQUOT clear.** Wrote directly into `/workspace/jev-quilt/`, all bytes verified non-zero.
- **SSL_CERT_FILE was gateway-anchor-only AGAIN** (R-209/R-210 trap, 3rd occurrence). Rebuilt the 289-cert bundle before the first call. Check `env | grep SSL_CERT_FILE` every wipe — do not assume the export survived.
- **DEFECT B, 6th occurrence.** `history.jsonl` gitignored + shallow clone ⇒ absent ⇒ empty baseline ⇒ the script's exit-4 guard would have refused. Rebuilt from the tracked corpus: **821 files → 4,100 samples / 22 qids** (5 malformed entries skipped per DEFECT C).
- **Throughput — do NOT lower TIMEOUT_S.** elapsed median **0.176s** (healthy; R-210 0.142s, R-207 0.118s), p95 5.733s, max 9.437s, **8 stalls >1s**, all on TLS handshake timeouts. R-210's diagnosis holds: the bottleneck is the handshake budget, not the read ceiling. 30 rounds this session vs 23 (R-210) / 200 (R-207) — the network, not the script.

## Defect A — structurally closed this session

The R-211 arrival tripped DEFECT A's guard on purpose and for real: the script hardcoded `SESSION_DIR = rounds_r210`, so on arrival it printed `REFUSING TO RUN: ... rounds_r210 already holds 25 round files (would clobber real history)` and exited 3. **Fixed at the root:** `SESSION_DIR` is now derived from the run timestamp (`JEV_SESSION_TAG` env override, else `r%Y%m%dT%H%M%SZ`), so a new run can never target a prior session's directory. **Re-verified by re-invocation** (`JEV_SESSION_TAG=r210` still refuses) — a guard not re-run to trigger is not a fix.

## Answers to R-211's open asks

1. **q17 handled per R-210's decision** — reported as a stable REVIEW plateau, not as noise and not as decay. This session: n=4, mean 0.6500 vs base 0.6524, maxdev 0.0324 (1.15σ). Consistent with the three-day flat plateau.
2. **TLS handshake budget is the throughput lever, not TIMEOUT_S** — confirmed again (8 stalls >1s, all handshake; median 0.176s means the ceiling still has 20×+ headroom).
3. **`history.jsonl` still gitignored — 6th recurrence of manual seeding.** This is the standing ask, still open. The fix is one line in `.gitignore`; it has survived five prior reports unfixed.

## Per-session means (series context)

R-206 0.3820 · R-207 0.4153 · R-208 0.4260 · R-209 0.4172 · R-210 0.4306 · **R-211 0.4441** — all mid-band; cathedral 100% every session (5th–10th consecutive).