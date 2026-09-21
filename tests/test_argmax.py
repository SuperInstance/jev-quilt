import pytest

from jev_quilt.backends import Q16Backend


def test_argmax_picks_highest_weight():
    d = Q16Backend().decide({"rule": "argmax", "options": {"a": 10, "b": 70, "c": 20}}, None)
    assert d.kind == "choice"
    assert d.value == "b"
    assert abs(d.probabilities["b"] - 0.7) < 1e-12
    assert abs(d.probabilities["a"] - 0.1) < 1e-12


def test_argmax_empty_options_refuses():
    with pytest.raises(ValueError, match="empty"):
        Q16Backend().decide({"rule": "argmax", "options": {}}, None)


def test_argmax_zero_total_refuses():
    with pytest.raises(ValueError, match="positive"):
        Q16Backend().decide({"rule": "argmax", "options": {"a": 0, "b": 0}}, None)
