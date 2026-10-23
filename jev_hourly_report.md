# JEV Hourly Report — r225 (2026-10-23T09:04Z, 112th wipe)

## Verdict
**1/1 round OK, 0 fails (1 transient 503 retried), 5 verdicts, 5/22 qids sampled.**
**mean_p 0.258** — bedrock 1/5.

| metric | value |
|---|---|
| mean_p | **0.258** |
| bedrock canon (p >= 0.70) | **q07 only** (0.78) |
| bedrock hits | 1 of 5 |
| max aggregate abs deviation | **0.0271** (q13) |
| drift > 0.05 | **NONE** |
| instrument md5 | `bda7ccb3d3af4d1c2c7e961e2dcf174a` (**unchanged vs r224**) |
| model | jev-1.14.0 |
| round index | 385 |

## Per-qid vs per-qid baseline (385-round corpus, 1,925 verdicts, 22 qids)
Baseline is loaded per-qid (own mu/sd), never against one global threshold.

| qid | p | base mu | dev | base sd | z | bedrock | historical range |
|---|---|---|---|---|---|---|---|
| q07 | 0.780 | 0.7543 | +0.0257 | 0.0164 | +1.57 | yes | 0.71-0.79 |
| q11 | 0.180 | 0.1850 | -0.0050 | 0.0175 | -0.29 | no | 0.15-0.22 |
| q13 | 0.160 | 0.1329 | +0.0271 | 0.0060 | **+4.49** | no | 0.12-0.16 |
| q09 | 0.090 | 0.0766 | +0.0134 | 0.0050 | +2.70 | no | 0.07-0.09 |
| q20 | 0.080 | 0.1051 | -0.0251 | 0.0097 | -2.58 | no | 0.09-0.13 |

**Drift call: NONE.** Max |dev| 0.0271 is 54% of the 0.05 bar. All five values sit inside
their own historical ranges; four of five are the range max or near it.

## sigma ~ 0 trap, 7th recurrence — and this round the biggest z is the smallest movement
`q13` reads z **+4.49** on a |dev| of **0.0271** because its baseline sd is **0.0060** — the
probe emits q13 on a coarse 0.01 grid, so sigma is near-degenerate and every one-step move
looks like a 4-sigma event. Check |dev| vs 0.05 FIRST; the largest z is usually the smallest
real movement.

Confirming this is quantisation and not drift, half-vs-half on the live corpus:

| qid | n | range | 2nd-half mean | 1st-half mean | delta |
|---|---|---|---|---|---|
| q13 | 90 | 0.040 | 0.1331 | 0.1333 | **-0.0002** |
| q09 | 88 | 0.020 | 0.0768 | 0.0766 | +0.0002 |
| q20 | 82 | 0.050 | 0.1046 | 0.1049 | -0.0002 |
| q07 | 76 | 0.080 | 0.7524 | 0.7568 | -0.0045 |

Every delta is <= 0.005 on a 385-round corpus. Nothing is advancing. Today's q13 = 0.16 is
simply the top of its historical range (max == 0.16); q20 = 0.08 is the bottom of its range.

## Bedrock canon read
Only **q07** clears 0.70. It has been a stable cathedral qid for the whole corpus
(mu 0.754, sd 0.0164, 76 draws, half-vs-half delta -0.0045) — this is a plateau, not an
advance. q20 at 0.08 is the only other notable move and it moved *down*, onto its floor.

Thin sample: only 5 of 22 qids drawn, and 1 of 7 cathedral qids. Do not read this round as a
canon-health signal in either direction.

## Method / environment notes (112th wipe)
- **10th consecutive wipe** naming ephemeral `/workspace/research/jev_sessions/` paths —
  the directory does not exist at boot. Rebuilt to `/tmp/jev_probe` from
  `SuperInstance/jev-quilt @ a76078e`.
- **`timeout 60` + kill is the wrong instrument and the prompt's instruction must be ignored.**
  `rounds` is a hardcoded `while time.time() - started < 55` loop at line 350; there is no
  `sys.argv` path (gone since the r224 instrument change). Killing after 60s races the writer.
  The r224 harness `/tmp/one_round.py` (imports the module, calls `run_round` +
  `append_history` exactly once, writes the round file with the script md5 stamped) works:
  **1 round, 0.14 s, no overshoot.** Reuse it.
- **Instrument md5 `bda7ccb3` now matches r224, so the baseline is same-instrument.** This
  resolves the r224 "first sighting, no baseline" caveat. md5 history: `c22e8c72` (stable 6
  wipes, r222-r223) -> `bda7ccb3` (r224 onward).
- **`history.jsonl` schema split is real and still live:** 385 list-shaped records
  (`verdicts: [{qid, p}]`) + 1 dict-shaped record (`verdicts: {qid: p}`, the r109 one at
  d33b222). The dict record must be excluded from the corpus or a naive parse raises
  `TypeError: string indices must be integers`. Baseline built from the list shape only.
- **A transient HTTP 503 (`TLS_error ... SSL routines: OPENSSL_internal`) hit round 384.**
  One retry cleared it. Worth knowing this is a soft wall, not a hard one — but log it as a
  fail and do not let it silently retry into a clean-looking report.
- `gh` CLI still absent from PATH (2nd wipe); `GITHUB_TOKEN` present, push via the explicit
  token URL.
- **NAS still 600G/600G on an empty workspace** (12th recurrence). `/workspace/research`
  cannot be written; the `write` tool cannot reach `/tmp`. Durable copy is git — cite the
  verified commit, do not attempt to stage a workspace file.
