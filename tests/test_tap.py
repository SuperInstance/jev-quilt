"""tests/test_tap.py — the tap doctrine: KL-gates + the monadic proposal-gate."""
import math

import pytest

from jev_quilt import Bookkeeper, Q16
from jev_quilt.tap import TapGate, ProposalGate, kl_divergence

Q = Q16


def dist(**kw):
    return {k: Q(*v) for k, v in kw.items()}


def test_kl_identical_is_zero():
    p = dist(a=(1, 2), b=(1, 2))
    assert kl_divergence(p, dict(p)) == 0.0


def test_kl_asymmetric():
    p = dist(a=(1, 2), b=(1, 2))          # uniform
    q = dist(a=(9, 10), b=(1, 10))        # skewed
    assert kl_divergence(p, q) != kl_divergence(q, p)
    assert kl_divergence(p, q) > 0 and kl_divergence(q, p) > 0


def test_kl_missing_key_is_eps_not_crash():
    p = dist(a=(1, 1))
    q = dist(a=(1, 2), b=(1, 2))
    assert math.isfinite(kl_divergence(p, q))


def test_static_world_goes_silent():
    gate = TapGate()
    p = dist(a=(1, 2), b=(1, 2))
    for _ in range(20):
        emit, gain, th = gate.admit(p, dict(p))
        assert not emit
        assert gain == 0.0


def test_shift_emits_and_books_gain():
    gate = TapGate()
    p = dist(a=(1, 2), b=(1, 2))
    q = dist(a=(9, 10), b=(1, 10))
    emit, gain, th = gate.admit(p, q)
    assert emit and gain > th


def test_tap_throttles_after_burst():
    """Dynamic threshold: repeated equal shocks self-throttle (tap doctrine)."""
    gate = TapGate(k=1.0)
    calm = dist(a=(1, 2), b=(1, 2))
    shock = dist(a=(9, 10), b=(1, 10))
    emits = 0
    for i in range(12):
        emit, _, _ = gate.admit(calm, shock if i % 2 else calm)
        emits += emit
    # first shocks pass; rising mean+k*std throttles the later ones
    assert emits < 6
    assert len(gate.accepted) <= gate.window


def test_proposal_accepts_and_books_transition():
    keeper = Bookkeeper("g")
    gate = ProposalGate(keeper).add_invariant(
        "nonnegative", lambda q, ctx: q.num >= 0)
    ok, reason, r = gate.propose({}, {}, dist(a=(9, 10), b=(1, 10)), Q(3, 2))
    assert ok and r.decision_kind == "transition"


def test_proposal_refuses_invariant_and_books():
    keeper = Bookkeeper("g")
    gate = ProposalGate(keeper).add_invariant(
        "under_2", lambda q, ctx: q < Q(2, 1))
    ok, reason, r = gate.propose({}, {}, dist(a=(1, 1)), Q(5, 1))
    assert not ok and reason == "under_2" and r.decision_kind == "refusal"


def test_law1_identity_never_floats():
    """A float coordinate is refused BEFORE any invariant runs."""
    keeper = Bookkeeper("g")
    gate = ProposalGate(keeper).add_invariant("always", lambda q, ctx: True)
    ok, reason, r = gate.propose({}, {}, dist(a=(1, 1)), 3.14)
    assert not ok and reason == "identity_floats" and r.decision_kind == "refusal"


def test_throwing_invariant_refuses_not_crashes():
    keeper = Bookkeeper("g")
    gate = ProposalGate(keeper).add_invariant(
        "boom", lambda q, ctx: 1 / 0)
    ok, reason, _ = gate.propose({}, {}, dist(a=(1, 1)), Q(1, 1))
    assert not ok and "boom!" in reason


def test_refusal_and_transition_replay_together():
    keeper = Bookkeeper("g")
    gate = (ProposalGate(keeper)
            .add_invariant("under_4", lambda q, ctx: q < Q(4, 1)))
    gate.propose({}, {}, dist(a=(1, 1)), Q(2, 1))   # accept
    gate.propose({}, {}, dist(a=(1, 1)), Q(9, 1))   # refuse
    gate.propose({}, {}, dist(a=(1, 1)), 0.5)       # law 1 refuse
    kinds = [e.decision_kind for e in keeper.entries]
    assert kinds == ["transition", "refusal", "refusal"]
    assert keeper.replay()  # chain recomputes; no exception = coherent
