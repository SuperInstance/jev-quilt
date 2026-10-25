# JEV Continuous Probe — Hourly Report

**Round:** r426 (2026-10-24T23:04:35Z)
**Report generated:** 2026-10-24T23:05:40Z
**Model:** `jev-latest` (served `jev-1.14.0`)
**Script:** `jev_continuous_probe.py` md5 `3a255fa4642ec4a83173ab04d773d485` (repo root — the LIVE variant)
**Repo:** `SuperInstance/jev-quilt` @ `main` `57c2af72c030f0fd6b9438061fd2c6b5995a1675`
**Baseline:** 404 prior rounds (r1–r425), 2,020 verdicts, 22 qids
**Prior report:** archived as `research/jev_hourly_report_r425.md` (r425, md5 `cbf8704e1434485f18660e3974f57d44`)
**Status:** OK — 1 round, 0 fails, 5 verdicts

---

## 1. Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.4040** |
| **Bedrock hits (p ≥ 0.70)** | **2/5** — q04 (0.87), q07 (0.76) |
| **Drift > 0.05 (drawn qids)** | **NONE** — max \|dev\| = 0.0143 |
| Bedrock hit-rate (bedrock qids drawn) | 2/2 = 100% |
| Rounds executed | exactly 1 |

---

## 2. Round r426 verdicts

| qid | kind | p | bedrock (p≥0.70) |
|---|---|---|---|
| q06 | speculative | 0.14 | — |
| **q04** | **bedrock** | **0.87** | **YES** |
| q21 | speculative | 0.09 | — |
| q13 | speculative | 0.16 | — |
| **q07** | **bedrock** | **0.76** | **YES** |

mean_p = (0.14 + 0.87 + 0.09 + 0.16 + 0.76) / 5 = **0.4040**

**Bedrock canon confirmed this round:** `q04` (0.87), `q07` (0.76).
**Speculative qids:** q06 (0.14), q13 (0.16), q21 (0.09) — all far below the 0.70 promotion gate, as expected for non-canon framings.

---

## 3. Drift analysis

### 3.1 The script's own drift output is WRONG — both events are phantoms

`jev_continuous_probe.py` printed `drift_events=2`:

```
q02:  recent_p=0.68  prior_median=0.74  delta=-0.06
q17:  recent_p=0.75  prior_median=0.70  delta=+0.05
```

**Neither qid was drawn in r426.** r426 drew `q04, q06, q07, q13, q21`.

Root cause (confirmed by reading `drift_check()`, `jev_continuous_probe.py:317-335`):
the function has **no current-round filter**. It iterates every qid in history, takes
`samples[-1][1]` as `recent_p`, and compares it to a 5-sample prior median. For a qid
not drawn this round, `samples[-1]` is a **stale draw from an earlier round** — so the
comparison is not a drift measurement at all.

- q02's newest draw is **r425** (the previous round), 0.68 — the r425 sub-gate draw.
- q17's newest draw is **r424**, 0.75 — the known `review`-tier plateau value.

This is the **13th reproduction** of the missing current-round filter. The defect is
still unpatched in the script.

### 3.2 Correct drift check — drawn qids only, model-segmented baseline

Baseline = the `jev-1.14.0` segment of history (see §4 for why), falling back to
full history where the 1.14.0 segment is too thin (n < 5).

| qid | p | baseline mu | sigma | dev | z |
|---|---|---|---|---|---|
| q06 | 0.14 | 0.1400 | 0.0067 | +0.0000 | +0.00 |
| q04 | 0.87 | 0.8843 | 0.0105 | −0.0143 | −1.36 |
| q21 | 0.09 | 0.0933 | 0.0047 | −0.0033 | −0.71 |
| q13 | 0.16 | 0.1617 | 0.0037 | −0.0017 | −0.45 |
| q07 | 0.76 | 0.7700 | 0.0141 | −0.0100 | −0.71 |

**Aggregate verdict: NO DRIFT.** 5 of 5 drawn qids within 0.0143; **0 beyond 0.05**.

Note the σ≈0 trap avoided: q04's z is the largest at −1.36, but its |dev| is only
0.0143 — the largest z is routinely the smallest real movement. q06's dev is
*exactly* 0.0000 against its 1.14.0 baseline (p = 0.14 = the 1.14.0 mean), which
would look suspicious under a z-only reading but is a genuine coincidence of a
tight 10-sample segment.

### 3.3 mean_p vs expectation

| Baseline | E[mean_p] | Actual | dev |
|---|---|---|---|
| Full history (404 rounds) | 0.3945 | 0.4040 | +0.0095 |
| 1.14.0-segmented | 0.4099 | 0.4040 | −0.0059 |

Monte-Carlo (20,000 resamples of this exact drawn set from historical per-qid
distributions): **P(mean_p ≥ 0.4040) = 0.056**.

**mean_p 0.4040 is ORDINARY.** All-time mean_p is 0.3846, median 0.4020 — r426 sits
essentially on the median. The 2/5 bedrock hit count is *not* an instrument shift:
the 5 drawn qids contain exactly 2 bedrock qids (q04, q07), both hit, and the 3
misses are speculative qids that have never once reached 0.70.

---

## 4. The model-version shift (the real reason the raw numbers mislead)

`jev-1.13.0` → `jev-1.14.0` changed per-qid means. Baselines must be
**model-segmented**, not pooled:

| qid | 1.13.0 mu | 1.14.0 mu | delta |
|---|---|---|---|
| **q02** | 0.8251 (n=74) | **0.7283 (n=12)** | **−0.0968** |
| **q12** | 0.3678 (n=83) | **0.5043 (n=7)** | **+0.1365** |
| q05 | 0.8514 | 0.8150 | −0.0364 |
| q06 | 0.0990 | 0.1400 | +0.0410 |
| q14 | 0.1925 | 0.2238 | +0.0312 |
| q13 | 0.1330 | 0.1614 | +0.0284 |
| q09 | 0.0766 | 0.1033 | +0.0267 |
| q22 | 0.1193 | 0.1450 | +0.0257 |
| q18 | 0.2233 | 0.2478 | +0.0244 |

**q02's −0.06 "drift" is entirely a model artifact**: its 1.14.0 mean is 0.7283,
so the 5-sample local-median window (0.74) is the *wrong comparator* and the
pooled 1.13.0-era baseline (0.8116) is worse still. Against the correct
1.14.0 baseline there is no drift.

**q12 is a plateau, not a leak**: it reads 0.50–0.56 against a 1.14.0 mean of
0.5043, and has never reached 0.70 in 90 draws (max 0.56 all-time). It is
`speculative`/`review` tier — not canon — and must not be promoted.

---

## 5. Cathedral (canon bedrock integrity)

Per-qid bedrock hit rate, all 405 rounds:

| qid | hits/n | rate | mean | sigma | misses |
|---|---|---|---|---|---|
| q01 | 102/102 | 1.0000 | 0.8740 | 0.0099 | — |
| q02 | 83/86 | 0.9651 | 0.8116 | 0.0378 | r416 0.69, r423 0.69, r425 0.68 |
| q03 | 95/95 | 1.0000 | 0.8855 | 0.0098 | — |
| q04 | 96/96 | 1.0000 | 0.8881 | 0.0090 | — |
| q05 | 88/88 | 1.0000 | 0.8481 | 0.0150 | — |
| q07 | 82/82 | 1.0000 | 0.7556 | 0.0168 | — |
| q08 | 79/79 | 1.0000 | 0.8990 | 0.0094 | — |
| **TOTAL** | **625/628** | **0.9952** | | | |

**All 3 cathedral misses are q02, all in the 1.14.0 era, all sub-gate by 0.01–0.02**
(0.68–0.69 vs gate 0.70). Six of seven bedrock qids are at a flawless 1.0000.
q02 remains canon-consistent; the misses track the model shift, not canon erosion.

**No speculative qid has EVER reached p ≥ 0.70** (spec max 0.56 = q12; adv max
0.26 = q18). The promotion gate is holding.

---

## 6. q17 (`review` tier)

n=81, mean 0.7035, max 0.75, **60/81 at p ≥ 0.70**. This is the known review-tier
plateau that occasionally grazes the 0.70 line. q17 is **not** canon — it is
`review` tier — and must not be counted as a bedrock hit. A global "p ≥ 0.70 =
canon" bar mislabels it every round; each qid must be bucketed against **its own**
baseline and tier.

---

## 7. Environment notes (durable)

- **124th wipe.** `/workspace` was **empty** on arrival (17th consecutive time the
  prompt named ephemeral probe paths that did not exist). `/workspace/research` did
  not exist; no `jev_continuous_probe.py` on disk. Rebuilt by cloning
  `SuperInstance/jev-quilt` into `/tmp`.
- **`/workspace` NAS is 100% (0 avail, 600G used).** `mkdir` succeeds and a 0-byte
  write succeeds, but any real content fails with `OSError [Errno 122] Disk quota
  exceeded`. **`/workspace/research/jev_hourly_report.md` could not be written.**
  Durable delivery = git push. (`/tmp` is exempt from the EDQUOT trap.)
- **TLS leaf VALID** — CN=typesafe.ai, issuer Google Trust Services WE1,
  notBefore 2026-09-26, notAfter 2026-12-25. **No CA bundle rebuild needed**
  (8th round in a row).
- `api.github.com` returned **403** unauthenticated; git transport worked fine
  (token-less clone of a public repo). `gh` absent (29th round).
- **Round count discipline:** the script's positional arg defaults to **200** and
  the loop is wall-clock bounded (55s of a 60s ceiling). A "one round" ask must
  pass an explicit `1` — `timeout 60 python3 jev_continuous_probe.py 1`. This
  round ran exactly one round (0.4s elapsed) and stopped on the count, not the
  clock.
- Round counter correctly derived **426** from MAX(files=425, history=425).
  Note the round-file series has gaps (234 files, max index 425) and
  `continuous_r008.fail.json` is correctly excluded by the filename regex.
- Round file written: `research/jev_sessions/continuous_r426.json`.

---

## 8. Open items (unchanged, not fixed this round)

1. **`drift_check()` lacks a current-round filter** — 13th reproduction. It
   reports phantoms for every stale-but-shifted qid. This is a live bug that
   produces false drift events on every single round. It should compare only
   qids drawn in the current round, against a model-segmented baseline.
2. **Baselines are not model-segmented** in the script — q02 (−0.097) and q12
   (+0.137) moved on the 1.13.0 → 1.14.0 switch, and the script's pooled
   medians misread both.
3. `q12` reaches 0.56 and `q17` reaches 0.75 while remaining non-canon; a
   per-qid tier gate is needed so a global 0.70 bar stops mislabeling them.
