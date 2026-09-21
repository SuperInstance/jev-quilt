from jev_quilt import (Q16, WitnessRng, seed_from_state, seed_from_book,
                       opposite, is_canonical, TendencyReading)
from jev_quilt.cell import Cell, Hook
from jev_quilt.engine import Engine
from jev_quilt.predictor import MeanPredictor


def _book(n=5):
    eng = Engine()
    eng.register(Cell("s", (0, 0)))
    eng.register(Cell("a", (1, 0), input_hooks=[Hook("s")],
                      decision={"rule": "identity", "value": Q16(1, 10)},
                      predictor=MeanPredictor(k=4)))
    for t in range(1, n + 1):
        eng.emit("s", {"mag": Q16(1)}, state={"t": t})
    return eng.books["a"]


def test_seed_from_book_replay_identical():
    b1, b2 = _book(7), _book(7)
    assert seed_from_book(b1) == seed_from_book(b2)
    r1 = [WitnessRng(seed_from_book(b1)).next_q16() for _ in range(6)]
    r2 = [WitnessRng(seed_from_book(b2)).next_q16() for _ in range(6)]
    assert r1 == r2


def test_seed_diverges_with_history():
    b1 = _book(7)
    b2 = _book(8)   # one extra event
    assert seed_from_book(b1) != seed_from_book(b2)


def test_rolls_are_exact_dyadics_in_unit_interval():
    rng = WitnessRng(seed_from_state({"x": 1}))
    rolls = [rng.next_q16() for _ in range(64)]
    # every roll is a dyadic rational in [0,1): den is a power of two
    # (the Q16 ctor reduces by gcd; reduction of a dyadic stays dyadic)
    assert all(q.den & (q.den - 1) == 0 and q.den <= (1 << 16) for q in rolls)
    zero, one = Q16(0, 1), Q16(1, 1)
    assert all(not q < zero and q < one for q in rolls)  # [0,1): strict, exact


def test_weighted_pick_respects_zero_weight_never_picked():
    rng = WitnessRng(seed_from_state({"w": 1}))
    for _ in range(64):
        assert rng.weighted({"only": 3, "never": 0}) == "only"


def test_opposites_total_and_involutive_on_canonical():
    assert opposite("witness") == "forget"
    assert opposite("forget") == "witness"
    assert opposite("jev") == "jepa"
    assert opposite("JEV") == "jepa"           # case-insensitive
    assert opposite("unknown-thing") == "gap"  # total: absence is honest
    for k in ("witness", "jev", "calm", "tick"):
        assert opposite(opposite(k)) == k      # involution on canonical


def test_tendency_counts_exact_and_modal_prediction():
    tr = TendencyReading()
    assert tr.predict_symbol() is None
    for s in ("rock", "rock", "paper", "rock", "paper", "rock"):
        tr.update_symbol(s)
    assert tr.predict_symbol() == "rock"
    assert tr.confidence() == Q16(4, 6)        # exact modal share
    assert tr.total == 6
