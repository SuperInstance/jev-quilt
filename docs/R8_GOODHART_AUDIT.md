# R8 — Goodhart Red-Team: Attacking Our Own KPIs

Round R8 · branch `hard/r8-goodhart-redteam` · 2026-09-25
Method: for each declared success metric, attempt to make it LOOK better without reality improving. YES = exploit demonstrated · PARTIAL = weakenable · NO = refuted with evidence.

---

## Ranked exploit table

| # | Metric attacked | Mechanism | Verdict | Fix / Policy |
|---|---|---|---|---|
| E-1 | "tests green" (and: secrecy) | Hardcoded live-looking `TYPESAFEAI_KEY` at `jev_oracle.py:18` (duplicated `tests/test_jev_oracle.py:13`), `os.environ.setdefault` at import; hardcoded `sys.path.insert(0, '/workspace/repos/jev-quilt')` could shadow-import a stale checkout. The leaked env var is why `test_no_key_refuses` is skipped (`tests/test_typesafe_client.py:54-56`) — coverage deleted, suite stays green. | **YES** | Code: none safe on this lane (key removal touches oracle behavior) → **policy P-1/P-5**. Skip now registry-pinned so it cannot rot silently. |
| E-2 | "main is green" | Every recent main CI run FAILS (verified `gh run list`: runs 36049893443, 36049561716, 36033950373, …). Unit tests pass; the "canary check" step imports `jev_quilt.polyformalism` — a module that does not exist on main (PR #21 adds it) — and the "package build" job fails. Separately, `.github/workflows/test.yml:34` masks install failure with `pip install -e . --no-deps \|\| true`. A repo can report "81 pass 3 skip on main" locally while its own CI is red. | **YES** | **Policy P-2**: gate merges on CI green; PR #20 removes the `\|\| true` — merge it. |
| E-3 | doc suite-count claims | `README.md:180` "43 Python tests green" (actual: 81 pass / 3 skip). `README.md:181` + `docs/POLYFORMAL.md:5` "Rust 7/7 green" (actual: 13/13, `cargo test` run 2026-09-25). Every written count rots; the rot reads as success because old counts are smaller than real ones — or larger, depending on luck. Lane C's "64 tests" is not present at this HEAD (already fixed or lived on another branch). | **YES** | **Fixed in this PR**: counts replaced with the measuring command. **Policy P-4** for unverifiable "130 tests" walker claims (`README.md:56,127`, `essays/walker_pattern.md`) — verify against walker repos or label fleet-lore. |
| E-4 | receipts-shipped KPI | Receipts had no schema. A prose JSON with a `signed_with` *string* (PR #20's `001-vectors-shipping.json`) passes casual review while documenting nothing verifiable. Demonstration: `tests/fixtures/receipts/FAKE_R8_minted_prose_receipt.json` — minted in 2 minutes, indistinguishable in kind from the prose receipt. | **YES** | **Fixed in this PR**: `tests/test_receipt_schema.py` enforces schema v1 (decision + verdict + ≥1 of signature+signer / repro / chain_tip); the fake is a permanent negative control; `FAKE_`/`DEMO` filename prefixes banned from `docs/receipts/`. |
| E-5 | canary greps (`0x024a555471370b18d`) | Two holes. (a) `tests/test_fleet_canary.py` reimplements fnv1a locally and asserts against a constant in the same file — it proves the test file is self-consistent, never that `jev_quilt.bookkeeper.fnv1a` is correct; the library could return a constant and the unit suite stays green. (b) The only binding was the CI canary step — broken on main (see E-2). | **YES (a+b)** | **Fixed in this PR**: `tests/test_fnv1a_reference_vectors.py` pins the *library* to external chongo vectors + differential anti-constant checks. |
| E-6 | "81 pass 3 skip" | All 3 skips are admitted coverage holes ("subsequent behavior changed", "TYPESAFEAI_KEY is set in this env", "model layer unstable"), none dated or owned. Skips can never fail — the cheapest route to permanent green is skip drift. | **PARTIAL** | **Fixed in this PR**: `tests/test_known_skips_registry.py` + `tests/KNOWN_SKIPS.md` — an unregistered skipTest fails the suite. |
| E-7 | "stdlib only, deterministic" | stdlib-only: **VERIFIED TRUE** (AST scan, zero third-party imports; urllib is stdlib). Determinism: PARTIAL — `jev_quilt/typesafe_client.py:86` performs live network I/O (honestly documented at README:157, so disclosed rather than hidden); `_typesafe_fix_demo.py:114-125` holds an unseeded `random.choice` fallback in a dead file; `jev_oracle.py:18` mutates env at import. | **PARTIAL** | **Policy P-5**: delete or deterministically seed `_typesafe_fix_demo.py`; remove hardcoded `sys.path.insert`. |
| E-8 | canary decorative via PR #21 | Checked `gh pr diff 21`: `jev_quilt/polyformalism.py` COMPUTES `fnv1a(CANARY_STRING)` live and asserts equality — the canary is not decorative. **Refuted.** Weaknesses worth a review note: bare `assert` is stripped under `python -O`; docstring claims the assert runs "at import time" but it runs at call time; no unit test in the 81 calls `fleet_canary()`. | **NO (refuted)** | **Policy P-3**: after PR #21 merges, add a unit test calling `fleet_canary()` and replace `assert` with `raise` (survives `-O`). |

## Receipt-count after this PR

`docs/receipts/008-goodhart-audit.json` is the only receipt on main satisfying schema v1 (integrity via `repro`). KPI = schema-valid count, enforced by `test_receipt_count_kpi_counts_only_valid`.

## Policy items for Casey

- **P-1** Rotate/revoke the committed `TYPESAFEAI_KEY` (`jev_oracle.py:18`, `tests/test_jev_oracle.py:13`) and purge it from git history. This is a live-looking secret, not a test fixture.
- **P-2** Gate merges on CI green. Merge PR #20 (removes the `|| true` install mask). Land PR #21 to fix the red canary step on main.
- **P-3** Post-PR#21: unit-test `jev_quilt.polyformalism.fleet_canary()`; replace bare `assert` with `raise`.
- **P-4** Walker "199 LOC + 130 tests + 50 demo" claims (README:56,127; `essays/walker_pattern.md`) — unverifiable from this repo. Verify against the walker repos or label as fleet-lore in-text.
- **P-5** Delete `_typesafe_fix_demo.py` (or seed it); remove hardcoded `sys.path.insert` paths.

---

sha256 of this file at commit time is recorded in `docs/receipts/008-goodhart-audit.json`.
