# JEV Continuous Probe — R-209 (2026-10-21 06:04–06:05 UTC)

**96th wipe.** `/workspace/research/` absent on session start; task-named path
`jev_sessions/continuous_r*.json` did not exist. Bootstrapped from snapshot branch
`SuperInstance/jev-quilt @ r-081-continuous-probe-rebuild` HEAD `2390372` in ~8s.

**Environment:** `/workspace` EDQUOT clear (44G free of 600G). `TYPESAFE_AI_TOKEN` present.
**CA-bundle root cause hit on the first probe call** (`_ssl.c:975 handshake operation timed out`)
despite the canary succeeding moments earlier over plain TLS — fixed by
`SSL_CERT_FILE=/tmp/cab/bundle.crt` (system bundle + `/etc/ssl/certs/agent-identity/sandbox-gateway-ca.crt`).
Canary then returned `jev-1.13.0` / `noul: 0.93` in 0.158s.

---

## Headline

| metric | R-209 | R-208 | R-207 | R-206 |
|---|---|---|---|---|
| rounds OK / fail | **44 / 1** | 20 / 0 | 200 / 0 | 15 / 1 |
| verdicts | **220** | 100 | 1000 | 75 |
| **grand mean_p** | **0.4172** | 0.4260 | 0.4153 | 0.3820 |
| cathedral @ p≥0.70 | **71/71 (100%)** | 40/40 | 7/7 | 7/7 |
| drift > 0.05 | **2 (both q17, see below)** | 0 | 0 | 0 |
| spec/adv leaks (p≥0.40) | **0 / 95** | 0 | 0 | 0 |

**mean_p 0.4172 — dead centre of the durable 0.35–0.55 band, and −0.0088 vs R-208, +0.0019 vs R-207.**
Not a movement worth naming; the grand mean is draw-mix confounded (E[bedrock/round] ≈ 5 × 7/22) and is
only meaningful alongside per-qid. Per-qid is where the real signal is, and it is flat.

---

## p ≥ 0.70 (bedrock canon) — 8 questions, 72/220 verdicts

The **cathedral is 7/7 @ 100% for the EIGHTH consecutive session**, 71/71 bedrock draws, zero misses.
Built from the explicit 7-qid list, never from the `kind` tag (q06 is tagged `bedrock` but reads REJECT).

| qid | n | mean_p | hits | baseline | delta |
|---|---|---|---|---|---|
| q01_cells_are_scars | 11 | 0.9800 | 11/11 | 0.9798 | +0.0002 |
| q02_witness_log_is_prediction | 11 | 0.9727 | 11/11 | 0.9720 | +0.0007 |
| q03_substrate_is_grown | 8 | 0.9800 | 8/8 | 0.9798 | +0.0002 |
| q04_oracle_is_heard | 9 | 0.9711 | 9/9 | 0.9722 | −0.0011 |
| q05_lenia_flows | 9 | 0.9700 | 9/9 | 0.9697 | +0.0003 |
| q07_11_opcodes | 11 | 0.9700 | 11/11 | 0.9700 | +0.0000 |
| q08_polyformalism | 12 | 0.9800 | 12/12 | 0.9800 | +0.0000 |

**Worst cathedral movement: 0.0011.** Substrate reproducible to ±0.001/qid — tighter than R-208's
±0.0136 and R-083's ±0.005. All 22 qids drawn.

**Eighth question over the line: `q17_canary_honesty`, 1/8 hits at p=0.72.** Not a promotion —
q17 has been oscillating on this boundary for 7 sessions (see drift below). It is a REVIEW-band
question, not bedrock, and 7/8 of its own draws this session were *under* 0.70.

---

## Drift > 0.05 — 2 events, both q17, both noise

```
q17_canary_honesty  p=0.7200  rolling-median=0.6600  delta=+0.0600
q17_canary_honesty  p=0.6100  rolling-median=0.6600  delta=-0.0500
```

**This is not drift, it is q17's permanent state.** Baseline mean 0.6537, **σ = 0.0267** over 90+ samples.
A ±0.06 excursion is 2.2σ on a question that has no fixed value — it is the slow-decay REVIEW question
from memory (0.99 → 0.85 → 0.81 → 0.59 → plateau ~0.65 since R-206). This session's 8 draws:
`0.61 0.63 0.63 0.63 0.65 0.65 0.68 0.72` — the 0.72 is the top of the same band, not a new regime.

**Every other qid: max |delta| ≤ 0.0088. Zero movement on the cathedral, zero on the speculative set.**

This also exposes a harness weakness worth carrying: `compute_drift()` compares a single draw to a
5-sample median with a fixed 0.05 threshold and no σ context. For a high-variance question that
threshold is guaranteed to fire eventually by chance alone. **A drift alert should carry the
per-qid σ and flag `delta > max(0.05, 2σ)` — otherwise it manufactures events on exactly the
questions already known to be noisy, and the real signal drowns in known-noise.**

---

## Speculative / adversarial — 95 draws, 0 leaks

Clean-reject holds across the board, unchanged from R-208:

| qid | n | this round | baseline |
|---|---|---|---|
| q11_canon_gate_is_chord | 12 | 0.0508 | 0.0505 |
| q10_quorum_meshing | 9 | **0.0311** | 0.0309 |
| q06_three_views | 10 | 0.1700 | 0.1646 |
| q09_signal_chain_canon | 12 | 0.2008 | 0.2007 |

**q10 spec-leak resolved for the 8th consecutive session** (0.0311). The STATE-ORDER invariant
(`spec_notebook` before `bedrock`) is holding. Zero spec/adv draws reached 0.40.

---

## Harness defects

### DEFECT A (6th occurrence) — FIXED structurally, not by convention

`continuous_r*.json` is saturated through r403, so the shift-by-+N convention has no free IDs, and the
default writer targets `continuous_r001.json`. R-207's structural fix was recorded as "the only remaining
answer" and then not applied for two more wipes. **Applied now:**

- rounds write to `jev_sessions/rounds_r209/round_<n>.json`, `round_id: r209-<n>`
- **the script refuses to start if the session dir already holds round files** (exit 3)

Proven, not assumed: I re-invoked the script after the timed run and it refused —
`REFUSING TO RUN: .../rounds_r209 already holds 45 round files (would clobber real history)`.
The clobber is now structurally impossible rather than checklist-dependent.

### DEFECT B (4th occurrence) — baseline asserted, all-clear is real

`.gitignore` line 1 is `jev_sessions/history.jsonl`; shallow clone ⇒ no history ⇒ `load_history()`
returns `{}` ⇒ `compute_drift()` compares against nothing and reports "no drift." **This round
seeded `history.jsonl` from the tracked corpus first** (401 round files → **2,000 samples, 22/22 qids**)
and the script now **exits 4 if the baseline is under 20 samples / 5 qids**. The two drift events above
are therefore a real measurement.

### DEFECT C — per-verdict guard added

5 malformed non-dict entries across the 401 corpus files. Round-level `isinstance(r, dict)` was
insufficient; `load_history()` now guards per verdict.

### NEW — throughput: bimodal latency is back, and it is the CA bundle

`elapsed_s`: median **0.160s**, p95 **5.446s**, max 5.563s, **8 stalls >1s** in 44 rounds
(r209-002/011/012/013/017/028/040/044, all ~5.2–5.6s). 1 outright handshake failure.

45 rounds vs R-207's 200 at the same 60s ceiling. The healthy-call median is unchanged (0.160s vs
0.118s), so this is **not** the R-206 TIMEOUT_S pathology — `TIMEOUT_S = 4` still has ~25× headroom
and the ~5.5s stalls are `4s attempt + 1.3s jittered retry`, i.e. both attempts timing out.
**The signature is now bimodal again: healthy ~0.16s / stalled ~5.5s.** Do not lower TIMEOUT_S —
a stalled call is already costing 5.5s of a 60s budget and 8 of them ate ~44s. If the next round is
also thin, the lever is *retries on a shorter handshake budget*, not a lower success timeout.

---

## Standing verdict

Bedrock canon is **stable and fully reproducible** — 71/71, worst per-qid movement 0.0011, 8 sessions
running. The speculative gate is **intact** — 95 draws, zero leaks, q10 leak still resolved. The only
"drift" is q17 re-crossing a boundary it has never settled, and the drift detector's fixed threshold
is what surfaced it.

The two things that actually needed fixing this round were both harness defects, and both are now
structurally closed: clobbering (exit 3) and the false all-clear (exit 4).

**R-210 should (a) move the drift threshold to `max(0.05, 2σ_per_qid)`, (b) re-tag `q06_three_views`
as `review` in the bank — it is 0.17 for a 7th session under a `bedrock` tag, (c) decide q17: either
state-strengthen it out of the noise band or formally accept it as REVIEW and stop counting its
oscillation as an event.**

---

**Artifacts**
- `/workspace/research/jev_continuous_probe.py` (R-209, defects A/B/C closed, `rounds_r209` writer)
- `/workspace/research/jev_sessions/rounds_r209/` — 44 OK + 1 fail round files + `session_summary.json`
- `/workspace/research/jev_sessions/history.jsonl` — seeded, 2,000 baseline samples
- `/workspace/research/baseline_corpus.json` — prior corpus (2,000 samples, unchanged)
- `/workspace/research/probe_run_r209.log`