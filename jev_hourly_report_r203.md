# JEV Hourly Report — R-203 (2026-10-20 03:03Z)

**Session**: 90th+ wipe continuous probe (200-round run, R-203 of the durable continuous series).
**Rounds**: 199 ok / 1 fail of 200 attempted, **995 verdicts**, **wall 27s** (60s ceiling).
**Probe source**: `github.com/SuperInstance/jev-quilt` branch `r-081-continuous-probe-rebuild` (HEAD `810cf9f` = R-202 era), pulled into `/tmp/jev-quilt/` (workspace `/workspace/research/` was wiped on session start; NAS at 100% EDQUOT — durable 90w+).

**Grand mean_p**: **0.4196** (n=995) — inside the durable 0.35-0.55 band. R-088 (n=1000) was 0.4036, **Δ +0.0160** (within noise). 0.4196 is the **second-highest 200-round mean since R-083** (0.4033) but still well inside the canonical band.

## Per-QID summary (R-203, 199-round run)

| qid | kind | n | mean | hit_p70 | band |
|---|---|---:|---:|---:|---|
| `q01_cells_are_scars` | **bedrock** | 41 | **0.9800** | 41/41 (100%) | cathedral ✓ |
| `q02_witness_log_is_prediction` | **bedrock** | 45 | **0.9727** | 45/45 (100%) | cathedral ✓ |
| `q03_substrate_is_grown` | **bedrock** | 42 | **0.9800** | 42/42 (100%) | cathedral ✓ |
| `q04_oracle_is_heard` | **bedrock** | 45 | **0.9729** | 45/45 (100%) | cathedral ✓ |
| `q05_lenia_flows` | **bedrock** | 53 | **0.9698** | 53/53 (100%) | cathedral ✓ |
| `q07_11_opcodes` | **bedrock** | 55 | **0.9700** | 55/55 (100%) | cathedral ✓ |
| `q08_polyformalism` | **bedrock** | 43 | **0.9800** | 43/43 (100%) | cathedral ✓ |
| `q10_quorum_meshing` | speculative | 44 | 0.0309 | 0/44 (0%) | spec-clean ✓ |
| `q14_chain_dialing_real` | speculative | 44 | 0.0498 | 0/44 (0%) | spec-clean ✓ |
| `q15_jev_synapse` | speculative | 36 | 0.0503 | 0/36 (0%) | spec-clean ✓ |
| `q16_vibecoder_signal_chain` | speculative | 46 | 0.0400 | 0/46 (0%) | spec-clean ✓ |
| `q18_address_is_data` | speculative | 49 | 0.0498 | 0/49 (0%) | spec-clean ✓ |
| `q20_wolffs_law` | speculative | 46 | 0.0493 | 0/46 (0%) | spec-clean ✓ |
| `q21_memory_sandbox` | speculative | 40 | 0.0395 | 0/40 (0%) | spec-clean ✓ |
| `q22_provenance_conflict` | speculative | 44 | 0.0302 | 0/44 (0%) | spec-clean ✓ |
| `q19_style_resilience` | adversarial | 43 | 0.0395 | 0/43 (0%) | adv-clean ✓ |
| `q06_three_views` | review | 42 | 0.1624 | 0/42 (0%) | REJECT (durable) |
| `q11_canon_gate_is_chord` | review | 38 | 0.0508 | 0/38 (0%) | REJECT (durable) |
| `q13_witness_log_opcode` | review | 54 | 0.1120 | 0/54 (0%) | REJECT (durable) |
| `q17_canary_honesty` | review (canary) | 43 | 0.6509 | 5/43 (12%) | canary plateau ~0.65 |
| `q12_substrate_polyformal` | review | 53 | 0.6113 | 0/53 (0%) | borderline REVIEW |
| `q09_signal_chain_canon` | speculative | 49 | 0.2037 | 0/49 (0%) | borderline REJECT |

**Cathedral (7/7 bedrock @ 100% hit)**: mean 0.9753, std ≤ 0.005 — durable, the substrate is reproducible to ±0.005 per qid.
**Speculative (9/9)**: mean 0.0433, all clean-rejected, 0% leak.
**Adversarial (1/1)**: q19_style_resilience 0.0395 — clean-reject held.
**Review band**: q12 substrate_polyformal plateau 0.61 (REVIEW), q17 canary 0.65 (5/43 hit at p≥0.70, canary stable).

## Drift events > 0.05 (4)

| qid | current_p | median_p | Δ | n_history |
|---|---:|---:|---:|---:|
| `q17_canary_honesty` | 0.71 | 0.65 | **+0.06** | 4 |
| `q17_canary_honesty` | 0.62 | 0.67 | **-0.05** | 12 |
| `q17_canary_honesty` | 0.73 | 0.65 | **+0.08** | 18 |
| `q12_substrate_polyformal` | 0.56 | 0.62 | **-0.06** | 32 |

**3 of 4 drift events on q17 canary** — confirms the canary is intrinsically noisy (that's its job), but the canary mean (0.6509) holds inside the durable 0.59-0.75 plateau band. **1 drift on q12 substrate_polyformal** — within the q12 review band (0.55-0.65), not a structural change.

**No bedrock drift events.** Cathedral floor is intact at 0.97-0.98 across all 7 bedrock QIDs.

## Comparison to prior sessions

| Session | rounds | mean_p | bedrock_hits | spec_rejects | adv_rejects | drift>0.05 |
|---|---:|---:|---:|---:|---:|---:|
| **R-203** (this) | 199/200 | **0.4196** | 324 (32.6%) | 398 | 43 | 4 |
| R-202 (1r) | 1/1 | 0.6920 | 2/5 | 0 | 0 | 0 |
| R-201 (ref) | — | 0.5680 | — | — | — | — |
| R-200 (ref) | — | 0.5920 | — | — | — | — |
| R-088 | 200/200 | 0.4036 | 322 (32.2%) | 596 | — | 4 |
| R-083 | 200/200 | 0.4033 | 322 (32.2%) | 413 | 41 | 4 |
| R-082 | 200/200 | 0.3905 | 322 (32.2%) | — | — | 7 |
| R-081 | 194/200 | 0.4337 | 323 (33.3%) | 373 | 35 | 5 |
| R-088 → R-203 Δ | — | **+0.0160** | +2 | — | — | 0 |

R-203 mean_p 0.4196 is **+0.0160 vs R-088** — within the durable noise band, no structural shift. Bedrock hit rate 32.6% vs R-088 32.2% is identical to ±0.4pp.

## Bedrock hit list (R-203, 324/995 = 32.6%)

The 7 bedrock QIDs all hit at 100%:
- `q01_cells_are_scars` (41/41)
- `q02_witness_log_is_prediction` (45/45)
- `q03_substrate_is_grown` (42/42)
- `q04_oracle_is_heard` (45/45)
- `q05_lenia_flows` (53/53)
- `q07_11_opcodes` (55/55)
- `q08_polyformalism` (43/43)

Cathedral mean 0.9753 (std ≤ 0.005).

## Durable (carry forward)

- 90th+ wipe / NAS at 100% EDQUOT (durable 90w+). `mkdir` succeeds but writes return 0 bytes. Canonical mirror = `/tmp/jev_probe_run/jev_hourly_report.md` + (after push) `SuperInstance/jev-quilt` on branch `r-081-continuous-probe-rebuild`.
- The 5 protocol invariants (durable 50+ days) held: STATE-ORDER (spec_notebook before bedrock), 3 AUTH headers, `type: noul` discriminator, score-bucket-index → legend-midpoint normalization, retry-on-TLS-EOF+503. 199/200 = 99.5% success rate; the 1 fail was a connection-phase transient (skip-on-fail).
- Per-QID reproducibility: max per-qid Δ vs R-083 5-session median ≤ 0.005 on all 7 bedrock QIDs. Substrate is rock-solid.
- q17 canary plateau 0.6509 — within 0.59-0.75 durable band. 3 of 4 drift events are q17 noise, not substrate change. The canary is doing its job.
- Spec-leak (q10 quorum_meshing, durable 2+ sessions) is RESOLVED: q10 mean 0.0309, 0/44 hit at p≥0.70. STATE-ORDER fix is durable.
- q12 substrate_polyformal at 0.6113 (REVIEW, 0/53 hit) — within its 0.55-0.65 plateau, not a demotion candidate. State-strengthening not warranted.

## Files (R-203)

- `/tmp/jev_probe_run/jev_continuous_probe.py` (copy of canonical `810cf9f`)
- `/tmp/jev_probe_run/jev_sessions/continuous_r001-r200.json` (199 round JSONs, 1 fail written as `.fail.json`)
- `/tmp/jev_probe_run/jev_sessions/session_summary.json` (per-QID summary)
- `/tmp/jev_probe_run/jev_sessions/history.jsonl` (81,182 B — 199 round records)
- `/tmp/jev_probe_run/jev_hourly_report.md` (this report)
- **NOT yet pushed** to `SuperInstance/jev-quilt` (workflow: copy into clone, commit, push with `git -c credential.helper=...` form; will attempt after this report)
- **NOT saved to** `/workspace/research/jev_hourly_report.md` — NAS at 100% EDQUOT, write returned 0 bytes; canonical mirror is `/tmp/` + GitHub

## Action items (R-203 + carry forward)

1. **PUSH R-203 to `r-081-continuous-probe-rebuild`** — round JSONs + this report. Follow the durable pattern: copy into `/tmp/jev-quilt/jev_sessions/`, rename `r001-r200` → `r401-r600` (round-index-within-run, NOT global — ts is the disambiguator; durable 88w+), commit, push with `git -c credential.helper="!f() { echo username=x-access-token; echo password=$GITHUB_TOKEN; }; f"` (NOT URL-embedded token).
2. **NAS at 100% EDQUOT (durable 90w+, 90th+ wipe)** — the user keeps asking for `/workspace/research/jev_hourly_report.md` writes. Each session this fails (mkdir OK, write returns 0 bytes). **The canonical mirror is now `/tmp/jev_probe_run/jev_hourly_report.md` and GitHub.** Confirm with user that GitHub is the canonical path going forward, OR escalate the NAS quota issue.
3. **Rotate GITHUB_TOKEN** — durable 90w+ security note. Previous session used `git remote add https://x-access-token:${TOKEN}@...` form which leaks into `git remote -v` output. Use `git -c credential.helper=...` form going forward.
4. **R-204 hour-probe** — not run this session. If asked, same one-round pattern: `cd /tmp/jev_probe_run && timeout 60 python3 jev_continuous_probe.py --rounds 1 --out /tmp/jev_probe_run_r204`, then aggregate.
5. **8th consecutive clean probe (R-202 was 7th, R-203 carries it).** If R-204 breaks the streak (e.g., a cathedral QID falls below 100% hit or a bedrock QID drops below 0.95 mean), that's the alarm.
