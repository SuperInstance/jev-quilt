"""Predictors: the feeling under the double-entry bookkeeping.

A predictor sits beneath a cell's ledger and says, before each decision,
what it expects the decision's graded value to be. The bookkeeper records
both sides of the comparison — the pre-committed prediction and the
outcome — so surprise is an exact, replayable quantity.

This is the JEPA slot, deliberately model-agnostic: v0 ships an exact
mean-of-K predictor; a JEPA world-model plugs in behind the same two
methods. Law 5 holds throughout: surprise is graded (Q16), alarm is
binary (surprise > floor).
"""

from __future__ import annotations
from typing import Optional, Protocol

from .q16 import Q16


class Predictor(Protocol):
    def predict(self) -> Optional[Q16]: ...   # None = not warmed yet
    def update(self, outcome: Q16) -> None: ...


class MeanPredictor:
    """Exact running mean of the last K outcomes. Fully closed in ℚ:
    sum is exact, 1/K is exact (K | 10^6 kept by choosing K from
    {1,2,4,5,8,10,16,20,25,...} — v0 asserts K in that family and
    refuses otherwise, because an inexact predictor would be a lie
    wearing the ledger's clothes."""

    EXACT_K = {1, 2, 4, 5, 8, 10, 16, 20, 25, 32, 40, 50, 64, 80, 100,
               125, 128, 160, 200, 250, 256, 320, 400, 500, 512, 625,
               640, 800, 1000, 1024}

    def __init__(self, k: int = 4):
        if k not in self.EXACT_K:
            raise ValueError(f"MeanPredictor: k={k} would make 1/K inexact; "
                             f"choose from the exact family")
        self.k = k
        self._window: list[Q16] = []

    def predict(self) -> Optional[Q16]:
        if len(self._window) < self.k:
            return None
        return sum(self._window, Q16(0)) * Q16(1, self.k)

    def update(self, outcome: Q16) -> None:
        self._window.append(outcome)
        if len(self._window) > self.k:
            self._window.pop(0)

    @property
    def warmed(self) -> bool:
        return len(self._window) >= self.k


def surprise(outcome: Q16, predicted: Q16) -> Q16:
    """Exact graded difference between feeling and fact."""
    d = outcome - predicted
    return Q16(abs(d.num), d.den)


def alarm(outcome: Q16, predicted: Q16, floor: Q16) -> bool:
    """Binary viability of the intuition (law 5's other side)."""
    return surprise(outcome, predicted) > floor
