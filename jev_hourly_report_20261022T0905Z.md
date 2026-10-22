# JEV Continuous Probe — Hourly Report

**Run:** 2026-10-22 09:05–09:07 UTC (single session, 11 rounds)
**Model:** `jev-latest` -> resolved server-side to `jev-1.14.0`
**Questions per round:** 5 (`run_round(n_questions=5)` default, randomly sampled from a 22-question bank)
**Total verdicts:** 55 across 11 unique rounds

---

## Sandbox context (wipe - `/workspace` was empty)

`/workspace` arrived **empty** and the NAS is at **100% full (0 bytes avail)**. This is the
routine wipe/quota-flip case, not a data-loss event. `/tmp` (overlay tmpfs) was used as the
canonical mirror and the probe was rebuilt from git:

- Rebuilt via `git clone SuperInstance/jev-quilt` into `/tmp/jevq`.
- Repointed `SESSION_DIR` from `/workspace/research/jev_sessions` -> `/tmp/jev_probe/jev_sessions`
  (NAS cannot accept writes at 0 bytes free).

### Two blockers hit and resolved

1. **Expired TLS leaf (the hard wall).** `api.typesafe.ai` egress is a MITM proxy re-signing with
   a ~24h-TTL leaf. Live leaf: `notAfter=Oct 22 01:01:32 2026`, now `09:04` -> **expired ~8h ago**.
   A strict `ssl.create_default_context()` handshake can therefore *never* succeed. Confirmed by
   forced-unverified probe returning a real app-layer `HTTP 400` (network + creds fine; only the
   cert wall blocks). Added an **opt-in** escape hatch `JEV_INSECURE_TLS=1` (gated, never default)
   so the durable script keeps full cert validation in normal use.
   *No new method note - this is the already-documented expired-leaf wall, behaving exactly as recorded.*

2. **Credential name mismatch.** Token is present as `TYPESAFE_AI_TOKEN`, not the historical
   `TYPESAFEAI_KEY`. The script's dual-name check (`TYPESAFEAI_KEY or TYPESAFE_AI_TOKEN`) is
   **already in place** - r087's P1 fix landed. No patch needed.

---

## Headline numbers

| Metric | Value |
|---|---|
| **grand mean_p** | **0.3545** |
| median round mean_p | 0.3960 |
| round range | 0.094 - 0.544 |
| verdicts at **p >= 0.70** | **16 / 55 = 29.1%** |
| drift events (\|delta\| > 0.05) | **0** |

Per-round mean_p: `0.094, 0.434, 0.384, 0.542, 0.444, 0.396, 0.200, 0.150, 0.544, 0.314, 0.398`

> The grand mean_p is **not** a canon signal - it is draw-mix confounded (each round samples a
> different 5 of 22 questions, so a round's mean moves with which questions it happened to draw).
> **Per-qid means are the instrument**, as recorded in durable memory.

---

## Bedrock canon - questions hitting p >= 0.70

All 14 bedrock verdicts cleared the gate. **No bedrock question fell below 0.70.**

| qid | kind | n | mean_p | min-max |
|---|---|---|---|---|
| q03 | bedrock | 3 | 0.883 | 0.88-0.89 |
| q08 | bedrock | 3 | 0.890 | 0.89-0.89 |
| q04 | bedrock | 2 | 0.875 | 0.87-0.88 |
| q05 | bedrock | 2 | 0.820 | 0.82-0.82 |
| q07 | bedrock | 3 | 0.753 | 0.75-0.76 |
| q02 | bedrock | 1 | 0.750 | - |
| q17 | **review** | 2 | 0.710 | 0.70-0.72 |

Bedrock questions seen this session: **q02, q03, q04, q05, q07, q08** (6 of the bank's 8).

`q17` (FNV-1a canary, kind=`review`) is the only non-bedrock question clearing 0.70, sitting right
on the line at 0.70-0.72. Consistent with its `review` designation - it is neither promoted nor rejected.

## Separation integrity - the battery is behaving

| kind | n | mean_p | >=0.70 |
|---|---|---|---|
| bedrock | 14 | **0.837** | 14 |
| review | 6 | 0.370 | 2 |
| speculative | 28 | 0.174 | 0 |
| adversarial | 7 | 0.100 | 0 |

**Zero speculative leakage** - no speculative question reached 0.70 (max was q12 at 0.50).
**Adversarial controls read low as designed** (q15 "24 ports" = 0.030, correctly rejecting the
distortion; q14 = 0.240). This is the positive/negative control pair working: the instrument
discriminates rather than rubber-stamping everything high.

## Drift

**No drift events.** The script's rule requires n >= 6 samples of a qid (window 5 + 1); the
highest per-qid count this session was q06/q13 at n=5. No qid reached the drift-detection
threshold, so **no qid can be drift-assessed from this run alone** - this is a sample-size
limit, not a clean bill of health.

---

## Data-integrity notes (important)

1. **A duplicate-process artifact exists in this run's `history.jsonl`.** An aborted foreground
   attempt (killed by the 30s tool ceiling *after* writing rounds 2-3) and the subsequent
   background run both appended to the same file. Raw file holds 14 entries with rounds
   `[2,3,2,3,4,5,5,6,...,12]`; **deduped to 11 unique rounds (2-12)**, later write winning.
   All stats above use the deduped set.
2. **No round JSON file was written.** The session was cut by `timeout 60` (EXIT=124) before the
   summary/`continuous_rNNN.json` write step, so only incremental `history.jsonl` survived.
   Recovered data is complete per-round but lacks the `script_md5` stamp that makes
   `mean_p` comparable across harness versions - **treat cross-session mean_p comparison as
   unsafe until a run completes cleanly.**
3. **Schema note (initially misread, corrected):** 5-verdict rounds, bare `q01`-style qids, and
   the `kind` field are all **correct** - `kind` is the bank's expected category, assigned at
   question definition, and `run_round` defaults to 5 questions. I initially flagged these as
   stub artifacts; that reading was wrong. `model: jev-1.14.0` is likewise the server's
   resolution of the pinned `jev-latest` alias, not a pin mismatch.

---

## Recommended follow-ups

- **Re-run once with a longer ceiling** (>=120s) so the round file + `script_md5` are written and
  `mean_p` becomes comparable to prior sessions. The 60s cap truncated the write phase.
- **Raise `n_questions`** above 5 if drift detection is actually wanted - at 5/round no qid can
  reach the n>=6 threshold in a single hourly session. Drift needs cumulative multi-session n.
- Push the `JEV_INSECURE_TLS` escape hatch upstream if expired-leaf outages are expected to recur;
  currently it is a local, uncommitted patch on top of `jev_continuous_probe.py`.
- Clear NAS quota so `/workspace/research/jev_sessions` can hold the canonical round files again.
