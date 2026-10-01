# Mercury Spine — verify() as a theorem (design v0, uncompiled-honest)

STATUS: DESIGN DOC. No `mmc` on any fleet node as of 2026-09-21; every
claim below is a *statement to be proven*, not a proven fact. The day an
mmc lands, the acceptance block at the bottom is the contract.

This is §6.4 of JEV-SPEC: the formal spine. The Haskell Cell.hs and
mercury bookkeeper.m polyform files are sketches; this doc says what the
spine must state so the sketches can be promoted to claims.

## 1. What the spine is for

Python/Rust/TS/WASM/GDScript ports pin *behavior* (vectors, tamper,
back-compat). Mercury pins *why the behavior is enough*: that replaying
a hash-chained receipt log and re-running the engine are the same
operation, stated as logic predicates a compiler can check.

## 2. The three theorems

**T1 (receipt uniqueness / law 4 as logic).** Every state change of a
cell has exactly one receipt, and `receipt_n.chain = fnv1a(receipt_{n-1}.chain, payload_hash_n)`.
Stated in Mercury: `book/5` is `det` — total on all inputs, no silent
failure path. Refusal is a *booked* receipt ("refused"), never an
absence. Absence of a receipt for a state change is unrepresentable.

**T2 (wake = replay).** `wake_state(Receipts, Ticks, HeadChain)` is
`det`, and for every prefix `R_i` of `Receipts`:
`replay(engine, R_1..R_i) == state_i`. The engine is a fold over
receipts; boot-from-checkpoint is a fold from a certified prefix.
Corollary: compactification (checkpoints) cannot change semantics — it
only shortens the fold. This is the formal backing of the homomorphic
WAL compactification already shipped on main.

**T3 (floor and deadband as predicates).** Viability floor and deadband
are `semidet` predicates, not tunables smuggled in code:
`floor_holds(Cell) :- rational_exact(Cell.k), within_q16(Cell.k).`
`deadband_silent(Surprise, Width) :- abs_q16(Surprise) =< Width.`
Anything passing the floor with zero ethos must still be refused —
the floor is multiplicative, never additive (negative-space GAN
doctrine carries into the logic).

## 3. Hash status — honest placeholder

`bookkeeper.m` carries a LABELED placeholder hash until a fleet fnv1a
port exists in Mercury with the pinned vector
`café Δ 日本語 → 0x024a555471370b18d` (bytes-not-characters, per
JEV-SPEC §3). No theorem in this doc depends on the placeholder's
value; T1–T3 quantify over `payload_hash`, whatever its definition.

## 4. Acceptance when mmc lands (the contract)

1. `mmc --make` clean on the spine module; no `unsafe` equivalents.
2. All det/semidet annotations as claimed (T1 det-ness is checked by
   the compiler, not by review).
3. Pinned fnv1a vector reproduced in Mercury, both directions.
4. A tamper case that *fails to type-check or fails chain_valid* —
   never passes silently.
5. Empty-payload back-compat: the stored-hash rule of PR #2-era
   receipts replays unchanged.
6. This file's STATUS header flips to PROVEN with the mmc version
   pinned; until then it stays DESIGN DOC.

## 5. What this doc refuses

- It does not claim the current engine *satisfies* T1–T3. That proof
  needs the engine's semantics stated in the same logic — a bigger
  job, filed here as the sequel (spine v1: model the engine fold).
- It does not replace the executable ports as the operational gate.
  Ports catch regressions nightly; the spine is the explanation that
  must eventually catch the ports.
