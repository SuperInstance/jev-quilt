# JEV Continuous Probe — r419 (2026-10-24T13:04:20Z)

**Repo:** `SuperInstance/jev-quilt` · **HEAD before:** `d12f43c` (r418) · **Model:** `jev-1.14.0` (23rd consecutive)
**Script md5:** `3a255fa4642ec4a83173ab04d773d485` — **unchanged from r417/r418 ⇒ mean_p is directly comparable**
**Run:** `python3 -u jev_continuous_probe.py 1` (explicit positional count — the arg defaults to looping for the full 55 s internal ceiling)
**Result:** 1 round OK, 0 fails, 5 verdicts, exit 0, 0.153 s/round, round file `research/jev_sessions/continuous_r419.json`

---

## 1. Headline numbers

| Metric | r419 | r418 | r417 | r416 |
|---|---|---|---|---|
| **mean_p** | **0.5380** | 0.1480 | 0.4180 | 0.2400 |
| **bedrock hits (p ≥ 0.70)** | **3/5** | 0/5 | 2/5 | 0/5 |
| class mix | 3 bedrock + 2 spec | 3 spec + 2 adv | 2 bedrock + 2 spec + 1 adv | 1 bedrock + 3 spec + 1 adv |
| script `drift_events` | 1 | 1 | 1 | 1 |
| **drift verdict (drawn-only)** | **NO DRIFT** (max \|dev\| 0.0500) | NO DRIFT | NO DRIFT | REAL (q02) |

**mean_p = 0.5380. Bedrock hits: q01 (0.86), q04 (0.87), q05 (0.78) — 3 of 5, all ≥ 0.70.**

---

## 2. r419 verdicts

| qid | kind | p | bedrock hit (p ≥ 0.70) |
|---|---|---|---|
| q01 | bedrock | 0.86 | ✅ |
| q05 | bedrock | 0.78 | ✅ |
| q04 | bedrock | 0.87 | ✅ |
| q06 | speculative | 0.13 | ❌ |
| q10 | speculative | 0.05 | ❌ |

All three bedrock questions drawn cleared the p ≥ 0.70 canon gate. Both speculative questions stayed where they belong (q06 0.13, q10 0.05 — both at their all-time floors).

---

## 3. Is mean_p 0.5380 remarkable? — NO, it is an ordinary draw (class-mix corrected)

`mean_p` is a **class-mix number**, never read alone. Per-kind μ over the last 40 samples/qid:

| kind | μ | n |
|---|---|---|
| bedrock | 0.8491 | 280 |
| review | 0.4491 | 80 |
| speculative | 0.1498 | 400 |
| adversarial | 0.1091 | 120 |

r419's mix is 3 bedrock + 2 speculative ⇒ **expected mean_p = 0.5694**. Observed 0.5380 ⇒ **dev −0.0314**.
MC bootstrap (class-conditional, n = 20,000) ⇒ **P(mean_p ≥ 0.5380) = 0.856** ⇒ r419 is a *typical* draw for this mix, slightly below its own expectation and nothing more.

**Context:** last-20 window mean_p = 0.4202; **309 of 379** historical 20-round windows sit below it (corpus 82nd percentile). r419's 0.5380 is the **highest of all 379 windows** — but that is a direct consequence of drawing 3 bedrock questions out of 5, not evidence of any shift. This is the mean_p-class-mix rule holding for the **6th consecutive round** (r414–r419).

---

## 4. Drift — the script's flag is a PHANTOM (10th reproduction)

`drift_check()` scans the **entire history** and flags any qid whose *last recorded* p deviates > 0.05 from its prior median — **regardless of whether that qid was drawn this round**.

Script output: `drift_events=1` → `q12, recent_p 0.56, prior_median 0.50, delta +0.06`.

**q12 was NOT drawn in r419.** Drawn set = {q01, q05, q04, q06, q10}. ⇒ **PHANTOM — 10th consecutive reproduction** (r409 → r419).

**Drawn-only drift (dev = this p − prior-5 median):**

| qid | p | prior-5 median | dev |
|---|---|---|---|
| q01 | 0.86 | 0.86 | +0.0000 |
| q04 | 0.87 | 0.88 | −0.0100 |
| q05 | 0.78 | 0.83 | **−0.0500** |
| q06 | 0.13 | 0.14 | −0.0100 |
| q10 | 0.05 | 0.05 | +0.0000 |

**max |dev| = 0.0500 — not > 0.05 ⇒ NO DRIFT** by the standard threshold.

### 4.1 The q12 plateau — and why the script's own window is misleading

q12's all-time trajectory: 0.32 (r330) → 0.42 (r350) → 0.40 (r370) → **0.50 (r398) → 0.51 → 0.46 → 0.54 → 0.56 (r409)**, then flat. Against the **prior-10** median (0.42) the deviation is **+0.14**, not +0.06.

The script's `window=5` computes its median over `[0.50, 0.51, 0.46, 0.54, 0.56]` — i.e. it **includes the recent elevated values in the baseline**, which shrinks the apparent delta and, worse, keeps re-firing on the same stale r409 sample every round. q12's true shape is a **0.30–0.56 plateau with a recent upper band**, not a drift. It remains **speculative by `spec_notebook` regardless of score** — no promotion. 0.56 has been its all-time max since r409 and it has not been re-drawn since.

---

## 5. ⚠️ The real finding: q05 is a genuine new all-time low

q05's dev vs its prior-5 median is exactly **−0.0500**, which *misses* the > 0.05 threshold. But the threshold is not the whole story:

- **0.78 is q05's all-time minimum** — and the **only** sub-0.80 sample in **86 draws** (previous min was 0.82).
- **z = −5.05σ** against q05's all-time mean (0.8491, sd 0.0137).
- Against a **prior-15** median (0.84) the deviation is **−0.0600 ⇒ exceeds 0.05**.
- It is the **largest single-step** q05 has ever shown: prior new-min steps were −0.01, −0.01, −0.03, −0.03; this is **−0.04** in one draw.

**Why this is NOT the r416 q02 version artifact:**

| | r416 (q02 = 0.69) | r419 (q05 = 0.78) |
|---|---|---|
| Model | jev-1.14.0 (post-switch) | jev-1.14.0 (same, 23rd round) |
| Other bedrock qids in same draw | q03/q04/q08 **flat** | q01 (−0.01), q04 (−0.01) **flat** |
| Speculative mirror signal | q12/q06/q14/q18/q13 **rising** | q06 (−0.01), q10 (−0.01) **flat/down** |
| Deviation | −0.08 vs prior-10 | −0.05 vs prior-10, −0.06 vs prior-15 |
| Reading | version artifact, explained | **unexplained, single-qid, isolated** |

⇒ **q05's dip is isolated to q05.** No correlated movement in sibling bedrock qids, no speculative mirror rise, no model change. This is the signature of a **genuine single-question movement**, and it should be **watched, not dismissed**. If r420–r422 draw q05 and it returns to 0.82–0.83, r419 was an outlier draw. If it prints 0.78–0.80 again, that is a **real q05-level shift** and the canon gate for q05 (currently the weakest bedrock at μ 0.8491) needs a baseline re-derivation.

**Verdict: NO DRIFT (max drawn \|dev\| = 0.0500, under threshold) — but r419 carries one genuine amber flag on q05 (new all-time min, −5.05σ) that the script's threshold-based drift check structurally cannot report.**

---

## 6. Cathedral (bedrock canon) — unchanged, 99.84%

| qid | n | hits | hit rate | mean_p | min_p |
|---|---|---|---|---|---|
| q01 | 100 | 100 | **100.0%** | 0.8744 | 0.84 |
| q02 | 83 | 82 | 98.8% | 0.8154 | 0.69 |
| q03 | 95 | 95 | **100.0%** | 0.8855 | 0.86 |
| q04 | 94 | 94 | **100.0%** | 0.8884 | 0.87 |
| q05 | 86 | 86 | **100.0%** | 0.8491 | **0.78** ← r419 |
| q07 | 79 | 79 | **100.0%** | 0.7548 | 0.71 |
| q08 | 77 | 77 | **100.0%** | 0.8995 | 0.87 |
| **TOTAL** | **614** | **613** | **99.84%** | | |

Six of seven bedrock questions remain at a 100% all-time hit rate. q02 remains the only non-perfect bedrock (98.8%, from the r416 model step). **No promotion, no demotion, no qid changed class.** q10/q11/q12/q13 remain speculative per `spec_notebook` regardless of score.

---

## 7. Method notes (durable)

1. **mean_p is a class-mix number — never read it alone.** Compute the class-conditional expectation + MC bootstrap *first*. r419's 0.5380 looks like the round's peak in 379 windows; it is a 3-bedrock draw, nothing more.
2. **"N bedrock hits" is vacuous when bedrock_drawn = 0.** r418 drew zero bedrock; r419 drew three. Hit count only means something alongside the mix.
3. **`drift_check()` scans the whole history — 10 phantoms now.** It will keep re-firing on q12's stale r409 sample until q12 is next drawn. The standing cheap fix remains: **pass the drawn qid set into the function** and restrict the scan to it.
4. **The `window=5` prior median includes recent values in the baseline**, which damps a real delta (q12: +0.06 reported vs +0.14 actual vs prior-10) *and* creates a sticky flag that survives many rounds.
5. **A threshold verdict is not a finding.** q05 missed > 0.05 by exactly 0.0000 while setting a new all-time minimum at −5.05σ. Always check *is this the all-time extreme* alongside *is dev over threshold* — the two answer different questions.
6. **Bucket each qid against its OWN baseline**, and de-duplicate `history.jsonl` by round number before any baseline math (8 duplicate rounds r384–r391 live in that file).

---

## 8. Environment (114th wipe)

- **`/workspace` arrived EMPTY** (only `.plugin-cache`) — the user's stated path `/workspace/research/jev_sessions/continuous_r*.json` did not exist; the repo was re-cloned to the overlay and the history re-derived from `research/jev_sessions/`.
- **NAS at 100% (0 avail).** Every write path into `/workspace` yields a **0-byte stub that `ls` shows as a real file** (26th observation of the silent-zero trap). ⇒ **`/workspace/research/jev_hourly_report.md` is UNWRITABLE; the durable copy is git** (`research/jev_hourly_report_r419.md` in the repo).
- **Repo root is the live script** (`jev_continuous_probe.py`, md5 `3a255fa4…`), not the `continuous/` variant.
- `SSL_CERT_FILE` = gateway-anchor-only (11th recurrence) ⇒ rebuilt a **578-cert** bundle at `/tmp/bundle.pem` (232,614 bytes).
- `TYPESAFE_AI_TOKEN` set, `TYPESAFEAI_KEY` unset (script accepts either). API healthy: `GET /v1/systemone` → **405** (POST-only) = reachable, do not read 405 as failure.
- `gh` absent (22nd). Clone/push need `GIT_SSL_NO_VERIFY=1`; push to the explicit token URL and verify with `git fetch` + `git rev-parse FETCH_HEAD:<path>`.
- **Work in `/tmp/<repo>`** (overlay, 28 G free) — the overlay is NOT subject to the NAS EDQUOT trap.
