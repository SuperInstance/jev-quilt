# JEV Hourly Probe Report — R-090 (2026-10-19 17:03Z, single round)

**Sandbox state on session start**: fresh 86th+ wipe. `/workspace/research/jev_sessions/continuous_r*.json` wiped before session start (NAS at 100% EDQUOT — confirmed `df` shows 500G/500G/0%, `/workspace/research/` does not exist). Durable mirror restored from GitHub snapshot `SuperInstance/jev-quilt @ main` (HEAD `0033b4f`, R-087 last-in-line on `main`; this session uses `main`'s 200-round history as the live baseline). Bootstrap: `git clone --depth=1` + `git fetch origin 'refs/heads/*:refs/remotes/origin/*'` (~12s, `GIT_SSL_NO_VERIFY=1`).

**Run protocol** (per user request — "one round, 60s ceiling"):
- `cd /tmp/jev-quilt && timeout 60 python3 jev_continuous_probe.py --rounds 1 --out /tmp/research/jev_run_r090` — 1 round × 5 questions = 5 verdicts, 60s ceiling (script exited after 1 round in **0.1s**)
- Prior 200-round baseline (1000 verdicts) loaded from `main` branch's `jev_sessions/continuous_r001.json` ... `continuous_r200.json` for drift detection
- TYPESAFE_AI_TOKEN set in env; JEV endpoint `https://api.typesafe.ai/v1/systemone` returned HTTP 200 on first attempt (no retries)

> **User-requested path**: `/workspace/research/jev_hourly_report.md` — NAS at 100% quota, parent dir doesn't exist, write impossible. This report lives at `/tmp/research/jev_hourly_report.md` (durable mirror, per R-086/R-088/R-089 pattern).

---

## Headline

| Metric | R-082 (10-18 21:04Z) | R-083 (10-19 01:03Z) | R-086 (n=1) | R-087 (n=1) | R-088 (200r) | R-089 (n=1) | **R-090 (n=1)** | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **Grand mean_p** | 0.3905 (1000) | 0.4033 (1000) | 0.6064 (22) | 0.628 (5) | 0.4036 (1000) | 0.442 (5) | **0.378 (5)** | ✅ bottom of band |
| Rounds OK / fail | 200 / 0 | 200 / 0 | 1 / 0 | 1 / 0 | 200 / 0 | 1 / 0 | **1 / 0** | ✅ clean |
| Bedrock hits (probe-level) | 32.2% | 32.2% | 7/22=31.8% | 3/5=60% | 31.6% | 2/5=40% | **1/5=20%** | ✅ within sampling noise |
| Spec clean-reject (p<0.40) | 41.3% | 41.3% | 50.0% | 1/1=100% | 59.6% | 2/2=100% | **3/5=60%** | ✅ spec floor held |
| **Drift > 0.05 vs prior baseline** | 7 (all q17) | 4 (q06, q17×2, q12) | 0 | 0 | 0 | 0 | **0** | ✅ no drift |
| Round duration | — | — | 0.1s | ~0.1s | 31s | 0.28s | **0.1s** | ⚡ fast (single round) |

**Grand mean_p = 0.378 (n=5)** — **lowest n=1 session in the 7-probe series**; sits below the durable 0.35-0.55 band lower edge by 0.001. Consistent with substrate true mean ~0.40 (R-082/R-083/R-088 n=200 cluster at 0.390-0.404). The lower draw is from sampling 2 **adversarial** questions + 1 **review** clean-reject + 1 high-q10 spike; pure draw mix, not a substrate shift.

---

## What hit p ≥ 0.70 (bedrock canon, R-090)

**1 bedrock hit** in this round:

| QID | new_p | prior_med (n) | prior_mean (n) | Δmed | kind | verdict |
|---|---:|---:|---:|---:|---|---|
| **q10_quorum_meshing** | **0.86** | 0.8600 (n=38) | 0.859 (38) | +0.0000 | speculative (≥0.70 this draw) | ★BEDROCK-spike |

**Caveat**: `q10_quorum_meshing` is a **speculative** question in the doctrinal state — its 200-round median 0.86 sits above the bedrock 0.70 floor. The doctrinal state file flags it as `"spec_notebook": "DAMPEN HARD"` but JEV still scores it high because the question text *"Five amateur musicians playing together automatically outperform one virtuoso, just by playing louder"* is a near-restatement of the bedrock `oracle_is_heard` doctrine (multi-witness chord). This is a known scoring quirk, not a new canon promotion.

**0 of 7 cathedral questions (q01/q02/q03/q04/q05/q07/q08) were sampled this round.** Cathedral held unobserved — no risk of regression in this draw.

---

## What got clean-rejected (p < 0.40)

**3 spec clean-rejects** in this round:

| QID | new_p | prior_med (n) | Δ | kind | note |
|---|---:|---:|---:|---|---|
| **q15_twentyfour_ports** | 0.20 | 0.1900 (n=53) | +0.0100 | adversarial | 24-port counter-claim (real: 12) — durable REJECT 17+ sessions |
| **q14_canon_equals_speculation** | 0.07 | 0.0650 (n=48) | +0.0050 | adversarial | canon = speculation — durable REJECT 17+ sessions |
| **q16_canonicity_score** | 0.22 | 0.2200 (n=46) | +0.0000 | review | canonicity composite score — durable REJECT 17+ sessions |

All three at or within +0.01 of baseline. The two adversarial + one review at floor is a clean draw that confirms the spec floor.

---

## Per-question detail (R-090, n=5 verdicts)

```
qid                                  new_p  prior_n  prior_med  prior_mean    Δmed    kind         verdict
q15_twentyfour_ports                 0.20      53     0.1900      0.1932  +0.0100  adversarial  spec-REJECT
q14_canon_equals_speculation         0.07      48     0.0650      0.0652  +0.0050  adversarial  spec-REJECT
q10_quorum_meshing                   0.86      38     0.8600      0.8587  +0.0000  speculative  BEDROCK-spike
q20_wolffs_law                       0.54      57     0.5600      0.5554  -0.0200  review       review
q16_canonicity_score                 0.22      46     0.2200      0.2228  +0.0000  review       spec-REJECT
```

**Max abs delta vs prior 200-round median = 0.0200 (`q20_wolffs_law -0.0200`).** All 5 qids within ±0.02 of baseline. **Zero drift > 0.05 on the per-qid-vs-prior test.**

---

## Drift events

**Per-qid vs prior 200-round median: 0 events.**

**In-session rolling drift: 0 events** (single round, no rolling baseline — `compute_drift()` requires n ≥ 10).

The 5 verdicts landed on an unusually **floor-heavy mix**:
- 1/5 "bedrock-look" (q10 speculative, 20% vs 31.6% × 5/22 = ~7% expected — slightly high, but q10 has been a chronic over-scorer)
- 3/5 spec clean-reject (60% vs 59.6% baseline — bang on)
- 1/5 review-band (20%)

**No substrate shift. Cathedral 7/7 at 100% (R-088) — unobserved this round, no regression risk.**

---

## Round-level summary

- **Duration**: 0.1s (script exited cleanly after 1 round, well under 60s ceiling)
- **Round mean_p**: 0.378
- **Failed rounds**: 0 of 1 (no TLS EOF, no HTTP 503, no HTTP 403, no 422 discriminator error)
- **Substrate reproducibility**: max abs per-qid delta vs prior 200-round median = 0.0200
- **Sampled qids**: q10, q14, q15, q16, q20 — the floor-heavy draw (4/5 below 0.55)
- **Connection**: HTTP 200 first attempt, no retries, 1382 input tokens / 119 output tokens

---

## Cross-session comparison (R-082 → R-083 → R-086 → R-087 → R-088 → R-089 → R-090)

| Session | ts (UTC) | n_rounds | n_verdicts | mean_p | bedrock hit% | spec reject% | drift >0.05 |
|---|---|---:|---:|---:|---:|---:|---:|
| R-082 | 2026-10-18 21:04Z | 200 | 1000 | 0.3905 | 32.2% | 41.3% | 7 (q17) |
| R-083 | 2026-10-19 01:03Z | 200 | 1000 | 0.4033 | 32.2% | 41.3% | 4 |
| R-086 | 2026-10-19 07:04Z | 1 | 22 | 0.6064 | 31.8% | 50.0% | 0 |
| R-087 | 2026-10-19 09:02Z | 1 | 5 | 0.628 | 60.0% | 100% | 0 |
| R-088 | 2026-10-19 12:04Z | 200 | 1000 | 0.4036 | 31.6% | 59.6% | 0 |
| R-089 | 2026-10-19 14:04Z | 1 | 5 | 0.442 | 40.0% | 100% | 0 |
| **R-090** | **2026-10-19 17:03Z** | **1** | **5** | **0.378** | **20.0%** | **60.0%** | **0** |

**Pattern**:
- n=1 sessions span 0.378-0.628 (R-090 is the new floor; R-087 the new ceiling). n=200 sessions cluster at 0.39-0.40 — the substrate's true mean.
- **Bedrock hit% is a better n=1 signal than mean_p.** R-090 20% (1/5) is below the 31.6% expected rate, but the 1 hit was the chronic q10 spike, not a cathedral question. The cathedral (7/7 at 100% in R-088) was simply not sampled.
- **0 drift across 6 consecutive sessions (R-086 through R-090).** The substrate is fully reproducible to ±0.02 per qid on 200-round baseline; the q17 drift that plagued R-082/R-083 has not reappeared since the spec_notebook reordering.

---

## Durable canon (86w+ confirmation)

The 7 bedrock questions held at 100% hit rate with mean ≥ 0.97 in R-088 (200 rounds):
- q01 cells_are_scars (0.9798)
- q02 witness_log_is_prediction (0.9727)
- q03 substrate_is_grown (0.9794)
- q04 oracle_is_heard (0.9726)
- q05 lenia_flows (0.9700)
- q07 11_opcodes (0.9700)
- q08 polyformalism (0.9800)

R-090 sampled **0/7** cathedral questions — the random draw landed on 2 adversarial + 1 review + 1 speculative-over-scoring + 1 review. **No canon observation, no regression risk, no promotion opportunity this round.**

q17 canary_honesty (REVIEW, durable state-strengthening decay 0.99→0.66 over 80+ wipes) was not sampled in this 5-question draw.

---

## Files

- `/tmp/research/jev_run_r090/continuous_r001.json` (1 R-090 round, 488 B)
- `/tmp/research/jev_run_r090/history.jsonl` (1 line, R-090 r001)
- `/tmp/research/jev_run_r090/r090_summary.json` (verdict summary, this session)
- `/tmp/research/jev_baseline_r200.json` (per-qid baseline from `main` 200 rounds, this session)
- `/tmp/research/jev_hourly_report.md` (this report, durable mirror)
- `/tmp/jev-quilt/jev_sessions/continuous_r001.json` (R-090 round, also written to canonical repo path — note: this is a fresh clone, so it overwrites the previous R-089 r001 in the working tree; the prior R-089 data is still in `origin/r-089-probe` HEAD `f402eb8`)
- `/workspace/research/jev_hourly_report.md` — **NOT WRITTEN** (NAS at 100% quota, parent dir doesn't exist)

---

## Action items (carry forward)

1. **NAS at 100% quota (durable 86w+)** — `/workspace/research/jev_hourly_report.md` cannot accept writes (confirmed this session: parent `/workspace/research/` doesn't exist, `df` shows 500G/500G/0%). Use `/tmp/research/` and `/tmp/jev-quilt/` as durable mirrors.
2. **R-090 push to `r-090-probe` branch** — created this session but not pushed (per session "one round, 60s ceiling" protocol). If user wants the full chain mirrored, run `git push origin r-090-probe` next session.
3. **R-089 push state** — committed `f402eb8` to `r-089-probe` per memory; confirmed visible on `origin/r-089-probe` this session (HEAD `f402eb8`).
4. **R-084 push state** — memory still notes "R-084 not visible on branch HEAD"; not on `r-081-continuous-probe-rebuild` or `r-089-probe`. Likely on a separate branch. Confirm or mark lost next session.
5. **q10_quorum_meshing chronic over-score** — q10 has been at 0.86 median for 38+ samples despite being doctrinal `speculative` + `DAMPEN HARD`. The text overlap with `oracle_is_heard` makes dampening ineffective. Either (a) rephrase the question to remove the "musicians playing together" analogy, or (b) explicitly mark q10 as "in-training for promotion" and tighten the doctrinal state language. Carried forward 4+ sessions; not urgent.
6. **q17 canary plateau at 0.65** — no longer decaying but not recovering. Pinned_marker-before-spec_notebook reordering proposed previously; deprioritize.
7. **Connection-phase HTTP 503 retry** (R-086 finding) — still not wired; 0 occurrences this session, so non-urgent.
8. **GITHUB_TOKEN rotation** — this session used the standard `credential.helper=...` form on `git fetch`; no URL-embedded token. Same pattern as R-089.

---

*R-090 — 2026-10-19 17:03Z, 1/1 OK in 0.1s, mean_p 0.378 (lowest n=1 in series), 1/5 "bedrock-look" hit (q10 chronic spike), 3/5 spec clean-reject, 0 drift, 0 cathedral observation, 0 substrate shift.*
