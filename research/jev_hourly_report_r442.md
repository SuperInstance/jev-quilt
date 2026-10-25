# JEV Continuous Probe — Hourly Report

**Round r442** · 2026-10-25T16:05:07Z · model `jev-1.14.0` · script md5 `3a255fa4642ec4a83173ab04d773d485`
Corpus: `SuperInstance/jev-quilt` @ `512877f` · 27th consecutive wipe (workspace empty on arrival, NAS 100%)

---

## 1. Headline

| Quantity | Value |
|---|---|
| **mean_p** | **0.3520** |
| **Bedrock hits (p >= 0.70)** | **2 / 5** — q05 = 0.80, q02 = 0.71 |
| **Drift > 0.05** | **NONE** (0 of 5 drawn qids, own-model segment) |
| Script's own `drift_events` | 1 — **PHANTOM** (q12, not drawn this round) |

The round was executed with **exactly one** round: `python3 jev_continuous_probe.py 1`
(0.16 s, 5 verdicts, 0 fails). The script's positional `rounds` argument defaults to **200**;
passing `1` explicitly is what keeps "one round" from racing the writer to flush many rounds.

---

## 2. This round's verdicts

| qid | kind | p | bedrock hit (>= 0.70) |
|---|---|---|---|
| q10 | speculative | 0.05 | no |
| **q02** | **bedrock** | **0.71** | **YES** |
| q13 | speculative | 0.17 | no |
| **q05** | **bedrock** | **0.80** | **YES** |
| q15 | adversarial | 0.03 | no |

mean_p = (0.05 + 0.71 + 0.17 + 0.80 + 0.03) / 5 = **0.3520**

---

## 3. Drift analysis (recomputed — the script's own verdict is not a health signal)

### Method actually used
1. **Corpus assembled from all three locations** — flat `jev_sessions/continuous_r*.json` (250),
   `jev_sessions/r087/` (100), `jev_sessions/rounds/` (2) = **352 round files**, plus
   `history.jsonl` (445 lines) → **2,221 deduped verdict records**, dedup key `(qid, p, round)`.
   A glob matching only the flat directory would have found 250 of 442 rounds.
2. **Baselines segmented by model.** `history.jsonl` is the only place the *resolved* model lives
   (round files all carry the static request alias `jev-latest`): `jev-1.13.0` = rounds 1–395
   (1,986 obs), `jev-1.14.0` = rounds 396–442 (235 obs). Pooling across the switch fuses a
   model artifact into the signal.
3. **Restricted to qids DRAWN this round** — the script's `drift_check()` compares every qid's
   last value to a 5-sample local median whether or not that qid was drawn, so stale qids re-fire
   old events.
4. **|dev| checked first, sigma second** — a large z on a near-zero sigma is a routine artifact.

### Result — per drawn qid, current-model segment (excluding today's own value)

| qid | today | n_seg | mu_seg | sigma | dev | z | \|dev\|>0.05 |
|---|---|---|---|---|---|---|---|
| q02 | 0.71 | 14 | 0.7286 | 0.0282 | −0.0186 | −0.66 | — clear |
| q05 | 0.80 | 11 | 0.8182 | 0.0175 | −0.0182 | −1.04 | — clear |
| q10 | 0.05 | 13 | 0.0515 | 0.0036 | −0.0015 | −0.43 | — clear |
| q13 | 0.17 | 10 | 0.1600 | 0.0045 | +0.0100 | +2.24 | — clear |
| q15 | 0.03 | 7 | 0.0300 | 0.0000 | 0.0000 | n/a (σ=0) | — clear |

**DRIFT: NONE.** 0 of 5 drawn qids exceed |dev| = 0.05.

Note the **σ ≈ 0 trap** firing in the expected way: q13 posts the largest z of the round
(**+2.24**) on a |dev| of only **0.0100** — a 2σ wobble on a 0.0045 sigma, comfortably inside
the noise band. Largest z ≠ largest real movement; **|dev| first** is what makes the verdict.

### 🔴 The pooled baseline would have manufactured a false flag (r428 hazard, 2nd q02 victim)

| qid | POOLED (all models) | SEGMENT (1.14.0) | verdict |
|---|---|---|---|
| **q02** | mu 0.8088, dev **−0.0988**, z **−2.47** | mu 0.7286, dev **−0.0186**, z −0.66 | **POOLED FALSE FLAG** |
| q05 | mu 0.8472, dev −0.0472, z −2.95 | mu 0.8182, dev −0.0182, z −1.04 | z-only false alarm |
| q10 | mu 0.0652, dev −0.0152, z −2.22 | mu 0.0515, dev −0.0015, z −0.43 | z-only false alarm |
| q13 | mu 0.1360, dev +0.0340, z +3.24 | mu 0.1600, dev +0.0100, z +2.24 | z-only false alarm |
| q15 | mu 0.0253, dev +0.0047, z +0.94 | mu 0.0300, dev 0.0000, z n/a | clear |

q02's 1.13.0→1.14.0 switch moved it by ≈ −0.08; the pooled baseline keeps that artifact fused in
and inflates the deviation by **5.3×**, turning a dead-on-baseline 0.71 into a textbook drift flag.
Four of five drawn qids also show a **|dev| below 0.05 while the z-score looks alarming** — a
threshold-only check on the pooled value would have reported four false positives today.

### Script's own `drift_events = 1` — **PHANTOM (17th repro)**
It fires on **q12**, which was **not drawn** this round. The script's drift list is a *candidate*
list over the whole history, never a health verdict.

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
| **442** | **jev-1.14.0** | **0.3520** | **2** | **q05, q02** |

Full series (r1–r441): n = 432, mu = 0.3845, median = 0.4020, sd = 0.1416.
**Today z_series = −0.23, rank 176/433 (40.5th percentile)** — squarely mid-band.

### Monte-Carlo (200k draws, 5 qids uniform from ALL 22, p sampled from the 1.14.0 segment)
- E[mean_p] = 0.3999, sd = 0.1333
- **P(mean_p <= 0.3520) = 0.3535** — today's value is unremarkable
- P(k bedrock hits): 0 → 9.27 % · 1 → 32.86 % · **2 → 37.53 % (modal)** · 3 → 17.13 % ·
  4 → 3.04 % · 5 → 0.17 %

**Today's 2/5 is the modal outcome.** A round draws 5 qids at random from 22, so `mean_p` and the
bedrock count are properties of the *draw*, not of the canon — 0/5 and 2/5 are both ordinary.

---

## 5. Cathedral health (per-qid, current-model segment)

**Bedrock — 6 of 7 at 100 %:**

| qid | n_seg | mean_p | hit rate | ever >= 0.70 (all rounds) |
|---|---|---|---|---|
| q08 | 9 | 0.8900 | 100.0 % | 89 |
| q03 | 10 | 0.8820 | 100.0 % | 101 |
| q04 | 10 | 0.8820 | 100.0 % | 102 |
| q01 | 13 | 0.8562 | 100.0 % | 109 |
| q05 | 11 | 0.8182 | 100.0 % | 100 |
| q07 | 11 | 0.7700 | 100.0 % | 91 |
| **q02** | 14 | 0.7286 | **78.6 %** | 89 |

q02 remains the sole imperfect bedrock qid — hair-under-gate misses, never a collapse. Its 0.71
today is 3 observations above its segment floor (0.68) and well inside its 0.68–0.75 band.

**Review:** q17 (n=10, mean 0.7130, 80 % >= 0.70) is the only non-bedrock qid that ever crosses
0.70 — a 0.66–0.75 plateau, judged against its own baseline. q16 (n=9, mean 0.1933) never does.

**Speculative + adversarial: 0 crossings at >= 0.70 across the entire corpus — 0 / 1,345.**
(Excludes review qids, as required; q17 contributes all of the review-side crossings.)

---

## 6. Verdict

**No drift. No canon regression. r442 is an ordinary draw.**

- mean_p 0.3520 sits at the **40.5th percentile** of the 433-round series, z = −0.23.
- 2/5 bedrock hits is the **modal** outcome of the draw distribution.
- Both bedrock hits (q05 0.80, q02 0.71) are within one segment sigma of their own baselines.
- Zero drawn qids exceed |dev| = 0.05; the only flag the script emitted is a **stale phantom on
  an undrawn qid**.
- Cathedral intact: 6 of 7 bedrock at 100 %, q02 at 78.6 %, and **zero** speculative/adversarial
  qids have ever crossed 0.70.

---

## 7. Environment (27th wipe, durable)

- `/workspace` **EMPTY** on arrival (27th consecutive) → bootstrapped `SuperInstance/jev-quilt` into
  `/tmp/jev/jev-quilt` via `git clone --depth 50` (full `https://github.com/owner/repo.git` URL —
  the short form fatals).
- NAS at **100 % (0 avail)** → `rm -rf /workspace/research` **first**, then
  `ln -s /tmp/jev/jev-quilt/research /workspace/research`. The deliverable path resolves and the
  bytes live on the /tmp overlay. (Symlinking *into* an existing directory creates a nested link —
  the `rm -rf` is mandatory.)
- **TLS leaf VALID** (CN=typesafe.ai, Let's Encrypt YE2, notAfter 2026-12-21) → no CA rebuild.
- The script **already reads `TYPESAFE_AI_TOKEN` natively** (lines 43–45 accept
  `TYPESAFEAI_KEY | TYPESAFE_AI_TOKEN | TYPESAFE_API_KEY`) → the `JEV_API_KEY` mapping used in
  earlier rounds is **no longer needed**. Check the source before adding it.
- **Variant A confirmed** (md5 `3a255fa4`, positional `sys.argv[1]` defaulting to 200) →
  `python3 jev_continuous_probe.py 1`; exactly 1 round in 0.16 s.
- Round counter: files → 441, history → 441, start = **442** (persistent, aborts on shadowing).
- Corpus layout: flat `jev_sessions/continuous_r*.json` (250) + `jev_sessions/r087/` (100) +
  `jev_sessions/rounds/` (2) = 352 round files; `history.jsonl` 445 lines.
