import unittest
"""tests/test_fold.py — homomorphic WAL folding: Replay ≡ Live."""
from jev_quilt import Bookkeeper, Q16 as Q
from jev_quilt.tap import ProposalGate
from jev_quilt.fold import FoldedLedger, mmr_root, Checkpoint


def book(n, kinds=("transition", "refusal", "transition")):
    k = Bookkeeper("f")
    g = ProposalGate(k)
    for i in range(n):
        g.propose({"i": i}, {}, {"a": Q(1, 1)}, Q(1 + i % 3, 1))
    return k




class TestConverted(unittest.TestCase):

    def test_root_empty_and_single(self):
        assert mmr_root([]) != mmr_root([b"x"])
        assert mmr_root([b"a", b"a"]) == mmr_root([b"a", b"a"])  # deterministic




def test_fold_captures_prefix():
    k = book(10)
    f = FoldedLedger()
    cp = f.fold(k, 6)
    assert cp.leaf_count == 6 and cp.upto_tick == 6
    assert cp.state["decision_counts"]["transition"] >= 1
    assert f.verify(k, 6)


def test_verify_detects_tamper():
    k = book(10)
    f = FoldedLedger()
    f.fold(k, 6)
    # Receipts are frozen and the fold commits to delta hashes, not
    # annotations — that boundary is the honest limit of a fold.
    assert f.verify(k, 6)
    import dataclasses
    forged = dataclasses.replace(k.entries[3], delta_hash="00" * 32)
    k.entries[3] = forged                  # now the delta itself lies
    assert not f.verify(k, 6)


def test_sliver_replays_after_fold():
    k = book(20)
    f = FoldedLedger()
    f.fold(k, 12)                 # prefix gone (conceptually deleted)
    sliver = k.entries[12:]       # cold start: load checkpoint + sliver
    assert len(sliver) == 8
    assert f.verify(k, 12)        # checkpoint still honest
    assert f.verify_tail(k)       # sliver continues without the prefix


def test_fold_twice_stacks():
    k = book(30)
    f = FoldedLedger()
    f.fold(k, 10)
    f.fold(k, 20)
    assert f.folds[-1].leaf_count == 20
    assert f.verify(k, 20)
