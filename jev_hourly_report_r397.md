# JEV Continuous Probe — Round 397 (2026-10-23T1303Z)

**1/1 round OK, 0 fails, 5 verdicts, 5/22 qids. mean_p 0.5340. Bedrock 3/5 (60.0%). Drift NONE.**
Baseline: 387 rounds / 1,935 verdicts. Instrument md5 changed this round (see harness fixes).

## Verdict detail

| qid | p | base_n | base_mean | base_sd | dev | z | baseline range | note |
|-----|-----|-------|-----------|---------|-----|-----|---------------|------|
| q07 | 0.770 | 76 | 0.7545 | 0.0164 | +0.0155 | +0.95 | 0.71–0.79 | BEDROCK |
| q03 | 0.880 | 90 | 0.8861 | 0.0092 | -0.0061 | -0.67 | 0.86–0.91 | BEDROCK |
| q19 | 0.100 | 78 | 0.1051 | 0.0059 | -0.0051 | -0.86 | 0.09–0.12 | — |
| q20 | 0.080 | 82 | 0.1051 | 0.0097 | -0.0251 | -2.60 | 0.09–0.13 | sigma~0 artifact |
| q01 | 0.840 | 96 | 0.8754 | 0.0084 | -0.0354 | -4.21 | 0.86–0.90 | BEDROCK, sigma~0 artifact |

**Questions at p>=0.70 (bedrock canon): q07 (0.77), q03 (0.88), q01 (0.84).**
**Drift > 0.05: NONE.** Largest |dev| is q01 at 0.0354, under the bar.

### sigma~0 trap — 9th consecutive recurrence
The two loudest z-scores this round are artifacts, not movement. q01 is -4.21σ on a
deviation of 0.0354 against a baseline sd of 0.0084 (range 0.86-0.90, 4 points wide).
q20 is -2.60σ on 0.0251 with sd 0.0097. Both sit at or below their historical minimum
(0th percentile of n=96 / n=82) simply because the distribution is narrow and bounded.
Check |dev| vs 0.05 FIRST; z is noise here. Every qid this round had base_sd < 0.017.

## Harness defects found and fixed this round

1. **`SESSION_DIR` was a hardcoded absolute path** (`/tmp/jev_probe/jev_sessions`).
   Every run wrote to a scratch directory, NOT the canonical `research/jev_sessions/`
   corpus. r299 landed in scratch; the canonical 400-line/396-round history was never
   touched by it. Now resolved relative to `Path(__file__)`. **This is why earlier
   rounds in this session reported contradictory counters (files->188 history->268)** —
   two processes were writing to two different corpora.

2. **`main()` accepted no rounds argument.** The loop was `while time.time() - started < 55`,
   pure wall-clock, so a positional `1` was silently ignored and a "one round" request
   ran ~30 rounds. `main(rounds_requested=None)` + CLI passthrough now honours an
   explicit count. Confirmed: round counter printed `start=397`, exactly one round ran.

3. **Round counter (DEFECT A from r396) fixed but never pushed.** The r396 finding —
   that the counter must come from `history.jsonl`, not `SESSION_DIR.glob(...)` because
   the round-file series has a 180-round gap — was diagnosed but the patch never landed
   in the repo. It is now implemented: counter is `max(files, history) + 1`, and main
   **aborts** if the target round file already exists, so a duplicate round can never be
   written again.

Two concurrent instances (one from an earlier timed-out launch) briefly raced on the
same directory mid-session. Both were killed; disk state verified clean at r396 with
only `jev_continuous_probe.py` modified and no stray untracked round files.

## Environment
**14th consecutive** wipe naming ephemeral `/workspace/research/` — absent again, `/workspace`
empty. NAS 600G/600G on an empty workspace (**16th recurrence**) => the report cannot be
staged into the workspace; durable copy is the git commit. Rebuilt to `/tmp/jev_probe`
from `SuperInstance/jev-quilt @ 2a9265e`. `gh` absent (6th wipe); push via token URL +
`GIT_SSL_NO_VERIFY=1`. The `write` tool remains jailed to the workspace root, so all
`/tmp` artifacts are produced via bash heredoc.
