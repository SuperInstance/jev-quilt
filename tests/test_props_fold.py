"""Property suite: jev_quilt/fold.py (homomorphic WAL compactification).

Docstring claims pinned here:
  - mmr_root: "Bagged-peaks MMR root over sha256 leaves (append-order
    matters)." -> determinism + order-sensitivity properties.
  - fold.py module: "recomputing the MMR over the sliver, seeded from the
    checkpoint root, must equal the root over the full chain. If the
    divergence is non-zero, the fold was a rumor." -> fold/verify
    agreement on honest books, and divergence detection on tampered
    folded prefixes.
  - verify docstring: "Replay ≡ Live: the prefix's recomputed root must
    equal the fold taken when it was collapsed."
  - verify_tail docstring: "The sliver after the fold must continue the
    chain honestly" -> see prop_verify_tail_detects_tampered_sliver
    below, which PINS A REAL VIOLATION OF THIS CLAIM on main
    (tracked as expected-failure in test_props_* wiring; receipt
    tests/receipts/005-r2-properties.json).

Empty-input behavior (documented implicitly by mmr_root's n == 0 branch
and fold's `prefix[-1] if prefix else 0` guards) is pinned explicitly:
fold(book, 0) yields an empty checkpoint and verify(book, 0) holds.
"""

from __future__ import annotations

import hashlib
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from jev_quilt.bookkeeper import Bookkeeper, Receipt
from jev_quilt.fold import FoldedLedger, mmr_root, _h

from tests.property_runner import run_property, DEFAULT_N


def _random_book(rng, max_n=30):
    bk = Bookkeeper(f"fold{rng.randint(0, 999)}")
    n = rng.randint(1, max_n)
    for i in range(n):
        bk.book({"v": rng.randint(0, 10 ** 6)}, {"d": rng.randint(0, 10 ** 6)},
                rng.choice(["kind_a", "kind_b", "kind_c"]), {"p": rng.randint(0, 100)})
    return bk, n


# ---------------------------------------------------------------- properties

def prop_mmr_deterministic(rng):
    """mmr_root is a pure function of the leaf list."""
    for _ in range(10):
        leaves = [hashlib.sha256(str(rng.random()).encode()).digest() for _ in range(rng.randint(0, 20))]
        if mmr_root(leaves) != mmr_root(list(leaves)):
            return False, {"n": len(leaves)}
    return True, None


def prop_mmr_empty_is_documented_constant(rng):
    """mmr_root's n == 0 branch: the empty tree hashes to a fixed
    constant (currently _h(b'mmr:empty')); pin the constant itself so a
    silent change to the empty-tree rule is caught."""
    want = _h(b"mmr:empty")
    for _ in range(5):
        if mmr_root([]) != want:
            return False, {"got": mmr_root([]).hex()}
    return True, None


def prop_mmr_append_order_matters(rng):
    """mmr_root docstring: 'append-order matters' — swapping two distinct
    leaves changes the root."""
    for _ in range(20):
        leaves = [hashlib.sha256(f"{rng.random()}".encode()).digest() for _ in range(rng.randint(2, 10))]
        swapped = list(leaves)
        i = rng.randrange(len(swapped) - 1)
        swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
        if leaves[i] == leaves[i + 1]:
            continue
        if mmr_root(leaves) == mmr_root(swapped):
            return False, {"i": i, "n": len(leaves)}
    return True, None


def prop_fold_verify_roundtrip_on_honest_book(rng):
    """fold.py module law: 'recomputing the MMR over the sliver, seeded
    from the checkpoint root, must equal the root over the full chain.'
    On main, fold() then verify() on an untouched book must agree."""
    for _ in range(10):
        bk, n = _random_book(rng)
        fl = FoldedLedger()
        upto = rng.randint(1, n)
        fl.fold(bk, upto)
        if not fl.verify(bk, upto):
            return False, {"n": n, "upto": upto}
        # state vector: counts must match the actual prefix composition
        cp = fl.folds[-1]
        want = {}
        for e in bk.entries[:upto]:
            want[e.decision_kind] = want.get(e.decision_kind, 0) + 1
        if cp.state["decision_counts"] != want:
            return False, {"counts": cp.state["decision_counts"], "want": want}
        if cp.leaf_count != upto or cp.upto_tick != bk.entries[upto - 1].tick:
            return False, {"leaf_count": cp.leaf_count, "upto": upto}
    return True, None


def prop_fold_of_empty_prefix_is_identity_checkpoint(rng):
    """Empty-input behavior vs the code's own guards: fold(book, 0) must
    produce upto_tick=0, the empty-tree root, empty counts, no last hash,
    and verify(book, 0) must hold afterwards."""
    for _ in range(5):
        bk, _ = _random_book(rng)
        fl = FoldedLedger()
        cp = fl.fold(bk, 0)
        if cp.upto_tick != 0 or cp.leaf_count != 0:
            return False, {"upto_tick": cp.upto_tick, "leaf_count": cp.leaf_count}
        if cp.root != mmr_root([]):
            return False, {"root": cp.root.hex()}
        if cp.state["decision_counts"] != {} or cp.state["last_state_hash"] is not None:
            return False, {"state": cp.state}
        if not fl.verify(bk, 0):
            return False, {"verify_empty": False}
    return True, None


def prop_verify_rejects_tampered_folded_prefix(rng):
    """verify docstring: 'Divergence = tamper or a lying checkpoint' —
    a folded prefix that is rewritten after folding must fail verify()."""
    for _ in range(10):
        bk, n = _random_book(rng)
        fl = FoldedLedger()
        upto = rng.randint(1, n)
        fl.fold(bk, upto)
        idx = rng.randrange(upto)
        e = bk.entries[idx]
        bk.entries[idx] = Receipt(tick=e.tick, state_hash=e.state_hash,
                                  delta_hash="00" * 32, decision_kind=e.decision_kind,
                                  payload_hash=e.payload_hash, payload=e.payload)
        if fl.verify(bk, upto):
            return False, {"tampered_idx": idx, "upto": upto, "verify": True}
    return True, None


def prop_verify_requires_matching_fold(rng):
    """verify() structural gates: no folds -> False; leaf_count mismatch
    in BOTH directions -> False. (Current code gates; pinned so refactors
    keep the gates.)"""
    for _ in range(10):
        bk, n = _random_book(rng, max_n=30)
        if n < 3:
            continue
        upto = rng.randint(2, n - 1)
        fl = FoldedLedger()
        if fl.verify(bk, upto):
            return False, {"verify_without_folds": True}
        fl.fold(bk, upto)
        if fl.verify(bk, upto + 1):          # asked to prove more than folded
            return False, {"upto_mismatch_accepted": "over"}
        if fl.verify(bk, upto - 1):          # asked to prove less than folded
            return False, {"upto_mismatch_accepted": "under"}
    return True, None


def prop_verify_tail_detects_tampered_sliver(rng):
    """VIOLATION OF DOCSTRING on main — pinned as expected-failure.

    verify_tail docstring: 'The sliver after the fold must continue the
    chain honestly'. But the implementation returns
        mmr_root(combined) != b"" if sliver else full == cp.root
    and mmr_root() never returns b"", so with ANY non-empty sliver the
    check is vacuously True: a tampered sliver receipt passes.

    This property asserts the DOCUMENTED behavior (tampered sliver ->
    verify_tail False). It fails on main. See
    tests/receipts/005-r2-properties.json -> violations_found."""
    for _ in range(10):
        bk, n = _random_book(rng, max_n=30)
        fl = FoldedLedger()
        upto = rng.randint(1, n - 1) if n > 1 else 1
        fl.fold(bk, upto)
        if n > upto:
            idx = rng.randrange(upto, n)
            e = bk.entries[idx]
            bk.entries[idx] = Receipt(tick=e.tick, state_hash=e.state_hash,
                                      delta_hash="ff" * 32, decision_kind=e.decision_kind,
                                      payload_hash=e.payload_hash, payload=e.payload)
            if fl.verify_tail(bk):
                return False, {"tampered_sliver_idx": idx, "upto": upto,
                               "verify_tail": True}
    return True, None


def prop_fold_recompute_is_idempotent(rng):
    """Folding the same prefix of the same book twice yields the same
    root and state vector (the fold is a pure function of the prefix)."""
    for _ in range(10):
        bk, n = _random_book(rng)
        upto = rng.randint(1, n)
        fl1, fl2 = FoldedLedger(), FoldedLedger()
        cp1 = fl1.fold(bk, upto)
        cp2 = fl2.fold(bk, upto)
        if cp1.root != cp2.root or cp1.state != cp2.state:
            return False, {"upto": upto}
    return True, None


PROPERTIES = [
    prop_mmr_deterministic,
    prop_mmr_empty_is_documented_constant,
    prop_mmr_append_order_matters,
    prop_fold_verify_roundtrip_on_honest_book,
    prop_fold_of_empty_prefix_is_identity_checkpoint,
    prop_verify_rejects_tampered_folded_prefix,
    prop_verify_requires_matching_fold,
    prop_verify_tail_detects_tampered_sliver,   # FAILS on main: docstring violation
    prop_fold_recompute_is_idempotent,
]


# ------------------------------------------------------- unittest wiring

import unittest  # noqa: E402


class TestFoldProperties(unittest.TestCase):
    def _check(self, fn):
        ok, cx = run_property(fn)
        self.assertTrue(ok, f"property {fn.__qualname__} failed: {cx!r}")

    def test_mmr_deterministic(self): self._check(prop_mmr_deterministic)
    def test_mmr_empty_constant(self): self._check(prop_mmr_empty_is_documented_constant)
    def test_mmr_append_order_matters(self): self._check(prop_mmr_append_order_matters)
    def test_fold_verify_roundtrip(self): self._check(prop_fold_verify_roundtrip_on_honest_book)
    def test_empty_prefix_checkpoint(self): self._check(prop_fold_of_empty_prefix_is_identity_checkpoint)
    def test_verify_rejects_tampered_prefix(self): self._check(prop_verify_rejects_tampered_folded_prefix)
    def test_verify_requires_matching_fold(self): self._check(prop_verify_requires_matching_fold)

    def test_verify_tail_detects_tampered_sliver(self):
        # FAIL-first: asserts the DOCUMENTED behavior; fails on main because
        # verify_tail's sliver check is vacuous. Marked expectedFailure in
        # the follow-up commit (see tests/receipts/005-r2-properties.json).
        self._check(prop_verify_tail_detects_tampered_sliver)

    def test_fold_recompute_idempotent(self): self._check(prop_fold_recompute_is_idempotent)


if __name__ == "__main__":
    unittest.main()
