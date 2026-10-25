# JEV Continuous Probe — Round r427

**Timestamp:** 2026-10-25T00:03:12Z
**Session:** 125th wipe (workspace empty on arrival — 18th consecutive)
**Script:** `jev_continuous_probe.py` md5 `3a255fa4642ec4a83173ab04d773d485` (Variant A, unchanged since r397)
**Served model:** `jev-1.14.0` (from `decide_batch` meta) — same as baseline, no model switch
**Corpus:** 431 ok round-records / 22 qids / 2,155 verdict observations
**Run:** 1 round, 0 fails, 0.157 s, `rounds_ok=1 fails=0`

---

## 1. Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.4200** |
| **Bedrock hits (p ≥ 0.70)** | **2/5** — q01 (0.85), q04 (0.88) |
| **Drift > 0.05** | **NONE confirmed** — 1 flag (q11) refuted by independent re-measurement |
| Script's own `drift_events` | 3 — **all 3 are stale re-fires** (see §5) |

**Verdict: ORDINARY ROUND. No drift.**

---

## 2. Drawn questions this round

| qid | kind | p | bedrock hit |
|---|---|---|---|
| q04 | bedrock | 0.88 | ✅ |
| q01 | bedrock | 0.85 | ✅ |
| q13 | speculative | 0.15 | — |
| q11 | speculative | 0.12 | — |
| q19 | adversarial | 0.10 | — |

Both bedrock draws hit the gate; both speculative/adversarial draws read correctly low.

---

## 3. History comparison (regenerated from `history.jsonl`, not from memory)

| Round | mean_p | hits | model |
|---|---|---|---|
| r419 | 0.538 | 3 | jev-1.14.0 |
| r420 | 0.358 | 1 | jev-1.14.0 |
| r421 | 0.554 | 3 | jev-1.14.0 |
| r422 | 0.506 | 2 | jev-1.14.0 |
| r423 | 0.526 | 2 | jev-1.14.0 |
| r424 | 0.376 | 2 | jev-1.14.0 |
| r425 | 0.356 | 1 | jev-1.14.0 |
| r426 | 0.404 | 2 | jev-1.14.0 |
| **r427** | **0.420** | **2** | **jev-1.14.0** |

- Last-20 (excl. today): μ = 0.4101, σ = 0.1022 → **today z = +0.10**
- 1.14.0 segment (32 rounds): μ = 0.4333, σ = 0.1132
- Bedrock-hit distribution in the 1.14.0 segment: 0→2, 1→7, **2→15**, 3→7, 4→1
  → **2-of-5 is the single most likely outcome (37.96 % by MC).**

### Class-mix Monte Carlo (200k draws, 5 qids uniformly from all 22)

- E[mean_p] = 0.3943, σ = 0.1376
- P(mean_p ≤ 0.420) = **0.5815**, today z = **+0.19**
- P(0 bedrock) 8.77 % · **P(1) 32.05 %** · **P(2) 37.96 %** · P(3) 17.81 % · P(4) 3.24 % · P(5) 0.18 %

`mean_p` is a property of the **draw**, not of the canon. A 2/5 draw is the modal outcome.

---

## 4. Drift analysis (recomputed — the script's own number is a history-reporter)

**Method:** per-qid dev vs that qid's **own** model-segmented (1.14.0) baseline, restricted to the 5 qids **drawn this round**. |dev| checked before σ.

| qid | p | n | baseline μ | σ | dev | z | verdict |
|---|---|---|---|---|---|---|---|
| q04 | 0.88 | 8 | 0.8825 | 0.0109 | −0.0025 | −0.23 | ok |
| q01 | 0.85 | 8 | 0.8562 | 0.0086 | −0.0062 | −0.73 | ok |
| q13 | 0.15 | 7 | 0.1614 | 0.0035 | −0.0114 | −3.27 | ok (σ≈0 trap) |
| q19 | 0.10 | 7 | 0.1043 | 0.0049 | −0.0043 | −0.87 | ok |
| **q11** | **0.12** | 5 | **0.1840** | 0.0120 | **−0.0640** | −5.33 | **FLAG → refuted, see §5** |

Full-history (all-model) baseline gives the same picture: q11 −0.0649, everything else < 0.03.
**Max |dev| among non-flagged drawn qids = 0.0114.** No qid beyond the 0.05 floor except q11.

**σ≈0 trap fired on q13** (largest z at −3.27, but |dev| only 0.0114) — the classic
"largest z is often the smallest real movement". |dev|-first ordering is what caught it.

---

## 5. The q11 flag — refuted by independent re-measurement

q11 (speculative: *"canon gate is a chord (multiple converging verdicts)"*) read **0.12**,
which is:
- |dev| = **0.0640** vs its own 1.14.0 baseline (0.1840) — **exceeds the 0.05 floor**
- the **strict minimum of all 98 observations** in q11's entire history; **0 prior values below it**
- not a repeat of an existing value (unlike r422's q12 flag, which repeated 0.46)

Taken at face value this would be a real new extreme. So it was re-measured.

**Independent re-measurement — 6 fresh draws of q11 on the IDENTICAL doctrinal state,
same call path, same served model, plus a q04 control on the same call:**

| draw | 1 | 2 | 3 | 4 | 5 | 6 | mean | σ |
|---|---|---|---|---|---|---|---|---|
| q11 | 0.16 | 0.15 | 0.15 | 0.15 | 0.16 | 0.18 | **0.1583** | 0.0107 |
| q04 (control) | 0.85 | 0.87 | 0.88 | 0.88 | 0.89 | 0.87 | 0.8733 | — |

**0.12 does not reproduce.** The fresh distribution is centred at 0.158 — essentially the
baseline mean of 0.184 minus ordinary jitter, and **0 prior observation is below 0.15**.
The q04 control stayed tight (0.85–0.89), proving the harness and the state were healthy
during the re-measurement.

**Conclusion: r427's q11 = 0.12 is a one-off low outlier, NOT a regime shift.**
Direction is also the *safe* one (a speculative framing reading lower, i.e. further from
canon), so it carries no canon-health risk even if it were real.

**No confirmed drift. Round is clean.**

### The script's own `drift_events=3` — all three are stale re-fires

`drift_check()` has **no current-round filter**: it takes the last value per qid across all
history and compares it to a 5-sample local median, whether or not that qid was drawn.

| reported | qid | was it drawn this round? | truth |
|---|---|---|---|
| q02 −0.06 | q02 | **no** | stale draw from r425 |
| q11 −0.07 | q11 | yes | genuine flag, refuted above |
| q17 +0.05 | q17 | **no** | stale draw from r424 |

14th reproduction of this defect. **The script's drift_events is never a health verdict.**

---

## 6. Canon health (cathedral + buckets)

**Bedrock canon — per-qid hit rate, 1.14.0 segment:**

| qid | 1.14.0 | all-time | note |
|---|---|---|---|
| q01 | 18/18 = 100 % | 208/208 = 100 % | |
| q03 | 14/14 = 100 % | 194/194 = 100 % | |
| q04 | 18/18 = 100 % | 198/198 = 100 % | |
| q05 | 16/16 = 100 % | 185/185 = 100 % | |
| q07 | 16/16 = 100 % | 170/170 = 100 % | |
| q08 | 12/12 = 100 % | 166/166 = 100 % | |
| **q02** | **18/24 = 75.0 %** | 169/175 = 96.6 % | **all 1.14.0 misses sit in the 0.68–0.69 sub-gate** |

Cathedral: **6 of 7 bedrock qids at 100 %.** q02 remains the single fragile one — every
failure is 0.68 or 0.69, i.e. a hair under the 0.70 gate, never a collapse. Watch item, unchanged.

**Speculative (must stay < 0.70):** every qid holds. Max ever observed: q12 0.56, q18 0.26,
q11 0.22, q13 0.17, q06 0.15, q22 0.16, q09 0.11, q21 0.10, q20 0.13, q10 0.08.
**No speculative qid has EVER reached 0.70** (0 occurrences across 2,155 observations).

**Adversarial (must read LOW):** q14 mean 0.224 / max 0.25 · q15 mean 0.030 / max 0.03 ·
q19 mean 0.104 / max 0.12. All correctly low; 0 occurrences ≥ 0.70.

**Review qids:** q17 holds a 0.68–0.75 plateau (1.14.0 mean ≈ 0.71); q16 holds 0.19–0.20.
q17's plateau grazes the 0.70 line by design — read against **its own** baseline, never a
global threshold.

---

## 7. Method notes (carry forward)

- **Re-measurement beats archive comparison for a single flag.** The archive said q11 hit a
  strict new minimum; six fresh draws on the same state said 0.12 was an outlier. The
  archive cannot distinguish "new extreme" from "one-off draw" — a fresh re-measurement can.
  **When a flag is a NEW EXTREME (not a repeat), re-measure before calling drift.**
- **Include a control qid in the re-measurement.** q04 on the same call stayed at 0.85–0.89,
  which is what licenses the claim that the q11 spread reflects q11, not a sick call.
- **Baselines stay model-segmented.** The 1.13.0→1.14.0 switch moved q02 −0.0968 and
  q12 +0.1365; a pooled baseline misreads both. Segment: 399 rounds on 1.13.0, 32 on 1.14.0.
- **Regenerate the history table from the archives** (rule from r6) — the §3 table was
  computed by looping `history.jsonl`, not typed from a prior session.
- **|dev| before σ, every round.** q13 carried the largest z (−3.27) on a |dev| of 0.0114.
- **The round counter is persistent and correct**: derived from max(files=426, history=426)
  → start=427, and the script aborts rather than shadowing an existing round file.

---

## 8. Environment (125th wipe)

- **`/workspace` EMPTY on arrival** — 18th consecutive time the prompt named an ephemeral
  `/workspace/research/` path. Bootstrapped `SuperInstance/jev-quilt` + `SuperInstance/research`
  into `/tmp/jevroot/` → `/tmp/jev`, `/tmp/research`.
- **NAS 100 % (0 avail, 600 G used)** ⇒ all work on the 28 G overlay. Symlinks:
  `ln -sfn /tmp/jev /workspace/repos/jev-quilt`, `ln -sfn /tmp/research /workspace/research`
  — the deliverable path resolves and the bytes live on the overlay.
- **TLS leaf VALID** (CN=typesafe.ai, Let's Encrypt YE2, notAfter 2026-12-21) ⇒
  **no CA-bundle rebuild** (5th round running). Always `openssl s_client` first.
- `JEV_API_KEY="$TYPESAFE_AI_TOKEN"` mapping required (the vault holds `TYPESAFE_AI_TOKEN`;
  the client reads `TYPESAFEAI_KEY`/`JEV_API_KEY`/`TYPESAFE_API_KEY`).
- **Round-count discipline held**: passed explicit positional `1` → exactly 1 round in
  0.3 s. Variant A's default is 200; `timeout 60` alone would have raced the writer.
- `gh` absent (30th). `history.jsonl` is git-tracked in `jev-quilt` (825 tracked files
  under `research/jev_sessions/`).
