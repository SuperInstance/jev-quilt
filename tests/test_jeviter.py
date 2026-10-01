import unittest
"""tests/test_jeviter.py — JEV as a new type of iterator."""
from jev_quilt import Q16 as Q
from jev_quilt.jeviter import simulate

CALM = {"a": Q(1, 2), "b": Q(1, 2)}
SHIFT = {"a": Q(9, 10), "b": Q(1, 10)}




class TestConverted(unittest.TestCase):

    def test_static_stream_yields_nothing(self):
        events, keeper = simulate([dict(CALM) for _ in range(50)])
        assert events == []
        assert len(keeper.entries) == 51          # 50 silences + 1 exhaustion
        assert keeper.entries[-1].decision_kind == "exhausted"
        assert keeper.replay()




def test_shift_yields_exactly_once():
    events, keeper = simulate([dict(CALM)] * 10 + [dict(SHIFT)] * 10)
    assert len(events) == 1
    assert events[0].gain > 0
    kinds = [e.decision_kind for e in keeper.entries]
    assert kinds.count("event") == 1 and kinds.count("silence") == 18


def test_pulls_counted_per_event():
    events, _ = simulate([dict(CALM)] * 5 + [dict(SHIFT)] * 5)
    assert events[0].pulls == 6               # five silences, then the yield


def test_repeated_shifts_are_throttled():
    stream = [dict(CALM), dict(SHIFT)] * 20
    events, _ = simulate(stream, k=1.0)
    assert 0 < len(events) < 40               # tap throttles oscillation


def test_exhaustion_receipt_carries_count():
    _, keeper = simulate([dict(CALM)] * 7)
    last = keeper.entries[-1]
    assert last.decision_kind == "exhausted"
    assert '"emitted": 0' in last.payload


def test_non_q16_values_coerced_exactly():
    events, _ = simulate([{"a": 1, "b": 2}, {"a": 9, "b": 1}])
    assert len(events) == 1                   # ints become exact rationals
    assert events[0].value["a"] == Q(9, 10)   # normalized exact
