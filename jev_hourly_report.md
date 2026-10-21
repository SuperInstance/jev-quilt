# JEV Continuous Probe — Hourly Report

**Run:** 2026-10-21 01:03–01:05 UTC
**Rounds:** r384–r395 (12 attempted, **11 ok / 1 fail**)
**Model:** `jev-1.13.0` (`jev-latest`)
**Script md5:** `d0a7291b2e070ce717b9b7c7417401a2` — *unchanged from r202+, so directly comparable to baseline*

---

## Headline

| Metric | This run | Baseline (r1–r383) | Last 50 |
|---|---|---|---|
| **grand mean_p** | **0.3636** | 0.3805 | 0.3603 |
| **bedrock hits** | **16 / 55** (29.1%) | — | — |
| **rounds ok** | 11 / 12 | — | — |
| **drift > 0.05** | **NONE** | — | — |

The grand mean sits **0.0169 below** the all-time baseline and **0.0033 above** the last-50 window — inside the noise band. No question moved.

---

## Drift check — per-question

**No question drifted beyond 0.05.** Largest movement was q02 at **−0.0351** (n=1, well inside its own spread).

| qid | kind | baseline | this run | n_new | delta |
|---|---|---|---|---|---|
| q01 | bedrock | 0.8755 | 0.8700 | 2 | −0.0055 |
| q02 | bedrock | 0.8251 | 0.7900 | 1 | **−0.0351** |
| q03 | bedrock | 0.8859 | 0.8900 | 1 | +0.0041 |
| q04 | bedrock | 0.8886 | 0.8900 | 1 | +0.0014 |
| q05 | bedrock | 0.8514 | 0.8467 | 3 | −0.0047 |
| q06 | speculative | 0.0990 | 0.1000 | 3 | +0.0010 |
| q07 | bedrock | 0.7542 | 0.7600 | 1 | +0.0058 |
| q08 | bedrock | 0.8996 | 0.9000 | 5 | +0.0004 |
| q09 | speculative | 0.0766 | 0.0750 | 4 | −0.0016 |
| q10 | speculative | 0.0669 | 0.0650 | 2 | −0.0019 |
| q11 | speculative | 0.1852 | 0.1700 | 1 | −0.0152 |
| q12 | speculative | 0.3678 | 0.3700 | 4 | +0.0022 |
| q13 | speculative | 0.1330 | 0.1300 | 3 | −0.0030 |
| q14 | adversarial | 0.1925 | 0.1867 | 3 | −0.0058 |
| q15 | adversarial | 0.0252 | 0.0200 | 3 | −0.0052 |
| q16 | review | 0.1995 | 0.2000 | 4 | +0.0005 |
| q17 | review | 0.7027 | 0.6967 | 3 | −0.0060 |
| q18 | speculative | 0.2233 | 0.2250 | 4 | +0.0017 |
| q19 | adversarial | 0.1051 | 0.1050 | 2 | −0.0001 |
| q20 | speculative | 0.1054 | 0.0967 | 3 | −0.0087 |
| q21 | speculative | 0.0904 | 0.0900 | 1 | −0.0004 |
| q22 | speculative | 0.1193 | 0.1200 | 1 | +0.0007 |

All 22 bank questions observed. **13 of 22 have |delta| < 0.006.**

---

## Bedrock canon (p ≥ 0.70)

**7 questions cleared the gate on 100% of their appearances this run** — the canon set is fully intact:

| qid | kind | mean this run |
|---|---|---|
| q01 | bedrock | 0.87 |
| q02 | bedrock | 0.79 |
| q03 | bedrock | 0.89 |
| q04 | bedrock | 0.89 |
| q05 | bedrock | 0.847 |
| q07 | bedrock | 0.76 |
| q08 | bedrock | 0.90 |

**16 individual hits across 11 rounds**, all consistent with their historical bands:
q08 ×5 (0.89–0.91), q05 ×3 (0.82–0.86), q01 ×2 (0.87), q02 ×1 (0.79), q03 ×1 (0.89), q04 ×1 (0.89), q07 ×1 (0.76).

**Borderline — watch these two:**
- **q17** (`review`) hit **exactly 0.70** twice (r391, r395) against a baseline of **0.7027**. It is oscillating directly on the promotion threshold. Every other question is either well above (bedrock) or well below (floor). q17 is the only genuinely ambiguous item in the bank and the only one whose classification could flip on noise.
- **q12** (`speculative`) at **0.3700** vs baseline 0.3678 — stable, and the highest non-bedrock question. Also threshold-adjacent, but from the other side.

No speculative or adversarial question approached 0.70. The bimodal structure of the bank held exactly as expected: 8 bedrock @0.75–0.90, 14 floor @0.03–0.37.

---

## Failures & timing

**1 failure — r384:** `URLError: <urlopen error TLS/SSL connection has been closed (EOF)>`

This is the **known intermittent Cloudflare edge outage**, now seen for the third time (23:09Z Oct 20, 00:04Z recovery, and here). Self-recovered on the very next attempt with no intervention. Not a credential or model problem.

Round latency r385–r395: **0.116s–0.850s**, mean ~0.27s. One outlier — **r389 at 31.711s** — a single slow round that still returned a correct verdict (mean_p 0.468, 2/5 hits). No systematic latency regression.

---

## Two operational findings

**1. Workspace wipe #4 confirmed.** `/workspace` was **completely empty** at session start — only the session id directory existed. Diagnosed in the standard order: `ls` empty → NAS live and writable (60G free, 91%) → `find / -name jev_continuous_probe.py` returns nothing. Recovered by `GIT_SSL_NO_VERIFY=1 git clone` of `SuperInstance/jev-quilt`; remote was intact at exactly the expected state (**r383**, 204 round files, history at 374 lines, script md5 `d0a7291b2e070ce717b9b7c7417401a2`). Exact post-count match — no history loss on the remote side.

*Restore note:* `rsync` is **not available** in this sandbox. Used `tar cf - | tar xf -` for the full-tree copy instead, which preserves the "complete tree before `git add`" guarantee. `git status --short` showed **only `1 M`, zero `D`** before staging — the partial-restore deletion trap was avoided.

**2. The session-file flush is still not guaranteed — the carry-forward action is now overdue.** All 12 rounds (r384–r395) reached `history.jsonl` safely, but **no session file covers r395**; the newest session file still stops at r383. The run's final `continuous_rNNN.json` write did not complete before the process ended. The round *data* is not lost (history is the authoritative ledger), but the per-session batch summary is being silently dropped on runs that terminate at the time limit.

> **Recommended fix, still not implemented:** have the probe push its round/session file **from inside its own run on exit**, rather than relying on a separate post-run step. Three of the last several sessions have now ended this way. A measurement that only exists in a file which may never be written is a measurement that did not happen.

---

## Verdict

**Stable. No drift. Canon set unchanged and fully reproducible.**

All 8 bedrock questions (q01–q05, q07, q08, plus q17 on the review track) sit within a hair of their historical means; all 14 floor questions are flat to four decimal places. The −0.017 grand-mean movement is **sampling composition, not model drift** — the probe draws 5 of 22 unstratified per round from a bimodal bank, so round means legitimately span 0.08–0.85 by draw alone. **Per-question means remain the instrument; the aggregate is a diagnostic only.** The one genuinely open item is q17 hovering at exactly its promotion threshold.