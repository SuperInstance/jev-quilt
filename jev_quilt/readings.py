"""Readings: a JEV cell hosting a variety of JEPA emulations.

A "reading" is one way a world-model can predict — mean, persistence,
period, drift. Each is exact, each books its own surprise, and a JEV
Choice (the engine's own argmax rule) selects which reading to trust
per tick by calibrated integer weights over their exact alarm counts.

That is JEV simulating JEPA concretely: not a metaphor, a managing
relation. The ensemble's committed prediction is the selected reading's
prediction; the ledger books WHICH reading was trusted, so the selection
itself is auditable. Where every reading stays alarmed, the ensemble
names the hole: model class wrong — a real-JEPA-shaped gap, not a knob.

Protocol note: predict()/update() match the engine's Predictor slot
exactly — an ensemble drops into any cell that takes a predictor.
Alarm accounting for the WEIGHTS lives inside the ensemble (its own
floor); the RECEIPT's alarm stays engine-side. Two ledgers, two jobs.
"""

from __future__ import annotations
from typing import Optional

from .q16 import Q16
from .predictor import MeanPredictor, surprise


class ConstReading:
    """Persistence: tomorrow is today. Exact trivially."""

    def __init__(self):
        self._last: Optional[Q16] = None

    def predict(self) -> Optional[Q16]:
        return self._last

    def update(self, outcome: Q16) -> None:
        self._last = outcome


class NgramReading:
    """Period-k: the value k beats ago repeats. For periodic signals the
    strongest cheap reader — it locks exactly once one full period is seen."""

    def __init__(self, k: int):
        if k < 1:
            raise ValueError("ngram k>=1")
        self.k = k
        self._window: list[Q16] = []

    def predict(self) -> Optional[Q16]:
        if len(self._window) < self.k:
            return None
        return self._window[0]  # the value k beats ago

    def update(self, outcome: Q16) -> None:
        self._window.append(outcome)
        if len(self._window) > self.k:
            self._window.pop(0)


class DriftReading:
    """Trend: last value + mean increment. Exact-K increments window."""

    def __init__(self, k: int = 4):
        if k not in MeanPredictor.EXACT_K:
            raise ValueError("drift: k must be in the exact family")
        self._mean = MeanPredictor(k=k)
        self._last: Optional[Q16] = None

    def predict(self) -> Optional[Q16]:
        m = self._mean.predict()
        if m is None or self._last is None:
            return None
        return self._last + m

    def update(self, outcome: Q16) -> None:
        # increment = outcome - previous outcome (consecutive difference).
        # The first draft double-lagged via a _prev field and learned
        # two-step differences — the ramp test caught it.
        if self._last is not None:
            self._mean.update(outcome - self._last)
        self._last = outcome


class ReadingEnsemble:
    """JEV managing its JEPA readings. Each reading earns an integer
    weight = MAXC - min(alarms, MAXC); ties break alphabetically for
    determinism. The committed prediction comes from the trusted
    reading; last_choice records which one, for the receipt residue."""

    MAXC = 64

    def __init__(self, readings: dict[str, object], floor: Q16 = Q16(15, 100)):
        if not readings:
            raise ValueError("ensemble needs >=1 reading")
        self.readings = readings
        self.floor = floor
        self.alarms: dict[str, int] = {n: 0 for n in readings}
        self.last_choice: Optional[str] = None

    def _weights(self) -> dict[str, int]:
        return {n: self.MAXC - min(a, self.MAXC)
                for n, a in self.alarms.items()}

    def predict(self) -> Optional[Q16]:
        weights = self._weights()
        best = max(weights.values())
        chosen = sorted(n for n, w in weights.items() if w == best)[0]
        self.last_choice = chosen
        return self.readings[chosen].predict()

    def update(self, outcome: Q16) -> None:
        for name, r in self.readings.items():
            pred = r.predict()
            r.update(outcome)
            if pred is not None and surprise(outcome, pred) > self.floor:
                self.alarms[name] += 1
