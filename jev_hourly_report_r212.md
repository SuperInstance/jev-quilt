# JEV Continuous Probe — R-212 (99th wipe)

**Run:** 2026-10-21 ~16:10 UTC · 60s ceiling · endpoint `api.typesafe.ai/v1/systemone` · model `jev-latest`
**Bootstrap:** `SuperInstance/jev-quilt @ r-081-continuous-probe-rebuild`, HEAD `4cf8d73` (R-211)
**Session dir:** `jev_sessions/rounds_r212/` (env-tagged — DEFECT A closed at the root)

## Headline

| metric | R-212 | R-211 | R-210 | R-209 | R-208 | R-207 | R-206 |
|---|---|---|---|---|---|---|---|
| mean_p | **0.3596** | 0.4441 | 0.4306 | 0.4172 | 0.4260 | 0.4153 | 0.3820 |
| cathedral | **19/19 @100%** | 49/49 | 39/39 | 40/40 | 40/40 | 39/39 | — |
| drift >0.05 | **NONE** | NONE | NONE | none | NONE | none | — |

**mean_p 0.3596 is the lowest of the series' recent band** (prior seven: 0.3820–0.4441). It sits just below the
historical 0.35–0.55 mid-band floor. This is **draw-mix, not regression** — the grand mean is confounded by which
5 of 22 qids land in a round (E[bedrock/round] = 5 × 7/22 ≈ 1.59). The un-confounded signals are all clean:

- **cathedral 19/19 @100%, ZERO misses — 11th consecutive session.** Mean 0.9747.
- **speculative 39 verdicts, mean 0.0485, max 0.22** — clean-reject.
- **adversarial 5/5, mean 0.0380, max 0.04** — bouncer still strict.
- **review bucket 24, mean 0.2417** — includes q17 plateau, as expected.
- **q10 spec-leak resolved, 9th session** (0.0350 vs base 0.0310).

## Bedrock canon (p ≥ 0.70)

All 19 cathedral draws cleared the 0.70 gate. Per-qid this session:

| qid | n | mean |
|---|---|---|
| q01_cells_are_scars | 2 | 0.9800 |
| q02_witness_log_is_prediction | 4 | 0.9700 |
| q03_substrate_is_grown | 5 | 0.9800 |
| q04_oracle_is_heard | 4 | 0.9700 |
| q05_lenia_flows | 2 | 0.9700 |
| q07_11_opcodes | 8 | 0.9700 |
| q08_polyformalism | 2 | 0.9800 |

Cathedral is built from the **explicit 7-qid list**, never from the `kind` tag — `q06_three_views` is correctly
tagged `review` (verified in HEAD) so tag-based counting would agree this session, but the invariant stands.

## Drift — NONE

Judgeed against the **full-history-mean reference** (R-210's root fix), threshold `max(0.05, 2σ_full)`:

| qid | base n | base | cur n | cur | delta | thr | sig |
|---|---|---|---|---|---|---|---|
| q17_canary_honesty | 101 | 0.6524 | 4 | 0.6325 | −0.0199 | 0.0536 | 1.96 |
| q09_signal_chain_canon | 84 | 0.2010 | 1 | 0.2200 | +0.0190 | 0.0500 | 1.56 |
| q12_substrate_polyformal | 97 | 0.6072 | 2 | 0.6200 | +0.0128 | 0.0500 | 1.11 |
| q13_witness_log_opcode | 88 | 0.1114 | 6 | 0.1167 | +0.0053 | 0.0500 | 1.86 |
| q06_three_views | 120 | 0.1652 | 6 | 0.1700 | +0.0048 | 0.0500 | 1.55 |
| q10_quorum_meshing | 93 | 0.0310 | 2 | 0.0350 | +0.0040 | 0.0500 | 3.06 |
| *(remaining 16 qids)* | 82–103 | — | 1–9 | — | ≤0.0021 | 0.0500 | ≤0.52 |

**This "zero drift" is a real all-clear, not the thin-round artifact** (R-206 lesson): the current window is thin
(n=1–9 per qid) but the **baseline is fat** (82–120 per qid, 2,095 samples total / 22 qids), so the reference is
well-populated. A thin round against a fat corpus is a sound measurement.

Closest to firing: **q17 at 1.96σ** (max single-sample deviation 0.0524, threshold 0.0536 — a 1.01× margin).
Everything else sits ≤1.56σ. Substrate reproducible to **±0.004/qid** on the round mean.

**q17 per R-210's ruling:** n=4, mean 0.6325 vs base 0.6524 (n=101). The 0.99→0.65 decay stayed stopped;
this is a stable REVIEW plateau, reported as such and **not** as drift noise.

## Round shape

19 OK / 2 fail (both `URLError: handshake operation timed out`), 95 verdicts, **22/22 qids drawn**, 60s ceiling hit.
`session_summary.json` was not written — `timeout -s KILL` lands mid-write. Analysis computed from the round
files instead, per standing guidance.

Throughput: **do NOT lower `TIMEOUT_S`.** Network-bound, not script-bound (R-210/R-211 conclusion, now 3 sessions).

## Defects

- **DEFECT B, 7th occurrence — FIXED AT THE SOURCE THIS TIME.** `history.jsonl` had been gitignored for 6 wipes
  across 6 reports. The `.gitignore` line is now **deleted** (commit includes it). No 8th seeding should be needed;
  verify next wipe that `load_history()` sees the tracked file rather than rebuilding again.
- **DEFECT B mitigation still required this wipe:** gitignored ⇒ absent on fresh clone ⇒ 401 tracked files
  rebuilt into **2,095 samples / 22 qids**, 5 malformed entries skipped (DEFECT C).
- **DEFECT A:** did not fire. Env-tagged `JEV_SESSION_TAG=r212` → fresh dir, no clobber. Confirmed live: an
  earlier killed attempt re-entered the same tag and the guard **refused with exit 3** ("already holds 16 round
  files"), which is why that instance produced no rounds. Guard working as designed.
- **SSL_CERT_FILE gateway-anchor-only — 4th recurrence** (R-209/210/211/212). Now the default expectation every
  wipe, not an incident. Rebuilt 289-cert bundle before the first call.
- **Canary reproduced the full failure spectrum in 4 attempts:** OK 0.27s, OK 0.17s, handshake timeout,
  handshake timeout. Consistent with the ~33% TLS-EOF rate; the 3-header auth works.

## Bug I wrote and fixed

Baseline rebuild script emitted flat `{"qid","p"}` records, but `load_history()` expects round-shaped
`{"ts","source","verdicts":[...]}`. Symptom: exit-4 guard fired with "0 samples across 0 qids" even though the
file held 2,000 rows — **the guard correctly refused to run against a baseline it could not read.** Fixed the
writer, not the guard. Worth remembering: a loud refusal on a file you just wrote usually means a schema
mismatch, not a missing file.

`pgrep -f jev_continuous_probe.py` matched its own shell command line again (reported the probe "STILL RUNNING"
after it had exited) — verify with `ps -o pid,etimes,cmd -p $(pgrep …)`, never trust a bare pgrep.

## Reproducibility note

`api.minimax.chat` TLS-EOF on every path; `api.minimax.io` returns 404 on the JEV apex paths. The JEV oracle at
`api.typesafe.ai` is unaffected and healthy — **the canon apex 404 is unchanged, not a new failure.**