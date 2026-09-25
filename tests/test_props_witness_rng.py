"""Property suite: jev_quilt/witness_rng.py (deterministic ledger randomness).

Docstring claims pinned here (quoted in comments):
  - module: "Rolls are exact Q16 fractions carved from the hash bytes —
    never floats. Therefore replay-identical: replay the same events,
    the same receipts hash, the same seed, the same rolls."
  - WitnessRng: "bounded, exact, and fully determined by the seed";
    next_q16: "in [0, 1), exact dyadic".
  - seed_from_state: "Stable under key order."  (VERIFIED: json.dumps
    sort_keys=True honors it for same-type keys; mixed-type keys raise
    TypeError — pinned as an edge, with SUSPECT-adjacent comment.)
  - weighted: "Integer-weighted pick; ties resolve by lowest carve, exact."

VIOLATION OF DOCSTRING on main — pinned as expected-failure:
  - seed_from_book docstring: "tail=0 is the empty book (pre-first-decision
    reproducibility)". Actual behavior on main: tail=0 with a NON-empty
    book hashes the LAST receipt's sha — a completely different seed from
    the empty book. The property asserting the documented behavior fails;
    see tests/receipts/005-r2-properties.json -> violations_found.
    Per round rules the code is NOT fixed here; behavior is pinned and
    marked SUSPECT.
"""

from __future__ import annotations

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from jev_quilt.q16 import Q16
from jev_quilt.bookkeeper import Bookkeeper
from jev_quilt.witness_rng import WitnessRng, seed_from_state, seed_from_book

from tests.property_runner import run_property, DEFAULT_N


# ---------------------------------------------------------------- properties

def prop_next_q16_bounded_dyadic(rng):
    """WitnessRng docstring: 'bounded, exact, and fully determined by the
    seed'; next_q16 comment: 'in [0, 1), exact dyadic'. NOTE: the code
    constructs Q16(h, 1 << 16), and the Q16 constructor NORMALIZES by gcd,
    so the reduced denominator is a power of two <= 2^16 (not always
    2^16 itself when h is even). The honest invariants: value in [0, 1)
    and dyadic with den dividing 2^16 (q * 2^16 is an integer)."""
    for _ in range(10):
        r = WitnessRng(rng.randint(0, 2 ** 64 - 1))
        for _ in range(20):
            q = r.next_q16()
            if not isinstance(q, Q16):
                return False, {"not_q16": repr(q)}
            if not (q.num >= 0 and q < Q16(1)):
                return False, {"out_of_range": repr(q)}
            if (q * Q16(1 << 16, 1)).den != 1:
                return False, {"not_dyadic_16": repr(q)}
    return True, None


def prop_replay_identical_chains(rng):
    """module docstring: 'replay-identical: replay the same events, the
    same receipts hash, the same seed, the same rolls' — from a cold
    construction, same seed -> identical next_q16 chains; also below()
    and pick() chains."""
    for _ in range(10):
        seed = rng.randint(0, 2 ** 64 - 1)
        a, b = WitnessRng(seed), WitnessRng(seed)
        if [a.next_q16() for _ in range(16)] != [b.next_q16() for _ in range(16)]:
            return False, {"seed": seed, "op": "next_q16"}
        a, b = WitnessRng(seed), WitnessRng(seed)
        if [a.below(Q16(1, 2)) for _ in range(16)] != [b.below(Q16(1, 2)) for _ in range(16)]:
            return False, {"seed": seed, "op": "below"}
        opts = ["alpha", "beta", "gamma", "delta"]
        a, b = WitnessRng(seed), WitnessRng(seed)
        if [a.pick(opts) for _ in range(16)] != [b.pick(opts) for _ in range(16)]:
            return False, {"seed": seed, "op": "pick"}
    return True, None


def prop_pick_totality(rng):
    """pick: total on every non-empty options list (any size >= 1, any
    element type) and returns a MEMBER of options; empty list raises
    ValueError (code-pinned message: 'pick: empty options')."""
    for _ in range(30):
        n = rng.randint(1, 12)
        opts = [rng.randint(-10 ** 6, 10 ** 6) for _ in range(n)]
        r = WitnessRng(rng.randint(0, 2 ** 64 - 1))
        v = r.pick(opts)
        if v not in opts:
            return False, {"opts": opts, "got": v}
        try:
            r.pick([])
        except ValueError:
            continue
        return False, {"empty_options_accepted": True}
    return True, None


def prop_below_totality_extremes(rng):
    """below(): total across the full seed space sampled and the full
    threshold range. Boundary pins: below(0) is always False (values are
    non-negative); below(1) is always True (values strictly < 1)."""
    for _ in range(20):
        r = WitnessRng(rng.randint(0, 2 ** 64 - 1))
        for _ in range(5):
            q = Q16(rng.randint(0, 1 << 16), 1 << 16)
            if not isinstance(r.below(q), bool):
                return False, {"not_bool": True}
        if r.below(Q16(0)) is not False:
            return False, {"below_zero_true": True}
        if r.below(Q16(1)) is not True:
            return False, {"below_one_false": True}
    return True, None


def prop_weighted_totality_and_zero_weights(rng):
    """weighted: total on any non-empty int-weight dict; returns a key;
    zero-weight keys are never returned; empty dict raises ValueError
    (code-pinned message: 'weighted: empty')."""
    for _ in range(30):
        keys = [f"k{i}" for i in range(rng.randint(1, 8))]
        weights = {k: rng.randint(0, 6) for k in keys}
        if sum(weights.values()) == 0:
            weights[rng.choice(keys)] = 1
        r = WitnessRng(rng.randint(0, 2 ** 64 - 1))
        v = r.weighted(weights)
        if v not in weights:
            return False, {"weights": weights, "got": v}
        zero_keys = [k for k, w in weights.items() if w == 0]
        if zero_keys and v in zero_keys:
            return False, {"zero_weight_picked": v, "weights": weights}
        try:
            r.weighted({})
        except ValueError:
            continue
        return False, {"empty_weights_accepted": True}
    return True, None


def prop_weighted_deterministic_ties(rng):
    """weighted docstring: 'ties resolve by lowest carve, exact' — the
    deterministic half that IS verifiable: same seed + same weights ->
    same pick (replay), and with a single nonzero-weight key that key is
    always returned regardless of seed."""
    for _ in range(10):
        seed = rng.randint(0, 2 ** 64 - 1)
        weights = {"a": 1, "b": 1, "c": 1, "d": 1}
        x, y = WitnessRng(seed), WitnessRng(seed)
        if x.weighted(weights) != y.weighted(weights):
            return False, {"seed": seed}
        r = WitnessRng(rng.randint(0, 2 ** 64 - 1))
        if r.weighted({"only": 5, "ghost": 0}) != "only":
            return False, {"single_key_not_picked": True}
    return True, None


def prop_seed_from_state_key_order_stable(rng):
    """seed_from_state docstring: 'Stable under key order.'  Verified on
    main: json.dumps(sort_keys=True) makes the seed invariant under
    insertion order of same-type keys — including nested dicts."""
    for _ in range(20):
        base = {f"key{i}": rng.randint(0, 10 ** 6) for i in range(rng.randint(1, 8))}
        items = list(base.items())
        rng.shuffle(items)
        permuted = dict(items)
        if seed_from_state(base) != seed_from_state(permuted):
            return False, {"base": base, "permuted": permuted}
        nested = {"outer": base, "z": 1, "a": 2}
        nested2 = {"a": 2, "outer": permuted, "z": 1}
        if seed_from_state(nested) != seed_from_state(nested2):
            return False, {"nested_order_sensitive": True}
    return True, None


def prop_seed_from_state_mixed_key_types(rng):
    """SUSPECT-adjacent edge pin: json.dumps(sort_keys=True) compares keys,
    so a dict with BOTH int and str keys raises TypeError ('<' not supported
    between 'int' and 'str'). Key-order stability therefore only holds
    within a single key type. Current behavior pinned; the docstring's
    'any engine state dict' implication is broader than what works."""
    for _ in range(5):
        state = {1: "a", "b": 2}
        try:
            seed_from_state(state)
        except TypeError:
            continue
        return False, {"mixed_keys_accepted": True}
    return True, None


def prop_seed_from_book_tail_n_replay(rng):
    """seed_from_book docstring (the HONEST half): 'tail=n hashes
    receipts[-n:]' — replaying the same book construction yields the same
    seed, and tail beyond book length equals tail=full-book on the
    windowing rule (entries[-tail:] clamps)."""
    for _ in range(10):
        bk, n = _book(rng)
        if seed_from_book(bk, 2) != seed_from_book(bk, 2):
            return False, {"same_book_diff_seed": True}
        if n >= 2 and seed_from_book(bk, n + 5) != seed_from_book(bk, n):
            return False, {"clamp_mismatch": {"n": n}}
    return True, None


def prop_seed_from_book_tail0_is_empty_book(rng):
    """VIOLATION OF DOCSTRING on main — pinned as expected-failure.

    seed_from_book docstring: 'tail=0 is the empty book (pre-first-decision
    reproducibility)'. Read literally, a caller expects
        seed_from_book(any_book, 0) == seed_from_book(empty_book, 0)
    i.e. tail=0 means 'before any decision'. Actual main behavior: for a
    non-empty book, tail=0 falls into the else-branch and hashes the LAST
    receipt's sha — a seed that changes with every new decision, the
    opposite of 'pre-first-decision reproducibility'.

    This property asserts the DOCUMENTED behavior and fails on main.
    Per round rules the code is NOT fixed here. See
    tests/receipts/005-r2-properties.json -> violations_found."""
    for _ in range(10):
        bk, _ = _book(rng)
        empty = Bookkeeper("empty")
        if seed_from_book(bk, 0) != seed_from_book(empty, 0):
            return False, {"nonempty_tail0": seed_from_book(bk, 0),
                           "empty_tail0": seed_from_book(empty, 0)}
    return True, None


def _book(rng, lo=3, hi=12):
    bk = Bookkeeper(f"w{rng.randint(0, 999)}")
    n = rng.randint(lo, hi)
    for i in range(n):
        bk.book({"v": rng.randint(0, 10 ** 6)}, {"d": rng.randint(0, 10 ** 6)},
                rng.choice(["a", "b"]), {"p": rng.randint(0, 100)})
    return bk, n


PROPERTIES = [
    prop_next_q16_bounded_dyadic,
    prop_replay_identical_chains,
    prop_pick_totality,
    prop_below_totality_extremes,
    prop_weighted_totality_and_zero_weights,
    prop_weighted_deterministic_ties,
    prop_seed_from_state_key_order_stable,
    prop_seed_from_state_mixed_key_types,
    prop_seed_from_book_tail_n_replay,
    prop_seed_from_book_tail0_is_empty_book,   # FAILS on main: docstring violation
]


# ------------------------------------------------------- unittest wiring

import unittest  # noqa: E402


class TestWitnessRngProperties(unittest.TestCase):
    def _check(self, fn):
        ok, cx = run_property(fn)
        self.assertTrue(ok, f"property {fn.__qualname__} failed: {cx!r}")

    def test_next_q16_bounded(self): self._check(prop_next_q16_bounded_dyadic)
    def test_replay_identical(self): self._check(prop_replay_identical_chains)
    def test_pick_totality(self): self._check(prop_pick_totality)
    def test_below_totality(self): self._check(prop_below_totality_extremes)
    def test_weighted_totality(self): self._check(prop_weighted_totality_and_zero_weights)
    def test_weighted_deterministic(self): self._check(prop_weighted_deterministic_ties)
    def test_seed_from_state_key_order(self): self._check(prop_seed_from_state_key_order_stable)
    def test_seed_from_state_mixed_keys(self): self._check(prop_seed_from_state_mixed_key_types)
    def test_seed_from_book_tail_n(self): self._check(prop_seed_from_book_tail_n_replay)

    def test_seed_from_book_tail0_empty_book(self):
        # FAIL-first: asserts the DOCUMENTED behavior; fails on main.
        # Marked expectedFailure in the follow-up commit
        # (see tests/receipts/005-r2-properties.json).
        self._check(prop_seed_from_book_tail0_is_empty_book)


if __name__ == "__main__":
    unittest.main()
