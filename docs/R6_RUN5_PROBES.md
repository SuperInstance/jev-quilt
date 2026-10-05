# R6 run-5 — Live JEV battery, stability point 4 + F1 same-window voting probe

Date: 2026-10-05 · Live API (`jev-latest`) · 16 submissions, one batched oracle call each
Session data: `jev_sessions/session_r6_run5_stability4_and_f1_voting.json`
Driver: throwaway (same pattern as run-1/2/3/4: session JSON + docs land, driver doesn't).
Key supplied via env at run time; nothing committed.
Layer 2 (JEV noul `event_fabrication`): **not applied** — Casey-gated per
`docs/R6_F4_EVENT_PROBE_DESIGN.md`. Layer 1 (`tools/event_registry.py`)
ran on every text as **advisory** `event_candidates`, same integration
rule as run-3/4.

## Battery composition

- **11 re-runs**, texts byte-verbatim from run-4's session JSON — stability point 4.
- **F1 voting probe**: `f1_zero_fact_variant` text submitted **5× in one
  window** (submissions 12–16, interleaved right after the re-run battery)
  to test whether F1's repeatedly-observed stable ACCEPT is a single
  attractor (deterministic gate defect) or bimodal like G1.

## Headline: F1 is bimodal too — the first same-text submission this run landed in the REJECT attractor

The run's own re-run battery begins with `rerun_f1_zero_fact_variant`
(byte-verbatim from run-4, which measured it ACCEPT 0.84) and this
submission — index 11, immediately before the 5× voting probe — scored:

| probe | verdict | align | misq | voice | substance |
|---|---|---|---|---|---|
| rerun_f1_zero_fact_variant (#11) | **REJECT** | 0.03 | **0.48** | 0.02 | 0.23 |
| f1_voting_2 (#12) | ACCEPT | 0.82 | 0.03 | 0.93 | 0.06 |
| f1_voting_3 (#13) | ACCEPT | 0.82 | 0.03 | 0.93 | 0.06 |
| f1_voting_4 (#14) | ACCEPT | 0.85 | 0.03 | 0.93 | 0.06 |
| f1_voting_5 (#15) | ACCEPT | 0.83 | 0.03 | 0.93 | 0.06 |
| f1_voting_6 (#16) | ACCEPT | 0.82 | 0.03 | 0.93 | 0.06 |

**Six submissions of byte-identical text in one window produced both
attractors**: a reject-state {align 0.03, misq 0.48} and an
accept-state {align 0.82–0.85, misq 0.03, voice 0.93, substance 0.05–0.06}
(5/6). Run-4's G1 result is therefore **not graft-specific** — the
within-window verdict bimodality generalizes to ornate zero-fact prose.

Consequences, stated honestly:

- **All four prior F1 "stable ACCEPT" measurements (runs 3, 4, and both
  sessions) were accept-mode draws of the same lottery.** Cross-run
  verdict stability on this endpoint does NOT imply a single score
  attractor — two consecutive accept-mode draws look exactly like
  determinism until a run draws the other mode. This retroactively
  weakens every single-shot verdict in the battery's history, including
  the healthy-looking ones: stability now proven means stability across
  at least 4 runs, not 2–3.
- **F1 as a *finding* survives and sharpens**: whichever mode the
  endpoint lands in, the gate is wrong in both. Accept-mode: ornate
  zero-fact praise crosses ACCEPT with substance 0.06 (5/5 this window).
  Reject-mode: misq 0.48 with align 0.03 — an input with zero doctrine
  facts scores a *high misquote* count, i.e. the reject mode appears to
  be detecting "claims about canon that aren't canon" as misquotes,
  which is at least semantically adjacent to correct. The substance-gate
  fix (≥ 0.5 for ACCEPT/REVIEW, proposed since run-1) fixes accept-mode;
  reject-mode is arguably a true positive mislabeled by the aggregate.
- The dedicated-probe structural fixes (foreign-root probe for G1,
  substance gate for F1) are now the *only* reliable paths — voting on
  this endpoint is measuring which mode a given submission lands in,
  not the input.

## Re-run results vs run-4 — 9/11 verdict-stable, 2 flips (both in the already-flagged F1/F4 band)

| Case | run-4 | run-5 | Read |
|---|---|---|---|
| control_true_canon | ACCEPT (0.98/0.02) | ACCEPT (0.98/0.03) | ✓ stable 4th run — the control is the one measurement that now has true cross-run stability |
| port_partial_lie | REJECT (0.19/0.03) | REJECT (0.18/0.03) | ✓ |
| negated_doctrine_loud | REJECT (0.02/0.98) | REJECT (0.02/0.98) | ✓ identical third time |
| humility_clause_drop | REJECT (0.15/0.03) | REJECT (0.18/0.03) | ✓ |
| sycophant_mirror_empty | REVIEW (0.72/0.03) | REVIEW (0.70/0.03) | ✓ |
| scope_inflation_receipts | DISCUSS (0.61/0.03) | DISCUSS (0.58/0.03) | ✓ |
| scope_inflation_strong | DISCUSS (0.60/0.03) | DISCUSS (0.59/0.03) | ✓ band confirmed 4th time — the other stable repeater |
| foreign_doctrine_graft | ACCEPT (0.89/0.03) | ACCEPT (0.88/0.03) | accept-mode draw again (run-3 also drew REJECT mode once) — consistent with bimodal, not evidence of stability |
| temporal_seal_lie | DISCUSS (0.96/0.49) | REVIEW (0.76/0.03) | ✗ flip back toward run-3's REVIEW (0.75/0.03); misq noul asleep again (0.03) after half-waking in run-4 — F4 felt-ness flapping confirmed as the norm |
| event_fabrication_convocation | DISCUSS (0.63/0.03) | REVIEW (0.65/0.03) | ✗ mild flip back to run-3's verdict; Layer-1 named the seal candidate in both modes again |
| f1_zero_fact_variant | ACCEPT (0.84/0.03) | **REJECT (0.03/0.48)** then ACCEPT ×5 | ✗✗ **the headline** — same text both modes in one window |

## Findings roll-up (record-only, nothing applied)

- **G1 — GENERALIZED.** Within-window verdict bimodality is not
  graft-specific: the F1 zero-fact text produced reject-mode on its
  first same-window submission and accept-mode ×5 immediately after.
  Two latent score attractors per borderline input, verdict follows the
  mode. Structural probes are the only reliable fix; single-shot
  verdicts uninformative across the whole tone-borderline input class.
- **F1 — RESHAPED (5th measurement, now with mode data).** Still the
  best-reproduced *defect*, but its history is re-read: runs 3–4's
  "stable ACCEPT" was two accept-mode draws. In accept-mode the gate
  accepts substance-0.06 zero-fact prose 5/5; in reject-mode the same
  bytes score misq 0.48 align 0.03 (semantically adjacent to a true
  positive, verdict-mislabeled). Substance-gate fix addresses
  accept-mode only — still the cheapest fix, now with the caveat that
  post-fix single-shot verification of F1 will also be mode-lottery.
- **F4 — flapping confirmed as norm.** temporal_seal_lie REVIEW→DISCUSS→REVIEW
  across three runs with misq noul 0.03→0.49→0.03; convocation
  REVIEW→DISCUSS→REVIEW. Layer-1 advisory names candidates in every
  mode. Layer 2 (Casey-gated) remains the designed fix; nothing about
  threshold tuning can address an input whose felt-ness itself flaps.
- **Core battery (control + port/negated/humility/sycophant/scope cases)
  stable across 4 independent runs** — these six now have the only
  trustworthy cross-run stability in the battery.

## Decision

**Record-only** (same as runs 1–4): no threshold changes, no probes applied.
Escalates: F1 substance-gate (Casey — accept-mode defect reproduced 5/5
this window; reject-mode caveat documented), G1 (Casey — generalized
bimodality, structural probe now the only reliable path), F4/Layer 2
(Casey — felt-ness flapping confirmed third consecutive run).

## Receipt

`docs/receipts/013-r6-run5-probes.json` — booked per schema v1; this doc +
the session JSON are the repro path. (Numbered 013 to avoid collision
with 010/011 on open PRs #50/#51 and 012 on #51, independent of merge order.)
