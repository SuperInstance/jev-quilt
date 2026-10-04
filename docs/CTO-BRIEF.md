# jev-quilt — CTO Brief

## One-paragraph value statement

jev-quilt converts an AI fleet's decision-making and doctrine-keeping from
ad-hoc prompting into a receipted substrate: typed cells that decide in one
pass, hooks that wake only on real change, and a hash-chained bookkeeper that
makes every state change — and every silence — auditable. Around that kernel it
has produced the fleet's most-measured picture of a judge-model oracle (JEV):
when to trust it, when it hedges, and what it costs. If the SuperInstance fleet
is a laboratory, this repo is both its nervous system prototype and its
metrology lab for AI-as-judge.

## What it does & for whom

For agent-fleet builders and platform teams evaluating LLM-as-judge systems:
(1) a zero-dependency Python decision kernel (cells, delta hooks, deadbands,
exact rationals, replayable per-cell ledgers) usable headless or embedded;
(2) a production JEV submission validator (14-probe battery, verdict bands) for
gating content against a doctrine corpus; (3) a durable canon battery that
continuously re-verifies the judge's classifications; (4) a polyglot port
discipline (Rust verified; Haskell/Mercury labeled unverified) pinned by a
byte-exact fleet canary. Consumers inside the fleet: jeviter (iterated its
doctrine), quilt-jev-toolkit (copied its wire client verbatim), jev-net
(JEV-call neurons), and every lane that cites JEV_LEARNINGS before trusting a
judge verdict.

## Maturity assessment

**Working prototype, hardening** — honestly between prototype and hardened:

- Kernel: working; 257-test suite green (measured 2026-10-04: 39 s, 6
  registered skips, 2 expected failures); replay determinism pinned by tests;
  zero runtime dependencies. But v0.3: no plugin binaries, no network
  entanglement transport, no boat (README "Not yet").
- Oracle: working in production sessions (9 canonical pieces gated: 1 ACCEPT /
  5 REVIEW / 3 DISCUSS / 0 REJECT; inverted doctrine correctly REJECTED);
  measured accuracy bands (85.3% rich-state, 15/15 adversarial, 11/12
  landmines) are documented with known failure mode ("both X and Y").
- Ports: Rust verified on the metal (R8, 2026-09-25, 13 tests); Haskell and
  Mercury explicitly labeled UNVERIFIED.
- Evidence discipline: 486 session JSONs, decision receipts in
  `tests/receipts/`, continuous battery example runs — the strongest maturity
  signal in the repo.

## Risks

| Risk | Status / mitigation |
|---|---|
| Credential leakage (the fleet's recurring failure) | Mitigated: env-read only; R8 audit E-1 flagged a once-hardcoded key; wave-67 sweep (Task 67-p) found only dead/revoked tokens; one test skip stays open until removal is complete |
| Judge-model dependency (API loss, drift, price) | Mitigated in doctrine: exact-first backend resolution keeps the kernel fully functional offline; the continuous battery detects drift; transport-swap precedent exists (Task 67-j reused the wire protocol with a different judge) |
| Oracle known-bias ("both X and Y" landmine passes, phrasing sensitivity) | Documented, not eliminated: 11/12 landmine detection; re-prompt rule for the 0.40–0.60 band; multi-model chord as second signal |
| Stale documentation / stale counts | Standing law: counts are measured not written; suite is the source of truth; this wave adds a doc layer that quotes measured numbers |
| Single-maintainer bus factor (fleet lanes come and go; lanes have died mid-task) | Mitigated by this documentation package, the exoj-style durability of `continuous/`, and the journal protocol |

## Cost profile

Effectively free to run offline: zero dependencies, no services, local suite
~39 s. Online costs are JEV calls: ≈ 0.001–0.005 USD per oracle submission;
batching amortizes to ≈ 5 ms/question; the cross-model chord probe cost ~$0.05
for 24 invocations (as recorded). The continuous battery is hours-cheap at
"hourly probe" cadence. No paid infrastructure is required; everything runs on
free tiers plus a pay-per-call judge API.

## Strategic options

- **Invest** (recommended if the fleet continues): the missing observation
  opcodes (ATTEST/DELEGATE/CONTEST/MERGE/REVOKE/WITHDRAW) and conflict
  resolution are the specified-but-unbuilt core; building them turns the
  substrate theory into a substrate. The JEV×JEPA validator+predictor pairing
  is the highest-leverage research next step already scoped in
  JEV_SESSION_SUMMARY.md.
- **Maintain**: the kernel is stable and cheap; keep the suite green, keep the
  battery running, let sibling repos consume it.
- **Harvest learnings**: even frozen, JEV_LEARNINGS + the oracle spec + the
  chord method are the fleet's best export on LLM-as-judge metrology.
- **Retire**: not recommended — downstream repos (jeviter, quilt-jev-toolkit,
  jev-net) and the fleet canary discipline depend on it.

## Integration surface

- **Upstream**: SuperInstance/quilt (the reactive cell runtime whose semantics
  it generalizes), TypeSafe JEV API (judge transport), DeepInfra/Z.ai/etc. (the
  poly-GAN chord voices).
- **Downstream**: jeviter (shares the fnv1a-64 ledger law and the café canary;
  cross-verifies receipts byte-for-byte), quilt-jev-toolkit (its
  `jev_client.py` protocol is the copied-verbatim JEV wire client; hosts the
  organ boot protocol), jev-net / jev-net-worker (JEV-call neurons), AI-Writings
  (the KAT instrument jev-quilt pins via `tools/jev_kat_bridge.mjs`), duke-lab
  (WASM port) and quilt-engine-ports (GDScript).
- **Fleet hygiene**: the canary `fnv1a64("café Δ 日本語") =
  0x024a555471370b18d` is the cross-repo handshake; any new port joins by
  reproducing it.

*Prepared for the wave-69 documentation package; all numbers above are either
measured in this working tree on 2026-10-04 or cited to their receipt.*
