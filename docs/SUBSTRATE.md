# SUBSTRATE — what the quilt is made of

*Quilt is a concept before it is an architecture. This document is the
concept, written as algebra. Nothing here is new mathematics; the point
is that the fleet's doctrines are instances of old, respectable
structures, and saying so precisely is what lets them port across
languages without drift.*

---

## 1. Identity is a lattice

A cell is a point. The identity map is an embedding

    ι : Cells → ℤ²        (k, s)

This is the multigrid doctrine, already carved in the floor's tests:
**floats never touch identity**. (ℤ², +) is a free abelian group of rank
two; the quilt's grid is its Cayley graph. A coordinate is not "near"
another coordinate. Equality is exact because equality in ℤ² is exact.

## 2. Values are a ring, not a tolerance

The value domain is ℚ. The fixed-point format ℚ₁₆ = ℤ[1/10⁶] ⊂ ℚ is a
**subring**, not an approximation of ℚ. Exactness is not a precision
choice; it is closure: ℚ₁₆ is closed under + and × (up to the finite
representation), and equality in it is decidable. When the Python kernel
says `Q16(1,3) + Q16(1,6) == Q16(1,2)`, that is a ring computation, not
a float comparison with a lucky epsilon.

Everything the fleet calls "calibration," "confidence," or "viability"
must live in this ring or admit that it has left exactness. The
`to_f64_betrayal` port in the Rust substrate is the honest door:
projection may leave the ring, identity may not.

## 3. Hooks are a typed relation

    H ⊆ Cells × Cells × (ℚ⁺ ∪ {⊥}) × (State → Bool)

(q, ⊥) is the DEADBAND token. The fourth component is the `when` gate
added in v0.3 — hooks eat deltas, but they also *decline* deltas whose
shape is not theirs. In category language: H is a profunctor-thing at
best; resist the urge. It is a relation with a guard. Not everything in
the fleet needs to be a category. (The shed, not the cathedral.)

## 4. The engine is a fold

The event stream ε ∈ E* is the actual state. The Engine is a left fold:

    foldl step fabric₀ ε  =  fabricₜ

`step` = filter hooks (floor + predicate) → wake (catch up book) →
decide → viability floor → project → book. The fabric's mutable state is
a **cache** of the fold, always reconstructible from ε plus the books.
This is why replay ≡ truth is the design goal rather than a feature.

## 5. Receipts are a free monoid with a homomorphism

The bookkeeper's log is the free monoid (List, ++, []) over the
singleton receipt type. The chain is a monoid homomorphism

    chain : Receipt* → ({0,1}⁶⁴, ⊕-via-fnv1a)

and `verify` is the statement chain(replay) = recorded chain — i.e. the
log is a **list homomorphism**, which is why it parallelizes and
compresses. Hashing is fnv1a (integrity, not security) — the same
algorithm as the fleet's rate limiter and hermit's WAL, so the whole
fleet shares one notion of "chained."

## 6. The sheaf observation (the one fancy sentence)

Each cell's view of the fabric is a **local section**. The bookkeeper's
verify is the **gluing condition**: local histories agree on overlaps
because they replay from one shared event stream. A fabric whose books
verify is therefore a sheaf of consistent local histories over the cell
topology — the dormant `SuperInstance/sheaf-gossip` repos were reaching
for exactly this gluing, gossiped instead of folded. The bridge is real
and waiting; it is filed as a product seed, not built.

## 7. Plato, double-entry, first-person, RTS

These are the same shape wearing different clothes, and the quilt
borrows from all four:

| concept | what the quilt takes |
|---|---|
| **Plato** (rooms, occupants, affordances) | a cell is a room; a hook is an affordance; EFFECT is the spell |
| **double-entry bookkeeping** | every state change has two sides: the cell's new state AND its receipt; a book that doesn't balance is a lie |
| **first-person perspective** | a cell never sees the fabric — only its hooks' deltas and its own book; agency is local by construction |
| **RTS** | emit/wake is the tick; fog of war is the deadband + `when` gate; you do not re-decide what you cannot perceive |

Polyformalism is not decoration here. It is the proof that the concept
is portable: if five languages can hold the laws without breaking them,
the laws are the load-bearing part.

---

*v0, 2026-09-21. The math is old; the naming is ours.*
