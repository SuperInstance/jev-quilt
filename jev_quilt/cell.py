"""Cell, Hook, Projection — the typed decision surface.

Law 1: identity never floats (coord is integer (k, s)).
Law 2: hooks eat deltas, not values — below the floor is silence.
Law 3: decide here, project elsewhere.
Law 5: viability is binary; above the floor deltas are graded.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

DEADBAND = "deadband"


@dataclass(frozen=True)
class Hook:
    """Subscription to a sibling cell's delta."""
    source: str                    # registry name of the source cell
    on: str = "delta"              # "delta" | "value" (value reserved; default delta)
    floor: Any = DEADBAND          # DEADBAND token or a Q16 magnitude
    when: Optional[Callable[[Any], bool]] = None
    # predicate on the emitted state: wake only if the state says this
    # hook cares. This is the "touch shallow" gate — hooks eat deltas,
    # but they also DECLINE deltas whose shape isn't theirs.
    # (frozen dataclass holds the callable by reference; fine for v0.)


@dataclass(frozen=True)
class Projection:
    """Where this cell's decision goes — another cell decides, never renders;
    this cell renders, never decides. Types are declared at the edge."""
    to: str                        # target cell / bus / surface name
    as_type: str                   # "json" | "coefficient" | "choice" | "bytes" | ...


@dataclass
class Cell:
    name: str
    coord: tuple                    # (k, s) integers — quilt identity
    input_hooks: list = field(default_factory=list)
    decision: Any = None            # Choice | Score | Noul | Q16Rule (backend payload)
    backend: str = "auto"           # auto | q16 | openjev-local | typesafe-api
    outputs: list = field(default_factory=list)
    bookkeeper: bool = True

    def __post_init__(self):
        if not (isinstance(self.coord, tuple) and len(self.coord) == 2
                and all(isinstance(c, int) for c in self.coord)):
            raise TypeError(f"cell {self.name}: coord must be integer (k, s) — identity never floats")
        if self.backend not in ("auto", "q16", "openjev-local", "typesafe-api"):
            raise ValueError(f"cell {self.name}: unknown backend {self.backend!r}")

    def viability_floor(self, decision: Any) -> bool:
        """Law 5: binary floor before a decision may LINK/project.
        Subclasses/payloads override; default = decisions carry confidence
        and confidence > 0 is viable. Pure difference without viability
        collapses into dada noise."""
        conf = getattr(decision, "confidence", None)
        return True if conf is None else conf > 0.0
