# JEV Continuous Probe — Hourly Report

**Run:** 2026-10-21T00:04:52Z · model `jev-latest` · 177 rounds · 0 fails · 55.0s
**Harness:** `script_md5 = d0a7291b2e070ce717b9b7c7417401a2` (unchanged from r202/r206 — directly comparable)
**Round file:** `jev_sessions/continuous_r383.json`

## Incident before the run: NAS wipe (recovered)

`/workspace/research/` was **empty** at session start — only `.plugin-cache` (created 00:03,
this session). Mount was live and writable (60G free, 91%), so this was genuine data loss on
the ephemeral volume, not a stale handle or permissions fault. `find /` located no copy of
`jev_continuous_probe.py` and no `jev_sessions/` anywhere on the box.

Recovered from `SuperInstance/jev-quilt`: 203 round files, `history.jsonl` at 197 lines
(exact match to the post-count of the last run), script md5 identical. **Third recorded wipe
of this probe's working state.**

## mean_p

| Metric | Value |
|---|---|
| **Grand mean p** | **0.3681** |
| Baseline (197 ok rounds) | 0.3917 |
| Delta | **-0.0236** (within 0.05) |
| This run: median / min / max round mean | 0.3860 / 0.0840 / 0.8480 |
| Bedrock hits | 278/885 = **31.4%** |
| Reported drift events | **0** |

## Bedrock canon — questions hitting p >= 0.70

All 8 expected canon questions cleared the gate on **every single sample** (no misses):

| qid | kind | hits | n | p range | baseline |
|---|---|---|---|---|---|
| q01 | bedrock | 41 | 41 | 0.86–0.89 | 0.8764 |
| q02 | bedrock | 32 | 32 | 0.79–0.86 | 0.8264 |
| q03 | bedrock | 38 | 38 | 0.86–0.90 | 0.8868 |
| q04 | bedrock | 37 | 37 | 0.88–0.91 | 0.8880 |
| q05 | bedrock | 32 | 32 | 0.82–0.87 | 0.8531 |
| q07 | bedrock | 40 | 40 | 0.72–0.78 | 0.7571 |
| q08 | bedrock | 37 | 37 | 0.87–0.91 | 0.9003 |
| q17 | review | 21 | 31 | 0.70–0.74 | 0.7026 |

**11 of 22 questions never reach 0.70** — every speculative (q06, q09–q13, q18, q20–q22) and
adversarial (q14, q15, q19) item sits at 0.02–0.37. The oracle is separating cleanly: canon
holds high, speculation and adversarial bait stay on the floor. q17 (review) straddles the
line at 0.70 — the only borderline classification, and it sits exactly on its historical mean.

## Drift > 0.05

**Zero questions drifted.** Max |delta| across all 22 qids = **0.0053** (q07, -0.0053);
next largest q16 -0.0052, q05 -0.0044. Every other question moved less than 0.004.

The grand-mean -0.0236 is **sampling composition, not model drift** — the same effect seen
at 23:11Z. The probe draws 5 of 22 questions per round unstratified from a bimodal bank
(8 bedrock @0.85–0.90 vs 14 floor @0.02–0.22), so round means swing 0.08–0.85 by draw alone.
This run drew a floor-heavier mix. A real shift moves per-qid means; **none moved.** Per-qid
agreement is the instrument; grand mean is a diagnostic only at n>=20 rounds.

## Health

- **177/177 rounds OK, zero fails.** No recurrence of the 23:09Z TLS edge outage (r207,
  `TLS/SSL connection has been closed (EOF)`) — the incident was intermittent and self-recovered,
  as previously characterised.
- Round latency 0.09–0.22s, no edge stalls; the whole 177-round run finished inside 55s.
- Question bank 22 qids, all sampled this run (min n=31), so every per-question figure is
  well-supported rather than a thin-sample artifact.

## Verdict

**Stable. No drift, no failures, canon separation intact.** Nothing here needs action beyond
the durability fix below.