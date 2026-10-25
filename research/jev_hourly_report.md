# JEV Continuous Probe — Hourly Report

**Round r443** · 2026-10-25T17:05:20Z · model `jev-1.14.0` · script md5 `3a255fa4642ec4a83173ab04d773d485`
Corpus: `SuperInstance/jev-quilt` @ `5622711` · 28th consecutive wipe (workspace empty on arrival, NAS 100%)

---

## 1. Headline

| Quantity | Value |
|---|---|
| **mean_p** | **0.4500** |
| **Bedrock hits (p >= 0.70)** | **2 / 5** — q08 = 0.88, q04 = 0.86 |
| **Drift > 0.05** | **NONE** (0 of 5 drawn qids, own-model segment) |
| Script's own `drift_events` | 1 — **PHANTOM** (q12, not drawn this round) |

The round was executed with **exactly one** round: `python3 jev_continuous_probe.py 1`
(0.108 s, 5 verdicts, 0 fails). The script's positional `rounds` argument defaults to **200**;
passing `1` explicitly is what keeps "one round" from racing the writer to flush many rounds.

---

## 2. This round's verdicts

| qid | kind | p | bedrock hit (>= 0.70) |
|---|---|---|---|
| **q08** | **bedrock** | **0.88** | **YES** |
| **q04** | **bedrock** | **0.86** | **YES** |
| q11 | speculative | 0.15 | no |
| q14 | adversarial | 0.24 | no |
| q22 | speculative | 0.12 | no |

mean_p = (0.88 + 0.86 + 0.15 + 0.24 + 0.12) / 5 = **0.4500**

Both hits are bedrock-kind qids, and both are **100 %-hit-rate** qids in the current-model segment
(q08 and q04 have never missed the 0.70 gate since the 1.13.0 -> 1.14.0 switch). The three
non-hits are exactly where they belong: two speculative qids and one adversarial qid, all in
their 0.10–0.25 band.

---

## 3. Drift analysis (recomputed — the script's own verdict is not a health signal)

### Method actually used
1. **Corpus assembled from all three locations** — flat `jev_sessions/continuous_r*.json` (208),
   `jev_sessions/r087/` (100), `jev_sessions/rounds/` (3), the `research/jev_sessions/` tree
   (251 flat + 100 r087 + 3 rounds) = **663 round files**, plus `history.jsonl` (447 lines)
   -> **2,226 deduped verdict records**, dedup key `(qid, p, round)`.
   A glob matching only one flat directory would have found 250 of 443 rounds.
2. **Baselines segmented by model.** `history.jsonl` is the only place the *resolved* model lives
   (round files all carry the static request alias `jev-latest`): `jev-1.13.0` = rounds 1-391
   (1,986 obs), `jev-1.14.0` = rounds 396-443 (240 obs). Pooling across the switch fuses a
   model artifact into the signal.
3. **Restricted to qids DRAWN this round** — the script's `drift_check()` compares every qid's
   last value to a 5-sample local median whether or not that qid was drawn, so stale qids re-fire
   old events.
4. **|dev| checked first, sigma second** — a large z on a near-zero sigma is a routine artifact.

### Result — per drawn qid, current-model segment (excluding today's own value)

| qid | today | n_seg | mu_seg | sigma | dev | z | \|dev\|>0.05 |
|---|---|---|---|---|---|---|---|
| q08 | 0.88 | 9 | 0.8900 | 0.0115 | −0.0100 | −0.87 | — clear |
| q04 | 0.86 | 10 | 0.8820 | 0.0098 | −0.0220 | −2.25 | — clear |
| q11 | 0.15 | 10 | 0.1760 | 0.0237 | −0.0260 | −1.09 | — clear |
| q14 | 0.24 | 12 | 0.2275 | 0.0164 | +0.0125 | +0.76 | — clear |
| q22 | 0.12 | 5 | 0.1440 | 0.0080 | −0.0240 | −3.00 | — clear |

**DRIFT: NONE.** 0 of 5 drawn qids exceed |dev| = 0.05.

Note the **σ ≈ 0 trap** firing in the expected way: q22 posts the largest z of the round
(**−3.00**) on a |dev| of only **0.0240** — a 3σ wobble on a 0.0080 sigma, comfortably inside the
noise band. Largest z ≠ largest real movement; **|dev| first** is what makes the verdict.

### The pooled baseline would NOT have manufactured a false flag today (unlike r442)

| qid | POOLED (all models) | SEGMENT (1.14.0) | verdict |
|---|---|---|---|
| q08 | mu 0.8988, dev −0.0188, z −2.01 | mu 0.8900, dev −0.0100, z −0.87 | z-only false alarm |
| q04 | mu 0.8881, dev −0.0281, z −3.07 | mu 0.8820, dev −0.0220, z −2.25 | z-only false alarm |
| q11 | mu 0.1841, dev −0.0341, z −1.89 | mu 0.1760, dev −0.0260, z −1.09 | z-only false alarm |
| q14 | mu 0.1967, dev +0.0433, z +2.56 | mu 0.2275, dev +0.0125, z +0.76 | z-only false alarm |
| q22 | mu 0.1206, dev −0.0006, z −0.07 | mu 0.1440, dev −0.0240, z −3.00 | z-only false alarm |

**No qid crosses |dev| = 0.05 under either baseline** — the pooled check would not have produced
a false drift flag on r443, but it would have produced a z-score false alarm on **4 of 5** drawn
qids. The r442 hazard (pooled dev inflated 5.3× on q02) was not triggered today, yet the
z-only reading would still have been wrong four times out of five.

### Script's own `drift_events = 1` — **PHANTOM (18th repro)**
It fires on **q12**, which was **not drawn** this round. Its last observation is r438 = 0.54
against a 5-sample local median of 0.49 (delta 0.05) — a stale re-fire of an old event, not a
movement in r443. The script's drift list is a *candidate* list over the whole history, never a
health verdict. q12's own current-model series is a flat 0.46–0.56 plateau
(n=13, mu 0.5008) with no movement whatsoever.

---

## 4. Comparison with previous rounds (regenerated from the archives, not remembered)

| round | model | mean_p | hits | bedrock qids |
|---|---|---|---|---|
| 430 | jev-1.14.0 | 0.2840 | 1 | q07 |
| 431 | jev-1.14.0 | 0.4920 | 2 | q08, q01 |
| 432 | jev-1.14.0 | 0.1880 | 0 | — |
| 433 | jev-1.14.0 | 0.5060 | 3 | q07, q03, q17 |
| 434 | jev-1.14.0 | 0.2240 | 0 | — |
| 435 | jev-1.14.0 | 0.3220 | 1 | q04 |
| 436 | jev-1.14.0 | 0.4260 | 2 | q05, q01 |
| 437 | jev-1.14.0 | 0.2200 | 0 | — |
| 438 | jev-1.14.0 | 0.4900 | 2 | q08, q17 |
| 439 | jev-1.14.0 | 0.4020 | 2 | q05, q01 |
| 440 | jev-1.14.0 | 0.4180 | 2 | q03, q01 |
| 441 | jev-1.14.0 | 0.4040 | 2 | q05, q02 |
| 442 | jev-1.14.0 | 0.3520 | 2 | q05, q02 |
| **443** | **jev-1.14.0** | **0.4500** | **2** | **q08, q04** |

Full series (r1–r443): n = 434, mu = 0.3845, median = 0.4020, sd = 0.1414.
**Today z_series = +0.46, rank 310/434 (71.4th percentile)** — upper-mid band, but well inside
one sigma of the series mean.

### Monte-Carlo (200k draws, 5 qids uniform from ALL 22, p sampled from the 1.14.0 segment)
- E[mean_p] = 0.3993
- **P(mean_p <= 0.4500) = 0.6789** — today's value is unremarkable
- P(k bedrock hits): 0 → 9.19 % · 1 → 32.76 % · **2 → 37.65 % (modal)** · 3 → 17.24 % ·
  4 → 2.99 % · 5 → 0.16 %

**Today's 2/5 is the modal outcome.** A round draws 5 qids at random from 22, so `mean_p` and the
bedrock count are properties of the *draw*, not of the canon — 0/5 and 2/5 are both ordinary.

---

## 5. Cathedral health (per-qid, current-model segment)

**Bedrock — 6 of 7 at 100 %:**

| qid | n_seg | mean_p | hit rate | ever >= 0.70 (all rounds) |
|---|---|---|---|---|
| q08 | 10 | 0.8890 | 100.0 % | 90 |
| q03 | 10 | 0.8820 | 100.0 % | 101 |
| q04 | 11 | 0.8800 | 100.0 % | 103 |
| q01 | 13 | 0.8562 | 100.0 % | 109 |
| q05 | 12 | 0.8167 | 100.0 % | 100 |
| q07 | 11 | 0.7700 | 100.0 % | 91 |
| **q02** | 15 | 0.7273 | **80.0 %** | 89 |

q02 remains the sole imperfect bedrock qid — hair-under-gate misses, never a collapse. Both of
today's bedrock hits came from the 100 % cohort, so q02's imperfection did not even enter the
picture today.

**Review:** q17 (n=10, mean 0.7130, 80 % >= 0.70) is the only non-bedrock qid that ever crosses
0.70 — a 0.66–0.75 plateau, judged against its own baseline. q16 (n=9, mean 0.1933) never does.

**Speculative + adversarial: 0 crossings at >= 0.70 across the entire corpus — 0 / 1,348.**
(Excludes review qids, as required; q17 contributes all of the review-side crossings.)

---

## 6. Verdict

**No drift. No canon regression. r443 is an ordinary draw — a slightly bright one.**

- mean_p 0.4500 sits at the **71.4th percentile** of the 434-round series, z = +0.46.
- 2/5 bedrock hits is the **modal** outcome of the draw distribution (37.65 %).
- Both bedrock hits (q08 0.88, q04 0.86) are within one segment sigma of their own baselines.
- Zero drawn qids exceed |dev| = 0.05; the only flag the script emitted is a **stale phantom on
  an undrawn qid** (q12, 18th repro).
- Cathedral intact: 6 of 7 bedrock at 100 %, q02 at 80.0 %, and **zero** speculative/adversarial
  qids have ever crossed 0.70 in 1,348 observations.

---

## 7. Environment (28th wipe, durable)

- `/workspace` **EMPTY** on arrival (28th consecutive) -> bootstrapped `SuperInstance/jev-quilt`
  into `/tmp/c_jev-quilt` via `git clone --depth 1` + `git fetch --unshallow` (347 commits).
  **The short form fatals** — the full `https://github.com/owner/repo.git` URL is required.
- The probe script is **not** in `superinstance-advisor`; it lives in **`SuperInstance/jev-quilt`**
  (found by cloning the candidate `jev-*` repos and grepping for `jev_sessions/`).
- NAS at **100 % (0 avail)** -> `rm -rf /workspace/research` **first**, then
  `ln -s /tmp/c_jev-quilt/research /workspace/research`. The deliverable path resolves and the
  bytes live on the /tmp overlay. (Symlinking *into* an existing directory creates a nested link —
  the `rm -rf` is mandatory.)
- **TLS leaf VALID** (CN=typesafe.ai, Let's Encrypt YE2, notAfter 2026-12-21) -> no CA rebuild.
- The script **already reads `TYPESAFE_AI_TOKEN` natively** (lines 43-45 accept
  `TYPESAFEAI_KEY | TYPESAFE_AI_TOKEN | TYPESAFE_API_KEY`); only `TYPESAFE_AI_TOKEN` is set in
  this sandbox. No key mapping needed.
- `SESSION_DIR` is resolved **relative to the script's own location** (`<script_dir>/research/jev_sessions`),
  so the script must sit at the **repo root**. To make the documented command
  (`cd /workspace/research && python3 jev_continuous_probe.py 1`) work verbatim, a **launcher**
  was added at `research/jev_continuous_probe.py` that `runpy`-execs the root script with argv
  forwarded unchanged. Copying the real script into `research/` instead nests the session dir
  one level deeper (`research/research/jev_sessions`) and would silently start a fresh corpus.
- Script md5 `3a255fa4` — **unchanged** from r442, so mean_p is directly comparable and the qid
  map is stable.
- Round counter: files -> 442, history -> 442, start = **443** (persistent, aborts on shadowing).
- Corpus layout: 663 round files across 4 directories; `history.jsonl` 447 lines.
- **Round-arg trap (recurrence):** the positional `rounds` arg defaults to **200**. A "run one
  round" ask that launches the script bare and then kills it races the writer and flushes
  dozens of rounds. Always pass an explicit small count (`... 1`).
