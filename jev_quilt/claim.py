"""Reproducibility as `mmr_root`: federated discovery from strangers (G16).

`commons.py` proves two nodes' *proven routes* agree. It does not gate a
**scientific claim** on the agreement of the underlying raw books. This module
does: a claim earns standing iff N independent witnesses **reproduce** it —
their books fold to a single agreed root, confluent across gossip order, and
a drifting instrument is excluded rather than silently averaged in.
Reproducibility becomes a 32-byte comparison.

The one real design question, resolved at dispatch altitude, is the tension
between two predicate clauses that look contradictory:

  * one float's book diverges by a single delta → NOT `earns_standing`
    (`agrees_with` False) — an honest disagreement must halt, not be waved
    away because it is inconvenient;
  * a drifting float flagged by the calibrated floor is down-weighted, not
    silently averaged in — a known-bad instrument, once flagged by a
    pre-registered rule, is excluded before consensus, not blended into it.

The discriminator between the two is the `CalibratedFloor` (see
`calibrate.py`): a witness that disagrees but stays WITHIN the floor is a
real, unresolved disagreement (the claim is genuinely not reproducible, so it
must halt); a witness whose surprise CLEARS the floor is a flagged
instrument drift (a known-bad sensor, excluded from the trusted set before
consensus is taken). You may not discard an outlier because you dislike it;
you may discard it only when an independent, pre-registered drift criterion
flags it. That is the correct scientific stance, and it is exactly the line
the floor draws.

`earns_standing` is defined as: the *non-drifting* witnesses are UNANIMOUS on
one value, and there are at least `quorum` of them. Reproducibility means
everyone trusted got the same answer — not a majority vote; a majority with
a live dissenter is not reproducible.

Two properties carried over from `commons.py`/`fold.py`, deliberately:

  * **Content-addressed.** `Claim.root()` is an MMR root over canonical,
    sorted witness leaves (drifters included — the root is the full content
    address of what the swarm actually reported, so a single-delta
    divergence still shows up as a different root even when that witness is
    later excluded from consensus).
  * **Confluent (order-free).** Leaves are sorted before rooting, so gossip
    can arrive in any order and two nodes that saw the same witnesses still
    converge on the same root.

Exact and deterministic throughout: `reading_fn` yields a `Q16` magnitude,
`predictor.surprise` grades the miss against the swarm consensus magnitude,
and `CalibratedFloor` judges it — no float touches identity anywhere in this
module.

STRETCH / honest limits:

  * Cross-*language* reproducibility is asserted via the byte-canonical
    `_leaf` plus sorted `mmr_root` (the family's existing contract) and
    pinned by a hard-coded expected-root vector; both "nodes" exercised in
    this module's tests are the same Python implementation
    (cross-*instance*), same STRETCH carried by earlier rungs.
  * The drift criterion runs one `CalibratedFloor` over the swarm's surprise
    distribution rather than a temporal window, because a swarm here is a
    *set* of witnesses, not a time series: every witness's surprise is fed
    into the floor (sorted by witness id, for determinism) before any
    witness is judged against it, so the floor reflects the whole set's
    dispersion, not an arrival order. A maintainer who prefers a
    temporal/streaming swarm can apply the same floor per-tick instead —
    noted, not blocked on.
  * **Least-certain claim:** that unanimity-among-non-drifters (not a
    majority) is the right bar for `earns_standing`. It is the strict
    reading of reproducibility and it satisfies the predicate; a future rung
    could add a graded "N-of-M reproduced" standing if the fleet wants
    quorum-consensus rather than unanimity.
"""

from __future__ import annotations
import hashlib
from dataclasses import dataclass
from typing import Callable, Optional

from .q16 import Q16
from .predictor import surprise
from .calibrate import CalibratedFloor
from .fold import mmr_root


@dataclass(frozen=True)
class Reading:
    witness: str      # source id (a float / node)
    value: str        # the canonical reading, e.g. "north_shallow=42"
    drifting: bool    # flagged by the calibrated floor


def _leaf(witness: str, value: str) -> bytes:
    """A 32-byte content-addressed leaf for one witness's reading (\\x1f-delimited,
    same shape as commons._leaf, so no witness/value collision can forge another's
    leaf)."""
    canon = f"{witness}\x1f{value}"
    return hashlib.sha256(canon.encode("utf-8")).digest()


class Claim:
    """A scientific claim, backed by N independent witnesses' books.

    Built once via `from_books`; read through `readings`/`root`/`consensus`/
    `earns_standing`/`drifters`. Two `Claim`s built from the same witnesses'
    books — regardless of gossip order — agree bit-for-bit on `root()`."""

    def __init__(self, readings: list, *, quorum: int):
        self.quorum = max(1, quorum)
        self._readings = list(readings)

    # ── building ────────────────────────────────────────────────────
    @classmethod
    def from_books(cls, books: dict, *, reading_fn: Callable, quorum: int,
                    floor: Optional[CalibratedFloor] = None) -> "Claim":
        """Replay every witness's book through `reading_fn` (book -> (value,
        magnitude)), find the swarm's consensus magnitude (the mean magnitude
        of the witnesses agreeing on the modal value), grade every witness's
        surprise against it, and flag `drifting=True` for any witness whose
        surprise clears the `CalibratedFloor` (the `floor` arg, or a fresh
        default). Witnesses are processed in sorted order throughout so the
        result — drift flags included — never depends on `books`' iteration
        order (gossip order), only on its content."""
        cal = floor if floor is not None else CalibratedFloor()

        raw: dict = {}
        for name, book in books.items():
            value, magnitude = reading_fn(book)
            if not isinstance(magnitude, Q16):
                raise TypeError("claim.from_books: reading_fn must return a Q16 magnitude")
            raw[name] = (value, magnitude)

        names = sorted(raw.keys())

        # modal value: the most-reported value, ties broken lexicographically
        # (deterministic, same discipline as commons.recall's tie-break)
        counts: dict = {}
        for value, _mag in raw.values():
            counts[value] = counts.get(value, 0) + 1
        top = max(counts.values())
        modal_value = min(v for v, c in counts.items() if c == top)

        agreeing_mags = [mag for value, mag in raw.values() if value == modal_value]
        consensus_mag = sum(agreeing_mags, Q16(0)) * Q16(1, len(agreeing_mags))

        # every witness's surprise vs the swarm consensus magnitude, exact-ℚ
        surprises = {name: surprise(raw[name][1], consensus_mag) for name in names}

        # feed the WHOLE set's surprise distribution into the floor before
        # judging anyone against it (a swarm is a set, not a time series)
        for name in names:
            cal.update(surprises[name])
        f = cal.floor()

        readings = [
            Reading(witness=name, value=raw[name][0],
                    drifting=(f is not None and surprises[name] > f))
            for name in names
        ]
        return cls(readings, quorum=quorum)

    # ── reading ─────────────────────────────────────────────────────
    def readings(self, *, include_drifting: bool = False) -> list:
        """All readings, sorted by witness for determinism. Excludes drifters
        unless `include_drifting` is set."""
        rs = sorted(self._readings, key=lambda r: r.witness)
        if include_drifting:
            return rs
        return [r for r in rs if not r.drifting]

    def drifters(self) -> set:
        """Witness ids excluded by the calibrated floor (the audit trail)."""
        return {r.witness for r in self._readings if r.drifting}

    def consensus(self) -> Optional[str]:
        """The value all non-drifting witnesses agree on, if they are
        unanimous and number at least `quorum`; else None (honest absence —
        a majority with a live dissenter is not reproducible)."""
        trusted = self.readings(include_drifting=False)
        if len(trusted) < self.quorum:
            return None
        values = {r.value for r in trusted}
        if len(values) == 1:
            return next(iter(values))
        return None

    def earns_standing(self) -> bool:
        return self.consensus() is not None

    # ── proving agreement ───────────────────────────────────────────
    def root(self) -> bytes:
        """Content-addressed MMR root over EVERY witness's actual reading
        (drifters included — the root is the full content address of what
        the swarm reported). Leaves sorted by witness before rooting, so the
        root is confluent across gossip order and a single-delta divergence
        still changes it."""
        leaves = [_leaf(r.witness, r.value) for r in sorted(self._readings, key=lambda r: r.witness)]
        return mmr_root(leaves)

    def agrees_with(self, other: "Claim") -> bool:
        """Do two nodes hold the same claim? One 32-byte comparison."""
        return self.root() == other.root()


def claim_standing(claim: Claim, key: str, base_verdict: str) -> tuple:
    """The fourth verdict, conferred by a swarm rather than one cell's book.

    Thin bridge mirroring `standing.verdict`: `('ANSWER', claim.consensus())`
    when the claim `earns_standing()`, else `(base_verdict, None)` — the
    verdict the caller would otherwise take. `key` is accepted only for call-
    shape parity with `standing.verdict(standing, key, base_verdict)` (a
    `Claim` is already scoped to one question, so it plays no role in the
    formula) — one law, whether the evidence is one cell's book or a
    swarm's."""
    if claim.earns_standing():
        return ("ANSWER", claim.consensus())
    return (base_verdict, None)
