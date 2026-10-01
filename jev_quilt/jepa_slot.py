"""JEPA slot watch: the alarm ledger names where a world model plugs in.

The predictor seam is deliberately model-agnostic (predictor.py: "This
is the JEPA slot"). MeanPredictor is exact but class-limited: it cannot
see structure — periodicity, regime memory, anything a running mean
cannot represent. This scanner reads a run's alarm ledgers and surfaces
cells whose alarm DENSITY says the predictor class is wrong there: a
named, receipt-backed candidate for plugging a JEPA world-model behind
the same predict()/update() pair.

Honest-negative discipline: a cell that merely had a bad week is not a
candidate. The bar is a MAJORITY of wakes alarmed (after a small
warm-up floor on wake count), computed by exact integer compare — no
rounding, no float shares in the law. A book that fails the structural
verify() is reported as a problem, never as a slot: an unverifiable
alarm stream is noise, not evidence. (Residue-level tamper against a
book with no external replay anchor is out of scope — the caller's
stored replay hash is the referee there, not this scan.)
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .bookkeeper import Bookkeeper


@dataclass(frozen=True)
class SlotCandidate:
    """One cell whose alarm density says: the predictor CLASS is wrong
    here, not just the predictor's luck. This is the seam where a JEPA
    world-model plugs in behind predict()/update()."""

    cell: str
    wakes: int
    alarms: int

    @property
    def alarm_share(self) -> Fraction:
        return Fraction(self.alarms, self.wakes)

    def __str__(self) -> str:
        return (f"{self.cell}: {self.alarms}/{self.wakes} wakes alarmed "
                f"({float(self.alarm_share):.0%}) — predictor class cannot "
                f"see this world's structure; plug a world model behind "
                f"predict()/update()")


def scan(books: dict[str, Bookkeeper], min_wakes: int = 8) -> tuple[list[SlotCandidate], list[str]]:
    """Majority-alarmed cells = JEPA plug candidates.

    Returns (candidates, problems). A book that fails the structural
    verify() lands in problems — an unverifiable alarm stream is never
    evidence. A book under min_wakes is skipped (cold cells haven't
    shown enough surface to classify the predictor, only to warm it).
    """
    candidates: list[SlotCandidate] = []
    problems: list[str] = []
    for name, bk in books.items():
        if not bk.verify():
            problems.append(f"{name}: receipt chain does not verify")
            continue
        wakes = len(bk.entries)
        if wakes < min_wakes:
            continue
        alarms = sum(1 for e in bk.entries if '"alarmed": "true"' in e.payload)
        if 2 * alarms >= wakes:  # majority, exact integer compare
            candidates.append(SlotCandidate(name, wakes, alarms))
    return candidates, problems
