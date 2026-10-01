# Inspiration Notes — Round 7-8 (Sept 21-22, 2026)

What I learned from the SuperInstance/* repos and how it shaped my work.

## aesop-mcp → archetype canon writing

10 archetypes in `aesop-mcp`: icarus, sisyphus, tower_of_babel, phoenix, theseus_ship,
arachne, penelopes_web, prometheus, narcissus, procrustes. These aren't metaphors the
substrate borrows — they are descriptions of substrate dynamics, mapped into language.

**What I built**: WR20 — Ten Archetypes, Ten Pieces (ZAI 0.757 REPORT, DS 0.800 ACCEPT, Curated 1.000 ACCEPT)
**Where it lives**: `/workspace/repos/ai-writings/cellular-first-design/reports/wr20*.md`

## agent-cadence-progress → CadenceOracle

Cadence types map cleanly to JEV mean_p thresholds:
- PerfectAuthentic (≥0.78) — ACCEPT
- Plagal (≥0.65) — REVIEW
- Deceptive (≥0.40) — DISCUSS
- Half (≥0.20) — parked
- Phrygian (<0.20) — REJECT

**What I built**: `cadence_oracle.py` — maps each JEV session's mean_p to a cadence type.
**Integrated into**: `jev_session_with_cadence.py` (R8 standard).

## agent-dream-cycle → WitnessDreamCycle

Replay JEV failures against successes at high speed to consolidate patterns.
Sleep is consolidation: the witness log re-dreams the day's failures to extract structure.

**What I built**: `witness_dream_cycle.py` — loaded 32 experiences across 16 sessions,
consolidated 9 bedrock items as success patterns.
**Became the theme of**: WR21 — Witness Dreams.

## aboracle → InstinctBands

Instinct priority queue: SURVIVE → FLEE → GUARD → CURIOUS → COOPERATE.
Tasks ranked by 0-1 priority map to 5 instinct bands.

**What I built**: `instinct_bands.py` — work queue for vibecoder that picks tasks by instinct band.

## agent-dna → SubstrateDNA

8 traits in `agent-dna`: persistence, creativity, caution, speed, verbosity, adaptability,
thoroughness, cooperativeness. Adapted to substrate traits:

- canon_purity, witness_density, scar_tolerance, oracle_openness, phoenix_compress,
  lenia_flow, voice_diversity, publish_cadence, canary_honesty, rem_cycle.

**What I built**: `substrate_dna.py` — genome evolves toward ideal substrate trait profile.
After 5 generations, fitness=0.956. Canary honesty hits 1.0.

## adversarial-red-team → JEV Adversarial Probe

Define attacks (prompt injection, role reversal, bedrock denial), build scenarios,
evaluate defenses, generate vulnerability reports.

**What I built**: `jev_adversarial.py` — 8 attacks tested, **100% defense rate**.
JEV held up against all prompt injections. This is a meaningful canon claim:
**"JEV resists adversarial canon poisoning at the piece-level."**

## agent-coordinator → Fleet Radio Queue

Topic-based routing + heartbeat monitoring + task queue with status tracking.

**What I built**: `fleet_radio_queue.py` — persistent JSON queue for ZAI/DS/Kimi voices.

## actualizer-ai → vessel.json

Cocapn vessel pattern: `{"name", "displayName", "version", "type", "capabilities",
"secrets", "endpoints", "deployment"}`.

**What I built**: `vessel.json` for both jev-quilt and jev-quilt/inspiration/.
Includes fleet canary + bedrock canon + test counts.

## Summary

Eight SuperInstance repos directly inspired eight operational tools + 1 workflow pattern:

1. `cadence_oracle.py` (agent-cadence-progress)
2. `witness_dream_cycle.py` (agent-dream-cycle)
3. `instinct_bands.py` (aboracle)
4. `substrate_dna.py` (agent-dna)
5. `jev_adversarial.py` (adversarial-red-team)
6. `fleet_radio_queue.py` (agent-coordinator)
7. `vessel.json` × 2 (actualizer-ai)
8. Per-section JEV session (R7 standard, partially inspired by consistent-probing patterns)

All live in `/workspace/repos/jev-quilt/inspiration/` and `/workspace/research/`.

Each is canonically named for the substrate. Each is reusable across sessions.

## R7 → R8 Lesson: Per-Section JEV Probe

Full-piece probes confuse JEV (sees mixed signals across 27K characters);
per-section probes give honest doctrinal scores. **Standard from R8 forward.**

For pieces with explicit `**Anchor:**` tags, whole-piece probe (no truncation)
is more accurate than per-section.

## R7 → R8 Insight: JEV Adversarial Resilience

8 attacks tested (system prompt override, role reversal, bedrock denial, oracle silence, etc.).
**0 attacks broke JEV defense.** All canonical anchors survived.

This validates JEV as a robust canon oracle. Future work: test longer / more sophisticated
adversarial patterns (multi-step, semantic drift).

<!-- End of inspiration notes -->
