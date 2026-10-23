# JEV continuous probe — r398 (2026-10-23T14:03Z)

**1/1 round OK (r398), 0 fails, 5 verdicts, 5/22 qids. mean_p 0.4800, bedrock 2/5.**
**Drift: 1 event — q12, |dev| +0.1306. Cathedral 7/7 @ 100%, intact.**

## Round r398

| qid | kind | p | base mean ± sd (n) | dev | z | percentile |
|-----|------|------|---------------------|------|------|-----------|
| q08 | bedrock | 0.89 | 0.8995 ± 0.0086 (79) | −0.0095 | −1.11 | 6% |
| q17 | review | 0.70 | 0.7025 ± 0.0140 (79) | −0.0025 | −0.18 | 27% |
| **q12** | speculative | **0.50** | 0.3694 ± 0.0330 (88) | **+0.1306** | **+3.96** | **99%** |
| q13 | speculative | 0.17 | 0.1336 ± 0.0076 (91) | +0.0364 | +4.76 | 99% |
| q06 | speculative | 0.14 | 0.0995 ± 0.0063 (85) | +0.0405 | +6.42 | 99% |

**mean_p 0.4800** vs previous-12-round mean 0.4152 (dev +0.0648 — *not* a per-qid drift, just draw mix:
only 2 of 7 cathedral qids were drawn).

## Bedrock canon hits (p ≥ 0.70)

- **q08 = 0.89** ✅
- **q17 = 0.70** ✅ (at threshold; kind=review, 62/84 lifetime hits)

Cathedral integrity across the full corpus — all 7 bedrock qids at a **100% hit rate**, none disturbed:

    q01 0.8751 · q02 0.8247 · q03 0.8863 · q04 0.8889 · q05 0.8513 · q07 0.7543 · q08 0.8996

## Drift: q12 is a REAL excursion, not the σ≈0 trap

This is the important call of the round, and it is deliberately *not* the usual σ≈0 false alarm:

- |dev| **0.1306** is 2.6× the 0.05 threshold — the rule is |dev| first, z second, and this clears on |dev|.
- q12's distribution is **rock-stable across three eras**: early 0.3679, mid 0.3679, recent-29 0.3679. A flat baseline that a single draw jumps off is a real movement, not noise.
- **p=0.50 has occurred exactly 1 time in 88 draws — this one.** Prior max was 0.44; pre-r398 draws ≥0.50: **0/87**.
- z is +3.96 *and* |dev| is large, so the usual "largest z is often the smallest real movement" trap does not apply. (The two high-z spec rows q06 +6.42 / q13 +4.76 ARE that trap — |dev| 0.04 and 0.036, both under threshold.)

**Interpretation:** q12 is `kind=speculative`, 0/93 lifetime hits. A single upward excursion on a speculative
question does not promote it — the promotion gate is p>0.7 sustained, and this is one draw. Flag for
watch: if q12 reads ≥0.45 on the next two draws, treat as a genuine baseline shift rather than coincidence.

## Corpus state

- rounds **389** distinct (history 402 lines — duplicate-tail records present; first-occurrence-wins used)
- verdicts **1,945**, qids **22**, grand mean_p **0.3808**
- Round files present: 207. File series is still incomplete vs history (known 180-round gap) — counter
  correctly derived from `max(files, history)`.

## Environment

- **15th consecutive wipe** — `/workspace/research/` named but absent; rebuilt from `SuperInstance/jev-quilt @ c81f27b`.
- **Cert-anchor wall (not an outage):** python `urlopen` to `api.typesafe.ai` died with
  `SSLV3_ALERT_HANDSHAKE_FAILURE` while `curl` returned **HTTP/2 200** on the same host — the signature of
  the gateway-only trust anchor. Rebuilt the 289-cert combined bundle; health → 200. Generation side clean.
- **NAS 600G/600G (100%) on an empty workspace** — 17th recurrence. The `write` tool cannot stage into the
  workspace, so the durable copy is the git commit (this report travels with it).
- r229 fixes verified present in the shipped script: `main(rounds_requested=None)`, positional `sys.argv[1]`
  passthrough, `max(files, history)` counter, clobber guard. Positional `1` produced **exactly one** round.
- script md5 `3a255fa4642ec4a83173ab04d773d485` (r229 script, unchanged).
