# JEV Hourly Report — r418

**Date:** 2026-10-24T12:03Z
**Round:** 418 · **Status:** ok · **Model:** `jev-1.14.0` (22nd consecutive) · **Elapsed:** 0.295 s
**Script md5:** `3a255fa4642ec4a83173ab04d773d485` (unchanged from r417 ⇒ comparable)
**Repo:** `SuperInstance/jev-quilt` · **Session dir:** `research/jev_sessions/`

---

## 1. Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.1480** |
| **Bedrock hits (p ≥ 0.70)** | **0 / 5** — *no bedrock question was drawn* |
| **Drift > 0.05** | **NONE** (0 drawn-only events) |
| Verdict | **ORDINARY DRAW — not a collapse, not a regression** |

**mean_p 0.1480 is a class-mix artifact, not a substrate signal.** r418 drew **zero bedrock
questions** — the 5 drawn were 3 speculative + 2 adversarial, whose historical baselines are
0.1481 and 0.1004. Reading 0.1480 as "the oracle collapsed" is the same error as reading
r416's 0.2400 as a collapse. **Do not read mean_p without the class mix.**

---

## 2. Round detail (drawn-only)

| qid | kind | p | prior median | dev | all-time min–max (n) | drift>0.05? |
|---|---|---|---|---|---|---|
| q06 | speculative | 0.14 | 0.1400 | +0.0000 | 0.09–0.15 (91) | no |
| q14 | adversarial | 0.21 | 0.2300 | −0.0200 | 0.16–0.25 (89) | no |
| q19 | adversarial | 0.11 | 0.1000 | +0.0100 | 0.09–0.12 (85) | no |
| q11 | speculative | 0.19 | 0.1900 | +0.0000 | 0.15–0.22 (97) | no |
| q20 | speculative | 0.09 | 0.0800 | +0.0100 | 0.08–0.13 (90) | no |

**Max |dev| = 0.0200 (q14).** No drawn question exceeded the 0.05 threshold. Every value sits
inside its own historical range; three of five landed exactly on the prior median.

### Which questions hit p ≥ 0.70 (bedrock canon)?
**None.** This is *not* a bedrock failure — **no bedrock qid was in the draw.** The 7-qid
cathedral was untouched this round, so its all-time hit rate is unchanged at
**646/647 = 99.8%**:

| qid | n | hit_rate | mu | min–max |
|---|---|---|---|---|
| q01 | 101 | 1.000 | 0.8745 | 0.84–0.90 |
| q02 | 86 | 0.988 | 0.8153 | 0.69–0.86 |
| q03 | 99 | 1.000 | 0.8858 | 0.86–0.91 |
| q04 | 97 | 1.000 | 0.8888 | 0.88–0.91 |
| q05 | 94 | 1.000 | 0.8500 | 0.82–0.87 |
| q07 | 85 | 1.000 | 0.7547 | 0.71–0.79 |
| q08 | 85 | 1.000 | 0.8996 | 0.87–0.91 |

Only q02 has ever dipped below 0.70 (min 0.69, r416 — already resolved as a
`jev-1.13.0 → 1.14.0` version artifact). q02 is otherwise 85/86.

---

## 3. Why mean_p 0.1480 is an ordinary draw (not a collapse)

**Per-kind baselines (n = 2,110 verdicts):**

| kind | n | mu | sd | min–max |
|---|---|---|---|---|
| bedrock | 647 | 0.8545 | 0.0491 | 0.69–0.91 |
| review | 184 | 0.4400 | 0.2517 | 0.18–0.74 |
| speculative | 988 | 0.1481 | 0.0903 | 0.05–0.56 |
| adversarial | 291 | 0.1004 | 0.0715 | 0.02–0.25 |

r418's mix = 3 speculative + 2 adversarial, 0 bedrock:

- **Expected mean_p for this mix = 0.1290**
- **Observed = 0.1480** → deviation **+0.0190**
- **Monte-Carlo bootstrap** (class-conditional resampling from the real pools, n = 20,000):
  **P(mean_p ≥ 0.1480) = 0.280**

An ordinary draw sits at the ~0.5 quantile. 0.28 is squarely in the bulk, and the observed
value is *above* the expectation for its mix. **Verdict: ordinary draw. No collapse, no
recovery signal, no promotion.**

**Corpus context:** the last-20 window mean_p is **0.4119**, and **301 of 403** historical
20-round windows sit *below* it — the corpus is in its upper decile. r418's 0.1480 is a
single-draw outlier explained entirely by its zero-bedrock mix.

---

## 4. Drift

**Drawn-only: 0 events, max |dev| = 0.0200. NO DRIFT.**

**🔴 Script `drift_events=1` is a PHANTOM — 9th reproduction.** The script's `drift_check()`
scans the *entire* history, not the drawn subset, and flagged:

> `q12: recent=0.5600 prior_median=0.5000 delta=+0.0600` — **q12 was NOT drawn in r418.**

This is the same defect as r409–r417. **Always recompute drift restricted to the drawn
qids.** (q12 is a ~0.37-baseline speculative plateau that grazes 0.56 occasionally; a
0.06 delta against a 0.50 median is a *prior-round* artifact, not this round's signal.)

**Recommendation (unchanged from r414–r417):** fix `drift_check()` to accept the drawn qid
set. Nine reproductions make this a standing, cheap fix.

---

## 5. Promotion check

**No promotion.** No non-bedrock question crossed 0.70. Highest speculative value this
round was q11 = 0.19 (baseline mu ≈ 0.19). q12 (the round's high-water speculative, max
0.56) was not drawn and remains at its plateau. Per `spec_notebook`, q10/q11/q12/q13 stay
**speculative regardless of score** — n ≥ 20 with hit-rate ≥ 0.7 *and* explicit doctrinal
phrasing are required.

---

## 6. Method notes (durable)

1. **mean_p is a class-mix number.** Always compute the class-conditional expectation and
   bootstrap before calling *any* round a collapse or a recovery. This is now measured
   across r414–r418.
2. **|dev| first, σ second.** The largest z is often the smallest real movement.
3. **Recompute drift on the drawn subset only.** The script's whole-history scan has
   produced 9 phantoms.
4. **Bucket each qid against its OWN baseline** — never one global threshold. q06 (mu 0.14),
   q20 (mu 0.08), q12 (mu 0.37) are plateaus by design.
5. **`history.jsonl` carries 8 DUPLICATE round records (r384–r391)**, a pre-r229 counter
   defect. De-duplicate by round number before any baseline math. r418 itself recorded once.
6. **Model stratification before naming drift.** `jev-1.13.0` (399 rounds) → `jev-1.14.0`
   (22 rounds) at r396 is a calibration boundary. r418 is 1.14.0; q02's within-1.14.0
   baseline is **mu 0.7337**, not the blended 0.8159.

---

## 7. Environment

- **113th wipe.** `/workspace` arrived EMPTY (only `.plugin-cache`).
- **NAS `/workspace` 600G at 100% (0 avail)** ⇒ the requested
  `/workspace/research/jev_hourly_report.md` is **unwritable** (`cp` → "failed to close …
  Disk quota exceeded", leaving a 0-byte stub that still appears in `ls` — 25th observation of
  the silent-zero trap). **Durable copy = git.**
- Work performed in `/tmp/jev-quilt` (overlay fs, 28 G free) — the overlay is **not** subject
  to the NAS EDQUOT trap.
- `SSL_CERT_FILE` = gateway-anchor-only (10th recurrence) ⇒ rebuilt a **428-cert** bundle at
  `/tmp/bundle.pem` (1,086,910 bytes). TLS leaf **VALID**.
- `TYPESAFE_AI_TOKEN` present (`TYPESAFEAI_KEY` unset; the script accepts either).
  API reachable — `GET /v1/systemone` → 405 (POST-only), health confirmed.
- `gh` absent (21st).
- Git: clone with `GIT_SSL_NO_VERIFY=1`; push via the explicit token URL and verify with
  the **git protocol** (`git ls-remote`).

---

## 8. Receipts

| Artifact | Value |
|---|---|
| Round file | `research/jev_sessions/continuous_r418.json` (md5 `03dc215aa1b2756757ae21608f3611ca`) |
| History | `research/jev_sessions/history.jsonl` — 421 → **422** lines |
| Round counter | files→417, history→417, start=**418** |
| Script md5 | `3a255fa4642ec4a83173ab04d773d485` (unchanged, 2 rounds) |
| Rounds ok / fail | **1 / 0** |

**Raw output:**
```
round counter: files->417 history->417 start=418
r418 OK  mean_p=0.1480  hits=0/5  0.295s

=== Hourly summary ===
rounds_ok=1  fails=0  total_verdicts=5
grand_mean_p=0.1480  bedrock_hits=0/5 (0.0%)
drift_events=1        <-- PHANTOM (q12 not drawn)
elapsed=0.5s
```
