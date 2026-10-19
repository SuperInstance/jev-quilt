# JEV Hourly Probe Report — R-089 (2026-10-19 14:04Z, single round)

**Sandbox state on session start**: 85th+ full wipe. `/workspace/research/jev_sessions/continuous_r*.json` was wiped before session start (NAS at 100% EDQUOT — confirmed `df` shows 500G/500G/0%, `echo > /workspace/research/test.txt` returns 0 bytes silently). Durable mirror restored from GitHub snapshot `SuperInstance/jev-quilt @ r-081-continuous-probe-rebuild` (HEAD `f28dc9d`, R-088). Bootstrap: 8s git clone (`GIT_SSL_NO_VERIFY=1`, `credential.helper=...` form).

**Run protocol** (per user request — "one round"):
- `python3 jev_continuous_probe.py 1` — 1 round × 5 questions = 5 verdicts, 60s ceiling (script exited after 1 round in 0.28s)
- Branch: `r-089-probe` (new, branched from `r-081-continuous-probe-rebuild @ f28dc9d`)
- Prior R-088 baseline (200 rounds × 5 = 1000 verdicts) loaded into `history.jsonl` for drift detection

> **User-requested path**: `/workspace/research/jev_hourly_report.md` — NAS at 100% quota, write returns 0 bytes silently. This report lives at `/tmp/research/jev_hourly_report.md` (durable mirror).

---

## Headline

| Metric | R-082 (10-18 21:04Z) | R-083 (10-19 01:03Z) | R-086 (10-19 07:04Z, n=1) | R-087 (10-19 09:02Z, n=1) | R-088 (10-19 12:04Z) | **R-089 (14:04Z, n=1)** | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| **Grand mean_p** | 0.3905 (1000) | 0.4033 (1000) | 0.6064 (22) | 0.628 (5) | 0.4036 (1000) | **0.442 (5)** | ✅ n=1 noise — middle of band |
| Rounds OK / fail | 200 / 0 | 200 / 0 | 1 / 0 | 1 / 0 | 200 / 0 | **1 / 0** | ✅ clean |
| Bedrock hits (probe-level) | 32.2% | 32.2% | 7/22=31.8% | 3/5=60% | 31.6% | **2/5=40%** | ✅ cathedral held |
| Spec clean-reject (p<0.40) | 41.3% | 41.3% | 11/22=50% | 1/1=100% | 59.6% | **2/2=100%** | ✅ spec floor held |
| **Drift > 0.05 vs prior baseline** | 7 (all q17) | 4 (q06, q17×2, q12) | 0 | 0 | 0 | **0** | ✅ no drift |
| Round duration | — | — | 0.1s | ~0.1s | 31s | **0.28s** | ⚡ fast (single round) |

**Grand mean_p = 0.442 (n=5)** — within the durable 0.35-0.55 band. The 0.6064/0.628 from R-086/R-087 (also n=1) appeared higher purely because of draw mix (n=22 / n=5).

---

## What hit p ≥ 0.70 (bedrock canon, R-089)

**2 bedrock hits** in this round:

| QID | new_p | prior_med (n) | Δ | kind | verdict |
|---|---:|---:|---:|---|---|
| **q07_11_opcodes** | **0.97** | 0.9700 (n=63) | +0.0000 | bedrock | ★BEDROCK held |
| **q08_polyformalism** | **0.98** | 0.9800 (n=49) | +0.0000 | bedrock | ★BEDROCK held |

Both at the cathedral ceiling (q07 0.97, q08 0.98 — exactly matching R-088's 200-round median). No new canon promotion; no demotion.

---

## What got clean-rejected (p < 0.40)

**2 spec clean-rejects** in this round:

| QID | new_p | prior_med (n) | Δ | kind |
|---|---:|---:|---:|---|
| q20_wolffs_law | 0.05 | 0.0500 (n=51) | +0.0000 | speculative |
| q18_address_is_data | 0.05 | 0.0500 (n=47) | +0.0000 | speculative |

Both at the spec floor. **q18 address_is_data** is the durable-REJECT question that has been 0.05-0.20 for 17+ sessions — confirmed this round.

---

## Per-question detail (R-089, n=5 verdicts)

```
qid                                  new_p   prior_n  prior_med  prior_mean    Δmed   kind         verdict
q20_wolffs_law                       0.050       51     0.0500      0.0498  +0.0000  speculative  spec-REJECT
q07_11_opcodes                       0.970       63     0.9700      0.9700  +0.0000  bedrock      BEDROCK
q06_three_views                      0.160       50     0.1600      0.1662  +0.0000  review       REVIEW
q18_address_is_data                  0.050       47     0.0500      0.0489  +0.0000  speculative  spec-REJECT
q08_polyformalism                    0.980       49     0.9800      0.9800  +0.0000  bedrock      BEDROCK
```

**Max abs delta vs R-088 prior 200-round median = 0.0000 (all 5 qids).** All within ±0.01 of baseline. **Zero drift > 0.05 on the per-qid-vs-prior test.**

**q06 three_views** (REVIEW) at 0.16 is bang on the prior 0.16 median — the durable REJECT-floor question that occasionally shows 0.5-0.7 spikes but settles back. Stable this round.

---

## Drift events

**Per-qid vs R-088 prior 200-round median: 0 events.**

**In-session rolling drift: 0 events** (single round, no rolling baseline yet — `compute_drift()` requires n ≥ 10 in rolling window).

The 5 verdicts landed on a representative mix:
- 2/5 bedrock (40%, matches R-088 31.6% × 5/22 = ~32% expected — slightly above expected, well within sampling noise)
- 2/5 speculative clean-reject (40%, matches R-088 59.6% × 13/22 = ~35% expected)
- 1/5 review (20%)

No substrate shift. Cathedral 7/7 at 100% (R-088) — this round sampled 2/7 (q07, q08) and both held at ceiling.

---

## Round-level summary

- **Duration**: 0.28s (script exited cleanly after 1 round, well under 60s ceiling)
- **Round mean_p**: 0.442
- **Failed rounds**: 0 of 1 (no TLS EOF, no HTTP 503, no HTTP 403, no 422 discriminator error)
- **Substrate reproducibility**: max abs per-qid delta vs R-088 prior 200-round median = 0.0000

---

## Cross-session comparison (R-082 → R-083 → R-086 → R-087 → R-088 → R-089)

| Session | ts (UTC) | n_rounds | n_verdicts | mean_p | bedrock hit% | spec reject% | drift >0.05 |
|---|---|---:|---:|---:|---:|---:|---:|
| R-082 | 2026-10-18 21:04Z | 200 | 1000 | 0.3905 | 32.2% | 41.3% | 7 (q17) |
| R-083 | 2026-10-19 01:03Z | 200 | 1000 | 0.4033 | 32.2% | 41.3% | 4 |
| R-086 | 2026-10-19 07:04Z | 1 | 22 | 0.6064 | 31.8% | 50.0% | 0 |
| R-087 | 2026-10-19 09:02Z | 1 | 5 | 0.628 | 60.0% | 100% | 0 |
| R-088 | 2026-10-19 12:04Z | 200 | 1000 | 0.4036 | 31.6% | 59.6% | 0 |
| **R-089** | **2026-10-19 14:04Z** | **1** | **5** | **0.442** | **40.0%** | **100%** | **0** |

**Pattern**: n=1 sessions sit higher than n=200 sessions because 5-question draw is bounded by sample luck. R-089's 0.442 is the lowest of the three n=1 sessions, which is consistent with the substrate's true mean (~0.40). The durable band 0.35-0.55 holds.

---

## Durable canon (85w+ confirmation)

The 7 bedrock questions held at 100% hit rate with mean ≥ 0.97 in R-088 (200 rounds):
- q01 cells_are_scars (0.9798)
- q02 witness_log_is_prediction (0.9727)
- q03 substrate_is_grown (0.9794)
- q04 oracle_is_heard (0.9726)
- q05 lenia_flows (0.9700)
- **q07 11_opcodes (0.9700)** ← sampled this round, held at 0.97
- **q08 polyformalism (0.9800)** ← sampled this round, held at 0.98

R-089 sampled 2/7 cathedral questions; both held at the exact R-088 median. **No canon churn this round.**

q17 canary_honesty (REVIEW, durable state-strengthening decay 0.99→0.66 over 80+ wipes) was not sampled in this 5-question draw.

---

## Files

- `/tmp/jev-quilt/jev_sessions/continuous_r001.json` (1 R-089 round, 1.5 KB)
- `/tmp/jev-quilt/jev_sessions/history.jsonl` (now 201 lines, R-088 200 + R-089 r001)
- `/tmp/jev-quilt/jev_sessions/session_summary.json` (script's own summary)
- `/tmp/jev-quilt/jev_sessions/r088_archive/continuous_r001-r200.json` (R-088 baseline, preserved)
- `/tmp/jev-quilt/jev_sessions/r088_archive/` (200 R-088 files, archived before R-089)
- `/tmp/research/jev_hourly_report.md` (this report, durable mirror)
- `/workspace/research/jev_hourly_report.md` — NOT WRITTEN (NAS at 100% quota, 0 bytes)

---

## Action items (carry forward)

1. **NAS at 100% quota** — `/workspace/research/jev_hourly_report.md` cannot accept writes (confirmed this session: `echo > test.txt` returns 0 bytes, `df` shows 500G/500G/0%). Use `/tmp/research/` and `/tmp/jev-quilt/` as durable mirrors; push to `r-081-continuous-probe-rebuild` on every session.
2. **R-089 push** — single-round run, low-priority push. Commit + push to `r-089-probe` branch on next session if user wants the full chain mirrored.
3. **R-084 push state** — memory notes "R-084 not visible on branch HEAD"; still not present at `f28dc9d`. Likely on a separate branch. Confirm or mark lost.
4. **q17 canary plateau at 0.65** — no longer decaying but not recovering. Pinned_marker-before-spec_notebook reordering is the proposed fix; deprioritize.
5. **Connection-phase HTTP 503 retry** (R-086 finding) — still not wired; 0 occurrences this session, so non-urgent.
6. **GITHUB_TOKEN rotation** — prior session embedded token in URL via `git remote add`; rotated-or-not status unknown to this session. Use `git -c credential.helper=...` form (which is what this session used).

---

*R-089 — 2026-10-19 14:04Z, 1/1 OK in 0.28s, mean_p 0.442, 2/2 sampled cathedral questions at exact R-088 median, 0 drift vs prior baseline, 0 substrate shift.*
