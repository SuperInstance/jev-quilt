"""Witness RNG: deterministic randomness from the ledger's own state.

Spring from SuperInstance/substrate-rng (Mavis, 2026-09-20): "every cell IS
its witness log; from that state, a seed; from that seed, reproducible
randomness. Two visitors in the same room get the same rolls."

The quilt version: the seed is the tail hash of a bookkeeper's receipt
chain (or any engine state dict). Rolls are exact Q16 fractions carved
from the hash bytes — never floats. Therefore replay-identical: replay
the same events, the same receipts hash, the same seed, the same rolls.
Randomness that is itself bookable, hence auditable, hence honest.

Two engines in the same state roll the same futures. Imagination becomes
reproducible Monte-Carlo without trusting a PRNG's mood.
"""

from __future__ import annotations
import hashlib
import json
from typing import Iterable, Optional

from .q16 import Q16
from .bookkeeper import Bookkeeper


def seed_from_state(state: dict) -> int:
    """One seed from any engine state. Stable under key order."""
    raw = json.dumps(state, sort_keys=True, default=str).encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8], "big")


def seed_from_book(book: Bookkeeper, tail: int = 0) -> int:
    """Seed from the tail of a receipt chain: tail=0 is the empty book
    (pre-first-decision reproducibility), tail=n hashes receipts[-n:]."""
    if tail and book.entries:
        window = book.entries[-tail:]
        raw = "|".join(e.sha() for e in window).encode()
    else:
        raw = b""
        if book.entries:
            raw = book.entries[-1].sha().encode()
    return int.from_bytes(hashlib.sha256(raw or b"empty-witness").digest()[:8], "big")


class WitnessRng:
    """Exact-fraction RNG. next_q16() returns Q16(h, 2^16) where h is a
    16-bit carve of the evolving digest stream — bounded, exact, and
    fully determined by the seed."""

    def __init__(self, seed: int):
        self._ctr = 0
        self._seed = seed & ((1 << 64) - 1)

    def _carve(self) -> int:
        raw = f"{self._seed}:{self._ctr}".encode()
        self._ctr += 1
        return int.from_bytes(hashlib.sha256(raw).digest()[:2], "big")

    def next_q16(self) -> Q16:
        return Q16(self._carve(), 1 << 16)   # in [0, 1), exact dyadic

    def below(self, q: Q16) -> bool:
        return self.next_q16() < q

    def pick(self, options: list):
        if not options:
            raise ValueError("pick: empty options")
        idx = self._carve() % len(options)
        return options[idx]

    def weighted(self, weights: dict) -> object:
        """Integer-weighted pick; ties resolve by lowest carve, exact."""
        if not weights:
            raise ValueError("weighted: empty")
        total = sum(weights.values())
        roll = self._carve() % total
        acc = 0
        for k, w in weights.items():
            acc += w
            if roll < acc:
                return k
        raise AssertionError("unreachable")
