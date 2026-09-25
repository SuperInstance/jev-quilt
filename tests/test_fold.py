"""tests/test_fold.py — homomorphic WAL folding: Replay ≡ Live."""
import unittest
import dataclasses

from jev_quilt import Bookkeeper, Q16 as Q
from jev_quilt.tap import ProposalGate
from jev_quilt.fold import FoldedLedger, mmr_root, Checkpoint


def book(n, kinds=("transition", "refusal", "transition"), salt=0):
    k = Bookkeeper("f")
    g = ProposalGate(k)
    for i in range(n):
        g.propose({"i": i + salt}, {"d": i + salt}, {"a": Q(1, 1)}, Q(1 + i % 3, 1))
    return k


class TestConverted(unittest.TestCase):

    def test_root_empty_and_single(self):
        assert mmr_root([]) != mmr_root([b"x"])
        assert mmr_root([b"a", b"a"]) == mmr_root([b"a", b"a"])  # deterministic


class TestFoldLedger(unittest.TestCase):
    """Every test in this file MUST be a TestCase method: the documented
    runner (`python3 -m unittest discover -s tests -q`) never collects
    module-level plain functions. This class converts the file's
    pytest-style functions (review flag on PR #29) — logic unchanged,
    including the tamper pin that silently never ran before."""

    def test_fold_captures_prefix(self):
        k = book(10)
        f = FoldedLedger()
        cp = f.fold(k, 6)
        assert cp.leaf_count == 6 and cp.upto_tick == 6
        assert cp.state["decision_counts"]["transition"] >= 1
        assert f.verify(k, 6)

    def test_verify_detects_tamper(self):
        k = book(10)
        f = FoldedLedger()
        f.fold(k, 6)
        # Receipts are frozen and the fold commits to delta hashes, not
        # annotations — that boundary is the honest limit of a fold.
        assert f.verify(k, 6)
        forged = dataclasses.replace(k.entries[3], delta_hash="00" * 32)
        k.entries[3] = forged                  # now the delta itself lies
        assert not f.verify(k, 6)

    def test_sliver_replays_after_fold(self):
        k = book(20)
        f = FoldedLedger()
        f.fold(k, 12)                 # prefix gone (conceptually deleted)
        sliver = k.entries[12:]       # cold start: load checkpoint + sliver
        assert len(sliver) == 8
        assert f.verify(k, 12)        # checkpoint still honest
        assert f.verify_tail(k)       # sliver continues without the prefix

    def test_fold_twice_stacks(self):
        k = book(30)
        f = FoldedLedger()
        f.fold(k, 10)
        f.fold(k, 20)
        assert f.folds[-1].leaf_count == 20
        assert f.verify(k, 20)

    def test_tail_detects_spliced_checkpoint(self):
        """V1 pin (found by hard/r2 properties, PR #26): a checkpoint spliced
        from a DIFFERENT chain must fail the tail check. Pre-fix verify_tail
        was vacuous (`mmr_root(combined) != b""` — a sha256 digest is never
        empty), so any non-empty sliver returned True."""
        ka = book(20)
        kb = book(20, salt=10 ** 6)   # same shape, different content
        f = FoldedLedger()
        f.fold(ka, 12)
        assert f.verify(kb, 12) is False      # different prefix, different root
        assert f.verify_tail(kb) is False     # the sliver is from another chain

    def test_tail_detects_tick_discontinuity(self):
        """A sliver with dropped/duplicated receipts (ticks no longer
        contiguous after upto_tick) must fail. Pre-fix: returned True."""
        k = book(20)
        f = FoldedLedger()
        f.fold(k, 12)
        del k.entries[15]                     # drop one receipt from the sliver
        assert f.verify_tail(k) is False
        k2 = book(20)
        f2 = FoldedLedger()
        f2.fold(k2, 12)
        k2.entries[16] = dataclasses.replace(k2.entries[16], tick=999)
        assert f2.verify_tail(k2) is False    # tick no longer continues the fold

    def test_tail_seeded_replay_equals_full_chain(self):
        """The module law, pinned directly: replaying the sliver seeded from
        the checkpoint's peaks must equal the from-genesis root over the
        full chain — for every fold point."""
        from jev_quilt.fold import _peaks, _bag, _push
        for upto in (1, 2, 3, 5, 8, 12, 19):
            k = book(20)
            f = FoldedLedger()
            cp = f.fold(k, upto)
            assert f.verify_tail(k)
            # seeded replay, recomputed by hand against the public surface
            stack = list(cp.peaks)
            for j, e in enumerate(k.entries[upto:]):
                _push(stack, upto + j, f.leaf(e))
            assert _bag(stack, len(k.entries)) == mmr_root(
                [f.leaf(e) for e in k.entries])

    def test_tail_anchored_mode(self):
        """Prefix-deleted deployments carry the head root out-of-band. The
        seeded replay must reproduce the anchor; a lying anchor fails."""
        from jev_quilt.fold import _peaks, _bag, _push
        k = book(20)
        f = FoldedLedger()
        cp = f.fold(k, 12)
        stack = list(cp.peaks)
        for j, e in enumerate(k.entries[12:]):
            _push(stack, 12 + j, f.leaf(e))
        head = _bag(stack, 20)
        assert f.verify_tail(k, expected=head)
        assert not f.verify_tail(k, expected=b"\x00" * 32)


if __name__ == "__main__":
    unittest.main()
