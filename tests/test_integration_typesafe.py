"""Integration test: real TypeSafe API end-to-end. Requires TYPESAFEAI_KEY env."""
import os
import pytest
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from jev_quilt.typesafe_client import TypeSafeBackend

pytestmark = pytest.mark.skipif(not os.environ.get("TYPESAFEAI_KEY"),
                                reason="live API: TYPESAFEAI_KEY not set")
backend = TypeSafeBackend()

def test_api_available():
    assert backend.available(), "TYPESAFEAI_KEY not set"

def test_choice_returns_valid():
    if not backend.available():
        return
    ds, meta = backend.decide_batch(
        state="User greets with hello.",
        questions=[
            {"type": "choice", "name": "tone", "instructions": "What tone?",
             "criteria": {"warm": "friendly", "neutral": "informational"}},
        ],
    )
    assert len(ds) == 1
    assert ds[0].kind == "choice"
    assert ds[0].value in ("warm", "neutral")
    assert ds[0].confidence is not None
    assert meta["latency_ms"] < 1000

def test_noul_returns_probability():
    if not backend.available():
        return
    ds, meta = backend.decide_batch(
        state="User says: I love this!",
        questions=[
            {"type": "noul", "name": "is_positive", "instructions": "Is this message positive?"},
        ],
    )
    assert ds[0].kind == "noul"
    assert 0.0 <= ds[0].value <= 1.0

def test_batch_returns_n_decisions():
    if not backend.available():
        return
    ds, meta = backend.decide_batch(
        state="User: Hello!",
        questions=[
            {"type": "noul", "instructions": "is happy?"},
            {"type": "choice", "instructions": "tone?", "criteria": {"warm": "x", "cool": "y"}},
            {"type": "score", "instructions": "urgency?", "criteria": ["low", "med", "high"]},
        ],
    )
    assert len(ds) == 3
    assert meta["questions"] == 3

if __name__ == "__main__":
    test_api_available()
    test_choice_returns_valid()
    test_noul_returns_probability()
    test_batch_returns_n_decisions()
    print("✓ All integration tests passed")
