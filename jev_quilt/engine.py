"""Engine: the delta runtime. Hooks eat deltas, waking cells catch up
their book before deciding, decisions pass a binary viability floor
before they may project.

Law 2: hooks eat deltas, not values — below the floor is silence.
Law 4: wake = replay the book, then decide.
Law 5: below the viability floor → booked as REJECTED, never projected.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional

from .backends import resolve_backend, BackendDecision
from .bookkeeper import Bookkeeper
from .cell import Cell, Hook, DEADBAND
from .q16 import Q16


class _NullBookkeeper:
    """Cells without bookkeeping still decide; they just forget."""
    def book(self, *a, **k): return None
    def replay(self): return None
    def verify(self): return True
    def wake_state(self): return {"booked_ticks": 0, "chain": None}


DEFAULT_DEADBAND = Q16(0)  # DEADBAND token → no filtering unless the hook says otherwise


@dataclass
class WakeResult:
    cell: str
    woke: bool
    reason: str                          # "decided" | "silent_deadband" | "rejected" | "no_hook"
    decision: Optional[BackendDecision] = None
    projections_fired: list = field(default_factory=list)


class Engine:
    def __init__(self):
        self.cells: dict[str, Cell] = {}
        self.books: dict[str, Bookkeeper] = {}
        self.log: list[WakeResult] = []
        self._backends = {}

    def register(self, cell: Cell):
        self.cells[cell.name] = cell
        self.books[cell.name] = Bookkeeper(cell.name) if cell.bookkeeper else _NullBookkeeper()
        return cell

    def _backend_for(self, cell: Cell):
        if cell.name not in self._backends:
            self._backends[cell.name] = resolve_backend(cell.backend)
        return self._backends[cell.name]

    @staticmethod
    def _delta_magnitude(delta: Any) -> Optional[Q16]:
        if isinstance(delta, Q16):
            return delta if delta.num >= 0 else Q16(-delta.num, delta.den)
        if isinstance(delta, dict) and "mag" in delta:
            m = delta["mag"]
            return m if isinstance(m, Q16) else Q16(*m) if isinstance(m, tuple) else None
        return None

    def _passes_floor(self, hook: Hook, delta: Any) -> bool:
        if hook.floor is DEADBAND or hook.floor is None:
            return True
        mag = self._delta_magnitude(delta)
        if mag is None:
            return True  # unmeasurable deltas always wake (honest default)
        floor = hook.floor if isinstance(hook.floor, Q16) else Q16(*hook.floor)
        return mag >= floor

    def emit(self, source: str, delta: Any, state: Any = None) -> list[WakeResult]:
        """A source cell publishes a delta. Returns wake results for all
        hooked subscribers."""
        results = []
        for name, cell in self.cells.items():
            hooks = [h for h in cell.input_hooks if h.source == source]
            if not hooks:
                continue
            if not any(self._passes_floor(h, delta) for h in hooks):
                r = WakeResult(name, False, "silent_deadband")
                self.log.append(r)
                results.append(r)
                continue
            results.append(self._wake(cell, delta, state))
        return results

    def _wake(self, cell: Cell, delta: Any, state: Any) -> WakeResult:
        book = self.books[cell.name]
        catchup = book.wake_state()  # law 4: the book is caught up first
        backend = self._backend_for(cell)
        try:
            decision = backend.decide(cell.decision or {}, state)
        except Exception as e:
            # honest refusal: any backend failure books the miss, never
            # projects, never propagates — a crashing cell must not kill the fabric
            book.book(state, delta, "refused", {"error": str(e)[:200]})
            r = WakeResult(cell.name, True, "refused", None, [])
            self.log.append(r)
            return r
        book.book(state, delta, decision.kind, {"value": str(decision.value)})
        if not cell.viability_floor(decision):
            book.book(state, delta, "rejected", {"confidence": decision.confidence})
            r = WakeResult(cell.name, True, "rejected", decision, [])
            self.log.append(r)
            return r
        fired = [{"to": p.to, "as_type": p.as_type} for p in cell.outputs]
        r = WakeResult(cell.name, True, "decided", decision, fired)
        self.log.append(r)
        return r
