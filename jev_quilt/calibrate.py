"""Calibrated alarm floors: legality is not calibration.

`predictor.alarm(outcome, predicted, floor)` is law 5's binary side, but with a
FIXED floor it has a failure mode the fleet keeps rediscovering — the
*bored-middle*. In a long calm the ambient surprise is tiny; a floor set generous
enough for a normal regime sleeps straight through a small-but-real novelty
sitting in the quiet. The cell was never illegal. It was over-confident. Those are
different sins, and only the second one loses the reactor.

This module adds an adaptive floor that tracks the *calm* surprise level and sets
the alarm at `slack` times it — so it TIGHTENS where nothing has happened (staying
sensitive exactly in the bored middle) and a single spike still clears it because
the floor is computed from the window *before* the spike is folded in
(predict-before-update, the predictor's own discipline). Fully exact: the floor is
an exact-ℚ mean × an exact-ℚ slack, never a float where identity matters.

Pairs with `MeanPredictor`: the predictor says what to expect; `surprise` grades
the miss; `CalibratedFloor` says how big a miss is worth a raised hand *here*.
"""

from __future__ import annotations
from typing import Optional

from .q16 import Q16
from .predictor import MeanPredictor, surprise


class CalibratedFloor:
    """An adaptive alarm floor over the last K surprises, in exact ℚ.

    floor = max(floor_min, mean(last K surprises) * slack)

    A quiet window → a low floor → sensitive to a small novelty (defeats the
    bored-middle). A spike is judged against the pre-spike window, so it still
    alarms; afterwards its weight is only 1/K of the mean, so the floor relaxes
    back rather than staying inflated (no alarm storm, no permanent deafness).
    floor_min keeps an all-zero calm from setting a zero floor that would alarm
    on nothing.
    """

    EXACT_K = MeanPredictor.EXACT_K   # same 1/K-exact family; an inexact floor is a lie too

    def __init__(self, k: int = 8, slack: Q16 = Q16(5, 2), floor_min: Q16 = Q16(1, 1000)):
        if k not in self.EXACT_K:
            raise ValueError(f"CalibratedFloor: k={k} would make 1/K inexact; choose from the exact family")
        if not isinstance(slack, Q16) or not isinstance(floor_min, Q16):
            raise TypeError("CalibratedFloor: slack and floor_min must be Q16 (identity never floats)")
        self.k = k
        self.slack = slack
        self.floor_min = floor_min
        self._window: list[Q16] = []

    def floor(self) -> Optional[Q16]:
        """The current alarm floor, or None until warmed (a floor before evidence
        is a lie, same honesty as the predictor's warmup)."""
        if len(self._window) < self.k:
            return None
        mean = sum(self._window, Q16(0)) * Q16(1, self.k)
        f = mean * self.slack
        return f if f > self.floor_min else self.floor_min

    def update(self, s: Q16) -> None:
        """Fold in one observed surprise (call AFTER using floor() this tick)."""
        if not isinstance(s, Q16):
            raise TypeError("CalibratedFloor.update: surprise must be Q16")
        self._window.append(s)
        if len(self._window) > self.k:
            self._window.pop(0)

    @property
    def warmed(self) -> bool:
        return len(self._window) >= self.k


def alarm_calibrated(outcome: Q16, predicted: Q16, cal: CalibratedFloor,
                     *, learn: bool = True) -> bool:
    """Law 5 with a calibrated floor. Returns False (no alarm) until warmed —
    absence of evidence is not a raised hand. When `learn`, the observed surprise
    is folded into the floor after the judgment (predict-before-update)."""
    s = surprise(outcome, predicted)
    f = cal.floor()
    fired = f is not None and s > f
    if learn:
        cal.update(s)
    return fired
