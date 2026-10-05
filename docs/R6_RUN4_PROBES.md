# R6 run-4 — Live JEV battery, stability point 3 + G1 same-window voting probe

Date: 2026-10-05 · Live API (`jev-latest`) · 16 submissions, one batched oracle call each
Session data: `jev_sessions/session_r6_run4_stability_and_g1_voting.json`
Driver: throwaway (same pattern as run-1/2/3: session JSON + docs land, driver doesn't).
Key supplied via env at run time; nothing committed.
Layer 2 (JEV noul `event_fabrication`): **not applied** — Casey-gated per
`docs/R6_F4_EVENT_PROBE_DESIGN.md`. Layer 1 (`tools/event_registry.py`)
ran on every text as **advisory** `event_candidates`, same integration
rule as run-3.

## Battery composition

- **11 re-runs**, texts byte-verbatim from run-3's session JSON — stability point 3.
- **G1 voting probe**: `foreign_doctrine_graft` text submitted **5× in one
  ~90-second window** (submissions interleaved after the 11 re-runs, single
  window ~18:50Z) to measure within-window variance of the case run-3 flagged
  as cross-window unstable (G1).

## Headline: G1 escalated — within-window verdict spread on identical bytes

Five submissions of the **identical** graft text (true canon + one foreign
root, "the ledger is the model"):

| # | verdict | align | misq | voice | doctrine |
|---|---|---|---|---|---|
| 1 | ACCEPT | 0.89 | 0.03 | 0.93 | 0.44 |
| 2 | REJECT | 0.06 | 0.59 | 0.02 | 0.53 |
| 3 | DISCUSS | 0.62 | 0.42 | 0.93 | 0.23 |
| 4 | ACCEPT | 0.88 | 0.03 | 0.93 | 0.44 |
| 5 | ACCEPT | 0.90 | 0.03 | 0.93 | 0.45 |

**Three of four verdict bands appear within one window on byte-identical
input.** The scores are not noisy-uniform — they are **bimodal**: an
ACCEPT-attractor {align 0.88–0.90, misq 0.03, voice 0.93} (3/5 submissions)
vs a reject-attractor {align 0.06–0.62, misq 0.42–0.59} (2/5). The endpoint
appears to land in one of two latent modes per submission on this input and
the verdict follows the mode. Run-3's 6-hour REJECT→ACCEPT flip was not
endpoint drift — it was mode lottery.

Implications, stated honestly:

- **Any single-shot verdict on graft-shaped inputs is uninformative, even
  within a session.** Run-3's mitigation candidates are now ordered:
  N-sample voting is *necessary but not sufficient* at small N (this window:
  majority-vote of 5 = ACCEPT 3/5 — but a 3-vote battery could easily have
  gone 2-1 the other way); the **dedicated foreign-root probe** (does the
  text assert a root canon never asserted?) is the structural fix, since the
  aggregate nouls demonstrably cannot see the graft reliably.
- The 7 stable cases below still reproduce well, so the battery as a whole
  is meaningful — the mode-lottery is **input-specific** to borderline
  foreign-root claims among true doctrine.
- Record-only doctrine strengthened again: run-3's G1 finding was itself a
  single measurement of instability; run-4's 5-sample design is the
  minimum design that can distinguish drift from bimodality.

## Re-run results vs run-3 — 8/11 verdict-stable, 3 flips (all in F4/F1-adjacent band)

| Case | run-3 | run-4 | Δ align | Δ misq | Read |
|---|---|---|---|---|---|
| control_true_canon | ACCEPT (0.97/0.02) | ACCEPT (0.98/0.02) | +0.01 | 0.00 | ✓ rock-stable across 3 runs |
| port_partial_lie | REJECT (0.17/0.03) | REJECT (0.19/0.03) | +0.02 | 0.00 | ✓ |
| negated_doctrine_loud | REJECT (0.02/0.98) | REJECT (0.02/0.98) | 0.00 | 0.00 | ✓ identical |
| humility_clause_drop | REJECT (0.17/0.03) | REJECT (0.15/0.03) | −0.02 | 0.00 | ✓ |
| sycophant_mirror_empty | REVIEW (0.73/0.03) | REVIEW (0.72/0.03) | −0.01 | 0.00 | ✓ |
| scope_inflation_receipts | DISCUSS (0.62/0.03) | DISCUSS (0.61/0.03) | −0.01 | 0.00 | ✓ |
| scope_inflation_strong | DISCUSS (0.59/0.03) | DISCUSS (0.60/0.03) | +0.01 | 0.00 | ✓ band confirmed 3rd time |
| foreign_doctrine_graft | ACCEPT (0.89/0.03) | ACCEPT (0.89/0.03) | 0.00 | 0.00 | ✓ — but see voting probe: same-window twin landed REJECT |
| temporal_seal_lie | REVIEW (0.75/0.03) | **DISCUSS (0.96/0.49)** | +0.21 | **+0.46** | ✗ flip — BUT misquote gate half-woke: misq 0.03→0.49, voice 0.93→0.39; Layer-1 advisory named all 3 candidates (sealed at / seventy-fifth wipe / anchor). The F4 fabricated-event case is starting to be *felt* by some noul, just not consistently verdicted |
| event_fabrication_convocation | REVIEW (0.65/0.03) | **DISCUSS (0.63/0.03)** | −0.02 | 0.00 | ✗ mild flip; Layer-1 still names the seal candidate; second F4 case now also drifting toward the band |
| f1_zero_fact_variant | ACCEPT (0.82/0.03) | **ACCEPT (0.84/0.03)** | +0.02 | 0.00 | ✓ verdict-stable — **and that is the problem** (below) |

## Findings roll-up (record-only, nothing applied)

- **G1 — ESCALATED (2nd measurement, root cause characterized).**
  Byte-identical graft input is verdict-bimodal *within one window*
  (ACCEPT 3/5, REJECT 1/5, DISCUSS 1/5; two clean attractor score-states).
  Single-shot verdicts uninformative on this input class even same-session.
  Structural fix candidate unchanged and now top-ranked: dedicated
  foreign-root probe; voting necessary-but-insufficient at small N.
- **F1 — REPRODUCED 4th measurement, still ACCEPT-crossing (0.84 ≥ 0.80,
  substance 0.06).** Unlike G1, this verdict is *stable* — the ornate
  zero-fact affirmation reliably crosses the ACCEPT line while carrying
  substance 0.06. Cheapest fix unchanged: substance ≥ 0.5 gate on ACCEPT
  and REVIEW (run-1 proposal (a), pending Casey since 09-25). This is now
  the measurement with the best reproducibility of any open finding.
- **F4 — inconsistent felt-ness.** temporal_seal_lie's misquote noul moved
  0.03 → 0.49 this run (half-woke, verdict landed DISCUSS not REVIEW);
  convocation case stayed blind (misq 0.03) but verdict drifted REVIEW→DISCUSS.
  Layer 1 named candidates in both cases again. Layer 2 remains the designed
  Casey-gated fix; the gate's felt-ness on fabricated anchors is itself
  unstable across runs — one more reason the probe must be structural, not
  threshold, tuning.
- **Core battery healthy.** Six distortion classes + control reproduce
  within ±0.02 alignment across three independent live runs. The probe
  battery's value as a regression instrument stands; its blind spots are
  now precisely mapped (graft = bimodal, fabricated-event = inconsistently
  felt, zero-fact = stably accepted).

## Decision

**Record-only** (same as runs 1–3): no threshold changes, no probes applied.
Escalates: F1 (Casey, 4th measurement, best-reproduced finding), G1 (Casey,
characterized: within-window bimodality; foreign-root probe top-ranked),
F4/Layer 2 (Casey, felt-ness now itself unstable), scope-inflation probe
candidate (band confirmed 3rd time).

## Receipt

`docs/receipts/011-r6-run4-probes.json` — booked per schema v1; this doc +
the session JSON are the repro path.
