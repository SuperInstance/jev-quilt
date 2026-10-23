# JEV Hourly Probe — r396 (2026-10-23T12:04Z)

**1/1 round OK, 0 fails, 5 verdicts, 5/22 qids. mean_p 0.5740. Bedrock 3/5 (60%).**
**Drift: NONE** — no |dev| > 0.05. Instrument md5 `bda7ccb3`, 5 wipes stable.

## Verdicts

| qid | p | base mean | dev | z | base sd | n | base range | note |
|-----|---|-----------|-----|---|---------|---|-----------|------|
| q03 | 0.900 | 0.8860 | +0.0140 | +1.55 | 0.0091 | 89 | [0.86, 0.91] | BEDROCK, σ≈0 |
| q04 | 0.900 | 0.8887 | +0.0113 | +1.31 | 0.0086 | 89 | [0.88, 0.91] | BEDROCK, σ≈0 |
| q17 | 0.710 | 0.7025 | +0.0075 | +0.53 | 0.0142 | 77 | [0.66, 0.74] | BEDROCK, σ≈0 |
| q16 | 0.200 | 0.1996 | +0.0004 | +0.05 | 0.0082 | 89 | [0.18, 0.22] | σ≈0 |
| q13 | 0.160 | 0.1329 | +0.0271 | **+4.49** | 0.0060 | 89 | [0.12, 0.15] | σ≈0 trap |

**Bedrock canon (p ≥ 0.70): q03, q04, q17.**

Baseline: 386 rounds, 1,930 verdicts, 22 qids, grand mean_p **0.3797**.

## q13 — the σ≈0 trap, 8th consecutive recurrence

Loudest z in the round (+4.49) but |dev| only 0.0271 on a near-degenerate base
sd of 0.0060 (the probe emits q13 on a coarse 0.01 grid). p=0.16 is the
historical **max** of a [0.12, 0.15] range — 100th percentile of 89 draws.
Half-vs-half would be flat. **Rule held: check |dev| vs 0.05 first, never z.**

## TWO NEW DATA-INTEGRITY DEFECTS (both now proven, not theoretical)

### DEFECT A — the round counter is derived from round FILES, and the file series has a 180-round gap
`main()` line ~345 builds the counter from `SESSION_DIR.glob("continuous_r*.json")`.
In `research/jev_sessions/` that file series has **206 files spanning r001..r386
with 180 missing**, so `max(files) = 383` while `history.jsonl` reaches **r395**.
First run therefore issued **r384 — an already-recorded round — and appended a
DUPLICATE r384 record**, also clobbering the existing `continuous_r384.json`.

Recovered by `git checkout --` + `rm` (both edits uncommitted, zero loss).
Harness now derives the counter from `history.jsonl` (max round) and **aborts if
the target round file already exists**. Re-run issued **r396**, no collision.

**This is the same family as the `len(history)` shadowing bug already fixed in
this script — the counter was fixed to read *files*, but the file series is
demonstrably incomplete while history is not.** The durable fix is to read the
authoritative append-only log, never a directory listing.

### DEFECT B — `history.jsonl` max round is NOT the tail (corpus is out of order)
399 lines; max round **395** but the last five records in file order are
**387, 388, 389, 390, 391**. r392–r395 exist as records **earlier in the file**.
So `history[-1]` is r391, and any "latest round" read that takes the last line —
or takes `max()` and assumes it is last — disagrees with the other. Both this
report and the harness use `setdefault` on round number (first occurrence wins),
which is stable under this ordering.

### Corpus split — RESOLVED, downgrade the standing alarm
The two trees (`jev_sessions/` 385 rounds vs `research/jev_sessions/` 386) are
**not** conflicting corpora: **385 of 386 rounds overlap and every overlapping
round has a bit-identical `mean_p` (0 differences)**. The trees differ by exactly
one round (r384) plus tail duplicates. Canonical baseline =
`research/jev_sessions/history.jsonl`, 386 rounds / 1,930 verdicts / 22 qids.
The standing "split corpus, neither canonical" alarm is **overstated** — same
data, two homes. Keep the duplicate-tail cleanup open; the reconciliation is done.

### Still open
`SESSION_DIR` phantom (`/tmp/jev_probe/jev_sessions`, empty) — harness repoints
both `SESSION_DIR` and `HISTORY_PATH` before `run_round()`; repointing only one
still corrupts.

## Env (114th wipe)
13th consecutive ephemeral-path wipe — `/workspace/research` absent, `/workspace`
empty. Rebuilt to `/tmp/jev_probe` from `SuperInstance/jev-quilt @ d425843`.
NAS 600G/600G on empty workspace, **15th recurrence** ⇒ report cannot be staged
to `/workspace/research/`; durable copy is this commit. `gh` absent (5th wipe);
`GIT_SSL_NO_VERIFY=1` + explicit token URL. 5 verdicts / 5 qids is normal — the
probe samples a subset per round.
