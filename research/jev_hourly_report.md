# JEV Continuous Probe — Hourly Report

**Round r441** · 2026-10-25T15:0xZ · model `jev-1.14.0` · script md5 `3a255fa4642ec4a83173ab04d773d485`
Corpus: `SuperInstance/jev-quilt` @ `512877f` · 26th consecutive wipe (workspace empty on arrival, NAS 100%)

---

## 1. Headline

| Quantity | Value |
|---|---|
| **mean_p** | **0.4040** |
| **Bedrock hits (p >= 0.70)** | **2 / 5** — q05 = 0.85, q02 = 0.74 |
| **Drift > 0.05** | **NONE** (0 of 5 drawn qids, own-model segment) |
| Script's own `drift_events` | 1 — **PHANTOM** (q12, not drawn this round) |

The round was executed with **exactly one** round: `python3 jev_continuous_probe.py 1`
(0.3 s, 5 verdicts, 0 fails). The script's positional `rounds` argument defaults to **200**;
passing `1` explicitly is what keeps "one round" from racing the writer to flush many rounds.

---

## 2. This round's verdicts

| qid | kind | p | bedrock hit (>= 0.70) |
|---|---|---|---|
| q20 | speculative | 0.09 | no |
| q14 | adversarial | 0.23 | no |
| **q05** | **bedrock** | **0.85** | **YES** |
| **q02** | **bedrock** | **0.74** | **YES** |
| q19 | adversarial | 0.11 | no |

mean_p = (0.09 + 0.23 + 0.85 + 0.74 + 0.11) / 5 = **0.4040**

---

## 3. Drift analysis (recomputed — the script's own verdict is not a health signal)

### Method actually used
1. **Corpus assembled from all three locations** — flat `jev_sessions/continuous_r*.json` (249),
   `jev_sessions/r087/` (100), `jev_sessions/rounds/` (1) = **351 round files**, **2,100 deduped
   verdict records**, dedup key `(qid, p, round)`. A glob matching only the flat directory would
   have found 249 of 350 rounds and silently under-counted the baseline.
2. **Baselines segmented by model.** `history.jsonl` is the only place the *resolved* model lives
   (round files all carry the static request alias `jev-latest`): `jev-1.13.0` = rounds 1–395,
   `jev-1.14.0` = rounds 396–440+. **A pooled baseline fuses the 1.13.0 -> 1.14.0 model-switch
   artifact into the current signal and manufactures false drift.**
3. **Restricted to qids DRAWN this round.**
4. **|dev| FIRST, z second** — a near-degenerate sigma inflates z on a trivial movement.

### Per-qid deviation vs its OWN 1.14.0 baseline

| qid | today | n | mu | sd | dev | z | verdict |
|---|---|---|---|---|---|---|---|
| q14 | 0.23 | 12 | 0.2275 | 0.0164 | +0.0025 | +0.15 | clear |
| q19 | 0.11 | 12 | 0.1042 | 0.0076 | +0.0058 | +0.77 | clear |
| q05 | 0.85 | 11 | 0.8182 | 0.0175 | +0.0318 | +1.82 | clear |
| q02 | 0.74 | 14 | 0.7286 | 0.0282 | +0.0114 | +0.40 | clear |
| q20 | 0.09 | 12 | 0.0867 | 0.0062 | +0.0033 | +0.53 | clear |

**Maximum aggregate |dev| = 0.0318 (q05). Zero qids beyond 0.05. Drift: NONE.**

### The pooled-baseline trap fired again — and was rejected
Scoring the same round against the **pooled** (all-model) baseline:

| qid | today | pooled mu | pooled dev | z | pooled verdict | own-model verdict |
|---|---|---|---|---|---|---|
| q02 | 0.74 | 0.8098 (n=88) | **-0.0698** | -1.77 | **FLAG** | **clear (+0.0114)** |
| q14 | 0.23 | 0.1973 (n=88) | +0.0327 | +1.93 | clear | clear |
| q20 | 0.09 | 0.1029 (n=90) | -0.0129 | -1.14 | clear | clear |
| q05 | 0.85 | 0.8474 (n=91) | +0.0026 | +0.17 | clear | clear |
| q19 | 0.11 | 0.1050 (n=88) | +0.0050 | +0.80 | clear | clear |

q02's **pooled** dev is **-0.0698 (a textbook drift flag)**. Against its own 1.14.0 segment
(n=14, mu=0.7286) today's 0.74 is **+0.0114 — dead on baseline**. The pooled baseline inflates
the deviation by ~6x purely from the model switch. **This is a false flag, rejected.** It is the
same false-flag shape seen on q02 (r428), q12 (r435, r438, r439) and q06 (r436).

### The script's own `drift_events=1` is stale — rejected
`{'qid': 'q12', 'recent_p': 0.54, 'prior_median': 0.49, 'delta': 0.05}`
**q12 was NOT drawn this round.** The script's `drift_check()` compares every qid's last value
to a 5-sample local median whether or not that qid was drawn, so stale qids re-fire old events.
**16th reproduction of this phantom. Never quote it as a health verdict.**

---

## 4. Comparison to previous rounds (table computed from the archives, not from memory)

| round | model | mean_p | bedrock | hits |
|---|---|---|---|---|
| 430 | 1.14.0 | 0.2840 | 1/5 | q07=0.78 |
| 431 | 1.14.0 | 0.4920 | 2/5 | q08=0.89, q01=0.84 |
| 432 | 1.14.0 | 0.1880 | 0/5 | — |
| 433 | 1.14.0 | 0.5060 | 3/5 | q07=0.79, q03=0.89, q17=0.73 |
| 434 | 1.14.0 | 0.2240 | 0/5 | — |
| 435 | 1.14.0 | 0.3220 | 1/5 | q04=0.88 |
| 436 | 1.14.0 | 0.4260 | 2/5 | q05=0.82, q01=0.86 |
| 437 | 1.14.0 | 0.2200 | 0/5 | — |
| 438 | 1.14.0 | 0.4900 | 2/5 | q08=0.89, q17=0.73 |
| 439 | 1.14.0 | 0.4020 | 2/5 | q05=0.81, q01=0.86 |
| 440 | 1.14.0 | 0.4180 | 2/5 | q03=0.89, q01=0.87 |
| **441** | **1.14.0** | **0.4040** | **2/5** | **q05=0.85, q02=0.74** |

**Full series (420 rounds):** mean 0.3845 · median 0.4020 · min 0.0840 · max 0.8480 · sd 0.1420

- Today (0.4040) sits at **z = +0.14** vs the series mean — **rank 204 of 420 (48.6th percentile)**.
  Dead centre. No movement.
- Bedrock hits across the whole series: **2 hits x153, 1 hit x134, 3 hits x74, 0 hits x48, 4+ x11.**
  **2-of-5 is the modal outcome (36.5% of all rounds).** Today's 2/5 is the most ordinary result possible.
- The last 20 mean_p values: 0.5060 0.5260 0.3760 0.3560 0.4040 0.4200 0.3760 0.5400 0.2840 0.4920
  0.1880 0.5060 0.2240 0.3220 0.4260 0.2200 0.4900 0.4020 0.4180 **0.4040** — no trend, no decay.

### Monte-Carlo check (draw 5 qids uniformly from ALL 22, 200k trials)
- E[mean_p] = **0.3995**, sd 0.1332
- **P(mean_p <= 0.4040) = 0.5185** — today's value is the *median* of the distribution
- P(0 bedrock) 9.27% · **P(1) 32.84% · P(2) 37.56% (modal)** · P(3) 17.13% · P(4) 3.04% · P(5) 0.15%

Today's 2/5 and mean_p 0.4040 are **exactly what an ordinary draw looks like**. No signal.

---

## 5. Cathedral health (bedrock canon, current-model segment)

| qid | n | mu | sd | min | max | >= 0.70 rate |
|---|---|---|---|---|---|---|
| q01 | 14 | 0.8557 | 0.0090 | 0.84 | 0.87 | **100.0%** |
| q03 | 10 | 0.8820 | 0.0133 | 0.86 | 0.90 | **100.0%** |
| q04 | 11 | 0.8818 | 0.0094 | 0.87 | 0.90 | **100.0%** |
| q05 | 11 | 0.8182 | 0.0175 | 0.78 | 0.85 | **100.0%** |
| q07 | 11 | 0.7700 | 0.0148 | 0.75 | 0.79 | **100.0%** |
| q08 | 9 | 0.8900 | 0.0115 | 0.88 | 0.91 | **100.0%** |
| **q02** | **14** | **0.7286** | **0.0282** | **0.68** | **0.77** | **78.6%** |

**6 of 7 bedrock qids at 100%.** q02 remains the sole imperfect one — hair-under-gate misses
against a 0.70 threshold, never a collapse. Its current-model history is
`0.68 0.69 0.69 0.71 0.71 0.72 0.73 0.74 0.74 0.75 0.75 0.75 0.77 0.77`, and **today's 0.74 is a
REPEAT of an existing observed value** (twice in the segment) — archive-judgeable, so no
re-measurement round is required (the r427 rule applies only to a NEW extreme).

### Speculative / adversarial / review qids
- **No speculative or adversarial qid has EVER reached 0.70.** q06, q09, q10, q11, q12, q13, q14,
  q15, q18, q19, q20, q21, q22 — all 0 crossings.
- **q17 (review) is the only non-bedrock qid above 0.70** — a 0.71–0.75 plateau, 8 of 10 current-model
  observations >= 0.70, judged against its own baseline. **Any "speculative ever >= 0.70" claim must
  EXCLUDE review qids** — q17 contributes all of those crossings.

---

## 6. Verdict

**HEALTHY. No drift.**
- mean_p 0.4040, bedrock 2/5, both modal outcomes.
- Max |dev| across the 5 drawn qids = **0.0318**; **0 qids beyond the 0.05 threshold**.
- The one apparent flag (q02, pooled dev -0.0698) is the **model-switch artifact** and is rejected
  against the own-model segment (+0.0114).
- The script's own `drift_events=1` is on **q12, not drawn** — stale, 16th reproduction.
- Cathedral intact: 6/7 bedrock qids at 100%, q02's 0.74 a repeat of an existing value.

---

## 7. Environment receipts

| Item | State |
|---|---|
| Wipe | 26th consecutive — `/workspace` empty on arrival, rebuilt from git |
| Clone | `SuperInstance/jev-quilt` @ `512877f` -> `/tmp/jev/jev-quilt` (`/tmp` = 28 G overlay, not NAS) |
| NAS | **100% used, 0 bytes avail** — symlink used, not a file write |
| Deliverable path | `/workspace/research` -> `/tmp/jev/jev-quilt/research` (symlink; `rm -rf` first, then `ln -s`) |
| Script variant | **A** (md5 `3a255fa4`, positional `sys.argv[1]`, default 200) -> ran with explicit `1` |
| Round counter | files->440, history->440, start=**441** (no shadowing; target file did not exist) |
| TLS leaf | **VALID** — CN=typesafe.ai, Let's Encrypt YE2, notAfter 2026-12-21 -> no CA rebuild needed |
| API key | `TYPESAFE_AI_TOKEN` read natively by the script (no manual `JEV_API_KEY` mapping needed) |
| Script | 1 round, 5 verdicts, 0 fails, 0.3 s |
| Corpus | 351 round files across 3 locations; 2,100 deduped records; rounds 1–441, 9 gaps (r194–r202) |

### Method rules applied (durable)
- **Never quote the script's `drift_events`** — it reports HISTORY events, not this round's.
- **Score every baseline per model segment** — a pooled baseline manufactures false drift flags.
- **|dev| first, z second** — a near-degenerate sigma inflates z on a trivial movement.
- **Restrict drift to qids DRAWN this round.**
- **Regenerate comparison tables from the archives** — never from a remembered series.
- **A repeat-of-existing-value flag is archive-judgeable; a NEW extreme must be re-measured.**
- **MC draws 5 qids uniformly from ALL 22** — not from a bedrock/below partition.
- **Round-file `model` field is the static alias `jev-latest`**; the resolved model lives only in `history.jsonl`.
