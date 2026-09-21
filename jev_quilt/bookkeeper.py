"""Bookkeeper: per-cell append-only WAL of state changes.

Law 4: every state change is booked; replay ≡ live. A cell woken by a
delta replays its book to catch up, then decides.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import json
import time


@dataclass(frozen=True)
class Receipt:
    tick: int
    state_hash: str
    delta_hash: str
    decision_kind: str
    payload_hash: str
    payload: str = ""   # capped readable residue (see Bookkeeper.book)

    def sha(self) -> str:
        raw = f"{self.tick}|{self.state_hash}|{self.delta_hash}|{self.decision_kind}|{self.payload_hash}"
        return hashlib.sha256(raw.encode()).hexdigest()


@dataclass
class Bookkeeper:
    cell_name: str
    entries: list = field(default_factory=list)
    _tick: int = 0

    def book(self, state, delta, decision_kind: str, payload) -> Receipt:
        self._tick += 1
        # readable residue: the projection keeps the full record; the
        # receipt keeps a capped, hashed copy so replay can be AUDITED
        # without the projection (tracing is following, not guessing).
        residue = json.dumps(payload, sort_keys=True, default=str)[:200]
        r = Receipt(
            tick=self._tick,
            state_hash=hashlib.sha256(json.dumps(state, sort_keys=True, default=str).encode()).hexdigest(),
            delta_hash=hashlib.sha256(json.dumps(delta, sort_keys=True, default=str).encode()).hexdigest(),
            decision_kind=decision_kind,
            payload_hash=hashlib.sha256(residue.encode()).hexdigest(),
            payload=residue,
        )
        self.entries.append(r)
        return r

    def replay(self) -> str:
        """Recompute the chain hash from the book. Divergence vs the stored
        receipts = tampering or clock skew; replay is the referee."""
        h = hashlib.sha256()
        for e in self.entries:
            h.update(e.sha().encode())
        return h.hexdigest()

    def verify(self) -> bool:
        """Structural check: ticks strictly increasing, no empty tail."""
        ticks = [e.tick for e in self.entries]
        return ticks == list(range(1, len(ticks) + 1))

    def wake_state(self) -> dict:
        """State handed to a woken cell: last booked state (by hash) + catchup set."""
        return {
            "cell": self.cell_name,
            "booked_ticks": self._tick,
            "chain": self.replay() if self.entries else None,
        }
