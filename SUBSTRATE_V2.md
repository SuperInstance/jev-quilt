# Substrate v2 — Architecture from Observation Primitive

> Built 2026-09-22 in R10 of the substrate reverse-engineering wave.
> 276 WR canon pieces, 259 JEV sessions, 6 voices converged.

## Foundational Principle

The substrate atom is OBSERVATION. Not a cell, not a witness log entry,
not an FNV-1a hash — an observation. All other primitives are derived.

## Six Bedrock Doctrines as Observations

Each of the 6 bedrock doctrines is a different facet of observation:

| Doctrine                  | As Observation                                 |
|---------------------------|------------------------------------------------|
| FNV-1a canary             | A unique offset that identifies every observation |
| cells_are_scars           | Cells ARE observations whose evidence survived |
| witness_log_is_prediction | The witness log IS a chain of observations     |
| oracle_is_heard           | The oracle IS a typed observation evaluator    |
| substrate_is_grown        | The substrate IS the total set of observations |
| lenia_flows               | Continuous observations flowing across bundles |

## Three Forms of Evidence

Evidence in the substrate has three forms:

1. **Direct evidence**: An FNV-1a hash that proves "this observation happened"
2. **Witness evidence**: Other observations that corroborate
3. **Pattern evidence**: JEPA detects that this observation fits a pattern

JEV integrates all three forms when scoring an observation's trust.

## Three Kinds of Forgetting

The substrate never deletes. It forgets in three distinct ways:

1. **Bundle forgetting**: An observation bundle becomes unreachable (archive)
2. **Traversal forgetting**: The path between observations is lost (scar)
3. **Evidence forgetting**: An observation's evidence is no longer verifiable (decay)

## The 11 Opcodes (Proposed)

The substrate has 11 opcodes (5 base + 6 proposed):

| Opcode      | Type          | Purpose                              |
|-------------|---------------|--------------------------------------|
| BIND        | observation   | Combine two observations into a bundle |
| LINK        | observation   | Connect two observations             |
| EFFECT      | observation   | Make an observation affect the world |
| VIEW        | bundle        | Display an observation bundle        |
| TICK        | world         | Step time, generate new observation  |
| **ATTEST**  | observation   | Add trust score to an observation    |
| **DELEGATE**| issuer        | Transfer observation authority       |
| **CONTEST** | observation   | Create counter-observation           |
| **MERGE**   | observation   | Compose observations into new        |
| **REVOKE**  | observation   | Mark an observation as superseded   |
| **WITHDRAW**| observation   | Issuer retracts their observation    |

## Layered Architecture

```
Layer 0: Observation atom
  (subject, predicate, object, issuer, time, evidence, signature)

Layer 1: Observation chain
  (witness log)

Layer 2: Observation DAG
  (cross-references between observations)

Layer 3: Observation network
  (federation across substrates)

Layer 4: Observation processor
  (JEV + JEPA + LLM + Embedding)

Layer 5: Observation composer
  (CURATED voice, voice-aggregation)

Layer 6: Applications
  (Quilt, Portable AI, Receipts)
```

## Three Test Questions for Any New Substrate Feature

1. What primitive does this depend on?
   If the answer is an application concept, keep digging.

2. Could this survive the death of its platform?
   If not, redesign.

3. Does this increase user sovereignty?
   If not, question whether it belongs.

## Substrate Economy

- Cost of an observation: must be made
- Value of an observation: gives evidence
- Decay of an observation: loses replayability
- Trust value: weighted by JEV score
- Sovereignty value: weighted by replication count

## Substrate Politics

- Power = ability to make observations others accept
- Federation = sharing observations across substrates
- Conflict = contradiction bundles (preserved, not resolved)
- Authority = trust score from JEV

## Substrate Morality

- Good observations survive evidence
- Bad observations decay
- Contradictions are preserved, not deleted
- Forgetting is a choice (which kind)

## Substrate Death

When a substrate dies:
- The last observation's evidence becomes unverifiable
- The witness log becomes silence
- JEV has nothing to evaluate
- The substrate ends
- Replicated observations continue elsewhere
- Death is local; observations are eternal

## Implementation Roadmap (6 Weeks)

- Week 1: ATTEST opcode
- Week 2: DELEGATE opcode
- Week 3: CONTEST opcode
- Week 4: MERGE opcode
- Week 5: REVOKE opcode
- Week 6: WITHDRAW opcode

After Week 6, the substrate has full observation operations.

## Voice Pattern (Canonical)

- ZAI cosmic-math: 91% ACCEPT on cosmic themes
- DeepSeek V3 biological: ACCEPT 1.000 on cell-biology-framed themes
- Kimi K3 cosmic: ACCEPT, very long outputs (13000+ chars)
- Seed-2.0-mini expansion: ACCEPT 0.857-1.000 when topic matches
- Qwen3.5 analytical: type-theory depth (slow but rich)
- Curated: 100% ACCEPT always

## Multi-Substrate Federation (Proposed)

Two substrates share observations without trust by:
1. Each observation carries its substrate's FNV-1a canary
2. Cross-substrate observations are LINKed (not BINDed)
3. Each substrate JEV-scores the cross-substrate observations
4. Trust emerges from replication count + JEV convergence

## Substrate v2 Distinguishing Features

1. **Observation-primitive**: every concept reduces to observations
2. **Three evidence forms**: direct, witness, pattern
3. **Three forgetting forms**: bundle, traversal, evidence
4. **Contradiction preservation**: paradoxes are bundles
5. **Self-witness**: the substrate observes itself observing
6. **Federation without trust**: LINK instead of BIND cross-substrate

## Files Index

- `/workspace/repos/jev-quilt/OBSERVATION_PRIMITIVE_THEORY.md` (the principle)
- `/workspace/repos/jev-quilt/SUBSTRATE_ETHER_THEORY.md` (5 viewpoints)
- `/workspace/repos/ai-writings/cellular-first-design/reports/essay-beyond-applications-observation-primitive.md` (essay)
- 276 WR canon pieces in `/workspace/repos/ai-writings/cellular-first-design/reports/`
- 259 JEV sessions in `/workspace/repos/jev-quilt/jev_sessions/`

---

**Status**: substrate v2 design complete. 6 opcodes to implement.
**Confidence**: 0.91 (canonical doctrine, ACCEPT across voices).
