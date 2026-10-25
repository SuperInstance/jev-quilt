# JEV Hourly Probe Report — r444

**Run:** 2026-10-25T18:01:49Z · model `jev-1.14.0` · script md5 `3a255fa4` (unchanged, directly comparable to r443)
**Corpus:** 663 round files → 422 distinct historical rounds (r1–r443) + this round; 22 qids

---

## 1. Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.5460** |
| **Bedrock hits (p ≥ 0.70)** | **3 / 5** — q01 0.84, q03 0.87, q07 0.79 |
| **Real drift (> 0.05)** | **NONE** — 0 of 5 drawn qids |
| Series z | +1.15 (rank 361/422, 85.5th pct) |
| P(mean_p ≥ 0.546) under history | ~0.150 |

## 2. The round

| qid | kind | p | hit | same-model mu | dev | z |
|---|---|---|---|---|---|---|
| q03 | bedrock | 0.87 | ✅ | 0.8820 | −0.0120 | −0.90 |
| q06 | speculative | 0.14 | — | 0.1400 | +0.0000 | +0.00 |
| q01 | bedrock | 0.84 | ✅ | 0.8562 | −0.0162 | −1.75 |
| q07 | bedrock | 0.79 | ✅ | 0.7700 | +0.0200 | +1.35 |
| q20 | speculative | 0.09 | — | 0.0862 | +0.0038 | +0.62 |

## 3. Drift verdict — NONE

**0 of 5** drawn qids exceed |dev| = 0.05 under the same-model (`jev-1.14.0`) baseline.

### 🔴 The script's `drift_events=1` is a PHANTOM (19th repro)
The flag names **q12** — which was **not drawn** in r444. `drift_check()` (jev_continuous_probe.py:317)
scans the whole history and takes `samples[-1][1]` as "recent_p" for *every* qid, so an undrawn qid
re-reports its stale last value. q12's 0.54 is from **r438** (6 rounds stale).

Its delta is **exactly 0.05** (0.54 vs prior median 0.49) — a boundary value that the `> 0.05`
test treats as a hit only because of float representation. q12's own series (n=96, mean 0.386,
sd 0.055, range 0.30–0.56) is a **flat plateau that has never once crossed 0.70**. It is not drifting.

### 🔴 σ≈0 trap, 7th recurrence
**q01 posted the largest z of the round (−3.12) on a |dev| of only 0.0332** (pooled sd 0.0106).
The eye catches the z; |dev| says nothing is wrong. Under the same-model baseline q01's z falls to
**−1.75** and its dev to −0.0162. **|dev| first, z second.**

### Model-switch artifact
Historical rounds span two models: `jev-1.13.0` (r2–r395) and `jev-1.14.0` (r396–). Pooling them
inflates every sd and manufactures false z-scores. Under the pooled baseline **4 of 5** drawn qids
would false-alarm on z; under the same-model baseline **0** do.

| qid | pooled dev | pooled z | same-model dev | same-model z |
|---|---|---|---|---|
| q06 | +0.0357 | **+2.45** | +0.0000 | **+0.00** |
| q01 | −0.0332 | **−3.12** | −0.0162 | −1.75 |
| q07 | +0.0338 | +1.97 | +0.0200 | +1.35 |
| q03 | −0.0155 | −1.59 | −0.0120 | −0.90 |
| q20 | −0.0126 | −1.10 | +0.0038 | +0.62 |

## 4. 3/5 bedrock is DETERMINISTIC, not a signal

Given the drawn mix, 3/5 was the **only possible outcome**:
- q03, q01, q07 → hit_prob **1.000** each (all three are 100%-hit bedrock qids)
- q06, q20 → hit_prob **0.000** each (speculative, p≈0.10)

Monte-Carlo P(K=3 | drawn mix) = **1.0000**. The 3/5 count says **which questions were sampled**,
not how strong the oracle is. Compare like-for-like on bedrock only:
- r444 bedrock_mean = **0.8333** (q01 0.84, q03 0.87, q07 0.79) — *lower* than r443's 0.8700.
- mean_p rose because the draw mix shifted toward high-p bedrock qids, not because anything improved.

## 5. Cathedral — 6/7 at 100% (holds)

| qid | n | mu | sd | hit_rate |
|---|---|---|---|---|
| q01 | 107 | 0.8732 | 0.0106 | 100% |
| q02 | 88 | 0.8083 | 0.0406 | **96.6%** (3 misses: r416 0.69, r423 0.69, r425 0.68) |
| q03 | 97 | 0.8855 | 0.0097 | 100% |
| q04 | 98 | 0.8877 | 0.0095 | 100% |
| q05 | 93 | 0.8465 | 0.0166 | 100% |
| q07 | 85 | 0.7562 | 0.0171 | 100% |
| q08 | 84 | 0.8981 | 0.0098 | 100% |

q02 is the sole imperfect member — a high-variance bedrock (sd 0.041, 5x the others) that clips
the 0.70 gate by hair. Not a regression: q02's last three draws were 0.74, 0.71 (r441, r442) and
it was not drawn in r443/r444.

**Speculative + adversarial ever ≥ 0.70: 0 / 1,348.** The only non-bedrock qid that ever crosses
0.70 is **q17** (review, 73.8%, 0.66–0.75 plateau) — unchanged.

## 6. Bottom line

**r444 is an ordinary round.** mean_p 0.5460 sits at the 85th percentile, but P(mean_p ≥ 0.546) ≈ 0.150
under the historical distribution — a perfectly common draw. **No drift. No regression. No signal.**
The two things worth recording are method artifacts, not findings: the script's own drift counter
fired on a qid it did not sample (19th repro), and the pooled-baseline σ inflation would have
false-alarmed on 4 of 5 qids had the model switch not been segmented out.

---

### Environment notes (durable)
- **29th consecutive wipe** — `/workspace` empty at start; NAS at 100% (600G/600G).
- Recovery: clone `SuperInstance/jev-quilt` → `/tmp/jev-quilt` (GIT_SSL_NO_VERIFY=1), then
  `rm -rf /workspace/research && ln -s /tmp/jev-quilt /workspace/research`.
- Script md5 `3a255fa4` unchanged ⇒ mean_p directly comparable to r443.
- Root script `jev_continuous_probe.py` resolves `SESSION_DIR` relative to *its own* location
  ⇒ must sit at repo root. `research/jev_continuous_probe.py` is the runpy launcher (md5 `2bdd4768`).
- Round count is **positional**: `python3 jev_continuous_probe.py 1` — omitting it defaults to 200.
