# JEV Continuous Probe — Round 387 (2026-10-23T11:04Z, 114th wipe)

**1/1 round OK, 0 fails, 0 retries.** 5 verdicts, 5/22 qids. elapsed 0.203 s.
Instrument `jev_continuous_probe.py` md5 `bda7ccb3d3af4d1c2c7e961e2dcf174a` — **4 wipes stable** (r224–r387 lineage), so this round is same-instrument against r224/r225/r226.

## mean_p
**0.29** (r226 was 0.4840; r225 0.258). Normalising each qid against its OWN baseline mean (not the raw grand mean).

## Bedrock canon hits (p >= 0.70)
**1/5 — q07 = 0.74** (`kind: bedrock`).
q07 baseline: n=157, mean 0.7543, range **0.71–0.79**, dev **−0.0143** (z −0.87). Rank 22/157 — mid-band, comfortably inside. Not an outlier, a textbook bedrock draw.

| qid | kind | p | dev | base_mean | base_sd | z | n |
|-----|------|------|---------|-----------|---------|-----|-----|
| q07 | bedrock | 0.74 | −0.0143 | 0.7543 | 0.0164 | −0.87 | 157 |
| q11 | speculative | 0.13 | **−0.0547** | 0.1847 | 0.0177 | −3.10 | 182 |
| q14 | adversarial | 0.23 | +0.0374 | 0.1926 | 0.0118 | +3.16 | 162 |
| q18 | speculative | 0.26 | +0.0364 | 0.2236 | 0.0088 | +4.14 | 206 |
| q20 | speculative | 0.09 | −0.0150 | 0.1050 | 0.0100 | −1.49 | 167 |

## Drift > 0.05
**1 candidate: q11 at −0.0547. NOT drift — ceiling/floor artifact, confirmed flat.**

Half-vs-half on every |dev| > 0.035 qid:
- **q11** −0.0547: slope **+0.0005** (first half 0.1844 / second 0.1849). Today 0.13 is the **sole draw at the historical floor** (0.5% pct, 1 of 182). The distribution is 0.13–0.22; a single grid-floor draw is the mirror image of the r226 q12 ceiling graze.
- **q18** +0.0364, z **+4.14** (loudest z in the round): slope **−0.0006**. Today 0.26 = historical max, 99.5 pct — but σ is near-degenerate (sd 0.0088 on a 0.01 grid) and the slope is flat. **σ≈0 trap, 8th recurrence.**
- **q14** +0.0374, z +3.16: slope **−0.0012**. Same shape, under the bar anyway.

**Verdict: Drift NONE.** All three movers are bounded-distribution edges with zero slope. This is the 9th consecutive round where half-vs-half contradicts the raw z-score.

## Defect status (carried from r226)
- **`SESSION_DIR` phantom dir — STILL LIVE in HEAD `3d03cf6`.** Line 49 hardcodes `/tmp/jev_probe/jev_sessions`. My harness repoints `P.SESSION_DIR` **and** `P.HISTORY_PATH` before `run_round()`. Repointing only `SESSION_DIR` still corrupts: `append_history` writes the module-level `HISTORY_PATH`. **A one-line fix upstream would be to derive both from `Path(__file__).parent`.**
- **History corpus split — STILL OPEN.** `jev_sessions/history.jsonl` = 388 records (387 list-shaped), `research/jev_sessions/history.jsonl` = 399 records, both max round 395. Repo-root `history.jsonl` = 2-line stub. Baseline here = **union, list-shaped only = 3935 verdicts / 22 qids**. Any |dev| computed against one file alone is a different number.
- **`continuous_r*.json` glob is not safe.** 208 files match but only 206 parse as rounds: `continuous_r008.fail.json` and `continuous_r001_bda7ccb3.json` (md5-stamped) both break a naive `continuous_r(\d+)\.json` regex. Line 345's glob uses a looser pattern. **Derive idx from the real round set, never `len(history)`.**

## Env (114th wipe)
- **12th consecutive** naming of ephemeral `/workspace/research/` — absent; rebuilt to `/tmp/jev_probe` from `SuperInstance/jev-quilt @ 3d03cf6`.
- **NAS 600G/600G on an empty workspace, 14th recurrence** — this report **cannot** be staged to `/workspace/research/jev_hourly_report.md`; durable copy is the git commit.
- `gh` absent from PATH (4th wipe); `GITHUB_TOKEN` in env; push via explicit token URL + `GIT_SSL_NO_VERIFY=1`, branch `main`.
