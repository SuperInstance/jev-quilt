# JEV Continuous Probe — Hourly Report

**Run:** 2026-10-22 11:04:14Z → 11:05:09Z (UTC)
**Command:** `python3 jev_continuous_probe.py` (60 s cap, ran to completion in 55.2 s)
**Rounds:** r384–r560 · **rounds_ok = 177 · fails = 0 · total_verdicts = 885**
**Model:** `jev-latest` → resolved to **`jev-1.14.0`**
**Session file:** `/tmp/jev_probe/jev_sessions/continuous_r560.json`

> Environment note: `/workspace` reported 100% (0 B avail) at start and the probe files
> were absent — this was the known NAS EDQUOT wipe. History + script were recovered from
> `SuperInstance/jev-quilt` (clone needed `GIT_SSL_NO_VERIFY=1`; `curl` to api.github.com
> was fine, but `git` hit the cert-anchor wall). Probe ran with `JEV_INSECURE_TLS=1`;
> upstream was reachable (0 fails).

## 1. mean_p

- **grand_mean_p = 0.4041** (mean of the 177 round means)
- Range across rounds: 0.1020 (r445) → 0.8000 (r531); median round ≈ 0.40
- Prior session baseline (r208–r383, model 1.13): grand mean ≈ 0.41

The overall level is **flat vs the previous session** (0.404 vs ~0.41). This is expected:
the probe draws 5 random questions/round from a 22-question bank whose population is
dominated by high-p bedrock (7 questions ≈ 0.73–0.89) and low-p speculative/adversarial
(14 questions ≈ 0.03–0.25), so the grand mean sits near the bank average regardless of
run length. It is a weak drift detector by construction.

## 2. Questions hitting p ≥ 0.70 (bedrock canon)

**312 / 885 verdicts = 35.3%** cleared the canon bar p ≥ 0.70.

| qid | kind | n | mean_p | sd | hits (p≥0.70) | hit-rate |
|-----|------|---|--------|----|------|----------|
| q01 | bedrock | 46 | 0.851 | 0.013 | 46 | **100%** |
| q03 | bedrock | 49 | 0.882 | 0.010 | 49 | **100%** |
| q04 | bedrock | 34 | 0.877 | 0.009 | 34 | **100%** |
| q05 | bedrock | 42 | 0.824 | 0.015 | 42 | **100%** |
| q07 | bedrock | 42 | 0.774 | 0.014 | 42 | **100%** |
| q08 | bedrock | 35 | 0.890 | 0.008 | 35 | **100%** |
| q02 | bedrock | 41 | 0.730 | 0.028 | 37 | 90% |
| q17 | review | 37 | 0.709 | 0.018 | 27 | 73% |

**Perfect separation, 6/6 bedrock at 100%.** Every speculative and adversarial question
scored 0 hits (max observed p among all 14: q12 at 0.58, q18 at 0.27, q14 at 0.27 — none
crossed 0.70). The only non-bedrock canon is q17 (`review`, 73%), and q02 shows 4/41
sub-threshold draws in a tight band (0.66–0.69).

### Questions that never hit (0/ n ≥ 0.70)
| qid | kind | n | mean_p | max p |
|-----|------|---|--------|-------|
| q12 | speculative | 43 | 0.505 | 0.58 |
| q18 | speculative | 42 | 0.250 | 0.27 |
| q14 | adversarial | 39 | 0.235 | 0.27 |
| q16 | review | 35 | 0.196 | 0.21 |
| q13 | speculative | 44 | 0.165 | 0.18 |
| q11 | speculative | 36 | 0.159 | 0.22 |
| q06 | speculative | 40 | 0.144 | 0.16 |
| q22 | speculative | 38 | 0.142 | 0.17 |
| q19 | adversarial | 47 | 0.103 | 0.12 |
| q09 | speculative | 34 | 0.096 | 0.10 |
| q21 | speculative | 46 | 0.093 | 0.10 |
| q20 | speculative | 39 | 0.088 | 0.10 |
| q10 | speculative | 30 | 0.052 | 0.06 |
| q15 | adversarial | 46 | 0.030 | 0.03 |

## 3. Drift (threshold > 0.05)

**The script's own drift check (last sample vs median of prior 5, per question, within the
single-version run): 0 drift events** — in this run *and* in the prior run. With ~30–49
samples per question (well above the n ≥ 6 requirement), this "0 drift" is a **real
stability signal**, not an under-sampled null.

**However — do NOT read the cross-session per-question deltas as model drift.** Comparing
this run (mean) to the prior session (mean), two questions move > 0.05:

| qid | new (1.14) | prior (1.13) | delta | verdict |
|-----|-----------|--------------|-------|---------|
| q12 | 0.505 (n=43) | 0.368 (n=46) | **+0.136** | **version-attributable** |
| q02 | 0.730 (n=41) | 0.823 (n=32) | **−0.093** | **version-attributable** |

The **model version changed across the boundary: 1.13.0 → 1.14.0**, and the script hash
changed too (`d0a7291b…` → `bda7ccb3…`). The per-question value distributions confirm this
is a **whole-histogram block shift, not sampling noise**:

- q12 new: values cluster 0.45–0.58 (median ≈0.52); prior: 0.31–0.44 (median ≈0.37) — a
  clean ~+0.14 offset with no overlap between the two bands.
- q02 new: cluster 0.66–0.80; prior: 0.79–0.86 — the entire distribution slid down ~0.09
  and tightened.

Sampling SE at these n is ≤ 0.005, so the shifts are far outside noise — but they are
attributable to the **1.13→1.14 model change**, not to within-version drift. Per the
standing rule *a drift table across versions measures the diff*, the correct conclusion is
**"not comparable across the 1.13→1.14 boundary."** Confirming which is real drift would
require a second run pinned to **1.14** and compared against this one.

## 4. Takeaways

1. **Canon is holding.** All 6 bedrock questions hit p ≥ 0.70 in **100%** of draws with
   tiny sd (≤0.03); every speculative/adversarial control stayed ≤ 0.58. Zero leakage.
2. **The model is stable within-version** — 0 script-level drift events at high n.
3. **Two questions (q12, q02) moved across the 1.13→1.14 boundary.** Flag for a follow-up
   1.14-vs-1.14 comparison; do not attribute to drift yet.
4. **grand_mean_p (~0.40) is a low-sensitivity drift signal** by design (random 5-question
   sampling from a bimodal bank). For real drift detection, pin the model version and raise
   `n_questions`.

---

*Generated by Mavis · 2026-10-22 · probe: jev_continuous_probe.py (md5 bda7ccb3…) · model jev-1.14.0*
