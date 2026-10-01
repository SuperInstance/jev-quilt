"""throttle — JEV as a homeostatic circuit breaker.

Normal rate limiters shed everything over quota: the 10,001st request
dies even if it is the only interesting one all hour. The
HomeostaticThrottle inverts this with the tap's ratchet: a call whose
fingerprint matches recent traffic is SILENCE (shed, receipted, free);
a call that genuinely surprises the window ESCALATES to the wrapped
function. A flood of identical requests costs nothing — novelty-
degenerate traffic self-sheds. Compute flows to the unexpected.

Law-abiding throughout: fingerprints are exact Q16 histograms over
character classes (vowels/consonants/digits/separators/other — Law 1,
never a float identity); every shed and every escalation books a
receipt (a silence you cannot audit is indistinguishable from an
outage); the window is the boundary belief, so the threshold tracks
the traffic's own shape instead of a fixed line an adversary can find.

Live API runs need JEV_API_KEY/TYPESAFEAI_KEY — without it, the
throttle still books and sheds; only `fn` execution is gated.
"""

from __future__ import annotations

from .bookkeeper import Bookkeeper
from .jeviter import JevIterator
from .q16 import Q16
from .tap import TapGate


def _fingerprint_buckets(text: str) -> dict:
    """Character-class histogram — a text IS a distribution over its
    character classes. Counts are exact Q16 rationals; normalization is
    reciprocal multiplication (Law 1 — never float division). Case is
    folded; digits and other bytes get their own buckets."""
    VOWELS = set("aeiou")
    counts = {"vowels": 0, "cons": 0, "digits": 0, "sep": 0, "other": 0}
    for ch in (text.lower() or "\x00"):
        if ch in VOWELS: counts["vowels"] += 1
        elif ch.isalpha(): counts["cons"] += 1
        elif ch.isdigit(): counts["digits"] += 1
        elif ch in " -_\t": counts["sep"] += 1
        else: counts["other"] += 1
    total = None
    for n in counts.values():
        q = Q16(n, 1)
        total = q if total is None else total + q
    denom = total if (total is not None and total.num > 0) else Q16(1, 1)
    return {name: Q16(n * denom.den, denom.num) for name, n in counts.items()}


class HomeostaticThrottle:
    """Wrap `fn`; admit calls by surprise, not by count.

    window: how many recent ADMITTED calls shape the boundary belief.
    k:      tap multiplier — higher k sheds more (novelty bar up).
    """

    def __init__(self, fn, gate: TapGate | None = None, keeper: Bookkeeper | None = None,
                 k: float = 2.0, window: int = 16, cell: str = "jev-throttle"):
        self.fn = fn
        self.gate = gate or TapGate(k=k)
        self.keeper = keeper or Bookkeeper(cell)
        self.window = window
        self._boundary: list[dict] = []
        self.escalated = 0
        self.shed = 0

    def _belief(self) -> dict | None:
        if not self._boundary:
            return None
        keys = self._boundary[0].keys()
        tot = len(self._boundary)
        return {key: Q16(sum(1 for r in self._boundary if max(r, key=lambda k: r[k].num) == key), tot)
                for key in keys}

    def __call__(self, text: str, *args, **kwargs):
        reading = _fingerprint_buckets(text)
        base = self._belief()
        if base is None:                       # first call seeds — no
            self._boundary.append(reading)     # belief, no refusal
            return self._escalate(text, args, kwargs, note="seed")
        emit, gain, th = self.gate.admit(base, reading)
        if not emit:
            self.shed += 1
            self.keeper.book({"shed": self.shed}, {"text": text[:64]}, "shed",
                             {"gain": gain, "th": th})
            return None
        self._boundary.append(reading)
        self._boundary = self._boundary[-self.window:]
        return self._escalate(text, args, kwargs, note="surprise")

    def _escalate(self, text, args, kwargs, note):
        self.escalated += 1
        self.keeper.book({"escalated": self.escalated}, {"text": text[:64]},
                         "escalated", {"note": note})
        return self.fn(text, *args, **kwargs)
