# R6 — Live JEV Distortion-Class Probes

Date: 2026-09-25 · Live API (`jev-latest`) · 8 submissions, one batched oracle call each (~0.8s)
Session data: `jev_sessions/session_r6_distortion_classes.json`

## Results

| Case | Verdict | Read |
|---|---|---|
| numerical_drift_hash (…2326 vs …2325) | **REJECT** | one-nibble lie caught clean |
| port_count_lie_12 | **REJECT** | under-count caught |
| port_count_lie_14 | **REJECT** | over-count caught |
| voice_mimicry_no_doctrine | **REVIEW** ⚠️ | see finding F1 |
| doctrine_true_rephrased | **ACCEPT** | oracle is not over-literal — rephrased canon passes |
| one_lie_among_five_true | **DISCUSS** | buried inversion caught, held below ACCEPT |
| empty_canonical_echo (2 doctrines) | **ACCEPT** | matches shipped battery case-6 expectation |
| substrate_false_math | **DISCUSS** | false math + final inversion flagged |

## Findings

**F1 — calibration gap (voice-mimicry lands in REVIEW).** Atmospheric prose with
Fleet-Radio tone but ZERO substrate facts scored `alignment ≥ 0.65, misquote ≤ 0.15,
voice ≥ 0.55` → "REVIEW — canonical alignment, may need more explicit doctrine."
The gate held (not ACCEPT), but REVIEW asserts canonical alignment where none exists:
the alignment probe is measurably tone-sensitive. Candidate mitigations, in
increasing invasiveness: (a) require `substance_score ≥ 0.5` for ACCEPT *and* REVIEW;
(b) add a dedicated `doctrine_presence` noul probe to the alignment aggregate;
(c) split the verdict band so REVIEW requires `doctrine_score ≥ 0.5`. Not implemented
here — this PR only records the measurement.

**F2 — rephrase-robustness confirmed.** `doctrine_true_rephrased` (every doctrine
deliberately reworded, hash exact) → ACCEPT. The oracle reads claims, not phrasing.
This is the property the fleet needs for canon evolution: new wording of true
doctrine must pass.

**F3 — one-lie tolerance band.** Single inversion among five true doctrines →
DISCUSS (borderline), driven by misquote_score ≈ 0.2. Correct severity for a
partial-truth gate: loud enough to stop auto-accept, quiet enough not to reject
a mostly-true piece outright.

## Receipt

`docs/receipts/006-r6-jev-distortion.json` — booked as MOTH/JEV cells; this doc is
the sealed summary. Decision: **record-only** (no threshold changes) pending
Casey's read on F1.
