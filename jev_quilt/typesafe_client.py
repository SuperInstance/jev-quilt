"""TypeSafe Jev API backend (real client).

Wire protocol per the public SDK: POST {base}/v1/decide with
{state, questions:[{type, ...}]} -> decisions:[{type, value,
probabilities?, confidence?}]. Env: JEV_API_KEY or TYPESAFE_API_KEY;
JEV_BASE_URL or TYPESAFE_BASE_URL (default https://api.typesafe.ai).
"""

from __future__ import annotations
from dataclasses import dataclass
import json
import os
import time
import urllib.request
import urllib.error

from .backends import BackendDecision

DEFAULT_BASE = "https://api.typesafe.ai"


class TypeSafeBackend:
    name = "typesafe-api"

    def __init__(self, base_url: str | None = None, api_key: str | None = None,
                 timeout_s: float = 30.0):
        self.base = (base_url or os.environ.get("JEV_BASE_URL")
                     or os.environ.get("TYPESAFE_BASE_URL") or DEFAULT_BASE).rstrip("/")
        self.key = api_key or os.environ.get("JEV_API_KEY") or os.environ.get("TYPESAFE_API_KEY")
        self.timeout = timeout_s

    def available(self) -> bool:
        return bool(self.key)

    def decide_batch(self, state, questions: list[dict]) -> tuple[list[BackendDecision], dict]:
        """One parallel pass, N questions. Returns (decisions, meta) where
        meta carries latency + raw receipt fields for the bookkeeper."""
        if not self.key:
            raise RuntimeError("typesafe-api: no API key (JEV_API_KEY/TYPESAFE_API_KEY)")
        body = json.dumps({"state": state, "questions": questions}).encode()
        req = urllib.request.Request(
            f"{self.base}/v1/decide", data=body,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.key}"})
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"typesafe-api: HTTP {e.code}: {e.read().decode()[:300]}") from e
        latency_ms = (time.monotonic() - t0) * 1000
        decisions = []
        for d in payload.get("decisions", []):
            decisions.append(BackendDecision(
                kind=d.get("type", "unknown"),
                value=d.get("value"),
                probabilities=d.get("probabilities"),
                confidence=d.get("confidence"),
                receipt_note=f"typesafe.latency_ms={latency_ms:.1f}",
            ))
        meta = {"latency_ms": latency_ms, "questions": len(questions),
                "decisions": len(decisions), "model": payload.get("model", "jev")}
        return decisions, meta

    def decide(self, payload: dict, state) -> BackendDecision:
        """Single-question convenience over decide_batch."""
        q = payload.get("question")
        if q is None:
            raise ValueError("typesafe backend: payload needs 'question' dict")
        ds, _ = self.decide_batch(state, [q])
        return ds[0]
