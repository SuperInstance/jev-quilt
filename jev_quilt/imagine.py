"""Imagination: JEPA simulating a JEV decision.

A WorldModel is an exact transition table over a finite state space.
Deciding is NOT reading logits — it is rolling candidate futures and
scoring their terminal energies. But the surface act re-enacts JEV:
the output is a typed Choice with exact probabilities, bookable like
any other decision. JEPA imagines; JEV signs.

Exactness: energies are Q16; comparisons are cross-multiplication,
never float division; action weights are integers; probabilities =
weight / sum(weights), all exact. A horizon*actions budget refuses
rather than grows without bound — imagination is compute, and compute
must bill honestly.
"""

from __future__ import annotations
from typing import Callable

from .q16 import Q16
from .backends import BackendDecision

Transition = Callable[[Q16, str], Q16]   # (state, action) -> next state
Energy = Callable[[Q16], Q16]            # state -> cost (lower is better)

MAX_ROLLS = 4096  # honest compute budget; refuse beyond it


def _lt(a: Q16, b: Q16) -> bool:
    """Exact ordering: cross-multiplication, floats never consulted."""
    return a.num * b.den < b.num * a.den


class WorldModel:
    def __init__(self, transition: Transition, energy: Energy):
        self.transition = transition
        self.energy = energy

    def roll(self, state: Q16, action: str, horizon: int) -> Q16:
        s = state
        for _ in range(horizon):
            s = self.transition(s, action)
        return s


def imagine_choice(world: WorldModel, state: Q16, actions: list[str],
                   horizon: int) -> BackendDecision:
    """Roll every candidate action's future; emit the typed Choice JEV
    would emit — ranked by imagined terminal energy, probabilities exact."""
    if not actions:
        raise ValueError("imagine_choice: no actions")
    rolls = len(actions) * max(1, horizon)
    if rolls > MAX_ROLLS:
        raise ValueError(f"imagine_choice: budget {rolls} > {MAX_ROLLS} — "
                         f"shrink horizon or actions (imagination must bill honestly)")
    energies = {a: world.energy(world.roll(state, a, horizon)) for a in actions}
    hi = next(iter(energies.values()))
    for e in energies.values():
        if _lt(hi, e):
            hi = e
    weights = {}
    for a, e in energies.items():
        gap = hi - e                      # Q16 >= 0
        weights[a] = 1 + gap.num // gap.den   # integer rank distance, exact
    total = sum(weights.values())
    probs = {a: Q16(w, total) for a, w in weights.items()}
    best = actions[0]
    for a in actions[1:]:
        if _lt(energies[a], energies[best]):
            best = a
    return BackendDecision(
        kind="choice", value=best, confidence=Q16(weights[best], total).to_float(),
        receipt_note="imagine:horizon=%d;probs=%s" % (
            horizon, ",".join(f"{a}:{probs[a]}" for a in actions)),
    )


def imagine_score(world: WorldModel, state: Q16, rubric: list[Q16],
                  horizon: int, action: str = "continue") -> BackendDecision:
    """Score variant: roll ONE imagined future; nearest rubric point by
    exact distance. The Noul variant is honesty itself: if the terminal
    energy is farther than 1.0 from every rubric point, refuse to score."""
    if horizon > MAX_ROLLS:
        raise ValueError("imagine_score: budget exceeded")
    terminal = world.roll(state, action, horizon)
    e = world.energy(terminal)

    def d2(r: Q16) -> Q16:
        d = e - r
        return Q16(d.num * d.num, d.den * d.den)  # |e-r|^2, exact, comparable

    from functools import cmp_to_key
    best = min(rubric, key=cmp_to_key(lambda x, y: -1 if _lt(d2(x), d2(y))
                                      else (1 if _lt(d2(y), d2(x)) else 0)))
    d = e - best
    if d.num * d.num > d.den * d.den:   # |e-best| > 1, exact
        return BackendDecision(kind="noul", value=None, confidence=1.0,
                               receipt_note=f"imagine:noul;terminal_energy={e}")
    return BackendDecision(kind="score", value=best, confidence=1.0,
                           receipt_note=f"imagine:score;energy={e};nearest={best}")
