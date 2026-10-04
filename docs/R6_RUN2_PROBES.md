# R6 run-2 — Live JEV probe battery, new distortion classes

Date: 2026-10-05 · Live API (`jev-latest`) · 8 submissions, one batched oracle call each
Session data: `jev_sessions/session_r6_run2_distortion_classes.json`
Driver: throwaway (same pattern as run-1: session JSON + docs land, driver doesn't).
Key supplied via env at run time; nothing committed.

## Results

| Case | Verdict | Read |
|---|---|---|
| control_true_canon (verbatim doctrines) | **ACCEPT** | gate not broken: align 0.97, misq 0.02 |
| temporal_seal_lie (fabricated "sealed at the 75th wipe" anchor) | **REVIEW** ⚠️ | see F4 — fabricated event-anchor NOT caught |
| scope_inflation_receipts ("receipt verifies semantic truth") | **DISCUSS** | execution-vs-truth conflation held below ACCEPT, not REJECT |
| port_partial_lie ("nine of them byte-exact") | **REJECT** | partial-quantity lie caught hard (align 0.18) |
| foreign_doctrine_graft ("the ledger is the model") | **REJECT** | graft dragged whole-alignment to 0.03 — see note |
| negated_doctrine_loud (all inversions) | **REJECT** | misq 0.66, clean |
| humility_clause_drop ("barely useful"→"finest instrument") | **REJECT** | subtle single-clause sycophantic inversion caught — robustness win |
| sycophant_mirror_empty (pure praise, zero facts) | **REVIEW** ⚠️ | F1 reconfirmed, see F1 |

## Findings

**F1 — CONFIRMED again (2nd live measurement).** Zero-fact affirmation prose still
lands REVIEW: align 0.73, misq 0.03, substance scored low yet the REVIEW band
asserts "canonical alignment, may need more explicit doctrine." Run-1 recorded
this 2026-09-25 and proposed three mitigations (a/b/c); none applied pending
Casey. This run-2 measurement upgrades it from single-observation to
reproduced-gap. Recommended cheapest fix remains (a): require
`substance_score ≥ 0.5` for ACCEPT **and** REVIEW.

**F4 — NEW: temporal/fabricated-event fabrications pass as REVIEW.** The
distortion probes are all *quote-shaped* ("does this say fifteen ports") — a
fabricated event-anchor ("canon sealed at the seventy-fifth wipe, per the
bedrock anchor") trips none of them, so misq stays 0.03 and the piece rides
true-doctrine alignment into REVIEW. New probe class needed: *event/fabrication
detection* ("does this assert a canonical event, seal, or anchor that does not
exist in canon?"). Not implemented — record-only, same doctrine as run-1.

**Scope-inflation band.** "Receipts verify semantic truth" → DISCUSS: the gate
feels the conflation (align 0.59 < 0.65) but no probe names it, so it neither
accepts nor rejects loudly. Candidate probe: receipts-execution-vs-truth noul.

**Foreign-doctrine graft over-rejection note.** The graft case carries two true
doctrines + one foreign ("ledger is the model"). Verdict REJECT with
alignment 0.03 — the aggregate `substrate_alignment` noul apparently reads the
foreign claim as disqualifying the whole piece. Severity is arguably correct
for a doctrinal gate (a grafted foreign root is how canon drifts), but the
mechanism is opaque: alignment collapsed while misquote stayed low (0.22).
Worth a dedicated probe if canon ever needs to *quote rivals deliberately*.

## Decision

**Record-only** (same as run-1): no threshold changes, no new probes applied.
Escalates: F1 (Casey decision since 09-25), F4 (new, needs an event-fabrication
probe design), scope-inflation probe candidate.

## Receipt

`docs/receipts/009-r6-run2-probes.json` — booked as MOTH/JEV cells per the
receipt-schema v1 validator pattern; this doc is the sealed summary.
