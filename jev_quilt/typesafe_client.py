"""TypeSafe Jev API backend (real client).

Wire protocol (verified 2026-09-21):
POST {base}/v1/systemone with body
{model, state, questions:{name:{type, instructions, criteria}}}
where type is lowercase: "noul" | "choice" | "score".
- noul: instructions is the yes/no question/statement
- choice: instructions + criteria dict {option_name: description}
- score: instructions + criteria list (ordered rubric levels)

Response: {model, answers:{name:{type, value/noul/score, confidence, probabilities}}}

Env: JEV_API_KEY or TYPESAFE_API_KEY or TYPESAFEAI_KEY;
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
        # Try multiple env var names for the API key
        self.key = (api_key
                    or os.environ.get("JEV_API_KEY")
                    or os.environ.get("TYPESAFE_API_KEY")
                    or os.environ.get("TYPESAFEAI_KEY"))
        self.timeout = timeout_s

    def available(self) -> bool:
        return bool(self.key)

    def decide_batch(self, state, questions: list[dict], model: str = "jev-latest") -> tuple[list[BackendDecision], dict]:
        """One parallel pass, N questions. Returns (decisions, meta)."""
        if not self.key:
            raise RuntimeError("typesafe-api: no API key (JEV_API_KEY/TYPESAFE_API_KEY/TYPESAFEAI_KEY)")

        # Build questions dict {name: {type, instructions, criteria}}
        qs = {}
        for i, q in enumerate(questions):
            name = q.get("name", f"q{i+1}")
            qtype = q.get("type", "noul").lower()
            if qtype == "choice":
                opts = q.get("options") or q.get("criteria") or {}
                if isinstance(opts, dict):
                    criteria = opts
                else:
                    criteria = {str(o): str(o) for o in opts}
                qs[name] = {"type": "choice",
                            "instructions": q.get("instructions") or q.get("question", ""),
                            "criteria": criteria}
            elif qtype == "score":
                criteria = q.get("criteria") or q.get("rubric") or ["low", "medium", "high"]
                qs[name] = {"type": "score",
                            "instructions": q.get("instructions") or q.get("question", ""),
                            "criteria": criteria}
            else:  # noul
                qs[name] = {"type": "noul",
                            "instructions": q.get("instructions") or q.get("question", "")}

        body = json.dumps({"model": model, "state": state, "questions": qs}).encode()
        req = urllib.request.Request(
            f"{self.base}/v1/systemone", data=body,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.key}"})
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                payload = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"typesafe-api: HTTP {e.code}: {e.read().decode()[:300]}") from e
        latency_ms = (time.monotonic() - t0) * 1000

        decisions = []
        for name, ans in payload.get("answers", {}).items():
            kind = ans.get("type", "")
            if kind == "noul":
                decisions.append(BackendDecision(
                    kind="noul", value=ans.get("noul"),
                    confidence=ans.get("noul"),
                    receipt_note=f"typesafe.latency_ms={latency_ms:.1f}"))
            elif kind == "choice":
                decisions.append(BackendDecision(
                    kind="choice", value=ans.get("choice"),
                    probabilities=ans.get("probabilities"),
                    confidence=ans.get("confidence"),
                    receipt_note=f"typesafe.latency_ms={latency_ms:.1f}"))
            elif kind == "score":
                decisions.append(BackendDecision(
                    kind="score", value=ans.get("score"),
                    probabilities=ans.get("probabilities"),
                    confidence=ans.get("confidence"),
                    receipt_note=f"typesafe.latency_ms={latency_ms:.1f}"))
        meta = {"latency_ms": latency_ms, "questions": len(questions),
                "decisions": len(decisions), "model": payload.get("model", "jev"),
                "input_tokens": payload.get("usage", {}).get("input_tokens", 0),
                "output_tokens": payload.get("usage", {}).get("output_tokens", 0)}
        return decisions, meta

    def decide(self, payload: dict, state) -> BackendDecision:
        """Single-question convenience over decide_batch. Backwards-compatible
        with the v0 contract: payload is a Question dict, state is the content."""
        q = dict(payload)
        if "question" in q and "instructions" not in q:
            q["instructions"] = q.pop("question")
        ds, _ = self.decide_batch(state, [q])
        return ds[0]
