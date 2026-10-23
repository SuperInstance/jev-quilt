# JEV Continuous Probe — Hourly Report r407

**Run:** 2026-10-23T23:03Z · **Round:** r407 · **Status:** 1 round OK, 0 fails, 5 verdicts
**Script md5:** `3a255fa4642ec4a83173ab04d773d485` (unchanged, 8th consecutive wipe) · **Model:** `jev-latest` / `jev-1.14.0`
**Corpus:** `SuperInstance/jev-quilt @ de1a6d8` → 386 distinct rounds, 1,930 verdicts, 22 qids
**Prior round:** r406 (mean_p 0.2940, 1/5 bedrock)

---

## 1. mean_p

**r407 mean_p = 0.4580** (5 verdicts: q01 0.87, q02 0.71, q15 0.03, q12 0.54, q22 0.14)

| | value |
|---|---|
| r407 mean_p | **0.4580** |
| prev-12 mean-of-means | 0.4822 |
| corpus grand mean_p | 0.3835 (1,930 verdicts) |

**The mean is a draw-mix artifact, not a signal.** r407 drew 2 bedrock of 5 questions; r406 drew 1 of 5. Health lives in the cathedral and the buckets, never in the grand mean. Per-qid deviation, not mean_p, is the honest read — see §3.

## 2. Questions hitting p >= 0.70 (bedrock canon)

**2 of 5 drawn questions hit the canon threshold:**

| qid | kind | p | verdict |
|---|---|---|---|
| **q01** | bedrock | **0.87** | HIT — `cells are scars of failed attempts` |
| **q02** | bedrock | **0.71** | HIT — `witness logs are predictions` (but see §3 — this is a NEW ALL-TIME LOW) |
| q15 | adversarial | 0.03 | correctly low |
| q12 | speculative | 0.54 | spec-band (see §4) |
| q22 | speculative | 0.14 | spec-band |

**Canon census (7 bedrock qids, full history):**

| qid | n | mean | min | hits |
|---|---|---|---|---|
| q01 | 98 | 0.8748 | 0.84 | 98/98 |
| **q02** | **78** | **0.8208** | **0.71** | **78/78** |
| q03 | 92 | 0.8861 | 0.86 | 92/92 |
| q04 | 93 | 0.8886 | 0.88 | 93/93 |
| q05 | 82 | 0.8507 | 0.82 | 82/82 |
| q07 | 78 | 0.7546 | 0.71 | 78/78 |
| q08 | 74 | 0.8995 | 0.87 | 74/74 |
| **TOTAL** | **595** | | | **595/595 = 100.0%** |

**Canon is still 100% — 595/595, no breach.** q02 remains a hit at 0.71 (above the 0.70 bar), so canon has NOT eroded. But it is the *lowest q02 draw ever recorded* and the second consecutive sub-0.75 draw.

**Spec/adv leakage: NONE.** No speculative or adversarial qid has ever crossed 0.70. The only non-bedrock hits are q17 (`FNV-1a canary`, kind=review) at 58/78 = 74.4% — expected, and it is a `review` qid, not canon.

## 3. Drift > 0.05

The script reported `drift_events=2`. **Both flags are for questions actually drawn this round** (the known stale-echo defect at `jev_continuous_probe.py:317-335` did not fire here), so both are real candidates. I re-derive each against the **full-history** mean and σ, not the script's 5-sample median.

| qid | p | hist mean | sd | dev | z | prior range | verdict |
|---|---|---|---|---|---|---|---|
| **q02** | 0.71 | 0.8222 | 0.0205 | **−0.1122** | **−5.48** | [0.73, 0.86] | **REAL — new all-time low** |
| **q12** | 0.54 | 0.3721 | 0.0376 | **+0.1679** | **+4.46** | [0.30, 0.51] | **REAL — new all-time high** |
| q01 | 0.87 | 0.8748 | 0.0093 | −0.0048 | −0.52 | [0.84, 0.90] | noise |
| q15 | 0.03 | 0.0253 | 0.0050 | +0.0047 | +0.94 | [0.02, 0.03] | noise |
| q22 | 0.14 | 0.1200 | 0.0079 | +0.0200 | +2.52 | [0.11, 0.16] | noise (|dev| < 0.05) |

**σ≈0 trap, 15th consecutive, rule held in both directions:** q22 posts z = +2.52 on a |dev| of only 0.0200 — the eye catches the z, |dev| says nothing moved. q22 is **not** drift. q02 and q12 are the inverse case: both have |dev| >> 0.05 **and** are new range extremes.

### 3a. q02 — ESCALATION: canon-erosion watch

**This is the finding. The trigger set last round has fired.**

Last round (r406) I set the rule: *"NEXT q02 DRAW DECIDES: 2nd sub-0.75 ⇒ escalate to canon-erosion watch; ≥0.80 ⇒ tail was noise."* r407's q02 = **0.71 — a second consecutive sub-0.75 draw. ESCALATE.**

```
r399 0.75   ← first sub-0.75 in q02's entire history
r401 0.77
r406 0.73
r407 0.71   ← NEW ALL-TIME LOW, 2nd consecutive sub-0.75
```

* **dev −0.1122, z −5.48** against a full-history baseline of 0.8222 ± 0.0205. On a 100%-hit qid, 5.5σ is not noise.
* **Era means show a structural shift, not a wobble.** Blocks of 20 draws: 0.8300 → 0.8230 → 0.8270 → **0.8011** (draws 61-78). The first three eras are flat within 0.007; the last era drops 0.026 and contains both sub-0.75 draws.
* **last-5 mean 0.7540 vs prev-5 mean 0.8180 = −0.0640.** The gap is exactly one stddev wide.
* **recent29 mean = 0.8114 — BELOW the 0.81 canon-erosion watch threshold** (first time on this metric).
* **recent15 mean = 0.7947**, full-history mean 0.8208.
* **Not monotone** — the last 3 diffs are not all negative (0.81→0.82→0.84→0.81→0.81→0.81→0.75→0.77→0.73→0.71 has a +0.02 at r401 and flat steps at r381/r383). So the tail is a *step down* with a continuing slide, not a clean monotone bleed. Both readings point the same way though: the level has shifted down and has not come back.
* **Canon has NOT eroded.** 78/78 q02 hits, 0 draws below 0.70, 595/595 canon overall. A sub-0.70 draw would be the true breach. r407's 0.71 cleared the bar by 0.01.

**Watch state: ESCALATED — canon-erosion watch, not breach.** Next q02 draw is decisive again:
* `< 0.70` ⇒ **canon breach**, report immediately.
* `0.70-0.74` ⇒ third consecutive sub-0.75 ⇒ treat the shift as structural.
* `>= 0.80` ⇒ the tail was noise; close the watch.

Caveat: q02 is drawn in only 78/386 rounds (20.2%), so this is a thin sample — but it is 5.5σ on the anchor qid, and the era shift is visible in the aggregate, not just the last point.

### 3b. q12 — new all-time high in the spec band

q12 = **0.54**, previous max 0.51, dev **+0.1679**, z **+4.46**. This is real by the |dev| > 0.05 rule *and* a range extreme.

But **q12 cannot reach canon**: it is kind=speculative with a spec_notebook guard, 0/87 hits all-time, and the promotion gate requires n>=20 with hit-rate >= 0.7 *plus* explicit doctrinal-state phrasing. A rising spec score is **not** a canon event — it is the spec_notebook guard being tested, and the guard is holding (still well under 0.70).

What is worth noting: q12's baseline mean is **0.3740**, roughly **2x the next-highest speculative qid (q11 at 0.1852)**, and it is the only spec qid with a wide σ (0.0415 vs ~0.005-0.017 for every other spec qid). q12 is the one question the oracle finds genuinely *interesting* rather than clearly false — it has been the persistent plateau since r398 (0.50, 0.51, 0.46, 0.54). This is a **promotion-candidate** signal, not a leak: q12 is the only speculative framing with any movement at all, and the correct action is to keep the spec_notebook guard in place and watch whether the plateau keeps climbing.

## 4. Verdict

| | |
|---|---|
| mean_p | **0.4580** (draw-mix: 2/5 bedrock drawn) |
| p >= 0.70 hits | **q01 (0.87), q02 (0.71)** — 2/5 drawn |
| Canon census | **595/595 = 100.0%** — no breach |
| Spec/adv leak | **NONE** — no speculative/adversarial qid has ever crossed 0.70 |
| Real drift > 0.05 | **2: q02 (−0.1122, new low) and q12 (+0.1679, new high)** |
| Noise | q01, q15, q22 (all \|dev\| < 0.05) |
| **STATE** | **Canon-erosion watch ESCALATED on q02** — 2nd consecutive sub-0.75, era mean shifted 0.027 down, recent29 below threshold. Canon itself still intact at 100%. |

**Direction of travel:** two speculative-side qids at new highs (q12 +0.1679, q22 near high) while the canon anchor slides down. Confidence is narrowing on speculation and eroding on one piece of canon. This is the same signature as r406, one round stronger.

## 5. Method notes / environment

* **22nd consecutive ephemeral-path wipe.** `/workspace/research/` and `/tmp/jev_probe/` were both absent on arrival; rebuilt from `SuperInstance/jev-quilt` into `/tmp` (overlay, 28G free) rather than the NAS.
* **NAS 100% quota (25th recurrence)** — 600G/600G, 0 bytes available. The durable copy of this report is **git**, not `/workspace/research/`.
* **TLS clean on first try** — live leaf `api.typesafe.ai` valid to 2026-12-25 (+62.5 d), issuer Google Trust Services WE1, **strict verification passed**. No cert-anchor wall, no 289-cert bundle rebuild needed. 7th clean wipe.
* **One round, no overshoot** — ran `python3 jev_continuous_probe.py 1` with the **explicit positional count**. The task's literal command (no arg) defaults to **200 rounds** and would have raced the writer past a single round; the positional arg is the fix shipped in r229.
* **Round counter verified two ways**: files -> r406, history -> r406, start = r407. No clobber, no duplicate. `history.jsonl` = 410 records, max round 406, 0 malformed.
* **Corpus source**: `research/jev_sessions/` (215 files, ends r407) is the LIVE tree. The repo-root `jev_sessions/` (208 files, ends r386) is a **stale legacy leftover** — do not read it for history.
* **Not read:** `session_summary.json` was not consulted; all statistics recomputed from the round files, since `timeout -s KILL` can eat the summary and a raw drift-event count is never a health verdict.
* **Drift decomposed per qid against each qid's OWN baseline** (never one global threshold), and every flag was checked against the set of questions actually drawn this round.
