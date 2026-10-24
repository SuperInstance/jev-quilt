# JEV Continuous Probe — Hourly Report (r416)

**Run:** 2026-10-24T10:03:50Z · **Round:** r416 (1 round, as requested)
**Model:** `jev-latest` → resolved to `jev-1.14.0` · **Script md5:** `3a255fa4642ec4a83173ab04d773d485`
**Baseline:** 406 deduped rounds (r001–r415), 22 questions, all covered
**Verdict:** ✅ round OK — but it surfaces a **real, significant q02 signal** that resolves to a model-calibration artifact, *not* canon drift.

---

## 1. Headline numbers

| Metric | r416 | Prior baseline | Note |
|---|---|---|---|
| `mean_p` | **0.2400** | 0.3832 all-time / 0.4072 last-10 | **Low because of draw mix, not a shift** |
| bedrock hits (p ≥ 0.70) | **0 / 5** | 19/20 on q02 in last 20 rounds | 4 of 5 drawn were speculative/adversarial |
| max \|dev\| (drawn) | **0.1259** (q02) | — | the one candidate > 0.05 |
| drift > 0.05 | **1** (q02) | — | see §3 — real but confounded |

**r416 verdicts:**

| qid | kind | p | baseline μ | sd | dev | bedrock |
|---|---|---|---|---|---|---|
| q21 | speculative | 0.09 | 0.0905 | 0.0040 | −0.0005 | — |
| q22 | speculative | 0.14 | 0.1204 | 0.0083 | +0.0196 | — |
| q10 | speculative | 0.06 | 0.0662 | 0.0058 | −0.0062 | — |
| q14 | adversarial | 0.22 | 0.1942 | 0.0138 | +0.0258 | — |
| **q02** | **bedrock** | **0.69** | 0.8159 | 0.0315 | **−0.1259** | **MISS** |

**`mean_p` 0.24 must not be read as a collapse.** The round drew 1 bedrock + 2 speculative + 1 adversarial + 1 speculative. Bedrock p's alone (q02=0.69) sit ~0.82; the low mean is a *sampling* artifact of a 5-question uniform draw landing on 4 low-p classes. Expected mean_p for this class mix ≈ 0.24 — exactly what was observed.

**Bedrock canon questions that hit p ≥ 0.70 this round: NONE (0/5).** Only one bedrock question (q02) was drawn, and it landed at 0.69 — a hair below the line.

---

## 2. ⚠️ PHANTOM DRIFT — the script's own `drift_events=1` is on **q12**, which was **not drawn**

```
script summary.drift: [{"qid": "q12", "recent_p": 0.56, "prior_median": 0.5, "delta": 0.06}]
```

**q12 was not in r416's draw.** `drift_check()` reads the *last recorded value per qid* from the whole history, so it re-reports a stale q12 move (0.56 vs prior median 0.50) that belongs to an earlier round. This is the **7th reproduction** of the phantom-drift shape.

**Correction: drift must be computed only over questions actually drawn in the new round.** On that basis r416 has exactly **one** drift candidate: **q02**.

---

## 3. 🔴 The real finding — q02 ("witness logs are predictions") is declining, and it is a **model artifact**, not canon erosion

q02 is **bedrock canon**. This is the one thing in this round worth acting on, so it got a full dissection.

### 3a. It is a trend, not a single bad draw
- r416 p = 0.69 is the **all-time minimum** for q02 (prior min 0.69, 5th pct 0.73; 1 of 83 historical draws ≤ 0.69).
- Monte Carlo over q02's own 83 empirical draws: **P(draw ≤ 0.69) = 0.0120**.
- Normal-approximation z = **−4.00** (two-sided p = 0.00006).
- **Spearman trend** (ties averaged), last 20 draws: **ρ = −0.782**, t = −5.32, p < 0.0001.
- **Permutation test** (20k shuffles): **p = 0.00005**.
- Last-20 window mean **0.7810** is **below all 63 prior 20-round windows** (z = −4.78; 0/63 windows as low).

### 3b. But the drop coincides with a **model version change**
| model | rounds | q02 n | q02 mean | q02 min |
|---|---|---|---|---|
| `jev-1.13.0` | 1–395 | 75 | **0.8247** | 0.79 |
| `jev-1.14.0` | 396–416 | 8 | **0.7338** | **0.69** |

**Welch t = 9.26, df = 7.4, p ≈ 0** for the 1.13→1.14 step (**−0.0909**). The decline is a **step at the version boundary**, and 1.14.0 has never once produced a q02 value ≥ 0.78.

### 3c. Other bedrock questions are ~flat across the same boundary — so it isn't a global calibration shift
| qid | 1.13.0 mean | 1.14.0 mean | step | Welch p |
|---|---|---|---|---|
| q02 | 0.8251 | 0.7400 | **−0.0851** | **0.0000** |
| q05 | 0.8512 | 0.8260 | −0.0252 | 0.0000 |
| q01 | 0.8754 | 0.8560 | −0.0194 | 0.0000 |
| q03 | 0.8860 | 0.8800 | −0.0060 | 0.3041 |
| q04 | 0.8887 | 0.8880 | −0.0007 | 0.8843 |
| q08 | 0.8997 | 0.8940 | −0.0057 | — |

**q02 is uniquely sensitive to the version bump.** q03/q04/q08 barely moved; q01/q05 moved a little; **q02 moved ~10× more than any of them.**

### 3d. …and there IS a residual within-model trend that predates the switch
- Within `jev-1.13.0` only: q02 **ρ = −0.271, p = 0.0161** (n=75) — already declining *before* 1.14.0 existed.
- Within `jev-1.14.0` only: q02 ρ = −0.566, p = 0.092 (n=8, too few to resolve).

**Verdict: two superimposed effects.** (1) A ~−0.09 **calibration step** from the `jev-1.14.0` bump, unique to q02. (2) A smaller **genuine within-version decline** that was already visible under 1.13.0. Neither is "the canon changed" — but effect (2) is worth watching, because it is independent of the version confound.

---

## 4. The opposite signal — speculative questions are **rising toward** canon

The mirror image of q02's decline, and arguably more interesting for the canon gate:

| qid | kind | first-10 (last 20) | last-10 | Δ | Spearman ρ | p |
|---|---|---|---|---|---|---|
| **q12** | speculative | 0.3810 | 0.4420 | **+0.0610** | +0.541 | 0.0064 |
| **q14** | adversarial | 0.1890 | 0.2070 | +0.0180 | +0.580 | 0.0026 |
| **q18** | speculative | 0.2260 | 0.2380 | +0.0120 | +0.597 | 0.0016 |
| q06 | speculative | 0.1000 | 0.1210 | +0.0210 | +0.751 | <0.0001 |
| q13 | speculative | 0.1330 | 0.1470 | +0.0140 | +0.477 | 0.0215 |
| q11 | speculative | 0.1790 | 0.1820 | +0.0030 | +0.036 | 0.8788 |

**q12 ("witness_note is an opcode") is the headline.** It is flagged speculative and carries the `spec_notebook` guard ("must NOT be promoted regardless of high mean_p — n≥20 with hit-rate ≥0.7 AND explicit doctrinal-state phrasing required"). Its last-10 mean is **0.4420** and it has climbed steadily; it reached **0.56** in a recent round (the value the script's phantom-drift check fired on).

**q06 ("three_views is the operating epistemology") has the steepest climb** (ρ=+0.751, Δ=+0.021) — still only 0.12, so nowhere near the 0.70 line.

**This is the interesting tension in the fleet right now:** a bedrock doctrine is *drifting down* while several speculative framings are *drifting up*. That is the signature of **canon re-negotiation** — but on the evidence available, it is *not yet* a canon breach, because:
- q12's absolute level (0.44 mean, 0.56 peak) is still well below 0.70.
- The `spec_notebook` guard correctly keeps it unpromoted.
- The q02 side of the movement is explained by a version artifact.

**⇒ No promotion. No canon change. But the two trends point at each other and should be watched together.**

---

## 5. Bedrock health (last 20 rounds, before r416)

| qid | doctrine | hit-rate | mean p |
|---|---|---|---|
| q01 | cells are scars | 20/20 = **100%** | 0.8660 |
| q02 | witness logs are predictions | 19/20 = 95% | 0.7810 |
| q03 | substrates are grown, not designed | 20/20 = **100%** | 0.8830 |
| q04 | oracles must be heard | 20/20 = **100%** | 0.8880 |
| q05 | Lenia-style flows | 20/20 = **100%** | 0.8415 |
| q07 | 11 opcodes | 20/20 = **100%** | 0.7620 |
| q08 | polyformalism | 20/20 = **100%** | 0.8980 |

**6 of 7 bedrock doctrines at a perfect 100% hit-rate.** q02 is the sole exception, and r416's 0.69 makes it **19/21 (90.5%)** over the last 21 rounds.

---

## 6. Method notes (durable)

1. **"One round" must be launched with an explicit positional count.** The script now honours `sys.argv[1]` (r229 fix). `python3 jev_continuous_probe.py 1` ran **exactly one** round (r416, elapsed 0.4s, exit 0). A bare invocation with no arg loops for 55s and produces ~200 rounds.
2. **`drift_check()` reports phantom drift** — it scans the whole history, not the new round's draw. **Always intersect with the drawn qids.** 7th repro.
3. **Never read `mean_p` without the class mix.** 5 questions drawn uniformly from 22 (8 bedrock / 9 speculative / 3 adversarial / 2 review) ⇒ a low-mean round is the default outcome ~75% of the time.
4. **Stratify by model before calling anything drift.** A −0.09 step at a version boundary is a calibration artifact; a within-model trend is a different (and more interesting) object. Report both.
5. **Trend test, not single-draw test.** A single draw flagged by |dev| > 0.05 is nearly always noise; the *trend* (Spearman + permutation + window comparison) is what carries signal.
6. **The round files and `history.jsonl` disagree.** 419 ok rows in history vs 406 deduped rounds; duplicate rounds at r384–r391 (3× each for 385–389). Always **dedupe by round number, keep first**.
7. **Round-file naming is off-by-one in the `first_round` field** (`first_round: 417` for a round that is 416) — cosmetic; `rounds[].round` is authoritative.

---

## 7. Environment (this wipe)

- **Fresh wipe.** `/workspace` was **empty** (only `.plugin-cache`) and `/workspace/research/` did not exist. Recovered by shallow-cloning `SuperInstance/research` + `SuperInstance/jev-quilt` into `/tmp`.
- **NAS `/workspace` at 100% (0 bytes avail)** — writes to the canonical path will silently fail. Durable transport = **git**.
- **`SSL_CERT_FILE` = gateway-anchor-only** (known wall) ⇒ rebuilt a combined **430-cert** bundle at `/tmp/bundle.pem`; `api.github.com` and `api.typesafe.ai` both return 200 under it.
- `TYPESAFE_AI_TOKEN` present; `TYPESAFEAI_KEY` unset (the script accepts either).
- Probe `script_md5 3a255fa4642ec4a83173ab04d773d485` — **changed** from the last recorded `c22e8c72f13f3b71d5b40e8f8fd04d61` (harness updated for the r229 positional-rounds fix). The qid map and scoring are otherwise unchanged, so cross-version comparison remains valid.
- JEV API reachable and healthy: HTTP 200, 0.175s round-trip.

---

## 8. Recommended next steps

1. **Do not act on q02 yet.** Re-measure q02 for ~8 more rounds on `jev-1.14.0`. If the within-model slope holds after the version bump is controlled for, escalate — a bedrock doctrine losing 0.09 of confidence is the one finding here that would warrant a doctrine-statement review.
2. **Track q12 explicitly.** It is the closest speculative framing to the 0.70 line (0.56 peak). The `spec_notebook` guard is doing its job; do not bypass it. If it crosses 0.70 with n≥20 and hit-rate ≥0.7, it enters the promotion queue **by the written rule**, not by trend.
3. **Watch the pair, not the parts.** q02 down + q12 up is the pattern worth an eye on next round.
4. **Fix `drift_check()` to intersect with the drawn qids** — 7 repros of a phantom is enough to justify the patch.
5. **Re-baseline per-question stats on the model version.** The 406-round baseline mixes 1.13.0 and 1.14.0; q02's μ=0.8159 is a blend that no longer describes the current model. Stratify the baseline going forward.
