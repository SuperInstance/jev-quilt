"""Bookkeeper: per-cell append-only WAL of state changes.

Law 4: every state change is booked; replay ≡ live. A cell woken by a
delta replays its book to catch up, then decides.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import json
import time


def fnv1a(data: bytes) -> int:
    """fnv1a-64 over raw BYTES — the same algorithm the fleet's rate
    limiter, the hermit WAL, and the Rust substrate use. Hashing the
    UTF-8 encoding (never str iteration / ord()) keeps payload_hash
    identical across languages: a Rust receipt and a Python receipt for
    the same residue must agree, non-ASCII included."""
    h = 0xcbf29ce484222325
    for b in data:
        h ^= b
        h = (h * 0x100000001b3) % (1 << 64)
    return h


@dataclass(frozen=True)
class Receipt:
    tick: int
    state_hash: str
    delta_hash: str
    decision_kind: str
    payload_hash: str
    payload: str = ""   # capped readable residue (see Bookkeeper.book)

    def sha(self) -> str:
        # The chain binds the residue TEXT, not merely its hash field:
        # a residue-carrying receipt re-derives payload_hash from the
        # retained payload, so editing payload alone breaks replay
        # (same rule as the Rust substrate's verify). Empty payload keeps
        # the stored hash — the historical formula, back-compat pinned.
        payload_hash = (f"{fnv1a(self.payload.encode('utf-8')):016x}"
                        if self.payload else self.payload_hash)
        raw = f"{self.tick}|{self.state_hash}|{self.delta_hash}|{self.decision_kind}|{payload_hash}"
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
            # payload_hash = fnv1a-64 over the residue's UTF-8 bytes —
            # the SAME rule as the Rust substrate (polyform/rust), so
            # cross-language receipt compare works, non-ASCII included.
            payload_hash=f"{fnv1a(residue.encode('utf-8')):016x}",
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
