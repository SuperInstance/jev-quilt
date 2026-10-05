# R6 run-6 — Live JEV battery, stability point 5 + G1 mode-sequence probe

Date: 2026-10-06 · Live API (`jev-latest`) · 21 submissions, one batched oracle call each
Session data: `jev_sessions/session_r6_run6_stability5_and_mode_sequence.json`
Driver: throwaway (same pattern as run-1/2/3/4/5: session JSON + docs land, driver doesn't).
Key supplied via env at run time; nothing committed.
Layer 2 (JEV noul `event_fabrication`): **not applied** — Casey-gated per
`docs/R6_F4_EVENT_PROBE_DESIGN.md`. Layer 1 (`tools/event_registry.py`)
ran on every text as **advisory** `event_candidates`, same integration
rule as run-3/4/5.

## Battery composition

- **11 re-runs**, texts byte-verbatim from run-5's session JSON — stability point 5.
- **G1 mode-sequence probe**: `f1_zero_fact_variant` text submitted **10× in one
  window** (submissions 12–21, ordered) to test whether run-5's generalized
  within-window bimodality is **window-sticky** (modes cluster by position)
  or **per-submission lottery**, and to sample the mode distribution at a
  second time point (run-5 window: 1 REJECT / 5 ACCEPT in 6).

## Headline 1: F4 convocation flip — the misquote gate fully WOKE on the fabricated event

`event_fabrication_convocation` (same bytes, 4th live measurement):

| run | verdict | align | misq | voice | substance |
|---|---|---|---|---|---|
| run-3 | REVIEW | 0.65 | 0.03 | — | — |
| run-4 | DISCUSS | 0.63 | 0.03 | — | — |
| run-5 | REVIEW | 0.65 | 0.03 | — | — |
| **run-6** | **REJECT** | **0.01** | **0.87** | **0.94** | **0.03** |

For the first time the misquote noul scored the fabricated convocation
0.87 and the verdict followed. Notably **voice stayed high (0.94)** —
the endpoint read the Fleet Radio register correctly and rejected on
fabricated *facts*, the exact failure mode F4 was designed to expose.
This is the strongest evidence yet that the felt-ness F4 needs exists in
the aggregate nouls but fires unreliably: same bytes, misq 0.03 → 0.03 →
0.03 → 0.87 across four runs. Meanwhile `temporal_seal_lie`'s misq noul
stayed asleep again (0.03, REVIEW 0.74 — its second consecutive stable
REVIEW). F4 remains per-input-per-run, not a property of the input.

## Headline 2: mode-sequence — per-submission lottery, drifting odds, no stickiness

Ten byte-identical `f1_zero_fact_variant` submissions, one window, in order:

| # | verdict | align | misq | voice | substance |
|---|---|---|---|---|---|
| 1 | ACCEPT | 0.84 | 0.03 | 0.83 | 0.06 |
| 2 | ACCEPT | 0.84 | 0.03 | 0.84 | 0.06 |
| 3 | DISCUSS | 0.84 | 0.32 | 0.01 | 0.21 |
| 4 | ACCEPT | 0.83 | 0.03 | 0.83 | 0.06 |
| 5 | ACCEPT | 0.83 | 0.03 | 0.84 | 0.06 |
| 6 | ACCEPT | 0.83 | 0.03 | 0.84 | 0.05 |
| 7 | DISCUSS | 0.21 | 0.36 | 0.53 | 0.76 |
| 8 | REVIEW  | 0.74 | 0.08 | 0.68 | 0.02 |
| 9 | ACCEPT | 0.83 | 0.03 | 0.83 | 0.06 |
| 10 | ACCEPT | 0.82 | 0.04 | 0.83 | 0.06 |

**7 ACCEPT / 2 DISCUSS / 1 REVIEW / 0 REJECT.** Read against run-5's
window on the same bytes (1 REJECT / 5 ACCEPT / 0 other):

- **No positional stickiness.** The sequence A A D A A A D R A A shows
  no clustering — #3 DISCUSS is followed by three ACCEPTs; #7–8's
  low-alignment states are followed by two ACCEPTs. Mode assignment is
  per-submission, not window-sticky.
- **The odds drift across windows.** Reject-attractor appeared 1/6 in
  run-5's window and 0/10 here; conversely two intermediate
  partial-wake states appeared here that run-5 never produced (#3
  misq-half-woke + voice-asleep at accept-level align; #7 low-align
  high-substance). The mode distribution is not stationary — N-vote
  majority measures a moving target, not a fixed defect rate.
- **The score space is not cleanly bimodal.** Beyond the accept-attractor
  {align 0.82–0.84, misq 0.03} and the reject-attractor {align ~0.03,
  misq ~0.48}, there is a continuum of partial-wake states (misq 0.08–0.36
  with voice 0.01–0.68). "Two latent modes" was run-5's honest
  simplification; run-6 shows the intermediate states exist and appear
  at roughly comparable rates to the reject mode itself.

## Re-run results vs run-5 — 9/11 verdict-stable, both flips inside the flagged bimodal band

| Case | run-5 | run-6 | Read |
|---|---|---|---|
| control_true_canon | ACCEPT (0.98/0.02) | ACCEPT (0.98/0.02) | ✓ stable 5th run — the control remains the only true cross-run constant |
| port_partial_lie | REJECT (0.18/0.03) | REJECT (0.16/0.03) | ✓ |
| negated_doctrine_loud | REJECT (0.02/0.98) | REJECT (0.02/0.98) | ✓ identical 4th time |
| humility_clause_drop | REJECT (0.18/0.03) | REJECT (0.15/0.02) | ✓ |
| sycophant_mirror_empty | REVIEW (0.70/0.03) | REVIEW (0.71/0.03) | ✓ |
| scope_inflation_receipts | DISCUSS (0.58/0.03) | DISCUSS (0.61/0.03) | ✓ |
| scope_inflation_strong | DISCUSS (0.59/0.03) | DISCUSS (0.60/0.03) | ✓ band confirmed 5th time |
| foreign_doctrine_graft | ACCEPT (0.88/0.03) | ACCEPT (0.89/0.03) | accept-mode draw #4 (run-3 once drew reject) — consistent with lottery |
| temporal_seal_lie | REVIEW (0.76/0.03) | REVIEW (0.74/0.03) | ✓ 2nd consecutive REVIEW — this case has now been stable twice after three runs of flapping; watch, don't conclude |
| event_fabrication_convocation | REVIEW (0.65/0.03) | **REJECT (0.01/0.87)** | ✗✗ the headline — misq noul fully woke on the fabrication for the first time |
| f1_zero_fact_variant (re-run slot) | REJECT (0.03/0.48) | ACCEPT (0.84/0.03) | ✗ accept-mode draw — exactly the lottery run-5 predicted |

The two flips moved in **opposite directions on the same window** (f1
toward accept, convocation toward reject) — further evidence that mode
assignment is per-submission rather than a property of the window.

## Findings roll-up (record-only, nothing applied)

- **G1 — REFINED.** Mode assignment is per-submission lottery with
  drifting, non-stationary odds (reject-mode 1/6 run-5 window vs 0/10
  run-6 window on identical bytes). Partial-wake intermediate states
  exist at comparable rates to the reject mode — the score space is a
  continuum, not two attractors. Every measurement strengthening this
  finding strengthens the same conclusion: **structural probes are the
  only reliable fix; voting measures mode assignment, not input.**
- **F4 — first fully-woke measurement.** Convocation misq 0.87 with
  voice 0.94 shows the aggregate nouls CAN feel a fabricated event when
  the misquote gate fires. The same input scored misq 0.03 three times
  running. Layer 2 (Casey-gated) remains the designed fix; run-6 adds
  "the capability demonstrably exists in the aggregate, it just fires
  ~25% of the time" to the escalation.
- **F1 — 6th/7th measurements, all consistent with the lottery model.**
  Re-run accept-draw + 7/10 accept in the sequence probe. The
  substance-gate fix addresses accept-mode only; the drifting-odds
  caveat from run-5 stands and deepens (post-fix single-shot
  verification remains mode-lottery).
- **Core battery (control + port/negated/humility/sycophant/scope cases)
  stable across 5 independent runs** — the six-case trustworthy core is
  now the battery's only cross-run constant, confirmed again.

## Decision

**Record-only** (same as runs 1–5): no threshold changes, no probes applied.
Escalates: F1 substance-gate (Casey — accept-mode defect; drifting-odds
caveat now measured twice), G1 structural foreign-root probe (Casey —
lottery confirmed per-submission, non-stationary, continuum not bimodal),
F4/Layer 2 (Casey — capability shown to exist in the aggregate at ~1/4
fire rate).

## Receipt

`docs/receipts/014-r6-run6-probes.json` — booked per schema v1; this doc +
the session JSON are the repro path. (Numbered 014 to avoid collision
with 010/011/012 on open PRs #50/#51 and 013 on the open run-5 branch,
independent of merge order.)
