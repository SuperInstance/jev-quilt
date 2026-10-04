# jev-quilt — Engineering Notes

## Architecture

Three layers, one law per layer: decide, book, prove.

```
            ┌──────────────────────────────────────────────────────────┐
  doctrine  │  essays/ · assets/ · ESSAYS_INDEX · CROSS_MODEL_INSIGHTS │
  corpus    │  OBSERVATION_PRIMITIVE_THEORY · SUBSTRATE_ETHER_THEORY   │
            └───────────────▲──────────────────────────────────────────┘
                            │ gated by
            ┌───────────────┴──────────────────────────────────────────┐
  JEV       │  jev_oracle.py (14-probe battery)                        │
  layer     │  continuous/ (22-question canon battery, hourly probe)   │
            │  jev_quilt/typesafe_client.py → POST /v1/systemone       │
            │  tools/jev_kat_bridge.mjs (instrument characterisation)  │
            └───────────────▲──────────────────────────────────────────┘
                            │ resolve_backend: auto → q16 → openjev → typesafe
            ┌───────────────┴──────────────────────────────────────────┐
  kernel    │  engine.py  emit → hooks → floor → wake(replay→decide)   │
  (v0.3)    │  cell.py    Cell/Hook/Projection, coord (k,s) integers   │
            │  bookkeeper.py  fnv1a-64 chained WAL, replay == live     │
            │  q16.py · predictor.py · readings.py · imagine.py · tap.py│
            │  signed_receipts.py · blake3.py · ed25519.py (receipt v2)│
            └───────────────▲──────────────────────────────────────────┘
                            │ ported byte-exact (canary
            ┌───────────────┴──────────────────────────────────────────┐
  ports     │  polyform/rust (verified R8) · haskell · mercury (labeled)│
            │  polyformalism/ fnv1a refs · duke-lab WASM · GDScript     │
            └──────────────────────────────────────────────────────────┘
```

Data flow of one decision: a delta arrives via `Engine.emit(source, delta,
state)`; each hooked cell's hook is checked (`on="delta"`, floor/deadband,
optional `when` predicate); below-floor deltas are booked as
`silent_deadband` and stop; a waking cell first replays its bookkeeper
(catch-up), then resolves its backend (`auto` prefers the deterministic q16
rule), decides in one pass, passes the binary viability floor (law 5 / the
TAP), and fires projections — which are other cells' inputs, never its own
renders (law 3). Every row is a hash-chained receipt; replay of the book
reproduces the state.

Parallel to the kernel, the JEV layer measures the judge: `jev_oracle.py`
validates submissions against the doctrine corpus; `continuous/` re-probes
JEV's canon classification on a schedule so drift or transport death is
noticed; `jev_kat_bridge.mjs` characterises the canonical instrument by
pinned-commit + sha256 without copying it.

## Invariants

- **I1 Identity never floats** (law 1) — enforced in `cell.py.__post_init__`
  (TypeError on non-integer `(k,s)`) and at compile time in
  `polyform/rust` (no float constructor). Q16 keeps the coprime invariant;
  `from_float` refuses at 1e-12.
- **I2 Receipt chain integrity** (law 4) — `bookkeeper.py` chains
  fnv1a-64-over-UTF-8 bodies; `verify()` replays from genesis; pinned by
  `tests/test_bookkeeper.py` and the fleet canary in
  `tests/test_fnv1a_reference_vectors.py` /
  `tests/test_fleet_canary.py` / `tests/test_polyformalism.py`.
- **I3 Replay determinism** — `tests/test_replay_determinism.py` asserts
  replay == live including non-ASCII residue; receipts carry no wall-clock.
- **I4 Silence is booked** — the engine never drops a below-floor delta;
  `WakeResult.reason="silent_deadband"` and a booked row are the proof
  (dialogue_spine's doctrine check asserts it).
- **I5 Skip registry** — every `skipTest` needs a dated
  `tests/KNOWN_SKIPS.md` row; `tests/test_known_skips_registry.py` fails
  otherwise.
- **I6 Env-only credentials** — `typesafe_client.py` raises a clear error with
  no key; R8 audit E-1 (docs/R8_GOODHART_AUDIT.md) is the registered residual.

## Failure modes & blast radius

- **TypeSafe transport dead** (observed: wave-67, Task 67-j — the
  TYPESAFEAI_KEY was lost): the oracle and battery become unavailable; the
  kernel is unaffected. Mitigation that worked fleet-wide: the wire protocol
  from `quilt-jev-toolkit/jev_client.py` was reused verbatim with a different
  judge (GLM via z-ai CLI); `continuous/` is the watchdog that notices.
- **Cloudflare 1010 / 403 / 422 / 503-class transport errors**: the
  continuous probe's fix-stack (User-Agent, Bearer header, type discriminators,
  jittered retry, skip-on-fail) exists because each was hit during the 26-wipe
  sessions; a run that hits them books nothing to history.jsonl (rule 5), so
  history stays honest.
- **Hashing drift in a port**: the canary test fails loudly; blast radius is
  the port only, because receipts are content-chained (a bad hash cannot forge
  history without failing `verify()` at its own row).
- **Bad oracle state phrasing**: JEV reads doctrinal state as the signal — a
  weak/dampened state can flip a verdict band. Contained by the battery's
  review-band honesty (q10/q18 reclassified to match measured behavior) and by
  JEV_LEARNINGS' phrasing-sensitivity tables.
- **Suite regressions**: caught by the 257-test suite; the skip registry
  prevents silent test-loss. A failing `test_known_skips_registry` means
  someone deleted or added a skip without paperwork.

## Performance & cost envelope

Measured numbers (receipts cited):

- Oracle latency: single batch of 14 questions ≈ 300 ms, ~1500–3000 input
  tokens, ~250–300 output tokens; ≈ 0.001–0.005 USD per submission at JEV
  pricing (JEV_ORACLE_SPEC.md "Cost & Latency").
- Batching: 1 q = 448 ms, 80 q = 435 ms ≈ 5 ms/q (JEV_LEARNINGS session 15);
  the toolkit's scale round measured 50 parallel calls in 3.3 s ≈ 66 ms/call.
- Canon battery: 80 rounds x 5 questions = 400 verdicts per run
  (`continuous/example_run/`).
- Local suite: 257 tests in ~39 s wall (measured 2026-10-04, Python 3.12);
  dialogue_spine and two_mirrors demos run in well under a second.
- Cross-model probe: ~$0.05 across 24 model invocations (CROSS_MODEL_INSIGHTS
  "Method") — [estimate label: cost figures are as recorded at run time].

## Operations

- Local: zero-dependency Python ≥ 3.10; run the suite, run the demos. No
  services to start.
- Live JEV: `TYPESAFEAI_KEY` (or `JEV_API_KEY` / `TYPESAFE_API_KEY`) from the
  environment; the client adds `Authorization: Bearer` and (in the continuous
  probe) the pinned User-Agent. Keys are never committed; wave-67 (Task 67-p)
  swept embedded tokens fleet-wide, the ones found here were dead/revoked, and
  the credential discipline since wave-67/68 is env-read only.
- Continuous: `continuous/jev_continuous_probe.py --rounds N --out DIR` then
  `analyze_jev.py`; designed to live in git so it survives sandbox wipes (the
  "26-wipe solution").
- No CI workflow file in this repo at the time of writing (unlike jeviter);
  the suite is run per-session and receipted in the journal — that is the
  operating habit, honestly stated.
- Fleet journal: SuperInstance/superinstance-lab → worklog.md, grep
  'jev-quilt'.

## Design decisions & why

1. **Exact-first backend resolution** (`auto → q16 → openjev-local →
   typesafe-api`). Deterministic decisions whenever possible; cloud is last
   and optional. Tradeoff: a q16 rule can only answer what its rule table
   encodes; the payoff is replayability and zero-cost offline operation.
2. **Per-cell bookkeeper (law 4) instead of a global WAL**. Each cell carries
   its own chain, so a cell is portable — the idea quilt-jev-toolkit's organ
   protocol later industrialized. Tradeoff: per-cell chain management; the
   payoff is replay == live at the unit that decides.
3. **Hooks eat deltas, not values (law 2)** with a deadband floor. A quieter
   world is the default; only surprising deltas wake logic. Tradeoff: you must
   book the silences (which the engine does) or quiet becomes indistinguishable
   from broken — the doctrine jeviter was spun from.
4. **The oracle is a chord, not a model** (CROSS_MODEL_INSIGHTS). Canon claims
   are confirmed across independent model families; JEV is one witness.
   Tradeoff: more calls per verdict; the payoff is measured (3/3 confirmation
   on bedrock, 3/3 rejection on speculation).
5. **Durable canon battery in git** (`continuous/`) instead of workspace-only
   research scripts. The 26-wipe battle produced a fix-stack that is now part
   of the contract; the probe surviving wipes is worth the repo noise.
6. **Measured-not-written documentation** ("do not write counts, run the
   suites"). The README deliberately carries a stale count as a visible
   reminder; receipts carry the real numbers. Tradeoff: docs go stale; the
   payoff is that no number in a receipt is a guess.
