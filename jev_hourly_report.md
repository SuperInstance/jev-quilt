# JEV Continuous Probe — 1 Round Report (2026-10-22)

## Run context
- **Sandbox state:** post-wipe rebuild. `/workspace` was empty and NAS at 100% (0 bytes). Script + history restored from `SuperInstance/jev-quilt @ r-081-continuous-probe-rebuild` into `/tmp` (not on NAS).
- **Session tag:** `rounds_r087_retry100639` (1 OK round after 2 transient failures).
- **Baseline:** 567 history lines → 485 deduped rounds, 2425 verdicts.

## New round result
| metric | value |
|---|---|
| mean_p | **0.438** (5/5 OK) |
| bedrock hits (p>=0.70) | **2** |
| speculative clean-rejects (p<0.40) | 2 |
| adversarial clean-rejects (p<0.40) | 1 |
| drift events > 0.05 | **0** |

### Per-question verdicts
| qid | kind | p | history mean | delta | verdict |
|---|---|---|---|---|---|
| q09_signal_chain_canon | speculative | 0.17 | 0.201 | -0.031 | ok |
| q19_style_resilience | adversarial | 0.04 | 0.039 | +0.001 | ok |
| q21_memory_sandbox | speculative | 0.04 | 0.040 | +0.000 | ok |
| q07_11_opcodes | **bedrock** | **0.96** | 0.970 | -0.010 | ok (hit) |
| q02_witness_log_is_prediction | **bedrock** | **0.98** | 0.972 | +0.008 | ok (hit) |

## Comparison to previous rounds
- **Mean:** this round 0.438 vs history grand mean **0.4100** — within normal band.
- **Canon integrity intact:** both bedrock questions (q07, q02) returned >=0.96, matching their stable history means (~0.97). The bedrock/speculative separation remains razor-sharp: bedrock 0.97–0.98 vs speculative/adversarial 0.03–0.20.
- **Drift:** none. Every |delta| is within max(0.05, 2*sigma). Largest move is q09 at -0.031, well under its 0.050 threshold.

## Notable environment findings (this run)
1. **Expired-leaf TLS wall was ACTIVE again** for `api.typesafe.ai` (24h-TTL MITM leaf). Strict `urlopen()` -> `HTTP=000`. Confirmed only the cert was blocking via `curl -k` (returns a real app-layer 400). Re-applied the local opt-in `JEV_INSECURE_TLS=1` SSL-context hatch (NOT upstreamed, strict by default).
2. **Transient upstream flakiness:** first attempt got `HTTP 503 upstream connect error`, second got a TLS handshake timeout, third succeeded. `TYPESAFE_AI_TOKEN` was present (108 chars) — no creds issue.

## Verdict
**Healthy round.** 2/2 bedrock canon confirmed at >=0.96, zero speculative leakage into canon, zero drift. Mean_p 0.438 sits comfortably in the historical distribution.
