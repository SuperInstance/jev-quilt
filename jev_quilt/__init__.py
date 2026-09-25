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
                       TendencyReading, ReadingEnsemble)
from .imagine import WorldModel, imagine_choice, imagine_score
from .witness_rng import WitnessRng, seed_from_state, seed_from_book
from .opposites import opposite, is_canonical, TABLE as OPPOSITES
from .engine import Engine, WakeResult
from .tap import TapGate, ProposalGate, kl_divergence
from .fold import FoldedLedger, Checkpoint, mmr_root
from . import blake3, ed25519, signed_receipts

__all__ = [
    "Cell", "Hook", "Projection", "DEADBAND",
    "Bookkeeper", "Receipt",
    "resolve_backend", "Q16Backend", "BackendDecision",
    "Q16", "MeanPredictor", "surprise", "alarm",
    "ConstReading", "NgramReading", "DriftReading", "TendencyReading",
    "ReadingEnsemble",
    "WorldModel", "imagine_choice", "imagine_score",
    "WitnessRng", "seed_from_state", "seed_from_book",
    "opposite", "is_canonical", "OPPOSITES",
    "Engine", "WakeResult",
    "TapGate", "ProposalGate", "kl_divergence",
    "FoldedLedger", "Checkpoint", "mmr_root",
    "blake3", "ed25519", "signed_receipts",
]

__version__ = "0.1.0"
