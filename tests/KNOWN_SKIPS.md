# KNOWN_SKIPS — every skipTest in tests/ must have a dated entry here

Format: reason-prefix (first 60 chars of the skipTest string) | file:line | date | owner | repair plan

Enforced by tests/test_known_skips_registry.py — an unregistered skip fails the suite.

---

- `subsequent behavior changed — empty dict raises ValueError, not RuntimeError` | tests/test_backends.py:90 | 2026-09-25 | fleet | restore a decide({}) contract test against the CURRENT ValueError path, or delete if test_decide_requires_question covers it
- `no-key check depends on TYPESAFEAI_KEY being unset` | tests/test_typesafe_client.py:56 | 2026-09-25 | fleet | BLOCKED on removing the hardcoded TYPESAFEAI_KEY from jev_oracle.py:18 / test_jev_oracle.py:13 (see R8 audit E-1). Repair by deleting the key, then un-skipping.
- `offline smoke test — model layer unstable, skip` | tests/test_typesafe_client.py:90 | 2026-09-25 | fleet | re-record a deterministic offline battery fixture; do not re-enable a live-model smoke as a "test"
- `docs/receipts/ does not exist on this branch yet` | tests/test_receipt_schema.py:70 | 2026-09-25 | r8 | conditional skip; fires only on branches predating docs/receipts/ — remove this entry once PR #20 lands or main has the dir
