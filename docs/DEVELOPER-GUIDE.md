# jev-quilt — Developer Guide

## Code layout

```
jev_quilt/                 the reference kernel (32 modules, ~4.5k lines)
  __init__.py              the exported surface; read this first for the map
  cell.py                  Cell / Hook / Projection, DEADBAND, viability floor
  engine.py                the delta runtime: emit → hook cares → floor → wake
                           (wake = replay book, then decide; WakeResult names why)
  bookkeeper.py            per-cell append-only WAL; fnv1a-64 chain over UTF-8;
                           Receipt binds residue text; refuse-don't-round
  q16.py                   exact rationals: coprime invariant, from_float 1e-12 refusal
  backends.py              resolve_backend: auto → q16 → openjev-local → typesafe-api
  typesafe_client.py       TypeSafeBackend: POST /v1/systemone, decide_batch
  predictor.py             MeanPredictor, surprise, alarm — feeling under the ledger
  readings.py              ConstReading / NgramReading / DriftReading / TendencyReading /
                           ReadingEnsemble — how a cell senses
  imagine.py               WorldModel, imagine_choice / imagine_score (counterfactuals)
  witness_rng.py           deterministic RNG seeded from substrate state/book
  opposites.py             canonical-vs-inverted phrase table (the landmines)
  tap.py                   TapGate / ProposalGate / kl_divergence (law 5: the TAP)
  fold.py                  FoldedLedger, Checkpoint, mmr_root
  standing.py, commons.py, diploma.py, claim.py, attest.py, orgbook.py,
  schoolhouse.py           the observation-primitive layer: Standing, Commons/Deposit,
                           Diploma issue/verify, Claim, Attestation, OrgBook/Dispatch,
                           Schoolhouse/Enrollment
  blake3.py, ed25519.py, signed_receipts.py   receipt v2 signing stack
  jeviter.py               the homeostatic iterator, same doctrine as the jeviter repo
  jepa_slot.py             JEPA self-prediction slot
  throttle.py, calibrate.py, inquire.py, experiments.py, _typesafe_fix_demo.py
jev_oracle.py              the 14-probe submission validator (root-level CLI)
continuous/                the durable canon battery (probe + analyzer + example_run)
jev_sessions/              486 raw probe session JSONs + history.jsonl
polyform/rust/             the metal port: Q16, Cell, Bookkeeper (cargo)
polyform/haskell/Cell.hs   phantom-typed port (UNVERIFIED — no ghc on build nodes)
polyform/mercury/bookkeeper.m  law 4 as logic (UNVERIFIED — no mmc)
polyformalism/             fnv1a reference in rust / c / python
tools/jev_kat_bridge.mjs   KAT bridge to AI-Writings' jev_kat instrument
                           (run: needs TYPESAFEAI_KEY; gate: offline)
vectors/                   signed-receipt + G20b/G20c reader known-answer vectors
tests/                     257 tests (measured 2026-10-04) + KNOWN_SKIPS.md registry
  receipts/                hardening-decision receipts; fixtures/ incl. FAKE_R8 minted-prose
examples/                  doctrine demos: dialogue_spine, fleet_pudding, flywheel(+_watch),
                           two_mirrors, elephant, echogram, rough_seas, exp_* experiments
essays/, assets/, docs/    the doctrine corpus (see KNOWLEDGE-MAP.md)
```

## Core concepts

1. **Cell** (`cell.py`) — the unit. Identity is `coord=(k, s)` integer tuple +
   declared type; a float coord raises TypeError (law 1). Carries hooks, a
   decision payload, backend, outputs (projections), bookkeeper flag, optional
   predictor and surprise floor.
2. **Hook** — subscription to a sibling's *delta* with a floor. `floor=DEADBAND`
   or a Q16 magnitude; optional `when` predicate declines deltas whose shape
   isn't the hook's ("touch shallow"). Law 2: hooks eat deltas, not values.
3. **Engine** (`engine.py`) — `emit(source, delta, state)` fans out; each hooked
   cell either wakes (replay book → decide → project) or is booked
   `silent_deadband` / `rejected` / `refused` / `no_hook`. WakeResult carries the
   reason — never a bare bool.
4. **Bookkeeper** (`bookkeeper.py`) — append-only `(tick, state_hash, delta,
   decision_receipt)` rows in a fnv1a-64 hash chain pinned to the fleet canary.
   Replay ≡ live is law 4; `verify()` re-walks the chain. G20a typed uncapped
   decision fields; residue text is bound into the receipt.
5. **Backends** (`backends.py`) — `auto` resolves exact-first: `q16`
   (deterministic, always available) → `openjev-local` (if reachable) →
   `typesafe-api` (if `TYPESAFE_API_KEY`/`TYPESAFEAI_KEY` set). Cloud last.
6. **The TAP** (`tap.py`) — law 5: viability is binary, difference is not.
   ProposalGate grades above the floor; kl_divergence compares profiles.

## How to extend

### Add a new decision backend

1. Open `jev_quilt/backends.py`; mirror `Q16Backend`: implement
   `decide(state, question) -> BackendDecision` (typed fields, uncapped — G20a).
2. Register it in `resolve_backend`'s chain with an explicit name
   (like `"openjev-local"`), keeping the exact-first ordering doctrine: any
   deterministic backend resolves before any model backend.
3. Add tests in `tests/test_backends.py` covering: no-question refusal
   (`ValueError` path — see the registered skip note), overflow/refusal
   behavior (refuse, never round), and decision field types.
4. If it needs a network, it must read credentials from env only, and its
   offline behavior must degrade to refusal, not exception storms.

### Add a kernel module to the public surface

1. Write the module with a doctrine header comment (see any existing module:
   the laws it implements are named in the docstring, pinned by tests).
2. Export it in `jev_quilt/__init__.py` and append to `__all__`.
3. Add `tests/test_<module>.py`; property-style tests go through
   `tests/property_runner.py` (see `test_props_*.py` for the pattern).
4. Run `python3 -m unittest discover -s tests -q` and quote the measured count
   in your receipt — never write a count you did not run.

### Add a probe to the oracle or the canon battery

- Oracle probes: extend `PROBES` in `jev_oracle.py` (tuples of
  `(name, instruction)`); keep the 14-probe scoring aggregation and verdict
  thresholds in `JEV_ORACLE_SPEC.md` in sync with what the code does.
- Canon battery: follow `continuous/README.md` "Maintenance": add
  `(qid, "noul", spec_text, doctrinal_kind)` to `QUESTION_BANK` in
  `continuous/jev_continuous_probe.py` AND the same `qid → kind` mapping to
  `QUESTION_KIND` in `continuous/analyze_jev.py`; if bedrock, add explicit
  phrasing to `DOCTRINAL_STATE["doctrines"]`. Remember fix-stack rule 6: read
  tuple index 1 (qtype), not index 3.

### Add a language port

`polyformalism/` holds fnv1a references in rust/c/python; `polyform/` holds the
kernel ports. A port must reproduce the canary byte-exactly
(`fnv1a64("café Δ 日本語") == 0x024a555471370b18d`) and replay-verify a
bookkeeper log produced by the Python kernel. `tools/jev_kat_bridge.mjs` shows
the pattern for consuming a canonical instrument by commit+sha256 pinning
without copying it.

## Testing

```bash
python3 -m unittest discover -s tests -q
# Measured 2026-10-04: Ran 257 tests in ~39s — OK (skipped=6, expected failures=2)
```

- Green means: all discovered tests pass, every skip is registered in
  `tests/KNOWN_SKIPS.md` (enforced by `tests/test_known_skips_registry.py`),
  and the expected failures are the two registered xfail rows.
- Live-API tests are separate: `tests/test_jev_oracle.py` is a standalone
  script (`python3 tests/test_jev_oracle.py` with `TYPESAFEAI_KEY` set);
  `tests/test_integration_typesafe.py` skips itself when the key is absent.
- Property tests: `tests/property_runner.py` drives the `test_props_*.py`
  modules.
- Rust port (if a toolchain is present): `cd polyform/rust && cargo test` —
  13 tests green as of R8 (2026-09-25, rustc 1.95); unverified on nodes
  without cargo.
- Determinism check: `tests/test_replay_determinism.py` pins replay-equality
  including non-ASCII residue (`"café Δ 日本語"` fixtures).

## Conventions

- **Doctrine headers**: every module starts with the laws it implements; tests
  pin them, comments only point at them ("pinned by tests, not comments" is the
  fleet phrase; jeviter states it verbatim).
- **Receipt discipline**: claims ride on receipts. Hardening decisions get JSON
  receipts in `tests/receipts/`; probe sessions land in `jev_sessions/`; skips
  get registry rows with date/owner/repair plan.
- **Refuse, don't round**: q16 refuses non-representable floats (1e-12
  tolerance refusal) and bookkeepers refuse malformed rows; overflow is `None`
  in the Rust port. Never silently coerce.
- **Counts are measured**: README carries a stale count on purpose-ish — the
  rule is "do not write counts, run the suites." Your receipts quote what you
  measured.
- **Naming**: cells are dotted names (`npc.tone`, `spine.greeting`); receipts
  and sessions are snake_case; essays/images use numbered prefixes that match
  the asset tables in the README.
- **Env-only credentials**: `JEV_API_KEY` / `TYPESAFE_API_KEY` /
  `TYPESAFEAI_KEY`. No key literal anywhere, ever (R8 audit E-1 is the cautionary
  tale; the associated test skip stays open until it's fully gone).

## Gotchas for editors

- Touching `bookkeeper.py` breaks every port: the fnv1a-64-over-UTF-8 chain and
  receipt body layout are pinned by `tests/test_bookkeeper.py`,
  `tests/test_fnv1a_reference_vectors.py`, `tests/test_polyformalism.py`, and
  cross-verified byte-exactly by jeviter and other repos. Changing the body
  shape is a fleet-breaking event, not a refactor.
- Touching `engine.py`'s wake reason strings will break consumers that branch
  on `WakeResult.reason` (`"decided" | "silent_deadband" | "rejected" |
  "refused" | "no_hook"`); `examples/dialogue_spine.py` and the suite both read
  them.
- `tests/test_receipt_schema.py` has a conditional skip tied to
  `docs/receipts/` existence — if you add or remove that directory, revisit the
  KNOWN_SKIPS row.
- The oracle's `CANON_STATE` in `jev_oracle.py` is doctrine, not config:
  editing the doctrine strings changes probe behavior across the battery
  (state phrasing is the entire game — continuous README, "the lever").
- `jev_sessions/` is append-only evidence; do not "clean up" old session files
  or rewrite `history.jsonl` — the continuous battery's skip-on-fail law depends
  on history being an honest record.
- `_typesafe_fix_demo.py` is a demo/fix artifact, not dead code to delete
  without checking the R8 audit trail (docs/R8_GOODHART_AUDIT.md).
- The suite imports `tests/test_jev_oracle.py`? No — it is deliberately a
  script. Keep its `if __name__` entry point intact so discovery does not
  attempt live calls.
