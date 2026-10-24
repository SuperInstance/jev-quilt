# JEV Continuous Probe — r409 (2026-10-24T0101Z)

**Run:** 1 round (explicit positional `1`), 0 fails, 5 verdicts. `mean_p = 0.3680`.  
**Script md5:** `3a255fa4642ec4a83173ab04d773d485` (unchanged, 10th wipe)  
**Model:** `jev-1.14.0` / `jev-latest`  
**Corpus (modern schema):** 388 rounds r1..r409, 1,940 verdicts, 22 qids, grand mean_p 0.3836

---

## Headline

| metric | value |
|---|---|
| mean_p (r409) | **0.3680** |
| bedrock hits p>=0.70 | **1/5 (20.0%)** — `q17` only |
| cathedral (kind=bedrock, p>=0.70) | **597/597 = 100.00%** |
| last-20-rounds cathedral | **39/39 = 100.00%** |
| spec/adversarial leaks (p>=0.70) | **0** |
| script-reported drift_events | 3 (2 stale/boundary, **1 real**) |
| real drift > 0.05 | **1 — `q12` +0.0600** |
| q02 canon-erosion watch | **NOT EXERCISED** (q02 not drawn) |

## r409 verdicts

| qid | kind | p | p>=0.70 |
|---|---|---|---|
| q06 | speculative | 0.14 | no |
| q17 | review | 0.72 | YES |
| q14 | adversarial | 0.23 | no |
| q12 | speculative | 0.56 | no |
| q11 | speculative | 0.19 | no |

Drawn: q06, q17, q14, q12, q11. **The only qid at p>=0.70 is `q17`** (review tier, 0.72) — review is deliberately *not* part of the cathedral, so r409 contains **zero bedrock canon hits**. That is a draw-mix artefact, not a failure: only q17's kind permits a high score.

---

## Drift — the script says 3, only 1 is real

Script output:

```
drift = [{"qid":"q02","recent_p":0.71,"prior_median":0.77,"delta":-0.06},
          {"qid":"q12","recent_p":0.56,"prior_median":0.50,"delta":0.06},
          {"qid":"q14","recent_p":0.23,"prior_median":0.18,"delta":0.05}]
```

| event | drawn in r409? | verdict |
|---|---|---|
| q02 −0.0600 | **NO** | **stale echo** — q02 was last drawn in r407 (0.71). `drift_check()` compares every qid's last value to a 5-sample median *whether or not that qid was drawn*, so r407's event re-fires. |
| q12 +0.0600 | yes | **REAL** — q12 = 0.56, a new all-time high, and a range extreme. |
| q14 +0.0500 | yes | **boundary artifact** — see below. |

### q14: the +0.05 that the corrupted history manufactured

The script reported `q14: recent 0.23, prior_median 0.18, delta +0.05`, and the rule is `abs(delta) > 0.05` — so it passed **on the boundary**.

Recomputing from the **round files** (the canonical source):

- q14 prior-5 draws (round files): `[0.17, 0.20, 0.19, 0.20, 0.22]` -> median **0.20**
- delta = 0.23 − 0.20 = **+0.0300** -> does **not** clear 0.05. **No drift.**

The script's `prior_median` of 0.18 comes from `history.jsonl`, which contains a **different** set of prior q14 draws. That file is corrupted (see below), and `drift_check()` / `per_question_stats()` both read from it rather than the round files.

**So the real drift count for r409 is 1, not 3.** Two of the three are artifacts. This is the 5th consecutive round the script's drift count over-reports (r405 1 stale; r406 1 real + 1 stale; r407 2 real; r408 2 stale, 0 real; r409 2 artifact, 1 real).

---

## THE FINDING — `history.jsonl` is a corrupted append-only log

`history.jsonl` has **413 records but only 400 distinct rounds**, and it is **not monotonic**:

```
line 385  round=395  ts=2026-10-21T01:05:04
line 386  round=384  ts=2026-10-21T11:05:12   <-- counter RESTARTED
line 387  round=385  ts=2026-10-21T11:05:28
...       (385-391 replayed a second time)
line 392  round=384  ts=2026-10-21T12:03:14   <-- counter RESTARTED AGAIN
...       (384-391 replayed a third time)
line 400  round=396  ts=2026-10-23T12:04:36
```

**Rounds 384–391 were replayed three times** on 2026-10-21 (01:04, 11:05, 12:03 UTC) with **different payloads each time** — e.g. round 384 appears as `[q20 .11, q21 .09, q07 .77, q15 .02, q14 .18]` and separately as `[q05 .85, q12 .34, q21 .09, q15 .02, q11 .18]`. Duplicate counts: 385/386/387/388/389 appear 3× each; 384/390/391 appear 2× each.

**Root cause:** the round counter is derived from the highest existing round *file*, and the round files for 384–391 do not exist (the batch file is `continuous_r383.json`, holding 177 rounds, then `continuous_r396.json`). Each of the three sessions therefore restarted its counter at 384 and re-appended. The round files are batched — `continuous_r193.json` holds 193 rounds, `continuous_r383.json` holds 177 — so a session can write a batch file whose top round is *below* the rounds it already logged.

**Impact:**

1. `drift_check()` and `per_question_stats()` read `history.jsonl` (via `load_history()`), **not** the round files. Every prior-5 median it computes is drawn from a corpus with duplicated rounds. This is what produced the phantom q14 event.
2. `history.jsonl` also has a **9-round gap at r194–r202** — present in the round files, absent from the log.
3. **The round files are clean and canonical** — 388 modern rounds, no duplicates, monotonic. All statistics in this report are computed from them, with the qid-prefix normalisation that the two-schema corpus requires.

**Recommended fix (not applied — reporting only):** make `drift_check()` and `per_question_stats()` read the round files, or de-duplicate `history.jsonl` by round number before use, and make the round counter account for batched files rather than the single highest file name.

---

## The one real drift: q12 at a new all-time high

- q12 = **0.56** — new all-time high (prior max 0.51, prior min 0.30)
- full-history mean 0.3761, sd 0.0457, n=88
- dev vs mean **+0.1839** (z +4.02); dev vs prior-5 median (0.50) **+0.0600**
- **clears the 0.05 bar on both measures** — real drift, and a range extreme (0.56 > max 0.51)

Trajectory:

```
  r349  0.41
  r350  0.42
  r353  0.37
  r356  0.36
  r370  0.40
  r375  0.38
  r377  0.37
  r398  0.50
  r401  0.51
  r403  0.46
  r407  0.54
  r409  0.56
```

**Interpretation — promotion-candidate signal, not a leak.** q12 is `kind=speculative` and has **0 hits in 88 draws all-time**. It is *not* in the canon gate, so a high p is not a canon breach. It is however climbing steadily: a 0.36–0.42 plateau through r377, then 0.50 (r398), 0.51 (r401), 0.46 (r403), 0.54 (r407), **0.56 (r409)**.

q12's baseline is ~2× the next spec qid (q11 0.1852) and it has by far the widest σ (0.0457 vs 0.005–0.017 for every other spec qid) — it is the one framing the oracle finds genuinely interesting rather than clearly false. The `spec_notebook` guard (q10–q13 must not be promoted) still holds: q12 has never crossed 0.70. **Keep the guard; watch whether the plateau keeps climbing.**

---

## q02 canon-erosion watch — NOT EXERCISED

q02 was **not drawn** in r409, so the watch from r406/r407 stands unchanged. The r409 q02 drift event is a **stale echo** of r407's 0.71 and must not be read as a new draw.

Last 10 q02 draws:

```
  r335:0.81  r338:0.82  r361:0.84  r379:0.81  r381:0.81  r383:0.81  r399:0.75  r401:0.77  r406:0.73  r407:0.71
```

- n=78, mean 0.8208, sd 0.0240, min 0.71, max 0.86
- era means (20-blocks): 0.8300, 0.8230, 0.8270, 0.8011
- last-5 0.7540 vs prev-5 0.8180 = **-0.0640**
- drawn in only 20.1% of rounds — thin, but the era shift is in the aggregate, not one point

**NEXT q02 DRAW DECIDES:**

- `< 0.70` => **canon breach** — report immediately
- `0.70–0.74` => 3rd consecutive sub-0.75 — treat the shift as structural
- `>= 0.80` => the tail was noise — close the watch

**Canon NOT breached:** q02 is 78/78 bedrock hits, 0 draws below 0.70, cathedral 597/597.

---

## Cathedral (modern schema only — 597/597 = 100.00%)

| qid | n | hits | rate | mean | sd | min | max |
|---|---|---|---|---|---|---|---|
| q01 | 98 | 98 | 100.00% | 0.8748 | 0.0093 | 0.84 | 0.90 |
| q02 | 78 | 78 | 100.00% | 0.8208 | 0.0240 | 0.71 | 0.86 |
| q03 | 92 | 92 | 100.00% | 0.8861 | 0.0092 | 0.86 | 0.91 |
| q04 | 93 | 93 | 100.00% | 0.8886 | 0.0087 | 0.88 | 0.91 |
| q05 | 83 | 83 | 100.00% | 0.8505 | 0.0109 | 0.82 | 0.87 |
| q07 | 79 | 79 | 100.00% | 0.7548 | 0.0164 | 0.71 | 0.79 |
| q08 | 74 | 74 | 100.00% | 0.8995 | 0.0087 | 0.87 | 0.91 |

`bedrock_hit` vs `p>=0.70` agreement across all 1,940 modern verdicts: **0 disagreements** — no inference needed in the modern era.

q17 (review tier, deliberately excluded from the cathedral): 59/79 = 74.7%, mean 0.7032.

---

## Environment (125th wipe)

- **24th consecutive ephemeral-path wipe** — `/workspace/research/` and `/tmp/jev_probe/` both absent; rebuilt from `SuperInstance/jev-quilt` into `/tmp` (overlay 28G free).
- **NAS 100% (27th recurrence)** — 600G/600G, 0 bytes. The whole `/workspace` mount IS the quota'd NAS; `/root` and `/tmp` are the overlay and ARE writable.
- **TLS clean first try** — live leaf `typesafe.ai` (CN) valid to **2026-12-25** (+62.4 d); stock Python context verified; 10th clean wipe, no cert-anchor wall, no 289-cert rebuild.
- **Positional `1` ran exactly one round**, no R-221 overshoot. The task's literal command (no arg) defaults to **200 rounds** — always pass the explicit count.
- Round counter verified two ways: files→408, history→408, start=409. No clobber, no duplicate round number produced.
- **Method gotcha — a corpus loader must handle two schemas.** The corpus holds 200 legacy files (`verdicts` = dict of `{qid_slug: p}`, no `kind`/`bedrock_hit`, and a *different question bank*) and 18 modern files (`verdicts` = list of `{qid, kind, p, bedrock_hit}`). Mixing them fabricates a cathedral regression — a naive count gave 592/602 = 98.34% and 6 qids "below 100%" when the true modern-era rate is 597/597 = 100%. **Assert the schema before reporting any rate.**
- **Method gotcha — a script bug surfaces as a plausible-looking number.** `sum(xs)` on tuples and `stdev()` on tuples both threw on the first two analysis passes. Shape-census first: print `type()` of every field before computing on it.

---

## Bottom line

1. **mean_p 0.3680**, 1/5 at p>=0.70 (`q17` only). Zero bedrock canon hits this round, purely a draw-mix artefact — no bedrock qid was drawn.
2. **Cathedral 597/597 = 100.00%**, last-20-rounds 39/39 = 100%, zero spec/adversarial leaks.
3. **One real drift: q12 = 0.56**, a new all-time high. Promotion-candidate signal, not a leak — 0/88 hits all-time, `spec_notebook` guard still holding below 0.70.
4. **The script's other 2 drift events are artifacts**: q02 is a stale echo (not drawn), q14 is a boundary case manufactured by a corrupted history file.
5. **New defect: `history.jsonl` is a corrupted append-only log** — rounds 384–391 replayed 3× with different payloads, counter restarted twice, 9-round gap at r194–r202. The round files are clean; the script's stats read the corrupt file. This is the root cause of the phantom q14 event.
6. **q02 canon-erosion watch not exercised** — stands unchanged, next q02 draw decides.
