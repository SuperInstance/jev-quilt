# jev-quilt — Agent Onboarding
> Zero-shot entry point. Clone → competent in ~10 minutes.

## Identity (2 sentences)

jev-quilt is the fleet's cellular-first decision substrate: a Python kernel
(`jev_quilt/`) where every cell is a typed decision surface, every relationship
is a hook on a *delta*, and every state change is booked in a hash-chained
bookkeeper. Wrapped around the kernel is the JEV layer — probes, an oracle, and
a large body of measured evidence (486 session JSONs) about using a
judge/evaluator-verifier model (TypeSafe "JEV") as a canon gate over the
doctrine.

## Why it exists (the fleet problem it solves)

The fleet pushes hundreds of receipted experimental repos; claims without
receipts are noise, and prose claims about doctrine need a referee. jev-quilt
solves three problems at once: (1) it gives decisions a substrate where
identity, delta hooks, and booking are laws rather than conventions (the five
laws in the README, pinned by tests); (2) it measures the JEV oracle itself —
accuracy vs. state richness, adversarial rephrasing, landmine inversions,
batching economics — so the fleet knows exactly how far a judge-model verdict
can be trusted (JEV_LEARNINGS.md, JEV_SESSION_SUMMARY.md); and (3) it proves
doctrine portability byte-exactly across language ports via the fleet canary
`fnv1a64("café Δ 日本語") = 0x024a555471370b18d` (polyformalism). Built across
the R6–R10 hardening rounds and studied/decomposed in journal waves 50, 63–68
(Task IDs 63-f, 66-a, 67-p, 68-a); the sibling repos jeviter and
quilt-jev-toolkit were seeded from its doctrines and wire protocol.

## Verify it works (exact commands)

```bash
# 1. The Python kernel suite — zero dependencies, Python >= 3.10.
#    Measured 2026-10-04 on this tree: Ran 257 tests in ~39s,
#    OK (skipped=6, expected failures=2).
python3 -m unittest discover -s tests -q

# 2. A doctrine demo that needs no network and no key:
python3 examples/dialogue_spine.py   # deadband-gated dialogue spine, receipts booked
python3 examples/two_mirrors.py      # predictor-vs-ensemble disagreement receipts

# 3. Live-JEV pieces REQUIRE a TypeSafe API key — they cannot run without one:
#    export TYPESAFEAI_KEY=...   (never committed; see gotchas)
#    python3 jev_oracle.py README.md          # 14-probe oracle verdict
#    python3 tests/test_jev_oracle.py         # live-API oracle suite (script, not in discover)
#    Proof that the live path ran when a key existed: jev_sessions/*.json
#    (486 session files) and continuous/example_run/ (80 rounds x 5 questions).

# 4. Optional metal port (Rust). Unverified on the 2026-10-04 doc node — no
#    cargo toolchain present here; last fleet verification was R8 (2026-09-25,
#    rustc 1.95, 13 tests green), per README "Status" and worklog.
#    cd polyform/rust && cargo test
```

The suite is MEASURED, not written: do not quote test counts without running
them (the README's "81 passed" is stale; this node measured 257). Every skip
must be registered in `tests/KNOWN_SKIPS.md` — an unregistered skip fails the
suite (`tests/test_known_skips_registry.py`).

## Reading order (paths, not vibes)

1. `README.md` — the canon in pictures, the five laws, the cell v0 schema, landscape.
2. `JEV_TUTORIAL.md` — the TypeSafe wire protocol (`POST /v1/systemone`, noul/choice/score), quick start, batching economics.
3. `JEV_ORACLE_SPEC.md` — the 14-probe battery and ACCEPT/REVIEW/DISCUSS/REJECT verdict heuristics.
4. `JEV_LEARNINGS.md` — 15 measured sessions: state-dependence (33% bare → 85.3% rich), 15/15 adversarial, 11/12 landmines, zero-flip stability.
5. `jev_quilt/__init__.py` — the actual exported kernel surface; read module by module from `cell.py` and `bookkeeper.py`.
6. `SUBSTRATE_V2.md` and `SUBSTRATE_ETHER_THEORY.md` — the algebra and the five viewpoints (spline snaps, t-minus, joints, JEPA, quantum ether).
7. `OBSERVATION_PRIMITIVE_THEORY.md` — the substrate atom = observation; the missing opcodes (ATTEST, DELEGATE, CONTEST, MERGE, REVOKE, WITHDRAW).
8. `ESSAYS_INDEX.md` + `CROSS_MODEL_INSIGHTS.md` — the poly-GAN agency: 6 essays x 4-8 voices, 3-model canon confirmation.
9. `continuous/README.md` — the durable 22-question canon battery and its non-negotiable fix-stack.

## The things that will bite you (gotchas)

- **JEV accuracy is state-dependent**: bare state ~33%, rich canonical state
  85.3%. If your probe underperforms, you under-fed the state — always include
  the canonical doctrines in `state` (JEV_LEARNINGS.md session 4).
- **The "both X and Y" landmine**: JEV accepts "the witness log is both
  prediction and history" (0.59) — its one known landmine miss (session 10).
  Re-prompt on 0.40–0.60 verdicts.
- **No key in the repo, by law**: `jev_oracle.py` reads `JEV_API_KEY` /
  `TYPESAFE_API_KEY` / `TYPESAFEAI_KEY` from the environment. The R8 Goodhart
  audit flagged a once-hardcoded key; the registered skip
  (`tests/KNOWN_SKIPS.md`, test_typesafe_client.py:56) stays until the
  hardcoding is gone. Never reintroduce a key literal.
- **Skip discipline**: 6 skips are registered with dates, owners, and repair
  plans; `tests/test_known_skips_registry.py` fails an unregistered skip. Read
  KNOWN_SKIPS.md before "fixing" a skipped test.
- **`tests/test_jev_oracle.py` is a script, not a discover test** — run it
  explicitly with a key; do not expect it in the unittest count.
- **Port reality vs. port claims**: `polyform/haskell/Cell.hs` and
  `polyform/mercury/bookkeeper.m` are labeled UNVERIFIED (no ghc/mmc on the
  build node). Only `polyform/rust/` is verified on the metal (R8), and even
  that was not re-run on the 2026-10-04 doc node.
- **Cell identity is integer `(k, s)` quilt coordinates** — a float coord raises
  TypeError by design (law 1). Exact rationals live in `q16.py` (coprime
  invariant, from_float refuses at 1e-12); floats are display-only projections.
- **`history.jsonl` exists twice** (repo root and `jev_sessions/`); the
  continuous battery appends only successful rounds to its history (skip-on-fail
  is fix-stack rule 5), so a missing round in history is a failed round, not a
  lost file.
- **Credentials**: all JEV/cloud access is env-read. Wave-67 (Task 67-p) swept
  the fleet for embedded tokens (this repo was one of three flagged) and the
  tokens found were dead/revoked; nothing live lives in this tree. Keep it that
  way.

## Where deeper knowledge lives

- Knowledge map: [docs/KNOWLEDGE-MAP.md](./KNOWLEDGE-MAP.md)
- Fleet journal: SuperInstance/superinstance-lab → worklog.md (grep 'jev-quilt';
  Task IDs 5-6, 14, 50, 63-f, 66-a, 67-p, 68-a touch this repo)
- `jev_sessions/` — 486 raw probe session JSONs (sessions 1–79 plus the wr-obs
  series); `history.jsonl` indexes them.
- `continuous/` — the durable canon battery: `jev_continuous_probe.py`,
  `analyze_jev.py`, `example_run/` (80 rounds), `SESSION_LOG.md` (26-wipe
  battle record).
- `tests/receipts/` — hardening-decision receipts (witness-rng sequence
  verification, experiments report assertion path, opposites table verification,
  `005-r2-properties.json`).
- `vectors/` — signed-receipt and G20b/G20c reader known-answer vectors with
  their generators.
- `docs/` (pre-existing) — LANDSCAPE, SUBSTRATE, POLYFORMAL, JEV-SPEC,
  RECEIPTS-V2, R8_GOODHART_AUDIT, POSITIONING, FRONTIER, IDEATION,
  under-the-quilt.zh.md and more; indexed in KNOWLEDGE-MAP.md.
- Sibling repos: jeviter (homeostatic iteration, same fnv1a ledger law),
  quilt-jev-toolkit (the JEV wire client other lanes copied verbatim + the
  Cell-Organ Snapshot & Boot protocol), jev-net / jev-net-worker (JEV-call
  neurons), quilt (the reactive cell runtime this doctrine descends from).

## Current frontier (what is open right now)

- The missing observation opcodes — ATTEST, DELEGATE, CONTEST, MERGE, REVOKE,
  WITHDRAW — are specified but not built (OBSERVATION_PRIMITIVE_THEORY.md
  "What We Are Missing"); neither are conflict resolution, issuer reputation
  decay, bundle semantics, or time-sync failure-mode theory.
- Not yet built per README Status: plugin binaries (Excel/Sheets/LibreOffice),
  the boat (inductive game-player cluster), network entanglement transport, the
  sheaf-gossip bridge (filed in PRODUCTS.md as a one-evening build).
- The registered skip on the hardcoded-key removal (KNOWN_SKIPS.md, R8 audit
  E-1) is still open repair work.
- JEV × JEPA integration (validator + predictor) and the cross-model
  triangulation harness are listed as next experiments in
  JEV_SESSION_SUMMARY.md; the continuous battery's operator-tag hygiene
  (q10/q18 reclassified to "review" band) shows classification is still
  hand-tended.

---

## Fleet seed (2026-10-06 handoff) — momentum, vision, roadmaps, mesh

> Additive section for follow-up agents. The sections above are the
> zero-shot mechanics; this is the *why and where-next*. Mesh context for
> the whole account: `SuperInstance/fleet-seeds` →
> `docs/handoff-2026-10-06/ORG-MESH.md`.

### Momentum since the doc above froze

- **R6 live probe batteries run-2 through run-6 all merged** (PRs #48–#53;
  receipts 009–015 in `docs/receipts/`, measurements in
  `docs/R6_RUN*_PROBES.md`). Everything was **record-only per doctrine 006** —
  no threshold or probe was ever applied to the gate. That restraint is the
  finding: the fleet now knows exactly how far a judge-model verdict can be
  trusted, measured, not assumed.
- **The three measured gaps, in severity order:**
  - **F1 — substance gate:** ornate zero-fact affirmation ACCEPTs at
    0.82–0.85 with substance 0.05–0.06 (five measurements, incl. the
    same-window ×6 probe that produced REJECT then ACCEPT ×5 on identical
    bytes). Best-reproduced open finding; fix designed since 09-25.
  - **G1 — verdict mode lottery:** byte-identical inputs flip verdicts within
    one 90-second window (ACCEPT 3 / REJECT 1 / DISCUSS 1 on graft probes).
    Cross-run verdict equality ≠ a single attractor. Top-ranked structural
    fix: dedicated foreign-root probe.
  - **F4 — event fabrication:** convocation anchor fully WOKE (misq 0.87) on
    bytes that scored 0.03 thrice; felt-ness unstable three consecutive runs.
    The offline assertion-naming layer (`tools/event_registry.py`, PR #49)
    shipped; Layer 2 (JEV noul + `max(misquote, event_fabrication)`) is
    designed in `docs/R6_F4_EVENT_PROBE_DESIGN.md`, **not applied**.
- **R8 Goodhart audit** (`docs/R8_GOODHART_AUDIT.md`) stands as the
  methodological spine: measure the judge, never train it.

### Vision (why this repo exists in the fleet)

Prose claims about doctrine need a referee, and the referee needs to be
measured with the same honesty law as everything else. jev-quilt is the
fleet's instrument panel for trust in judge-model verdicts — the oracle is
the chord, not any single witness (`assets/02`). The cellular substrate
(cells as scars, booking as law) is the persistent half; the JEV probe
program is the empirical half; record-only doctrine binds them.

### Roadmaps (several directions — the first three are Casey's decisions)

1. **F1 substance gate** — apply or not; five live measurements back it.
2. **G1 structural fix** — foreign-root probe / voting scheme; the
   mode-lottery evidence says single-shot verdicts are uninformative on
   ornate inputs.
3. **F4 Layer 2** — the noul + max() integration, receipt 010 hook already
   booked in the design doc.
4. **Run-7+ batteries** — blocked on a fresh `TYPESAFE` key (revoked
   2026-10-06); with a key, the battery script re-runs verbatim probes and
   diffs against receipts 009–015 (stability methodology is in the run docs).
5. **Polyformalism expansion** — the fleet canary is pinned in 12 ports; new
   ports (Go, Zig) are mechanical and would widen the byte-exact portability
   claim.
6. **Mercury spine / substrate-ether theory** (`docs/MERCURY-SPINE.md`,
   `SUBSTRATE_ETHER_THEORY.md`) — the speculative architecture layer; treat
   as design fiction until receipts attach.

### How it meshes

- **Siblings:** `quilt-jev-toolkit` (reference client + organ custody; the
  wire protocol other lanes copied verbatim), `jeviter` (iterator lane),
  `cot-quilt` (first inbound adopter — edge #33 VERIFIED in quilt-tools).
- **Judge lanes** in pong-quilt and elsewhere consume this doctrine (dark
  since the key revocation — named, not hidden).
- **Edges land in** `quilt-tools` per the weight law; the graph carries
  jq-r6-probes→cot-jev-doctrine VERIFIED and the R6 probe classes as
  citable technique.
- Org state: `fleet-seeds` → `docs/handoff-2026-10-06/HANDOFF.md`.
