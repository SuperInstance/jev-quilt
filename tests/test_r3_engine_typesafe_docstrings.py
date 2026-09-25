"""R3 docstring-vs-behavior pins — engine WakeResult + typesafe confidence.

The R3 sweep caught two drift sites in the jeviter/engine/typesafe/tap
lane:

* `WakeResult.reason`'s inline comment listed `"decided" | "rejected" |
  "silent_deadband"` but `Engine._wake` has always returned `"refused"`
  for backend exceptions (and tests already book it). The comment is
  corrected, and this file pins the public surface so the omission
  cannot drift back.
* `typesafe_client`'s module contract documents a separate `confidence`
  field in every systemone answer, but the `noul` branch was using the
  noul probability as confidence. A confident NO (`noul: 0.0`,
  `confidence: 0.93`) therefore looked non-viable to Law 5. The client
  now honors `confidence`, falling back to the noul probability only
  when the API omits it, and the module doc says so explicitly.
"""

import inspect
import io
import json

from jev_quilt import engine as engine_mod
from jev_quilt.backends import BackendDecision
from jev_quilt.typesafe_client import TypeSafeBackend


def test_wake_result_reason_comment_includes_backend_refusal():
    """R3 audit pin: WakeResult.reason documents every reason Engine emits."""
    src = inspect.getsource(engine_mod.WakeResult)
    assert '"refused"' in src
    assert '"decided"' in src
    assert '"rejected"' in src
    assert '"silent_deadband"' in src


def test_typesafe_module_doc_pins_confidence_fallback():
    """R3 audit pin: the contract cannot reintroduce noul-as-confidence."""
    import jev_quilt.typesafe_client as mod

    params = list(inspect.signature(TypeSafeBackend.decide).parameters)
    assert params[1:] == ["payload", "state"]
    doc = mod.__doc__ or ""
    assert "confidence" in doc
    assert "noul probability" in doc


def test_typesafe_noul_honors_api_confidence(monkeypatch):
    """A confident NO is viable: noul probability != confidence."""
    payload = {
        "model": "stub",
        "answers": {
            "is_active": {"type": "noul", "noul": 0.0, "confidence": 0.93},
        },
    }

    def fake_urlopen(req, timeout=None):
        assert req.full_url.endswith("/v1/systemone")
        return io.BytesIO(json.dumps(payload).encode("utf-8"))

    monkeypatch.setattr(
        "jev_quilt.typesafe_client.urllib.request.urlopen", fake_urlopen
    )
    decision = TypeSafeBackend(api_key="x").decide(
        {"type": "noul", "instructions": "Is it active?"}, {"state": "object"}
    )
    assert isinstance(decision, BackendDecision)
    assert decision.kind == "noul"
    assert decision.value == 0.0
    assert decision.confidence == 0.93


def test_typesafe_noul_confidence_falls_back_to_probability(monkeypatch):
    """Backward-compatible fallback when the API omits confidence."""
    payload = {
        "model": "stub",
        "answers": {"is_active": {"type": "noul", "noul": 0.75}},
    }

    def fake_urlopen(req, timeout=None):
        return io.BytesIO(json.dumps(payload).encode("utf-8"))

    monkeypatch.setattr(
        "jev_quilt.typesafe_client.urllib.request.urlopen", fake_urlopen
    )
    decision = TypeSafeBackend(api_key="x").decide(
        {"type": "noul", "instructions": "Is it active?"}, {}
    )
    assert decision.value == 0.75
    assert decision.confidence == 0.75
