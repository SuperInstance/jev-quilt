"""Hardening tests: jev_quilt.witness_rng.

Invariants promised by the module docstring, previously enforced by
nothing (test_substrate_springs covers seed replay, dyadic rolls, and
zero-weight never-picked — everything else below was unenforced):

  * "Stable under key order": seed_from_state must not depend on dict
    insertion order.
  * WitnessRng.pick: total (empty options raise, not hang), in-options
    (never returns a non-member), and replay-identical for one seed.
  * WitnessRng.below(q) is EXACTLY next_q16() < q — replaying the same
    seed must reproduce the same comparison, edge values included.
  * seed_from_book tail semantics: tail=1 over a non-empty book equals
    the default (last receipt seals the chain tip); tail=n seals
    receipts[-n:] as a joined window; two empty books share the
    pre-first-decision (empty-witness) seed.
  * weighted(): empty dict raises; the pick is a key of the dict and
    replay-identical for one seed.

Stdlib unittest only; deterministic; no network; no floats consulted.
"""

import unittest

from jev_quilt import Q16, WitnessRng, seed_from_state, seed_from_book
from jev_quilt.bookkeeper import Bookkeeper
from jev_quilt.cell import Cell, Hook
from jev_quilt.engine import Engine


def _book(n=5):
    # a cell only books when a hook WAKES it (engine.emit skips unhooked
    # cells) — the hook is load-bearing, not decorative
    eng = Engine()
    eng.register(Cell("s", (0, 0)))
    eng.register(Cell("a", (1, 0), input_hooks=[Hook("s")]))
    for t in range(1, n + 1):
        eng.emit("s", {"mag": Q16(1)}, state={"t": t})
    return eng.books["a"]


class TestSeedFromState(unittest.TestCase):

    def test_key_order_stable(self):
        s1 = seed_from_state({"alpha": 1, "beta": 2, "gamma": [3, 4]})
        s2 = seed_from_state({"gamma": [3, 4], "alpha": 1, "beta": 2})
        self.assertEqual(s1, s2)

    def test_different_states_diverge(self):
        self.assertNotEqual(seed_from_state({"x": 1}), seed_from_state({"x": 2}))

    def test_seed_is_64bit(self):
        self.assertLess(seed_from_state({"x": 1}), 1 << 64)


class TestPick(unittest.TestCase):

    def test_empty_options_refuse(self):
        rng = WitnessRng(seed_from_state({"w": 1}))
        with self.assertRaises(ValueError):
            rng.pick([])

    def test_picks_are_members_and_replay_identical(self):
        options = ["fork", "bind", "sever", "link"]
        s = seed_from_state({"room": "tavern"})
        r1 = WitnessRng(s)
        r2 = WitnessRng(s)
        seq1 = [r1.pick(options) for _ in range(32)]
        seq2 = [r2.pick(options) for _ in range(32)]
        self.assertEqual(seq1, seq2)
        for p in seq1:
            self.assertIn(p, options)

    def test_single_option_always_picked(self):
        rng = WitnessRng(seed_from_state({"only": 1}))
        for _ in range(16):
            self.assertEqual(rng.pick(["tick"]), "tick")


class TestBelow(unittest.TestCase):

    def test_edges_exact(self):
        s = seed_from_state({"edge": 1})
        rng_lo = WitnessRng(s)
        rng_hi = WitnessRng(s)
        zero, one = Q16(0, 1), Q16(1, 1)
        # rolls live in [0, 1): never below 0, always below 1
        for _ in range(32):
            self.assertFalse(rng_lo.below(zero))
            self.assertTrue(rng_hi.below(one))

    def test_below_matches_next_q16_comparison(self):
        s = seed_from_state({"cmp": 7})
        probe = WitnessRng(s)
        rolls = [probe.next_q16() for _ in range(16)]
        threshold = Q16(1, 3)
        replay = WitnessRng(s)
        for r in rolls:
            self.assertEqual(replay.below(threshold), r < threshold)


class TestWeighted(unittest.TestCase):

    def test_empty_refuses(self):
        rng = WitnessRng(seed_from_state({"w": 2}))
        with self.assertRaises(ValueError):
            rng.weighted({})

    def test_pick_is_key_and_replay_identical(self):
        weights = {"warm": 3, "guarded": 1, "defensive": 2}
        s = seed_from_state({"npc": "quartermaster"})
        r1 = WitnessRng(s)
        r2 = WitnessRng(s)
        for _ in range(32):
            pick = r1.weighted(weights)
            self.assertIn(pick, weights)
            self.assertEqual(pick, r2.weighted(weights))


class TestSeedFromBookTailSemantics(unittest.TestCase):

    def test_empty_books_share_pre_first_decision_seed(self):
        self.assertEqual(seed_from_book(Bookkeeper("x")),
                         seed_from_book(Bookkeeper("y")))

    def test_tail_one_equals_default_on_non_empty_book(self):
        b = _book(4)
        self.assertEqual(seed_from_book(b, tail=1), seed_from_book(b))

    def test_tail_window_ignores_older_history(self):
        # two books differing in an OLD event but sharing the same last
        # receipt must share the tail=1 seed (the window is the suffix)
        b_long = _book(6)
        b_short = _book(6)
        b_short.entries = b_short.entries[-1:]
        self.assertEqual(seed_from_book(b_long, tail=1),
                         seed_from_book(b_short, tail=1))

    def test_tail_full_book_differs_from_tail_one(self):
        b = _book(5)
        self.assertNotEqual(seed_from_book(b, tail=5), seed_from_book(b, tail=1))

    def test_seed_tracks_history_length(self):
        self.assertNotEqual(seed_from_book(_book(3)), seed_from_book(_book(4)))


if __name__ == "__main__":
    unittest.main()
