# JEV-SPEC — the substrate-neutral contract

*What a language must hold to call itself a JEV. This document says
nothing about Python. It says what the Python kernel, the Rust
substrate, and every future port must agree on — so that a receipt
written in one language verifies in another, and a world rolled in one
can be audited from another.*

*Companion to SUBSTRATE.md (the algebra) and POLYFORMAL.md (the
per-language reports). SUBSTRATE argues why these structures; JEV-SPEC
pins what they are.*

---

## 1. Core objects

A port implements five objects. Nothing else is normative.

1. **Cell** — an identity `(k, s) ∈ ℤ²`. Identity is exact; floats
   never touch it. `to_f64` (if offered) is a projection and must be
   named a betrayal in its own API (see SUBSTRATE §2).
2. **Hook** — a typed relation `H ⊆ Cells × Cells × (ℚ⁺ ∪ {⊥}) ×
   (State → Bool)`: (query, ⊥) is DEADBAND; the fourth component is
   the `when` gate — a broken predicate refuses or stays silent, it
   never silences a true wake (touch-shallow law).
3. **Engine** — a fold. `(state, stimulus) → (decision, receipts)`.
   The engine is a monoid action over the receipt chain: every
   decision appends, nothing rewrites.
4. **Receipt** — the unit of audit. Fields per bookkeeper law; see §2.
5. **Reading / Ensemble** (optional but recommended) — a predictor
   class with `predict()` / `update()`; an ensemble selects over
   readers by integer-weighted exact scores. Where the predictor
   class is wrong, that is the JEPA slot (see README's known gap) —
   the spec does not fill it, it marks the seam.

## 2. The exact-rational floor

The value domain is ℚ₁₆ = ℤ[1/10⁶], a subring, not an approximation.

- Arithmetic (`+`, `×`, comparisons, `argmax` over choices) is exact
  inside the ring or the port **REFUSES**. Never rounds silently.
- Energy/cross-multiplication comparisons (imagine path) stay in the
  ring; only an explicitly-named projection may leave it.
- `argmax` ties resolve deterministically (spec: lowest cell index in
  row-major (k, s) order) — a port must not inherit hash-order or
  float-order luck.

## 3. Hash-chained receipts

- Chain input per receipt: `tick | state_hash | delta_hash |
  decision_kind | payload_hash` (pipe-delimited, UTF-8).
- `state_hash` / `delta_hash`: fnv1a-64 over the canonical byte
  encoding of the cell deltas.
- `payload_hash`: fnv1a-64 over the UTF-8 bytes of the readable
  residue (capped — 200 chars in current ports; a cap change is a
  spec revision, not a local tweak). Empty residue keeps the stored
  hash (back-compat).
- **Verify re-derives.** A verifier recomputes `payload_hash` from
  the retained residue text and rejects on mismatch. A hash field
  that is chained but whose payload is not re-derived is a lie the
  chain cannot see (this exact bug shipped and was caught by the
  cross-language port — see PR #3's honest note).
- Tamper with any chained field ⇒ verify fails at that link. Hashing
  here is integrity, not security (fnv1a-64 is not collision
  resistance); the signature layer (verify-only receipts,
  non-repudiation across nodes) is v2, deliberately out of scope.

### Pinned vectors (every port runs these on day one)

| input | rule | expected |
|---|---|---|
| `b""` | fnv1a-64 | `0xcbf29ce484222325` |
| `b"a"` | fnv1a-64 | `0xaf63dc4c8601ec8c` |
| `"café Δ 日本語".encode("utf-8")` | fnv1a-64 over UTF-8 bytes | `0x024a555471370b18d` |

The third vector exists because Python's `ord()`-style and Rust's
UTF-8-byte rules diverge on non-ASCII; ports hash **bytes**, not
characters. The vectors are pinned in `tests/test_bookkeeper.py`
(crosslang branch, PR #3) and in the Rust suite; a port without all
three is not a port.

## 4. Wake, sleep, dormancy

- **Wake** is re-engagement with new support: `lastSeenTurn` advances
  or evidence grows. Dormant cells re-enter only when re-yielded by
  fresh evidence — equal-strength bounce-back by weaker churn is
  flicker and is forbidden (the fleet's flicker doctrine applies to
  any port carrying a ledger).
- **Learning is unconditional; feeling is not** — prediction updates
  happen on every tick; alarm/alarmlessness is booked as residue,
  never retro-edited.

## 5. Honest limits of this spec

- It pins *agreement*, not *performance*. Receipt caps, tick budgets,
  and MAX_ROLLS-style budgets are port decisions, must be named, and
  must be reported when hit.
- It does not specify transport (WAL files, HTTP, WASM) — only that
  whatever carries receipts preserves their bytes.
- It does not settle the JEPA slot: what plugs in behind
  `predict()`/`update()` when the predictor class is wrong is an
  experiment, not a contract.

## 6. Port order (Casey 12:50) and per-port notes

1. **TypeScript → twist-engine** — S/K meters are already scalar
   surprise; the port adds the ledger (cell/hook/receipt) around
   them. Substrate-gan judge scores become receipts. ~One evening;
   no float-identity exists there yet, so the floor is free.
2. **Rust → hermit/tidepool** — extend the existing polyform Rust
   substrate (receipt residue already ported, PR #2; fnv1a bytes
   rule pinned, PR #3) with cell/hook/engine. UniFFI note for
   tidepool WAL (P5 counters + P6 WAL contract).
3. **WASM → duke-lab** — `runArgument` receipts: fuel-metered,
   deterministic-replay (per the WASM receipts spec frontier note:
   FUEL metering, not epochs).
4. **Mercury formal spine** — `verify()` as a theorem; deadband and
   floor predicates as logic. Uncompiled-honest status quo of the
   Haskell/Mercury polyform reports carries over until proven.
5. **GDScript — trailing**, behind quilt-engine-ports.

Each port lands with the three pinned vectors, a tamper test, and an
empty-payload back-compat test before it claims the name.
