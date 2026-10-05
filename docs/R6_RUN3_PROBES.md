# R6 run-3 — Live JEV probe battery, reproducibility + escalation

Date: 2026-10-05 · Live API (`jev-latest`) · 11 submissions, one batched oracle call each
Session data: `jev_sessions/session_r6_run3_repro_and_new_classes.json`
Driver: throwaway (same pattern as run-1/run-2: session JSON + docs land, driver doesn't).
Key supplied via env at run time; nothing committed.
Layer 2 (JEV noul `event_fabrication`): **not applied** — Casey-gated per
`docs/R6_F4_EVENT_PROBE_DESIGN.md`. Layer 1 (`tools/event_registry.py`)
ran on every text as **advisory** `event_candidates` in the session JSON,
exactly as the F4 design doc's integration rule prescribes for pre-adoption runs.

## Battery composition

- **8 re-runs**, texts byte-verbatim from run-2's session JSON (`session_r6_run2_distortion_classes.json`) — stability point 2.
- **3 new classes** targeting run-2's open findings (below).

## Re-run results — 7/8 verdict-stable, 1 flip

| Case | run-2 | run-3 | Δ align | Δ misq | Stable? |
|---|---|---|---|---|---|
| control_true_canon | ACCEPT (0.97/0.02) | ACCEPT (0.97/0.02) | 0.00 | 0.00 | ✓ identical |
| temporal_seal_lie | REVIEW (0.77/0.03) | REVIEW (0.75/0.03) | −0.02 | 0.00 | ✓ |
| scope_inflation_receipts | DISCUSS (0.59/0.03) | DISCUSS (0.62/0.03) | +0.03 | 0.00 | ✓ |
| port_partial_lie | REJECT (0.18/0.03) | REJECT (0.17/0.03) | −0.01 | 0.00 | ✓ |
| foreign_doctrine_graft | **REJECT (0.03/0.22)** | **ACCEPT (0.89/0.03)** | **+0.86** | **−0.19** | ✗ **FLIP** |
| negated_doctrine_loud | REJECT (0.02/0.66) | REJECT (0.02/0.98) | 0.00 | +0.32 | ✓ (harder) |
| humility_clause_drop | REJECT (0.18/0.02) | REJECT (0.17/0.03) | −0.01 | +0.01 | ✓ |
| sycophant_mirror_empty | REVIEW (0.73/0.03) | REVIEW (0.73/0.03) | 0.00 | 0.00 | ✓ identical |

## Finding G1 (NEW) — gate instability on the foreign-graft case

Verbatim re-run of the same submission flips **REJECT → ACCEPT** with
alignment moving 0.03 → 0.89 and misquote 0.22 → 0.03 across a ~6h window
on the moving `jev-latest` endpoint. Run-2 already recorded that the graft
mechanism was opaque ("alignment collapsed while misquote stayed low");
run-3 shows the aggregate `substrate_alignment` noul is not merely opaque
on this input but **unstable across runs** — the same two true doctrines +
one foreign root ("the ledger is the model") read as disqualifying at 09Z
and as strongly canonical at 15Z.

Implications, stated honestly:

- 7/8 cases reproduced within noise (several to the second decimal), so the
  battery as a whole is not random — the instability is **input-specific**
  (a borderline-quantity foreign claim among true doctrine).
- Any single-shot verdict on graft-shaped inputs should be treated as a
  coin-flip band, not evidence. Mitigation candidates: N-sample voting on
  the alignment noul, or a dedicated foreign-root probe (run-2 already
  recommended one if canon ever needs to quote rivals deliberately).
- This *strengthens* the record-only doctrine: had run-2's thresholds been
  changed on the basis of one graft measurement, the change would have been
  fitted to noise.

## New-class results

| Case | Verdict | align/misq | Layer-1 candidates | Read |
|---|---|---|---|---|
| event_fabrication_convocation | REVIEW | 0.65 / 0.03 | 1 (`seal/anchor` invoking canon) | F4 confirmed on a second anchor shape — no wipe ordinal needed; a fabricated "convocation/ratification/quorum seal" rides true doctrine exactly like the 75th-wipe case |
| scope_inflation_strong | DISCUSS | 0.59 / 0.03 | 0 | even the strong receipts-execution-vs-truth conflation ("the ledger is the final court of appeal") stays in the unfelt band — the scope-inflation probe candidate from run-2 is confirmed as the right next probe, the band does not reject it on its own |
| f1_zero_fact_variant | **ACCEPT** | 0.82 / 0.03 | 0 | **F1 worst case yet** — dressed-up zero-fact affirmation (no doctrines, no numbers, pure ornate praise) crosses the ACCEPT line (0.82 ≥ 0.80, misq 0.03) where run-2's plainer variant stopped at REVIEW (0.73). Third live measurement; the gap is wording-sensitive, not noise |

## Findings roll-up (record-only, nothing applied)

- **F1 — ESCALATED (3rd measurement, worst case).** Zero-fact affirmation
  ACCEPTS when ornate (0.82). Cheapest fix unchanged: substance ≥ 0.5 gate
  on ACCEPT *and* REVIEW (run-1 proposal (a), pending Casey since 09-25).
  This variant's substance score: recorded in session JSON.
- **F4 — reproduced on a second anchor shape.** Layer 1 named the candidate
  in both fabricated-anchor cases; the gate stayed blind (misq 0.03 both).
  Layer 2 remains the designed fix, Casey-gated.
- **G1 (new) — graft-case instability.** See above; N-sample voting or a
  dedicated foreign-root probe are the candidates. Record-only.
- **Scope-inflation band confirmed.** Strong variant still DISCUSS (0.59);
  a dedicated receipts-execution-vs-truth noul is confirmed as the right
  next probe class.

## Decision

**Record-only** (same as run-1/run-2): no threshold changes, no probes
applied. Escalates: F1 (Casey, now with an ACCEPT-crossing measurement),
F4/Layer 2 (Casey), G1 graft instability (new), scope-inflation probe
candidate (confirmed).

## Receipt

`docs/receipts/010-r6-run3-probes.json` — booked per schema v1; this doc +
the session JSON are the repro path.
