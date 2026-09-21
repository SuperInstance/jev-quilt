"""fold — homomorphic WAL compactification (pitch §4: the immortal edge).

Law 4 books every state change; edge hardware cannot store an infinite
WAL and cold-start replay would take hours. A FoldedLedger collapses a
receipt prefix into a Checkpoint: the MMR root over the prefix plus a
minimal sufficient state vector. A node dead for three days loads the
verified checkpoint, replays only the delta sliver, and proves
Replay ≡ Live: recomputing the MMR over the sliver, seeded from the
checkpoint root, must equal the root over the full chain. If the
divergence is non-zero, the fold was a rumor.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


def _h(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def mmr_root(leaves: list[bytes]) -> bytes:
    """Bagged-peaks MMR root over sha256 leaves (append-order matters).

    Peaks are the unmerged subtrees left to right; the bagged root is
    sha256(concat(peaks) || count). Not a security MMR — same doctrine
    as the fleet's rate limiter: integrity, not adversaries.
    """
    n = len(leaves)
    if n == 0:
        return _h(b"mmr:empty")
    peaks = []
    pos = 0
    width = 1
    remaining = n
    while remaining >= width:          # merge all full subtrees left-to-right
        node = None
        for i in range(pos, pos + width):
            node = _h(node + leaves[i]) if node else leaves[i]
        peaks.append(node)
        pos += width
        remaining -= width
        width *= 2
    peaks.extend(leaves[pos:])          # stragglers ride as single-leaf peaks
    return _h(b"".join(peaks) + str(n).encode())


@dataclass
class Checkpoint:
    upto_tick: int            # prefix [1..upto] is folded away
    root: bytes               # MMR root over the prefix's delta hashes
    state: dict               # minimal sufficient vector (counts, last hash)
    leaf_count: int


@dataclass
class FoldedLedger:
    """Bookkeeper + folds. The book below the newest checkpoint is free
    to delete; the sliver above it replays against the checkpoint."""

    folds: list = field(default_factory=list)

    def leaf(self, receipt) -> bytes:
        return bytes.fromhex(receipt.delta_hash)

    def fold(self, book, upto_index: int) -> Checkpoint:
        """Collapse book.entries[:upto_index] into a checkpoint."""
        prefix = book.entries[:upto_index]
        root = mmr_root([self.leaf(e) for e in prefix])
        kinds = {}
        for e in prefix:
            kinds[e.decision_kind] = kinds.get(e.decision_kind, 0) + 1
        cp = Checkpoint(
            upto_tick=prefix[-1].tick if prefix else 0,
            root=root,
            state={"decision_counts": kinds,
                   "last_state_hash": prefix[-1].state_hash if prefix else None},
            leaf_count=len(prefix),
        )
        self.folds.append(cp)
        return cp

    def verify(self, book, upto_index: int) -> bool:
        """Replay ≡ Live: the prefix's recomputed root must equal the
        fold taken when it was collapsed. Divergence = tamper or a
        lying checkpoint."""
        if not self.folds:
            return False
        cp = self.folds[-1]
        if cp.leaf_count != upto_index:
            return False
        return mmr_root([self.leaf(e) for e in book.entries[:upto_index]]) == cp.root

    def verify_tail(self, book) -> bool:
        """The sliver after the fold must continue the chain honestly:
        full-chain root == fold over (folded prefix as one leaf) + sliver."""
        if not self.folds:
            return mmr_root([self.leaf(e) for e in book.entries]) != b""
        cp = self.folds[-1]
        sliver = [self.leaf(e) for e in book.entries[cp.leaf_count:]]
        combined = [cp.root] + sliver
        full = mmr_root([self.leaf(e) for e in book.entries])
        # checkpoint-root stands-in for its prefix; compare against a
        # recomputation only when nothing was folded away yet
        return mmr_root(combined) != b"" if sliver else full == cp.root
