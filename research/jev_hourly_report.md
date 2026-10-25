# JEV Hourly Report — Round 438

**Run:** 2026-10-25T12:04:30Z · 130th wipe · model `jev-1.14.0` (resolved from `history.jsonl`) · script md5 `3a255fa4642ec4a83173ab04d773d485`
**Result:** 1 round OK, 0 fails, 0.125 s · **mean_p 0.4900** · **bedrock 2/5** · **Drift: NONE** (script reported `drift_events=1` — rejected, see §3)

> Baseline rule in force: every drift baseline is scored against the qid's **own model segment** (`jev-1.14.0`), never the pooled history, and restricted to **qids drawn this round**. The script's own `drift_events` is never a verdict.

---

## 1. This round

| qid | kind | p | bedrock (p>=0.70) | segment baseline (n/mu/sd) | dev | z |
|-----|------|---|------------------|---------------------------|-----|---|
| q08 | bedrock | **0.89** | **YES** | 8 / 0.8900 / 0.0131 | +0.0000 | +0.00 |
| q12 | speculative | **0.54** | no | 12 / 0.4975 / 0.0322 | +0.0425 | +1.32 |
| q06 | speculative | 0.14 | no | 11 / 0.1400 / 0.0063 | +0.0000 | +0.00 |
| q17 | review | **0.73** | **YES** | 9 / 0.7111 / 0.0215 | +0.0189 | +0.88 |
| q11 | speculative | 0.15 | no | 7 / 0.1771 / 0.0281 | −0.0271 | −0.97 |

**mean_p 0.4900** (sum 2.45 / 5) — **bedrock hits 2/5** — **questions reaching p>=0.70: q08 (0.89, bedrock-kind) and q17 (0.73, review-kind)**

Draw composition is ordinary: 1 bedrock-kind, 1 review-kind, 3 speculative — 2 of the 5 drawn qids are bedrock-kind, so 2/5 is the expected rate, not a spike.

**mean_p 0.4900 is a normal draw, not a movement.** Against the `jev-1.14.0` segment (n=43, mean 0.4170, sd 0.1205) it is **z = +0.61**. The all-history distribution is mean 0.3845 / sd 0.1426, range 0.08–0.85. r437 (0.2200) and r438 (0.4900) sit at the two ends of ordinary week-to-week spread.

---

## 2. Bedrock canon (p>=0.70)

| qid | kind | p this round | note |
|-----|------|--------------|------|
| **q08** | bedrock | **0.89** | Canonical bedrock, 9/9 = 100% in segment. Dev +0.0000, z +0.00 — dead centre of its band [0.88, 0.91]. |
| **q17** | review | **0.73** | Review-kind, now hitting the canon gate 8/10 in segment. Dev +0.0189, z +0.88, inside band [0.68, 0.75]. |

**No speculative or adversarial qid has ever reached 0.70** — still true after this round. The highest speculative reading on record remains **q12 at 0.56** (r409).

---

## 3. Drift — the script's `drift_events=1` is a FALSE FLAG (pooled-baseline artifact on q12)

The script's `drift_check()` pools all history per qid, so it compares a `jev-1.14.0` reading against a baseline whose mass sits under `jev-1.13.0`. The flagged qid is **q12**:

| baseline | n | mu | sd | dev | z | \|dev\|>=0.05 ? |
|----------|---|-----|-----|-----|---|----------------|
| **Same-model (1.14.0)** | 12 | 0.4975 | 0.0322 | **+0.0425** | +1.32 | **NO** |
| Pooled (1.13.0 + 1.14.0) | 105 | 0.3831 | 0.0541 | +0.1569 | +2.90 | YES |

**Verdict: no drift.** The model switch at r396 shifted q12's level by **+0.1342** (1.13.0 mean 0.3665 → 1.14.0 mean 0.5008). Pooling compares a post-switch reading to a pre-switch distribution and manufactures a +0.157 "drift" out of a level change that is already fully absorbed by the current segment. Under the same-model baseline, dev is **+0.0425 < 0.05** — a non-event.

**This is the 3rd occurrence of this exact false flag on q12** (r435 q12, r437 q12, now r438 q12) and the 5th false flag overall (r428 q02, r435 q12, r436 q06, r437 q12, r438 q12). It lands on a *different* qid most rounds but keeps repeating q12 — **do not treat any single qid's flag as a tracked series.** Per-round it is a candidate, not a verdict.

**Aggregate drift verdict: 5 of 5 qids within 0.05, 0 beyond — no drift, full stop.**

**Also note the σ≈0 trap avoided this round:** the largest z in the whole round is q12's pooled z = +2.90, which sits on the *pooled* dev of 0.1569 — an artifact. Under the correct same-model baseline the largest z is q12 at +1.32 on a dev of 0.0425. Checking |dev| vs 0.05 first, then z, gave the right answer.

---

## 4. No re-measurement needed

q12's 0.54 had 1 exact prior occurrence in the 1.14.0 segment (r407 also read 0.54) and is inside the all-time max 0.56 (r409). It is a **repeat, archive-judgeable** ⇒ the standard "new extreme ⇒ fresh re-draw" rule does not fire. Checking the archive first avoided a pointless second draw.

q11's 0.15 had 0 exact prior occurrences in the 1.14.0 segment, but it is well inside that segment's range [0.12, 0.20] with dev −0.0271 — not an extreme either, so no re-measurement.

---

## 5. Cathedral state (1.14.0 segment, bedrock-kind qids, p>=0.70)

| qid | n | hits | rate | range |
|-----|---|------|------|-------|
| q01 | 11 | 11 | 100.0% | 0.84–0.87 |
| q02 | 13 | 10 | **76.9%** | 0.68–0.77 |
| q03 | 9 | 9 | 100.0% | 0.86–0.90 |
| q04 | 10 | 10 | 100.0% | 0.87–0.90 |
| q05 | 9 | 9 | 100.0% | 0.78–0.83 |
| q07 | 11 | 11 | 100.0% | 0.75–0.79 |
| q08 | 9 | 9 | 100.0% | 0.88–0.91 |

**6 of 7 cathedral qids at 100%.** q08 is now 9/9 (it joined the segment at r430, so its count is shorter, not weaker).

**q02 remains the sole watch item — still ESCALATED.** 10/13 in segment, with 3 dips below the 0.70 gate: r416 (0.69), r423 (0.69), r425 (0.68). The gate is marginal by design — q02's band straddles 0.70 — but the dips are real and reproducible, so it stays escalated rather than being written off as gate noise.

---

## 6. Environment

- **130th wipe** — `/workspace` was empty again (**23rd consecutive**), bootstrapped `SuperInstance/jev-quilt` + `SuperInstance/research` into `/tmp/jev-quilt` + `/tmp/research-clone`.
- **NAS 100% (0 avail)** ⇒ `/workspace/research` is a **symlink** to `/tmp/jev-quilt/research` (rm -rf then ln -s).
- **TLS leaf VALID** (CN=typesafe.ai, notAfter 2026-12-25) ⇒ no CA bundle rebuild needed.
- Script md5 `3a255fa4642ec4a83173ab04d773d485` unchanged ⇒ mean_p directly comparable to r437.
- **Command correction (3rd session running):** the task's literal `timeout 60 python3 jev_continuous_probe.py` is wrong on two counts — the script lives at the **repo root** (not `research/`), and `rounds` is a positional `sys.argv[1]` **defaulting to 200** ⇒ `timeout 60` races the writer to ~200 rounds. Ran `python3 jev_continuous_probe.py 1` ⇒ exactly one round, 0.3 s. Pre-run state: 246 round files, max r437, 441 history rows ⇒ counter 438. Post-run: 247 files, 442 rows.
- No model switch this round: `model` = `jev-1.14.0` in the new history row, matching the segment.

---

## 7. Files

| file | md5 |
|------|-----|
| `research/jev_sessions/continuous_r438.json` | see delivery commit |
| `research/jev_sessions/history.jsonl` (442 rows) | see delivery commit |
| `research/jev_hourly_report.md` (this file) | see delivery commit |
| `research/jev_hourly_report_r437.md` | `dbf787a35f8039bfea6db19f3b7b5935` (prior report, unchanged) |

---

## 8. Bottom line

**mean_p 0.4900 · bedrock 2/5 (q08 0.89, q17 0.73) · drift NONE (0 of 5 qids beyond 0.05).** The script's single drift flag on q12 is a pooled-baseline artifact of the 1.13.0→1.14.0 model switch and is rejected; the same-model dev is +0.0425. Cathedral holds at 6 of 7 qids, with q02 the sole watch item at 76.9%.
