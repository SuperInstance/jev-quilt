# POLYFORMAL — the five laws in five tongues

*One concept, many architectures. Each formalism holds the same laws;
where a formalism cannot hold one, the gap is labeled rather than hidden.
Verification status: **Python 43/43 green · Rust 7/7 green (cargo test,
rustc 1.95) · Mercury uncompiled (no mmc) · Haskell uncompiled (no ghc) ·
C below as struct sketch only.***

---

## Law 1 — identity never floats

| tongue | statement |
|---|---|
| Python | `Cell.coord: tuple[int, int]`; `Q16` normalizes to coprime; no `__float__` on identity paths |
| Rust | `struct Cell { coord: (i64, i64) }` — **no float constructor exists**; `to_f64_betrayal` named on `Q16` |
| Mercury | `receipt(tick, prev, kind, fp, chain) :: int` — the type is `int` everywhere |
| Haskell | `data Coord = Coord !Int !Int`; `toFloatBetrayal :: Q16 -> Float` lives only on `'Proj` |
| math | ι : Cells ↪ ℤ² (SUBSTRATE §1) |

## Law 2 — hooks eat deltas, not values

| tongue | statement |
|---|---|
| Python | `Hook(source, on="delta", floor=DEADBAND, when=pred)`; `Engine._passes_floor` + `_hook_cares` |
| Rust | `struct Hook { source, floor: Option<Q16>, when: Option<fn(&State) -> bool> }` (sketch, unbuilt) |
| Mercury | the guard is the `semidet` body of the wake predicate — failure = silence |
| Haskell | `floorQ :: Maybe Q16` — `Nothing` is the DEADBAND token |
| math | H ⊆ Cells² × (ℚ⁺ ∪ {⊥}) × Pred(State) (SUBSTRATE §3) |

## Law 3 — decide in one pass, project elsewhere

| tongue | statement |
|---|---|
| Python | `BackendDecision` is the only output of `backend.decide`; `Projection` is a *declaration*, not a call |
| Rust | `decide(&Question) -> Decision; // projections are data` |
| Mercury | det/semidet modes are the type system enforcing single-pass decidability |
| Haskell | `decide :: q -> Decision` is pure; effects only via the Booked class |
| math | decide ∈ E → D; project ∈ D → P; no decide → decide closure |

## Law 4 — every state change is booked

| tongue | statement |
|---|---|
| Python | `Bookkeeper.book()` on every wake; `verify()` replays the fnv1a chain |
| Rust | `Bookkeeper { tick, prev, log: Vec<Receipt> }`; `verify()` re-derives; **tamper test included** |
| Mercury | `chain_valid/2` is `semidet` — a false log has no proof |
| Haskell | `class Booked` — the receipt is part of the state type |
| math | chain : Receipt* → {0,1}⁶⁴, a list homomorphism (SUBSTRATE §5) |

## Law 5 — viability is binary, difference is graded

| tongue | statement |
|---|---|
| Python | `Cell.viability_floor(decision) -> bool`; `BackendDecision.value` carries the graded part |
| Rust | `decision.kind == "choice"` etc.; the floor is a `bool` function, never a threshold on floats |
| Mercury | modes again: `det` = viable, failure = not; the grade rides in `fp` |
| Haskell | the floor is a pure predicate; grading is data |
| math | viability ∈ {0,1}; grade ∈ ℚ₁₆ — different rings, kept apart on purpose |

---

## Honest gaps (polyformalism includes the cracks)

1. **Python fnv1a hashes codepoints, Rust hashes UTF-8 bytes.** Identical
   for ASCII; diverges for non-ASCII names. The chain is per-cell and
   self-consistent either way, but cross-language receipt comparison for
   non-ASCII cell names is BROKEN until the Python side goes bytes
   (`data.encode("utf-8")`). Filed; not yet fixed.
2. **Mercury `book/5` above ticks every receipt at 1** — real
   implementation must thread the tick counter through. The `semidet`
   `chain_valid` is the trustworthy part of that file.
3. **The C sketch is intentionally absent**: C's float/integer
   confusion is the disease law 1 exists to prevent; writing the
   substrate in C before the discipline is proven in safer metal would
   be theater. Rust is the compromise: manual enough to matter, strict
   enough to catch betrayal at compile time.
4. **Haskell `Booked` class is a contract, not an enforcement** — the
   type system cannot force you to call `receipt`. (Haskell lies about
   effects; Mercury does not. That is why Mercury gets the bookkeeper.)

---

*Rosetta status: the laws survived translation into every tongue tried.
The two compiled tongues agree with the tests. The rest are promises
with honest labels.*
