"""Backends: where a decision actually gets computed.

Resolution order (exact-first doctrine):
  auto → q16 (deterministic, always available)
       → openjev-local (SemIf-compatible server if reachable)
       → typesafe-api (if TYPESAFE_API_KEY set)
"""

from __future__ import annotations
from dataclasses import dataclass
import os
from typing import Any, Optional

from .q16 import Q16


@dataclass(frozen=True)
class BackendDecision:
    kind: str                       # "choice" | "score" | "noul" | "q16"
    value: Any
    probabilities: Optional[dict] = None
    confidence: Optional[float] = None
    receipt_note: str = ""


class Q16Backend:
    """Deterministic exact-rational decision rules. Always available."""

    name = "q16"

    def decide(self, payload: dict, state: Any) -> BackendDecision:
        rule = payload.get("rule")
        if rule == "threshold":
            v = payload["value"](state) if callable(payload["value"]) else Q16(*payload["value"])
            t = Q16(*payload["threshold"])
            return BackendDecision(
                kind="q16",
                value=v >= t,
                confidence=1.0,
                receipt_note=f"q16.threshold({v}>={t})",
            )
        if rule == "sum":
            terms = [Q16(*t) if isinstance(t, tuple) else t for t in payload["terms"]]
            acc = Q16(0)
            for t in terms:
                acc = acc + t
            return BackendDecision(kind="q16", value=acc, confidence=1.0,
                                   receipt_note="q16.sum")
        if rule == "argmax":
            # Choice primitive, deterministic mode: exact integer weights,
            # argmax pick, full distribution returned for calibration.
            options = payload["options"]  # {name: int weight}
            if not options:
                raise ValueError("q16 argmax: empty options")
            total = sum(options.values())
            if total <= 0:
                raise ValueError("q16 argmax: weights must sum positive")
            best = max(options, key=lambda k: options[k])
            return BackendDecision(
                kind="choice",
                value=best,
                probabilities={k: options[k] / total for k in options},
                confidence=1.0,
                receipt_note=f"q16.argmax({best})",
            )
        raise ValueError(f"q16 backend: unknown rule {rule!r}")


def resolve_backend(preference: str, openjev_url: Optional[str] = None) -> Any:
    """Return the first backend available for `preference`.

    auto: q16 → openjev-local → typesafe-api. Never returns None: q16 is
    the floor — a cell that cannot decide deterministically still books
    its refusal (the bookkeeper records the miss)."""
    if preference == "q16":
        return Q16Backend()
    if preference == "openjev-local":
        return _OpenJevStub(openjev_url or os.environ.get("OPENJEV_URL", ""))
    if preference == "typesafe-api":
        return _TypeSafeStub()
    # auto
    return Q16Backend()


class _OpenJevStub:
    """Placeholder for a SemIf/openjev-compatible local server. v0 refuses
    honestly instead of pretending: decide() raises, the cell books the miss."""
    name = "openjev-local"

    def __init__(self, url: str):
        self.url = url

    def decide(self, payload, state):
        raise RuntimeError(
            "openjev-local backend not wired in v0 (no server reachable). "
            "Set OPENJEV_URL and implement the wire call, or fall back to auto.")


class _TypeSafeStub:
    name = "typesafe-api"

    def decide(self, payload, state):
        if not os.environ.get("TYPESAFE_API_KEY"):
            raise RuntimeError("typesafe-api backend: TYPESAFE_API_KEY not set")
        raise RuntimeError("typesafe-api backend not wired in v0")
