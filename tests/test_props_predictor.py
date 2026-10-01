"""Property suite: jev_quilt/predictor.py (feeling under the ledger).

Docstring claims pinned here (quoted in comments):
  - Predictor protocol: "predict() -> Optional[Q16]: None = not warmed yet"
  - MeanPredictor: "Exact running mean of the last K outcomes. Fully
    closed in ℚ" — verified against a fractions.Fraction oracle.
  - MeanPredictor: "v0 asserts K in that family and refuses otherwise"
    (EXACT_K family enforcement).
  - surprise: "Exact graded difference between feeling and fact."
  - alarm: "Binary viability of the intuition (law 5's other side)."

No violations found on main for this module; every property passes.
"""

from __future__ import annotations

import sys
from fractions import Fraction

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from jev_quilt.q16 import Q16
from jev_quilt.predictor import MeanPredictor, surprise, alarm, Predictor

from tests.property_runner import run_property, DEFAULT_N


def _outcome(rng):
    return Q16(rng.randint(-10 ** 6, 10 ** 6), 10 ** 6)


# Small-K family for LOOP-HEAVY properties: predict() re-sums the whole
# window on every call, so O(n*k) oracle loops must keep k modest or the
# property suite takes hours. Large-k behavior is pinned separately in
# prop_convergence_to_constant_exact (single constant-sequence check).
_SMALL_K = (1, 2, 4, 5, 8, 10, 16, 20, 25, 32, 40, 50, 64, 80, 100)


def _small_k(rng):
    return rng.choice(_SMALL_K)


def _frac(q):
    return Fraction(q.num, q.den)


# ---------------------------------------------------------------- properties

def prop_predict_none_until_warmed(rng):
    """Predictor protocol docstring: 'predict() -> Optional[Q16]:
    None = not warmed yet' — before k updates, predict() must be None;
    from the k-th update on, it must be a Q16."""
    for _ in range(10):
        k = rng.choice(sorted(MeanPredictor.EXACT_K))
        p = MeanPredictor(k=k)
        warm_seq = [_outcome(rng) for _ in range(k)]
        for i, o in enumerate(warm_seq):
            pred = p.predict()
            if i < k and pred is not None:
                return False, {"k": k, "i": i, "pred": pred}
            p.update(o)
        if not isinstance(p.predict(), Q16):
            return False, {"k": k, "pred_after_warm": p.predict()}
        if not p.warmed:
            return False, {"k": k, "warmed": False}
    return True, None


def prop_convergence_to_constant_exact(rng):
    """MeanPredictor docstring: 'Exact running mean of the last K outcomes.'
    With a constant sequence, the running mean converges to that constant
    EXACTLY after the first k updates (Q16 exactness — no epsilon).
    Small-k: stays converged under the constant regime. Large-k (1024,
    the top of the EXACT_K family): converges exactly in a single pass."""
    for _ in range(10):
        k = rng.choice(_SMALL_K)
        v = _outcome(rng)
        p = MeanPredictor(k=k)
        for _ in range(k):
            p.update(v)
        if p.predict() != v:
            return False, {"k": k, "v": repr(v), "pred": repr(p.predict())}
        for _ in range(rng.randint(1, 5)):
            p.update(v)
            if p.predict() != v:
                return False, {"k": k, "drift": repr(p.predict())}
    # one large-k pass per seed: exactness must hold at the family top too
    big = MeanPredictor(k=1024)
    v = _outcome(rng)
    for _ in range(1024):
        big.update(v)
    if big.predict() != v:
        return False, {"k": 1024, "pred": repr(big.predict()), "v": repr(v)}
    return True, None


def prop_running_mean_matches_fraction_oracle(rng):
    """Metamorphic: 'Fully closed in ℚ' — at every step the prediction
    equals the exact rational mean of the last min(len, k) outcomes,
    checked against a Fraction oracle with random sequences. Loop cost
    is bounded via _SMALL_K (see note above)."""
    for _ in range(5):
        k = _small_k(rng)
        p = MeanPredictor(k=k)
        window = []
        n = rng.randint(1, k + 3)
        for _ in range(n):
            o = _outcome(rng)
            window.append(o)
            if len(window) > k:
                window.pop(0)
            p.update(o)
            pred = p.predict()
            if len(window) < k:
                if pred is not None:
                    return False, {"premature": repr(pred)}
                continue
            oracle = sum((_frac(x) for x in window), Fraction(0)) / k
            if _frac(pred) != oracle:
                return False, {"k": k, "pred": repr(pred), "oracle": str(oracle)}
    return True, None


def prop_exact_k_family_enforced(rng):
    """MeanPredictor docstring: 'v0 asserts K in that family and refuses
    otherwise, because an inexact predictor would be a lie wearing the
    ledger's clothes.' k not in EXACT_K -> ValueError at construction."""
    for _ in range(10):
        k = rng.randint(1, 1200)
        if k in MeanPredictor.EXACT_K:
            continue
        try:
            MeanPredictor(k=k)
        except ValueError:
            continue
        return False, {"k": k, "accepted": True}
    return True, None


def prop_window_slides_after_k(rng):
    """The window is last-k-only: after k+1 updates the oldest outcome no
    longer influences the prediction (pinned via a two-valued contrast —
    the mean must equal the oracle over exactly the last k)."""
    for _ in range(5):
        k = _small_k(rng)
        p = MeanPredictor(k=k)
        first = _outcome(rng)
        for _ in range(k):
            p.update(first)
        rest = [_outcome(rng) for _ in range(k)]
        window = [first] + rest[:-1]
        for o in rest:
            p.update(o)
            window.pop(0)
            window.append(o)
        oracle = sum((_frac(x) for x in window), Fraction(0)) / k
        if _frac(p.predict()) != oracle or _frac(p.predict()) == _frac(first):
            return False, {"k": k, "pred": repr(p.predict()), "oracle": str(oracle)}
    return True, None


def prop_surprise_is_exact_absolute_difference(rng):
    """surprise docstring: 'Exact graded difference between feeling and
    fact.' surprise(o, p) == |o - p| exactly; non-negative; symmetric;
    zero iff o == p."""
    for _ in range(50):
        o, p = _outcome(rng), _outcome(rng)
        s = surprise(o, p)
        d = o - p
        if s != Q16(abs(d.num), d.den):
            return False, {"o": repr(o), "p": repr(p), "s": repr(s)}
        if s < Q16(0):
            return False, {"negative_surprise": repr(s)}
        if surprise(o, p) != surprise(p, o):
            return False, {"asymmetric": True}
        if (surprise(o, o) == Q16(0)) is not True:
            return False, {"self_surprise": repr(surprise(o, o))}
    return True, None


def prop_alarm_iff_surprise_exceeds_floor(rng):
    """alarm docstring: 'Binary viability... (surprise > floor)'. alarm is
    EXACTLY surprise > floor, including the equality boundary (alarm must
    be False when surprise == floor)."""
    for _ in range(50):
        o, p = _outcome(rng), _outcome(rng)
        s = surprise(o, p)
        floor = rng.choice([s, s + Q16(1, 10 ** 6), s - Q16(1, 10 ** 6), Q16(0), Q16(2)])
        want = s > floor
        if alarm(o, p, floor) != want:
            return False, {"o": repr(o), "p": repr(p), "floor": repr(floor),
                           "s": repr(s), "got": alarm(o, p, floor)}
    return True, None


def prop_predictor_protocol_shape(rng):
    """MeanPredictor satisfies the Predictor protocol STRUCTURALLY
    (isinstance against a typing.Protocol is not runtime-checkable, so we
    check attributes): predict is a zero-arg callable returning Q16-or-None,
    update takes one Q16."""
    for _ in range(5):
        k = rng.choice(_SMALL_K)
        p = MeanPredictor(k=k)
        if not callable(getattr(p, "predict", None)) or not callable(getattr(p, "update", None)):
            return False, {"missing_methods": True}
        p.update(_outcome(rng))
        pred = p.predict()   # not warmed after a single update (k >= 1... None unless k==1)
        if pred is not None and not isinstance(pred, Q16):
            return False, {"bad_return": repr(pred)}
    return True, None


PROPERTIES = [
    prop_predict_none_until_warmed,
    prop_convergence_to_constant_exact,
    prop_running_mean_matches_fraction_oracle,
    prop_exact_k_family_enforced,
    prop_window_slides_after_k,
    prop_surprise_is_exact_absolute_difference,
    prop_alarm_iff_surprise_exceeds_floor,
    prop_predictor_protocol_shape,
]


# ------------------------------------------------------- unittest wiring

import unittest  # noqa: E402


class TestPredictorProperties(unittest.TestCase):
    def _check(self, fn):
        ok, cx = run_property(fn)
        self.assertTrue(ok, f"property {fn.__qualname__} failed: {cx!r}")

    def test_none_until_warmed(self): self._check(prop_predict_none_until_warmed)
    def test_convergence_exact(self): self._check(prop_convergence_to_constant_exact)
    def test_running_mean_oracle(self): self._check(prop_running_mean_matches_fraction_oracle)
    def test_exact_k_enforced(self): self._check(prop_exact_k_family_enforced)
    def test_window_slides(self): self._check(prop_window_slides_after_k)
    def test_surprise_exact(self): self._check(prop_surprise_is_exact_absolute_difference)
    def test_alarm_boundary(self): self._check(prop_alarm_iff_surprise_exceeds_floor)
    def test_protocol_shape(self): self._check(prop_predictor_protocol_shape)


if __name__ == "__main__":
    unittest.main()
