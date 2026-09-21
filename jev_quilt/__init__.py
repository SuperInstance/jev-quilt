"""jev-quilt reference kernel v0.

Cells, hooks, bookkeeper, backends. Exact-first doctrine:
q16 deterministic rules resolve before any model backend.
"""

from .cell import Cell, Hook, Projection, DEADBAND
from .bookkeeper import Bookkeeper, Receipt
from .backends import resolve_backend, Q16Backend, BackendDecision

__all__ = [
    "Cell", "Hook", "Projection", "DEADBAND",
    "Bookkeeper", "Receipt",
    "resolve_backend", "Q16Backend", "BackendDecision",
]

__version__ = "0.0.1"
