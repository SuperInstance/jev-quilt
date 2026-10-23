# JEV Continuous Probe — hourly report r224

**Run:** 2026-10-23T08:03:58Z · **1 round, 0 fails, 5 verdicts, 5/22 qids**
**Instrument:** `jev_continuous_probe.py` md5 `bda7ccb3d3af4d1c2c7e961e2dcf174a`
**Model:** `jev-1.14.0` · round elapsed 0.177 s · harness elapsed 0.2 s

## Headline
- **mean_p = 0.370** (archive grand mean over 374 rounds = 0.3805)
- **Bedrock canon (p >= 0.70): 2/5** — `q08` 0.88, `q05` 0.81
- **Drift > 0.05: NONE.** max aggregate |dev| = **0.0414** (`q05`)

## Verdicts vs 374-round baseline
| qid | kind | p | base_mu | base_sd | dev | z |
|---|---|---|---|---|---|---|
| q15 | adversarial | 0.03 | 0.0252 | 0.0050 | +0.0048 | +0.95 |
| q08 | bedrock | 0.88 | 0.8996 | 0.0087 | -0.0196 | -2.26 |
| q10 | speculative | 0.05 | 0.0669 | 0.0050 | -0.0169 | -3.38 |
| q05 | bedrock | 0.81 | 0.8514 | 0.0100 | -0.0414 | -4.15 |
| q20 | speculative | 0.08 | 0.1054 | 0.0097 | -0.0254 | -2.62 |

**Read the |dev| column before the z column.** Four of five verdicts carry |z| > 2 and
none of them is drift. `q05` is the loudest z in the round (-4.15) on the *smallest*
real movement (-0.0414) — one quantisation step on a 2-decimal endpoint against a
baseline sd of 0.0100. The sigma-near-zero trap, 6th recurrence.

## ⚠ Instrument changed — comparison is cross-version
The archive contains three distinct harness versions and **tonight's matches none**:

| round file | script_md5 |
|---|---|
| r192–r200 | no md5 field (pre-stamping) |
| r193 | `aa77a62e68cb4d93773a490c5d54ddc2` |
| r206, r383 | `d0a7291b2e070ce717b9b7c7417401a2` (the "unrecoverable baseline") |
| **tonight r001** | **`bda7ccb3d3af4d1c2c7e961e2dcf174a`** |

`bda7ccb3` is a **first sighting** — no prior round carries it, so there is no
same-instrument baseline. The baseline above is 374 rounds of `d0a7291b`/`aa77a62e`/
unstamped history. HEAD commit `d33b222` independently flags this ("instrument
changed, baseline md5 d0a7291b unrecoverable, schema split, round-counter collision").
The dev table is therefore **indicative, not like-for-like**. Tonight's own
`script_md5` field is the receipt that makes the break visible rather than silent.

## Three real improvements in the new harness
1. **Round counter derived from existing files**, not `len(history)` — fixes the
   r001-shadowing bug where a lost NAS history restarted the counter and every
   pre-wipe r001 was shadowed forever.
2. **`script_md5` stamped into every round file** — the exact mechanism that made
   the version break above detectable instead of a silent drift artifact.
3. **Hard `USER_AGENT`** on the JEV request.

## Regression: the one-round workaround is gone
`sys.argv` handling **no longer exists**. The round count is a hardcoded
`while time.time() - started < 55` loop — "one round" cannot be requested from the
CLI, and `timeout 60` + kill races the writer (that path flushed **154 rounds** in
~60 s on the r221 wipe). This round was produced by a thin harness importing the
script's own `run_round`/`append_history` and calling them exactly once: same
instrument, 1 round, 0.2 s, no overshoot. Worth folding back in as an argument.

## Environment (111th wipe)
- **9th consecutive** wipe naming ephemeral `/workspace/research/jev_sessions/`
  paths that do not exist. Rebuilt into `/tmp` from `SuperInstance/jev-quilt @ d33b222`.
- **NAS account quota still exhausted** — 600G/600G on an *empty* workspace,
  `/workspace` at 100% with 0 avail. 10th recurrence. `/tmp` unaffected (1%).
  Report staged in `/tmp` and pushed to git; the workspace copy cannot be staged.
- `git clone` needs `GIT_SSL_NO_VERIFY=1`; token URL form works.
