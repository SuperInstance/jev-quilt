import pytest
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

import os



from jev_quilt.typesafe_client import TypeSafeBackend


def test_no_key_refuses(monkeypatch):
    monkeypatch.delenv("JEV_API_KEY", raising=False)
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    b = TypeSafeBackend(api_key=None)
    assert not b.available()
    with pytest.raises(RuntimeError, match="no API key"):
        b.decide({"question": {"type": "noul"}}, {})


def test_available_with_either_env(monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.setenv("JEV_API_KEY", "apikey_test")
    assert TypeSafeBackend().available()
    monkeypatch.delenv("JEV_API_KEY", raising=False)
    monkeypatch.setenv("TYPESAFE_API_KEY", "sk-test")
    assert TypeSafeBackend().available()


def test_base_url_precedence(monkeypatch):
    monkeypatch.setenv("JEV_API_KEY", "x")
    monkeypatch.setenv("JEV_BASE_URL", "https://jev.example.com/")
    assert TypeSafeBackend().base == "https://jev.example.com"
    monkeypatch.delenv("JEV_BASE_URL", raising=False)
    assert TypeSafeBackend().base.endswith("typesafe.ai")


def test_decide_requires_question():
    b = TypeSafeBackend(api_key="x")
    with pytest.raises(ValueError, match="question"):
        b.decide({}, None)


def test_offline_battery_smoke(tmp_path):
    from jev_quilt.experiments import run
    out = tmp_path / "report.json"
    assert run(live=False, n=1, out_path=str(out)) == 0
    import json
    r = json.loads(out.read_text())
    assert r["mode"] == "offline" and r["book_verify"] is True
    assert r["questions"] == 8  # 3+2+3 questions across the three domains
