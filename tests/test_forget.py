"""G12 — provable forgetting. 1:1 with the predicate in GAPS.md and the test
plan in G12-architecture.md:

    C.deposit(k, a, 3); r0 = C.root()
    C.forget(k, a)                                    # books a tombstone leaf
    PASS iff C.recall(k) is None and C.weight(k, a) == 0
     AND     C.root() != r0                            # removal is a real, booked state change
     AND     mmr_root(surviving_leaves + [tombstone(k,a)]) == C.root()   # a peer replays the delta
     AND     after C.deposit(k, a, 1): C.weight(k, a) == 1   # no silent resurrection of old weight
"""

import copy
import hashlib
import unittest

from jev_quilt.commons import Commons, _leaf, _tombstone_leaf
from jev_quilt.fold import mmr_root


class TestForgetRemovesAndIsBooked(unittest.TestCase):
    def test_forget_removes_and_is_booked(self):
        c = Commons(quorum=1)
        c.deposit("route", "harbor", 3)
        r0 = c.root()

        c.forget("route", "harbor")

        self.assertIsNone(c.recall("route"))
        self.assertEqual(c.weight("route", "harbor"), 0)
        self.assertNotEqual(c.root(), r0)  # removal is a real, booked state change


class TestPeerReplaysErasure(unittest.TestCase):
    def test_peer_replays_erasure_to_same_root(self):
        c = Commons(quorum=1)
        c.deposit("route", "harbor", 3)
        c.deposit("route", "cove", 2)  # a surviving deposit alongside the forgotten one

        c.forget("route", "harbor")

        surviving_leaves = [_leaf(d.key, d.answer, d.weight) for d in c.deposits()]
        tombstone_leaves = [_tombstone_leaf("route", "harbor")]
        replayed = mmr_root(surviving_leaves + tombstone_leaves)

        self.assertEqual(replayed, c.root())


class TestNoSilentResurrection(unittest.TestCase):
    def test_no_silent_resurrection(self):
        c = Commons(quorum=1)
        c.deposit("route", "harbor", 3)
        c.forget("route", "harbor")

        c.deposit("route", "harbor", 1)

        self.assertEqual(c.weight("route", "harbor"), 1)  # not 4 — forgetting truly zeroed it


class TestEmptyTombstonesBackwardCompatible(unittest.TestCase):
    def test_empty_tombstones_root_is_backward_compatible(self):
        # Hard-coded expected-root vector: the pre-G12 root is
        # mmr_root over sha256(f"{key}\x1f{answer}\x1f{weight}") leaves,
        # sorted by (key, answer), with no tombstone leaves at all.
        def pre_g12_leaf(key, answer, weight):
            canon = f"{key}\x1f{answer}\x1f{weight}"
            return hashlib.sha256(canon.encode("utf-8")).digest()

        deposits = sorted([("k", "v", 2), ("m", "w", 1), ("n", "x", 4)])
        expected_root = mmr_root([pre_g12_leaf(k, a, w) for (k, a, w) in deposits])
        self.assertEqual(
            expected_root.hex(),
            "a9ed77e495460523232c19e392c9eb4dacd709b84ad419c31b0c61420bf36446",
        )

        c = Commons(quorum=1)
        c.deposit("k", "v", 2)
        c.deposit("m", "w", 1)
        c.deposit("n", "x", 4)
        # no forget() ever called: empty tombstone set

        self.assertEqual(c.root(), expected_root)


class TestForgetIsConfluent(unittest.TestCase):
    def test_forget_is_confluent(self):
        a = Commons(quorum=1)
        a.deposit("route", "harbor", 3)
        a.deposit("route", "cove", 2)
        a.forget("route", "harbor")

        b = Commons(quorum=1)
        b.deposit("route", "reef", 5)

        ab = copy.deepcopy(a).merge(copy.deepcopy(b))
        ba = copy.deepcopy(b).merge(copy.deepcopy(a))

        self.assertEqual(ab.root(), ba.root())
        self.assertTrue(ab.agrees_with(ba))
        # the forgotten pair stays gone in either merge order
        self.assertEqual(ab.weight("route", "harbor"), 0)
        self.assertEqual(ba.weight("route", "harbor"), 0)


class TestForgetAllAnswersForAKey(unittest.TestCase):
    def test_forget_all_answers_for_a_key(self):
        c = Commons(quorum=1)
        c.deposit("route", "harbor", 3)
        c.deposit("route", "cove", 2)
        c.deposit("other", "x", 9)

        c.forget("route")  # no answer given: clear every answer under "route"

        self.assertIsNone(c.recall("route"))
        self.assertEqual(c.weight("route", "harbor"), 0)
        self.assertEqual(c.weight("route", "cove"), 0)
        self.assertEqual(c.weight("route"), 0)
        # unrelated keys are untouched
        self.assertEqual(c.weight("other", "x"), 9)


if __name__ == "__main__":
    unittest.main()
