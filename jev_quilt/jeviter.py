"""jeviter — JEV as a new type of iterator.

The for-loop is a poll: for x in stream pulls every tick whether or
not the world moved. JevIterator inverts it. __next__ pulls from the
underlying stream until the tap admits — iteration driven by
information gain, not by index. Silenced pulls are booked (the
refusal-is-booked doctrine: a silence you cannot audit is
indistinguishable from a hang). StopIteration ends with a witnessed
exhaustion receipt. The loop doesn't run; it rests, and reacts.
"""

from __future__ import annotations

from dataclasses import dataclass

from .bookkeeper import Bookkeeper
from .q16 import Q16
from .tap import TapGate


@dataclass
class JevEvent:
    value: dict
    gain: float
    threshold: float
    pulls: int          # how many stream pulls this event cost
    tick: int


class JevIterator:
    """Iterate a stream by surprise, not by index.

    stream: iterable of dicts (each a reading over the same keys).
    gate:   TapGate — admits when KL(prev_admitted, reading) > dynamic.
    keeper: books 'silence' per rejected pull and 'event' per yield.
    """

    def __init__(self, stream, gate: TapGate, keeper: Bookkeeper):
        self.stream = iter(stream)
        self.gate = gate
        self.keeper = keeper
        self.last = None          # last ADMITTED belief (the boundary)
        self.pulls = 0
        self.emitted = 0

    def __iter__(self):
        return self

    def __next__(self) -> JevEvent:
        for raw in self.stream:
            self.pulls += 1
            reading = {k: (v if isinstance(v, Q16) else
                           (Q16(int(v), 1) if float(v).is_integer() else Q16(0, 1)))
                       for k, v in raw.items()}
            total = None
            for r in reading.values():                     # exact Q16 sum,
                total = r if total is None else total + r  # then each value
            if total is not None and total.num > 0:        # divided by it:
                reading = {k: Q16(r.num * total.den,      # reciprocals are
                                   r.den * total.num)      # exact — Law 1
                           for k, r in reading.items()}    # intact
            if self.last is None:           # no belief, no refusal —
                self.last = reading         # the first pull SEEDS the
                self.keeper.book({"pulls": self.pulls}, raw, "seed",
                                 {"note": "belief established; not news"})
                continue                    # and iteration waits for change
            emit, gain, th = self.gate.admit(self.last, reading)
            if not emit:
                self.keeper.book({"pulls": self.pulls}, raw, "silence",
                                 {"gain": gain, "th": th})
                continue
            self.last = reading
            self.emitted += 1
            self.keeper.book({"emitted": self.emitted}, raw, "event",
                             {"gain": gain, "th": th})
            return JevEvent(reading, gain, th, self.pulls, self.emitted)
        self.keeper.book({"pulls": self.pulls}, {}, "exhausted",
                         {"emitted": self.emitted})
        raise StopIteration


def simulate(stream, k: float = 2.0, cell: str = "jev-iter") -> tuple:
    """Run the iterator to exhaustion. Returns (events, keeper)."""
    keeper = Bookkeeper(cell)
    it = JevIterator(stream, TapGate(k=k), keeper)
    return list(it), keeper
