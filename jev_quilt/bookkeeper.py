"""Bookkeeper: per-cell append-only WAL of state changes.

Law 4: every state change is booked; replay ≡ live. A cell woken by a
delta replays its book to catch up, then decides.

G20a (closes C9 — fail-open revocation): `payload` stays exactly what it
always was, a capped, human-readable RENDER of the booked call — audited,
never decided from (Law 3). Callers that carry decision-bearing identity
(a dispatcher, a router — see `orgbook.py`) additionally hand `book()` a
small set of TYPED, UNCAPPED fields (`dispatch_id`, `runner`, `key`,
`correct`, `base_verdict`, `answer`). Those live as real dataclass fields
on `Receipt`, never JSON, never sliced — so a 200-char render budget can
never evict them (Law 1: identity never floats). `book()` refuses (raises)
rather than silently rounds a decision field it cannot carry EXACTLY —
non-str/bool typing, or a value containing the reserved `\x1f` the
canonical pipe-joined form uses as its delimiter (Law 6 clause iii:
booked ⇔ foldable). A booking that never sets these typed fields is
byte-for-byte unaffected: `Receipt.sha()` only extends its preimage when
at least one is present, so every existing chain/pin computed over plain
`book()` calls (the fleet's other cells, the cross-language vectors) is
untouched — this is a declared, additive pin change scoped to the
callers that opt in (see `orgbook.py`, `schoolhouse.py`).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional
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

    # ── G20a: typed, uncapped decision-bearing fields (Law 1/3/6) ──────
    # None for every receipt booked the historical way (no caller opts in
    # — the fleet's other cells, the cross-language vectors); populated
    # only by a caller that identifies a booking as a routing DECISION
    # (see `orgbook.record_dispatch`). Never capped, never read from JSON.
    dispatch_id: Optional[str] = None
    runner: Optional[str] = None
    key: Optional[str] = None
    correct: Optional[bool] = None
    base_verdict: Optional[str] = None
    answer: Optional[str] = None

    def decision_bytes(self) -> bytes:
        """Canonical `\x1f`-delimited UTF-8 form of the typed decision
        fields (same bytes-law shape as `attest.canonical_attestation_bytes`
        / `diploma.canonical_diploma_bytes`: pipe/unit-separator joined,
        no JSON, no repr). Empty bytes when NONE of the typed fields were
        set — the signal `sha()` uses to leave the historical preimage
        byte-for-byte alone."""
        fields = (self.dispatch_id, self.runner, self.key, self.correct,
                 self.base_verdict, self.answer)
        if all(f is None for f in fields):
            return b""
        def enc(v):
            if v is None:
                return ""
            if isinstance(v, bool):
                return "1" if v else "0"
            return v
        return "\x1f".join(enc(f) for f in fields).encode("utf-8")

    def sha(self) -> str:
        # The chain binds the residue TEXT, not merely its hash field:
        # a residue-carrying receipt re-derives payload_hash from the
        # retained payload, so editing payload alone breaks replay
        # (same rule as the Rust substrate's verify). Empty payload keeps
        # the stored hash — the historical formula, back-compat pinned.
        payload_hash = (f"{fnv1a(self.payload.encode('utf-8')):016x}"
                        if self.payload else self.payload_hash)
        raw = f"{self.tick}|{self.state_hash}|{self.delta_hash}|{self.decision_kind}|{payload_hash}"
        # G20a: the typed decision fields extend the preimage, EXACTLY
        # like the residue clause above — present only when a caller set
        # them, absent (byte-identical to the historical formula) otherwise.
        decision = self.decision_bytes()
        if decision:
            raw = raw + "|" + decision.decode("utf-8")
        return hashlib.sha256(raw.encode()).hexdigest()


def _refuse_unrepresentable_decision_fields(**fields) -> None:
    """Law 6 clause (iii), operational at the source: a decision-bearing
    field `book()` cannot carry EXACTLY through the typed canonical form is
    refused HERE — raised, like `attest` on an unreproduced claim — never
    rounded, coerced, or silently truncated (see the module docstring and
    `ai-writings/situations/FABLE-ANSWER.md` §3.3)."""
    for name, value in fields.items():
        if value is None:
            continue
        if name == "correct":
            if not isinstance(value, bool):
                raise ValueError(
                    f"Bookkeeper.book: decision field 'correct'={value!r} is "
                    "not a bool — a decision-bearing field is typed exactly, "
                    "never coerced; refused, not rounded")
            continue
        if not isinstance(value, str):
            raise ValueError(
                f"Bookkeeper.book: decision field {name!r}={value!r} is not "
                "a str — refused, not coerced")
        if "\x1f" in value:
            raise ValueError(
                f"Bookkeeper.book: decision field {name!r} contains the "
                "reserved U+001F unit separator and cannot be carried "
                "exactly in the canonical pipe-joined form — refused, not "
                "truncated (Law 6 totality)")


@dataclass
class Bookkeeper:
    cell_name: str
    entries: list = field(default_factory=list)
    _tick: int = 0

    def book(self, state, delta, decision_kind: str, payload, *,
             dispatch_id: Optional[str] = None, runner: Optional[str] = None,
             key: Optional[str] = None, correct: Optional[bool] = None,
             base_verdict: Optional[str] = None,
             answer: Optional[str] = None) -> Receipt:
        # Law 6 totality: refuse what cannot be carried EXACTLY, before any
        # tick is spent or any entry appended — a refused booking never
        # partially lands.
        _refuse_unrepresentable_decision_fields(
            dispatch_id=dispatch_id, runner=runner, key=key,
            correct=correct, base_verdict=base_verdict, answer=answer)
        self._tick += 1
        # readable residue: the projection keeps the full record; the
        # receipt keeps a capped, hashed copy so replay can be AUDITED
        # without the projection (tracing is following, not guessing).
        # This is a RENDER, never the decision's source of truth (Law 3)
        # — see the typed fields below for what a caller decides from.
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
            dispatch_id=dispatch_id, runner=runner, key=key, correct=correct,
            base_verdict=base_verdict, answer=answer,
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
