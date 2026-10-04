# jev-quilt — Knowledge Map
> The index of indexes. Everything deeper than the README, with one line on what each thing holds.

## In this repo

- `jev_quilt/` — the reference kernel: 32 modules (cell, engine, bookkeeper, q16,
  backends, predictor, readings, imagine, tap, fold, standing, commons, diploma,
  claim, attest, orgbook, schoolhouse, signed receipts, jeviter port, jepa_slot…).
- `jev_oracle.py` — the production 14-probe submission validator (root-level CLI).
- `continuous/` — the durable canon battery: `jev_continuous_probe.py`,
  `analyze_jev.py`, `example_run/` (80 rounds x 5 questions), `SESSION_LOG.md`
  (26-wipe record), its own `README.md` with the non-negotiable fix-stack.
- `jev_sessions/` — 486 raw probe session JSONs (sessions 1–79 plus the
  wr-obs/wr-N curated+zai series) + `history.jsonl` index; append-only evidence.
- `continuous_r001.json`, `canon_round_summary.json`, `vessel.json`,
  `history.jsonl` (root) — probe round artifacts and fleet vessel descriptors.
- `jev_sessions_continuous/` — per-wipe reports (47th…67th-wipe hourly reports).
- `runs/` — timestamped hourly-report runs (2026-10-01 … 2026-10-03).
- `research/`, `reports/` — hourly JEV report snapshots.
- `polyform/` — language ports: `rust/` (Cargo, verified R8), `haskell/Cell.hs`
  (phantom-typed; UNVERIFIED — no ghc), `mercury/bookkeeper.m` (law 4 as logic;
  UNVERIFIED — no mmc).
- `polyformalism/` — fnv1a reference implementations (rust/c/python) + README.
- `tools/jev_kat_bridge.mjs` — characterisation bridge to AI-Writings'
  `labs/jev-kat/jev_kat.mjs` instrument; pins by commit + sha256, never copies.
- `vectors/` — `signed_receipt_vectors.json`, G20b second-reader and G20c
  deposit-reader vectors + their generators.
- `tests/` — 257 tests (measured 2026-10-04) + `KNOWN_SKIPS.md` (the skip
  registry, enforced by test), `property_runner.py`, `r7_perf_harness.py`,
  `receipts/` (hardening-decision receipts), `fixtures/` (incl. the FAKE_R8
  minted-prose receipt used to prove forgery detection).
- `examples/` — runnable doctrine demos: `dialogue_spine.py` (measured
  spine_share), `fleet_pudding.py` (real lane decision, dogfood-recorded),
  `flywheel.py` / `flywheel_watch.py` / `flywheel_watch_positive_control.py`,
  `two_mirrors.py` (predictor-vs-ensemble disagreement), `elephant.py`,
  `echogram.py`, `rough_seas.py`, `watch_new_loops.py`, `jepa_slot_watch.py`,
  `exp_*.py` experiments + `run_all_experiments.sh`.
- `inspiration/` — vendored inspirations: cadence oracle, witness dream cycle,
  jev adversarial scripts with their results JSONs, `substrate_dna.py`,
  `vessel.json`, `INSPIRATION_NOTES.md`.
- `essays/` — the six multi-voice doctrine essays (indexed below).
- `assets/` — 28 canon images (00–24, two heroes) + `hero.mp4` +
  `polyformalism_12_ports.mp4`; each maps to a README doctrine table row.
- `docs/` — pre-existing doc layer (list below) + this wave-69 package.
- `download/decomposition-atlas`-equivalents: none in-repo; the wave-66
  decomposition JSONs live in the monorepo (worklog Task 66-a).

## Pre-existing docs (everything before wave-69)

- `README.md` — the canon in pictures (28-image tables), the five laws, cell v0
  schema, poly-GAN roster, landscape of JEV-likes, status + honest "not yet".
- `JEV_TUTORIAL.md` — the TypeSafe JEV wire protocol (POST /v1/systemone,
  noul/choice/score), quick start, batching economics, gotchas.
- `JEV_ORACLE_SPEC.md` — the 14-probe battery table, state format, output
  schema, verdict heuristics, validated test results.
- `JEV_LEARNINGS.md` — 15 measured sessions: state-dependence, knowns/unknowns,
  self-consistency profile, landmine table, "JEV will not validate" list.
- `JEV_SESSION_SUMMARY.md` — the executive summary of 12 probing sessions +
  the oracle's verdict bands and next experiments.
- `CROSS_MODEL_INSIGHTS.md` — 3 frontier models x 8 questions: 3/3 canon
  confirmation, the Kolmogorov-complexity divergence, the oracle-is-the-chord
  inversion; method and ~$0.05 cost receipt.
- `ESSAYS_INDEX.md` — the six essays with voice counts and the poly-GAN method;
  the reproduction recipe (brew scripts, now external).
- `OBSERVATION_PRIMITIVE_THEORY.md` — the substrate atom is OBSERVATION; the
  primitive→observation mapping; missing opcodes; the layer 0–6 stack; the
  three test questions for any new substrate feature.
- `SUBSTRATE_V2.md` — the algebra below the five laws (v2 substrate math).
- `SUBSTRATE_ETHER_THEORY.md` — the five viewpoints (spline snaps, t-minus,
  first-class joints, JEPA self-prediction, quantum ether).
- `PRODUCTS.md` — genre → product map (what the substrate could ship as).
- `SESSION_LOG.md` — the 26-wipe poly-GAN brew session record (what was built,
  image race costs).
- `ROUND_SUMMARY_R9.md`, `ROUND_SUMMARY_R10.md`, `ROUND_SUMMARY_R10_FINAL.md` —
  round-by-round hardening summaries (R9, R10, R10 final).
- `SUBSTRATE_VOICE_PATTERN_R9.md` — R9 voice-pattern study.
- `docs/LANDSCAPE.md` — the JEV-ecosystem research (TypeSafe Jev, SemIf,
  openjev, jevlike, NanoJev, browser-use/jev-ultrafast; HN caveat).
- `docs/SUBSTRATE.md`, `docs/POLYFORMAL.md` — the algebra; five laws x five
  tongues.
- `docs/JEV-SPEC.md` — the kernel-side JEV specification.
- `docs/RECEIPTS-V2.md` — signed receipt v2 (blake3 + ed25519) format doctrine.
- `docs/R6_JEV_DISTORTION_PROBES.md` — R6 distortion probe round.
- `docs/R8_GOODHART_AUDIT.md` — the Goodhart audit (incl. audit E-1: the
  hardcoded-key finding behind a still-open skip).
- `docs/MERCURY-SPINE.md`, `docs/POSITIONING.md`, `docs/FRONTIER.md`,
  `docs/IDEATION.md` — spine theory; where the repo sits; open frontier;
  genre ideation.
- `docs/under-the-quilt.zh.md` — the concept, in Chinese.
- `docs/landing/README.md` — landing-page sketch.
- `continuous/README.md`, `continuous/SESSION_LOG.md` — the battery's own
  doctrine and 26-wipe battle record.
- `tests/KNOWN_SKIPS.md` — every registered skip with date/owner/repair plan.
- `inspiration/INSPIRATION_NOTES.md`, `polyformalism/README.md` — provenance
  notes for vendored ideas and the fnv1a reference set.

## The essay files (one line each — the doctrine corpus)

- `essays/cell_as_scar.md` — 8 voices on "every cell is a scar recording where
  the substrate was already attempted" (geology/music/living-system metaphors).
- `essays/polyformalism.md` — 7 voices on byte-exact doctrine across 12 ports;
  each ends by pinning the canary 0x024a555471370b18d.
- `essays/oracle_chord.md` — 7 voices on "the oracle is the chord of
  substrate-witnesses agreeing, not any single model."
- `essays/walker_pattern.md` — 6 voices on the self-replicating walker unit
  (199 LOC + 130 tests + 50 demo) growing walkers.
- `essays/jev_bouncer.md` — 4 voices on JEV as the bouncer: speculators must
  show hit-rate ≥ 70% across ≥ 20 sessions or stay outside.
- `essays/witness_log_prediction.md` — 4 voices on the witness log AS
  prediction: the canonical past is the prior on the future (JEPA insight).

## In the fleet

- `SuperInstance/quilt` — upstream: the reactive cell runtime whose semantics
  jev-quilt generalizes into a decision substrate.
- `SuperInstance/jeviter` — downstream sibling: homeostatic iteration ("don't
  poll, rest and react"); its ledger hash-chain is pinned to the same café
  canary so receipts cross-verify with jev-quilt's Bookkeeper byte-exactly;
  jev-quilt also carries `jev_quilt/jeviter.py`, the Python port.
- `SuperInstance/quilt-jev-toolkit` — downstream sibling: minimal JEV wire
  client (other lanes copied `jev_client.py` verbatim — worklog Task 67-j) +
  canon gate + the Cell-Organ Snapshot & Boot protocol; runs the same
  noul/choice/score protocol jev-quilt's `typesafe_client.py` speaks.
- `SuperInstance/jev-net`, `SuperInstance/jev-net-worker` — downstream:
  JEV-call neurons, hosted nightly self-play (born wave-63).
- `SuperInstance/AI-Writings` — sibling instrument: `labs/jev-kat/jev_kat.mjs`
  is the canonical KAT for the JEV oracle instrument; jev-quilt pins it via
  `tools/jev_kat_bridge.mjs` (merged PR #70, 2026-09-29).
- `SuperInstance/duke-lab` — WASM port of the bookkeeper (receipt cross-verify
  partner); `SuperInstance/quilt-engine-ports` — GDScript port.
- `SuperInstance/tidepool`, `twist-engine`, `quilt-studio` — polyformalism
  siblings named in the README's family line.
- `SuperInstance/superinstance-lab` — the monorepo journal (worklog.md).

## In the journal

SuperInstance/superinstance-lab → worklog.md, grep `jev-quilt`. Task IDs that
touch this repo (verified 2026-10-04 against the local worklog):

- **Task 5-6** — surveyed jev-quilt among sibling repos (R10: 500 canon pieces,
  observation atom, 11 opcodes).
- **Task 14** — deep study: five laws, oracle-is-the-chord, cross-model
  insights; extracted the TypeSafe System One wire protocol from
  `typesafe_client.py` for quilt-cortex.
- **Task 50** — ecosystem recon: identified the JEV family (jev-quilt = JEV
  doctrine + systemone wire; jeviter; quilt-jev-toolkit).
- **Task 63-f** — census: jev-quilt systemone WIRE conformance 15/15 (09a4fd85).
- **Task 66-a** — substrate-family decomposition: studied cell.py, bookkeeper.py,
  q16.py, engine.py line-level; dog-food ran the suite (249 tests green then);
  20 parts written with file:line evidence.
- **Task 67-p** — credential sweep: embedded tokens found in three subrepo
  configs (incl. jev-quilt), all dead/revoked (401); receipted, not hidden.
- **Task 68-a** — remote census: si-fleet/jev-quilt +97 and jev-quilt +38
  commits ahead signals (others pushing).

## Receipts of record

- `tests/receipts/hardening-decision-witness-rng-sequence-verification.json` —
  the witness RNG hardening decision, receipted.
- `tests/receipts/hardening-decision-experiments-report-assertion-path.json` —
  assertion-path decision for experiments reports.
- `tests/receipts/hardening-decision-opposites-table-verification.json` —
  the opposites (landmine) table verification decision.
- `tests/receipts/005-r2-properties.json` — R2 property-run receipt.
- `continuous/example_run/` (80 rounds) + `continuous_r001.json` /
  `canon_round_summary.json` — proof the canon battery ran clean
  (Bedrock 7/7, Speculative 5/5, Adversarial 2/2 per continuous/README).
- `jev_sessions/session_8_adversarial.json` (15/15 adversarial),
  `session_10_landmines.json` (11/12), `session_7_consistency.json` (0 flips),
  `session_15_batching.json` (5 ms/q) — the load-bearing JEV measurements.
- `tests/fixtures/receipts/FAKE_R8_minted_prose_receipt.json` — the forged
  receipt used to prove the forgery detection path.
- `vectors/signed_receipt_vectors.json` + G20b/G20c vector files — known-answer
  proof for the signed-receipt stack.

## How to search further

```bash
# All JEV probe sessions mentioning a doctrine, e.g. "scar":
grep -l "scar" jev_sessions/*.json | head
# Session outcomes by number:
python3 -c "import json,glob; [print(f, json.load(open(f)).get('summary','')[:80]) for f in sorted(glob.glob('jev_sessions/session_[0-9]*.json'))]"
# Every receipted claim about the oracle:
grep -rn "verdict" JEV_ORACLE_SPEC.md JEV_LEARNINGS.md | head -30
# Skip registry state:
cat tests/KNOWN_SKIPS.md
# Fleet journal mentions:
grep -n "jev-quilt" /home/z/my-project/worklog.md
# Cross-repo canary pins:
grep -rn "0x024a555471370b18d" tests/ polyformalism/ essays/ | head
```
