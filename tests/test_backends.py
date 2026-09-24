import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

import os



from jev_quilt.backends import resolve_backend, Q16Backend, BackendDecision
from jev_quilt.q16 import Q16


def test_auto_resolves_q16():
    b = resolve_backend("auto")
    assert isinstance(b, Q16Backend)


def test_q16_threshold_rule():
    b = Q16Backend()
    d = b.decide({"rule": "threshold", "value": (7, 10), "threshold": (1, 2)}, None)
    assert isinstance(d, BackendDecision)
    assert d.value is True
    assert d.confidence == 1.0
    d2 = b.decide({"rule": "threshold", "value": (3, 10), "threshold": (1, 2)}, None)
    assert d2.value is False


def test_q16_sum_rule_exact():
    b = Q16Backend()
    d = b.decide({"rule": "sum", "terms": [(1, 10), (2, 10), (3, 10)]}, None)
    assert d.value == Q16(3, 5)


def test_unknown_rule_refuses():
    with pytest.raises(ValueError):
        Q16Backend().decide({"rule": "nonsense"}, None)


def test_openjev_stub_refuses_honestly():
    b = resolve_backend("openjev-local")
    with pytest.raises(RuntimeError, match="not wired"):
        b.decide({}, None)


def test_typesafe_stub_requires_key(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    b = resolve_backend("typesafe-api")
    with pytest.raises(RuntimeError, match="TYPESAFE_API_KEY"):
        b.decide({}, None)
