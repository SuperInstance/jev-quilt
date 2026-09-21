"""jev-quilt reference kernel v0.

Cells, hooks, bookkeeper, backends, delta engine, predictors, readings,
imagination. Exact-first doctrine: q16 deterministic rules resolve before
any model backend.
"""

from .cell import Cell, Hook, Projection, DEADBAND
from .bookkeeper import Bookkeeper, Receipt
from .backends import resolve_backend, Q16Backend, BackendDecision
from .q16 import Q16
from .predictor import MeanPredictor, surprise, alarm
from .readings import (ConstReading, NgramReading, DriftReading,
                       ReadingEnsemble)
from .imagine import WorldModel, imagine_choice, imagine_score
from .engine import Engine, WakeResult

__all__ = [
    "Cell", "Hook", "Projection", "DEADBAND",
    "Bookkeeper", "Receipt",
    "resolve_backend", "Q16Backend", "BackendDecision",
    "Q16", "MeanPredictor", "surprise", "alarm",
    "ConstReading", "NgramReading", "DriftReading", "ReadingEnsemble",
    "WorldModel", "imagine_choice", "imagine_score",
    "Engine", "WakeResult",
]

__version__ = "0.0.4"
