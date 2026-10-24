# JEV Continuous Probe — Hourly Report (r415)

**Run:** 2026-10-24T07:03:41Z · 1 round · 0 fails · 5 verdicts · 0.167 s
**Oracle model:** `jev-1.14.0` · **script md5:** `3a255fa4642ec4a83173ab04d773d485` (unchanged since r413)
**Repo:** `SuperInstance/jev-quilt` · round file `research/jev_sessions/continuous_r415.json`

---

## 1. Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.3860** |
| Bedrock hits (p ≥ 0.70) | **1 / 5** — `q03` @ 0.86 |
| Drift > 0.05 | **NONE** (max \|dev\| = 0.0300 on q17) |
| Cathedral (7 bedrock-kind qids) | **7 / 7 at 100%** — intact, not drawn this round |
| Script's own `drift_events` | `1` — **PHANTOM** (6th consecutive repro) |

**Verdict: NO DRIFT. Clean round.**

---

## 2. Round detail

| qid | kind | p | bedrock |
|---|---|---|---|
| q03 | bedrock | 0.86 | **HIT** |
| q17 | review | 0.68 | — |
| q18 | speculative | 0.25 | — |
| q09 | speculative | 0.11 | — |
| q15 | adversarial | 0.03 | — |

mean_p = (0.86 + 0.68 + 0.25 + 0.11 + 0.03) / 5 = **0.3860**

---

## 3. mean_p vs the same-model window

Baseline = **r396–r414**, the `jev-1.14.0` segment only (r1–r395 ran on `jev-1.13.0` and is a *different distribution* — see §5).

```
r396:0.574 r397:0.534 r398:0.480 r399:0.372 r400:0.558
r401:0.656 r402:0.652 r403:0.292 r404:0.440 r405:0.390
r406:0.294 r407:0.458 r408:0.438 r409:0.368 r410:0.418
r411:0.424 r412:0.552 r413:0.454 r414:0.280 r415:0.386
```

- Same-model window mean (n=20, incl. r415): **0.4510**, range [0.2800, 0.6560]
- r415 mean_p = **0.3860** → dev vs prior-window mean = **−0.0684**
- r415 is the **2nd lowest** of the last 20 rounds (only r414 = 0.280 is lower) — but well inside the observed band.

**mean_p is draw-mix confounded.** A round's mean_p depends on *which* qids get drawn; the cathedral lives in the 0.86–0.89 range while speculative qids sit at 0.03–0.25. r415 drew one bedrock + one review + three sub-0.25 draws. The health signal is the per-qid comparison in §4, not the round mean.

---

## 4. Per-qid drift — same-model baseline (r396–r414)

| qid | kind | p | baseline μ | dev | baseline σ | z | \|dev\|>0.05 |
|---|---|---|---|---|---|---|---|
| q03 | bedrock | 0.86 | 0.8800 | −0.0233 | 0.0151 | −1.54 | no |
| q17 | review | 0.68 | 0.7100 | **−0.0300** | 0.0089 | **−3.37** | no |
| q18 | speculative | 0.25 | 0.2460 | +0.0040 | 0.0102 | +0.39 | no |
| q15 | adversarial | 0.03 | 0.0300 | +0.0000 | 0.0000 | 0.00 | no |
| q09 | speculative | 0.11 | — (n=1 on 1.14.0) | — | — | — | no (see §6) |

**NO qid exceeded |dev| > 0.05. No drift.**

### σ-trap check — done explicitly

Ranked by |z| vs ranked by |dev|:

```
by |z|  : q17(z−3.37, dev−0.030) > q03(z−1.54, dev−0.023) > q18(z+0.39, dev+0.004) > q15(z 0.00, dev+0.000)
by |dev|: q17(z−3.37, dev−0.030) > q03(z−1.54, dev−0.023) > q18(z+0.39, dev+0.004) > q15(z 0.00, dev+0.000)
```

Orderings agree here, but note the trap's shape: **q17's z = −3.37 is the round's only alarming-looking number, yet its movement is 0.030 — below threshold and inside a σ of 0.0089.** q17 is a `review`-tier question whose baseline straddles the gate (draws: 0.71, 0.70, 0.72, 0.70, 0.72, **0.68**). A dip to 0.68 is the first sub-0.70 draw for q17 in the 1.14.0 era, but q17 is **review** kind — it was never a cathedral member, so this is a tier wobble, not a canon break. Flagged, not counted as drift.

---

## 5. Baseline boundary — the model cut, not the schema cut

Per the r414 correction, the baseline is segmented by **oracle model version**, not by file schema:

- `jev-1.13.0`: r1–r395 (399 rounds)
- `jev-1.14.0`: r396–r414 (19 rounds) ← **baseline used**

Cross-model offsets (1.13.0 μ → 1.14.0 μ), computed across all 22 qids:

| qid | 1.13.0 μ | 1.14.0 μ | Δ |
|---|---|---|---|
| **q02** | 0.8251 (n=74) | 0.7400 (n=7) | **−0.0851** |
| **q12** | 0.3678 (n=83) | 0.5140 (n=5) | **+0.1462** |

All other 20 qids move **< 0.05** across the model cut. The two genuine offsets are q02 and q12 — the same two identified in r414. **Pooling across the cut would manufacture false drift on exactly these two**, which is why the segmentation matters.

---

## 6. The script's `drift_events=1` is a PHANTOM (6th consecutive repro)

The probe reported `drift_events=1`. Reproducing the script's own `drift_check()` on the full pooled history:

```
{'qid': 'q12', 'recent_p': 0.56, 'prior_median': 0.5, 'delta': 0.06, 'recent_round': 409}
```

**`q12` was not drawn in r415.** The flagged "recent" sample is from **r409** — six rounds stale. Root cause: `drift_check()` keys off `samples[-1]` *per qid*, so a qid that simply wasn't drawn in the latest round surfaces a historical deviation as if it were current. It also pools across model versions, so q12 — the largest cross-model offset in the set (+0.146) — is doubly exposed.

**Consequence:** `drift_events` in the script's summary is a candidate list, not a verdict. The drift verdict is computed in §4 from the same-model baseline. Applying the script's own `drift_check()` to **only r415's five qids** returns `[]` — zero drift.

Repro count: r411 (q12 not drawn) · r413 (q12 not drawn) · r414 (q02 not drawn) · **r415 (q12 not drawn)** — with r409 the first instance of the q12 flag at r409 origin. The flag has now been phantom in 4 of the last 5 rounds.

---

## 7. Bedrock canon — 7/7 cathedral intact

The cathedral is the **7 `bedrock`-kind questions**, each at p ≥ 0.70 on every same-model draw:

| qid | n | hit rate | min | mean |
|---|---|---|---|---|
| q01 | 5 | 5/5 (100%) | 0.84 | 0.8560 |
| q02 | 7 | 7/7 (100%) | 0.71 | 0.7400 |
| q03 | 7 | 7/7 (100%) | 0.86 | 0.8800 |
| q04 | 5 | 5/5 (100%) | 0.88 | 0.8880 |
| q05 | 5 | 5/5 (100%) | 0.82 | 0.8260 |
| q07 | 5 | 5/5 (100%) | 0.75 | 0.7640 |
| q08 | 3 | 3/3 (100%) | 0.88 | 0.8933 |

**Cathedral: 7/7 at 100%.** r415 drew **q03** (one cathedral member, hit at 0.86) and none of the other six. The cathedral is intact and unchallenged this round.

A **8th** qid, `q17`, has a same-model mean of 0.7050 — it is `review` kind, not bedrock, and it is *not* a cathedral member. Its 0.68 draw in r415 is its first sub-0.70 value in the 1.14.0 era. If `q17` were promoted to bedrock tier, the cathedral would read 6/7 this round. It is not, and was not, counted as such.

---

## 8. q09 — single-draw, cross-model point (not drift)

q09 appears for the first time in the 1.14.0 era (r415, p=0.11). Its 83 prior draws are all `jev-1.13.0` at μ=0.0766, σ=0.0050, max 0.09.

- dev vs the 1.13.0 baseline = **+0.0334** → below the 0.05 threshold
- z vs the 1.13.0 baseline = **+6.71** → alarming, but σ is degenerate (0.005), so z is meaningless here
- n=1 on 1.14.0 → **no same-model baseline can be established yet**

**Verdict: not drift.** It is a single draw with no same-model distribution, and the cross-model delta is within threshold. q09 is simply under-sampled in the current era. It becomes assessable once it accumulates same-model draws.

---

## 9. Method notes

1. **Baseline cut = change in what was measured.** A file-format/schema difference is not a measurement change. The boundary here is the oracle version `jev-1.13.0` → `jev-1.14.0` at r396. Verified by measuring distributions on both sides of the candidate boundary, not by assuming.
2. **σ-trap check, run every round.** Sort drawn qids by |z| and by |dev|; if the orderings disagree, the largest |z| is the smallest real movement. Here they agree, but q17 remains the round's only large-|z| row and its |dev| is below threshold.
3. **Bucket each qid against its OWN baseline.** No global threshold — q17 legitimately straddles 0.70 (review tier) while q03 does not (bedrock tier).
4. **Check |dev| before |z|.** The largest z is often the smallest real movement.
5. **`drift_events` is a candidate list, not a verdict.** Verify the flagged qid was actually drawn in the current round before believing it.
6. **"One round" must be launched with an explicit count.** `python3 jev_continuous_probe.py 1` — the positional `rounds` arg defaults to unbounded; launching without it and killing after the fact races the writer and over-produces (see the r221 overshoot). Here: exactly 1 round file (`continuous_r415.json`), no `r416`, no process left running.
7. **The script's round-file `model` field is the *request* model** (`jev-latest`); the real oracle version lives on each round's `model` field (`jev-1.14.0`). Read the right one when segmenting.
8. **Round-file naming vs `first_round`.** `continuous_r415.json` stores `first_round: 416` (the next counter). Use the round *number* inside `rounds[]`, not the filename's `first_round`.

---

## 10. Environment

- **9th consecutive wipe.** `/workspace/research/` did not exist at session start; NAS `/workspace` at hard quota zero (600 G, 100 % used, 0 avail). The probe script and session history were gone from the NAS.
- **Recovery:** `git clone` of `SuperInstance/jev-quilt` into `/tmp` (30 G overlay, 28 G free) → 222 round files + `history.jsonl` (418 lines, 0 corrupt) recovered intact. `research/jev_sessions/` is a tracked path in the repo, so the working tree *is* the `research/` tree.
- **TLS:** leaf `notAfter Nov 27 2026` — expired-leaf wall **absent**; `api.github.com` returns 200 with default trust store. No bundle rebuild needed this wipe.
- **Round counter:** resolved to 415 from the file set (`files->414 history->414`), not from `len(history)`.
- **Durable copy is git.** The NAS cannot hold the report; `/workspace/research/jev_hourly_report.md` cannot be written from this sandbox. Report committed to the repo.
