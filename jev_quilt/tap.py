"""Tap doctrine — the KL-gate and the monadic proposal-gate.

From docs/JEV-CELLULAR-SHEAF-PITCH.md (Casey, 2026-09-21):

* Law 5 is dead. Static floors fail: too low = micro-noise floods the
  mesh; too high = gradual drift slips through. A stochastic cell emits
  a delta only when the INFORMATION GAIN (KL divergence) of its new
  distribution exceeds a DYNAMIC threshold. Static environment -> the
  network goes dead silent. Rapid shift -> the valves open.
* Law 1: identity never floats. The neural model PROPOSES (a Choice
  Distribution); the exact Q16 cell DISPOSES. The refusal is booked too
  — a gate that never records what it rejected is a rumor, not a gate.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

from .bookkeeper import Bookkeeper
from .q16 import Q16

Distribution = Dict[str, Q16]  # exact-rational probabilities; sum == 1


def kl_divergence(p: Distribution, q: Distribution) -> float:
    """KL(p || q) in nats, exact rationals in, float MEASURE out.

    The divergence is a gauge (compared against a threshold), never
    identity — floats may measure, they may not name. Keys missing in q
    contribute q=eps (absolute continuity enforced, never silent).
    """
    eps = 1e-12
    total = 0.0
    for k, pk in p.items():
        if pk.num == 0:
            continue
        qk = q.get(k, Q16(0, 1))
        qf = max(qk.to_float(), eps)
        total += pk.to_float() * math.log(pk.to_float() / qf)
    return total


@dataclass
class TapGate:
    """Information-theoretic deadband with a dynamic threshold.

    Threshold = mean + k·stdev of the recent ACCEPTED information gains
    (the tap remembers what surprise felt like, and demands bigger).
    Static world -> KL stays 0 -> silent AND the tap stays thirsty
    (threshold decays). Burst -> threshold rises -> self-throttling.
    """

    k: float = 2.0
    window: int = 8
    floor_min: float = 1e-9
    accepted: list = field(default_factory=list)

    def threshold(self) -> float:
        if not self.accepted:
            return self.floor_min
        if len(self.accepted) == 1:
            return max(self.accepted[0], self.floor_min)
        mean = sum(self.accepted) / len(self.accepted)
        var = sum((x - mean) ** 2 for x in self.accepted) / len(self.accepted)
        return max(mean + self.k * math.sqrt(var), self.floor_min)

    def admit(self, p: Distribution, q: Distribution) -> tuple:
        """Old belief p, new reading q. Returns (emit, gain, threshold)."""
        gain = kl_divergence(p, q)
        th = self.threshold()
        if gain > th:
            self.accepted.append(gain)
            self.accepted = self.accepted[-self.window:]
            return True, gain, th
        return False, gain, th


# The monadic proposal-gate: System 1 proposes, System 2 disposes.
# An invariant is a named exact-rational predicate over the proposed
# identity. Violations are booked as refusals — the titanium records
# every crash of probability into Law 1.
Invariant = Callable[[Q16], bool]


@dataclass
class ProposalGate:
    """Hard boundary between stochastic proposals and exact state.

    propose(name, choice_dist, q16_identity):
      1. Law 1: the identity MUST be Q16. A float coordinate is refused
         before any invariant runs — identity never floats.
      2. The top choice must be admitted by every invariant.
      3. Accept -> book 'transition'. Refuse -> book 'refusal' with the
         reason. BOTH are receipts; a silent gate is a rumor.
    """

    keeper: Bookkeeper
    invariants: list = field(default_factory=list)  # (name, Invariant)

    def add_invariant(self, name: str, fn: Invariant) -> "ProposalGate":
        self.invariants.append((name, fn))
        return self

    def propose(self, state, delta, choice_dist: Distribution,
                q16_identity) -> tuple:
        """Returns (accepted: bool, reason: str, receipt)."""
        if not isinstance(q16_identity, Q16):
            r = self.keeper.book(state, delta, "refusal",
                                 {"law": 1, "reason": "identity_floats",
                                  "got": type(q16_identity).__name__})
            return False, "identity_floats", r
        top = max(choice_dist.items(), key=lambda kv: kv[1].to_float())[0]
        for name, fn in self.invariants:
            try:
                ok = bool(fn(q16_identity))
            except Exception as exc:  # an invariant that throws refuses
                ok = False
                name = f"{name}!{type(exc).__name__}"
            if not ok:
                r = self.keeper.book(state, delta, "refusal",
                                     {"invariant": name, "choice": top,
                                      "q16": f"{q16_identity.num}/{q16_identity.den}"})
                return False, name, r
        r = self.keeper.book(state, delta, "transition",
                             {"choice": top,
                              "q16": f"{q16_identity.num}/{q16_identity.den}",
                              "p": max(v.to_float() for v in choice_dist.values())})
        return True, "ok", r
