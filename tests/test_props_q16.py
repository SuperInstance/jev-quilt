"""Property suite: jev_quilt/q16.py (exact-rational codec).

q16 is EXACT rational arithmetic — there is no quantization error to
tolerate, so the classic fixed-point invariants hold exactly:

  - (a + b) - b == a, exactly (the task's '~within quantization error'
    collapses to equality here; pinned as equality).
  - commutativity of add/mul; associativity of add/mul.
  - negation involution (note: Q16 defines no __neg__; the property
    constructs negation explicitly as Q16(-n, d) and pins that double
    negation is the identity — the missing dunder is noted in the
    receipt as a gap, not a violation).
  - identities: a + 0 == a; a * 1 == a.
  - normalization: constructor divides by gcd and forces den > 0.

Docstring contradictions found on main (behavior pinned, NOT fixed —
see tests/receipts/005-r2-properties.json -> docstring_contradictions):
  - module docstring: "Identity is (num:int64, den:int64)" — the
    constructor accepts arbitrarily large integers (no int64 bound).
  - module docstring: "denominators divide 10^6 exactly" — Q16(1, 3)
    constructs fine; only from_float() enforces the lattice.

Metamorphic oracle: fractions.Fraction is used as an independent
second implementation for comparison and arithmetic properties.
"""

from __future__ import annotations

import sys
from fractions import Fraction
from math import gcd

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from jev_quilt.q16 import Q16, commensurate, SCALE

from tests.property_runner import run_property, DEFAULT_N


def _rq(rng):
    """Random general rational (constructor accepts any nonzero den)."""
    return Q16(rng.randint(-10 ** 9, 10 ** 9), rng.choice([1, 2, 3, 4, 5, 7, 8, 10 ** 6, 10 ** 7]))


def _lattice_q(rng):
    """Random representable lattice value num/10^6."""
    return Q16(rng.randint(-10 ** 6, 10 ** 6), 10 ** 6)


def _frac(q):
    return Fraction(q.num, q.den)


# ---------------------------------------------------------------- properties

def prop_add_sub_inverse_exact(rng):
    """(a + b) - b == a, EXACTLY (exact-rational codec; no epsilon)."""
    for _ in range(50):
        a, b = _rq(rng), _rq(rng)
        if (a + b) - b != a:
            return False, {"a": repr(a), "b": repr(b)}
    return True, None


def prop_mul_div_inverse_exact(rng):
    """(a * b) / b == a for b != 0, EXACTLY."""
    for _ in range(50):
        a, b = _rq(rng), _rq(rng)
        if b.num == 0:
            continue
        if (a * b) / b != a:
            return False, {"a": repr(a), "b": repr(b)}
    return True, None


def prop_add_mul_commutative(rng):
    """a + b == b + a; a * b == b * a."""
    for _ in range(50):
        a, b = _rq(rng), _rq(rng)
        if a + b != b + a or a * b != b * a:
            return False, {"a": repr(a), "b": repr(b)}
    return True, None


def prop_add_mul_associative(rng):
    """(a + b) + c == a + (b + c); (a * b) * c == a * (b * c)."""
    for _ in range(30):
        a, b, c = _rq(rng), _rq(rng), _rq(rng)
        if (a + b) + c != a + (b + c):
            return False, {"op": "add", "a": repr(a), "b": repr(b), "c": repr(c)}
        if (a * b) * c != a * (b * c):
            return False, {"op": "mul", "a": repr(a), "b": repr(b), "c": repr(c)}
    return True, None


def prop_additive_and_multiplicative_identity(rng):
    """a + Q16(0) == a; a * Q16(1) == a; Q16(0) is unique-ish (pinned as
    identity behavior, not uniqueness)."""
    for _ in range(30):
        a = _rq(rng)
        if a + Q16(0) != a or Q16(0) + a != a:
            return False, {"a": repr(a), "op": "add0"}
        if a * Q16(1) != a or Q16(1) * a != a:
            return False, {"a": repr(a), "op": "mul1"}
    return True, None


def prop_negation_involution(rng):
    """negation involution: neg(neg(a)) == a where neg is Q16(-n, d).
    SUSPECT-adjacent note: q16.py defines no __neg__, so unary minus is a
    TypeError; this property pins the explicitly-constructed negation."""
    for _ in range(30):
        a = _rq(rng)
        if Q16(-(-a.num), a.den) != a:
            return False, {"a": repr(a)}
        if a + Q16(-a.num, a.den) != Q16(0):
            return False, {"a": repr(a), "sum": repr(a + Q16(-a.num, a.den))}
    return True, None


def prop_constructor_normalization(rng):
    """Constructor reduces by gcd and forces den > 0; equal rationals in
    different written forms compare equal and hash equal (dict round-trip)."""
    for _ in range(30):
        n, d = rng.randint(-10 ** 6, 10 ** 6), rng.randint(1, 10 ** 4)
        if n == 0:
            continue
        c = rng.randint(1, 100)
        q1, q2 = Q16(n, d), Q16(n * c, d * c)
        if q1 != q2 or hash(q1) != hash(q2):
            return False, {"q1": repr(q1), "q2": repr(q2)}
        if q1.den <= 0 or gcd(q1.num, q1.den) != 1:
            return False, {"not_reduced": repr(q1)}
        if {q1: "v"}[q2] != "v":
            return False, {"dict_lookup": repr(q2)}
    return True, None


def prop_from_float_roundtrip(rng):
    """from_float docstring: 'Projection INTO the lattice... never silently
    rounds identity' — for any representable value, from_float(to_float())
    is the identity."""
    for _ in range(50):
        q = _lattice_q(rng)
        if Q16.from_float(q.to_float()) != q:
            return False, {"q": repr(q), "f": q.to_float()}
    return True, None


def prop_from_float_rejects_off_lattice(rng):
    """from_float must raise ValueError on non-representable reals (the
    docstring's 'never silently rounds identity'). 1/3 is the canonical
    ternary ghost; n + 1/3 for any integer n is guaranteed off-lattice
    (denominator 3 survives reduction)."""
    for _ in range(20):
        bad = rng.choice([1 / 3, 2 / 3, 1 / 7, 2 / 7,
                          float(rng.randint(-50, 50)) + 1 / 3])
        try:
            Q16.from_float(bad)
        except ValueError:
            continue
        return False, {"accepted": bad}
    return True, None


def prop_zero_denominator_raises(rng):
    """Q16(n, 0) raises ZeroDivisionError (pinned by existing unit test;
    property version sweeps random n)."""
    for _ in range(20):
        n = rng.randint(-10 ** 6, 10 ** 6)
        try:
            Q16(n, 0)
        except ZeroDivisionError:
            continue
        return False, {"n": n}
    return True, None


def prop_comparison_matches_fraction_oracle(rng):
    """Metamorphic: <, <=, ==, >=, > agree with fractions.Fraction for
    random pairs, including cross-denominator cases."""
    for _ in range(50):
        a, b = _rq(rng), _rq(rng)
        fa, fb = _frac(a), _frac(b)
        if (a < b) != (fa < fb) or (a <= b) != (fa <= fb):
            return False, {"a": repr(a), "b": repr(b)}
        if (a > b) != (fa > fb) or (a >= b) != (fa >= fb):
            return False, {"a": repr(a), "b": repr(b)}
        if (a == b) != (fa == fb):
            return False, {"a": repr(a), "b": repr(b)}
    return True, None


def prop_arithmetic_matches_fraction_oracle(rng):
    """Metamorphic: +, -, * match the Fraction oracle exactly."""
    for _ in range(30):
        a, b = _rq(rng), _rq(rng)
        if _frac(a + b) != _frac(a) + _frac(b):
            return False, {"op": "add", "a": repr(a), "b": repr(b)}
        if _frac(a - b) != _frac(a) - _frac(b):
            return False, {"op": "sub", "a": repr(a), "b": repr(b)}
        if _frac(a * b) != _frac(a) * _frac(b):
            return False, {"op": "mul", "a": repr(a), "b": repr(b)}
    return True, None


def prop_commensurate_docstring_cases(rng):
    """commensurate docstring: 'a/b's reduced denominator divides 10^6.
    TRUE means the pair lives on a common decimal lattice; FALSE is a
    ternary ghost (e.g. 1/3 against 1)'."""
    for _ in range(20):
        a = _lattice_q(rng)
        if not commensurate(a, a):
            return False, {"self": repr(a)}
        if commensurate(Q16(1, 3), Q16(1, 1)):
            return False, {"ternary_ghost_accepted": True}
        if not commensurate(Q16(1, 3), Q16(1, 3)):
            return False, {"self_13": True}
        # zero divisor: defined as a.num == 0
        if commensurate(Q16(0), Q16(0)) is not True:
            return False, {"zero_zero": True}
        if commensurate(Q16(1), Q16(0)) is not False:
            return False, {"one_zero": True}
    return True, None


PROPERTIES = [
    prop_add_sub_inverse_exact,
    prop_mul_div_inverse_exact,
    prop_add_mul_commutative,
    prop_add_mul_associative,
    prop_additive_and_multiplicative_identity,
    prop_negation_involution,
    prop_constructor_normalization,
    prop_from_float_roundtrip,
    prop_from_float_rejects_off_lattice,
    prop_zero_denominator_raises,
    prop_comparison_matches_fraction_oracle,
    prop_arithmetic_matches_fraction_oracle,
    prop_commensurate_docstring_cases,
]


# ------------------------------------------------------- unittest wiring

import unittest  # noqa: E402


class TestQ16Properties(unittest.TestCase):
    def _check(self, fn):
        ok, cx = run_property(fn)
        self.assertTrue(ok, f"property {fn.__qualname__} failed: {cx!r}")

    def test_add_sub_inverse(self): self._check(prop_add_sub_inverse_exact)
    def test_mul_div_inverse(self): self._check(prop_mul_div_inverse_exact)
    def test_commutativity(self): self._check(prop_add_mul_commutative)
    def test_associativity(self): self._check(prop_add_mul_associative)
    def test_identities(self): self._check(prop_additive_and_multiplicative_identity)
    def test_negation_involution(self): self._check(prop_negation_involution)
    def test_normalization(self): self._check(prop_constructor_normalization)
    def test_from_float_roundtrip(self): self._check(prop_from_float_roundtrip)
    def test_from_float_rejects(self): self._check(prop_from_float_rejects_off_lattice)
    def test_zero_denominator(self): self._check(prop_zero_denominator_raises)
    def test_comparison_oracle(self): self._check(prop_comparison_matches_fraction_oracle)
    def test_arithmetic_oracle(self): self._check(prop_arithmetic_matches_fraction_oracle)
    def test_commensurate(self): self._check(prop_commensurate_docstring_cases)


if __name__ == "__main__":
    unittest.main()
