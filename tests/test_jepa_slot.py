import unittest
"""JEPA slot watch: the alarm ledger must NAME the predictor-class hole,
and must honestly stay silent when the predictor class is right."""

from jev_quilt import Cell, Hook, Q16, Engine, MeanPredictor, Projection
from jev_quilt.jepa_slot import scan, SlotCandidate


def _run(signal, ticks=40):
    eng = Engine()
    eng.register(Cell("world", (0, 0)))
    eng.register(Cell(
        "sense.x", (1, 0),
        input_hooks=[Hook("world")],
        decision={"rule": "identity", "value": signal(0)},
        predictor=MeanPredictor(k=4),
        surprise_floor=Q16(1, 10),
        outputs=[Projection("felt.x", "q16")],
    ))
    for t in range(1, ticks + 1):
        eng.cells["sense.x"].decision = {"rule": "identity", "value": signal(t)}
        eng.emit("world", {"tick": t}, state={"t": t})
    return eng.books


def _periodic(t):
    return Q16(t % 10 + 1, 10)


def _constant(t):
    return Q16(3, 10)




class TestConverted(unittest.TestCase):

    def test_periodic_world_surfaces_slot(self):
        books = _run(_periodic)
        candidates, problems = scan(books)
        assert problems == []
        assert [c.cell for c in candidates] == ["sense.x"]
        c = candidates[0]
        assert 2 * c.alarms >= c.wakes          # majority bar, exact
        assert c.alarm_share >= __import__("fractions").Fraction(1, 2)
        assert books["sense.x"].verify()




def test_constant_world_is_honest_negative():
    books = _run(_constant)
    candidates, problems = scan(books)
    assert candidates == []
    assert problems == []
    assert books["sense.x"].verify()


def test_structurally_broken_book_is_problem_not_candidate():
    books = _run(_periodic)
    # Structural tamper within verify()'s scope: forge a duplicate tick.
    # (Residue tamper vs a book with no external replay anchor is the
    # caller's replay-compare to catch, not this scan's — see module doc.)
    r = books["sense.x"].entries[3]
    object.__setattr__(r, "tick", 2)
    assert not books["sense.x"].verify()
    candidates, problems = scan(books)
    assert candidates == []
    assert any("sense.x" in p and "verify" in p for p in problems)


def test_cold_book_below_min_wakes_is_skipped():
    books = _run(_periodic, ticks=5)
    candidates, problems = scan(books, min_wakes=8)
    assert candidates == []
    assert problems == []


def test_share_is_exact_fraction():
    c = SlotCandidate("sense.x", wakes=8, alarms=5)
    assert c.alarm_share.numerator == 5 and c.alarm_share.denominator == 8
    assert "plug a world model" in str(c)
