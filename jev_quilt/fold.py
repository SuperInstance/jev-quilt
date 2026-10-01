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


def _push(stack: list, i: int, leaf: bytes) -> None:
    """MMR insert of leaf at 0-based position i (binary-counter rule).

    merges = popcount(i) - popcount(i + 1) + 1, i.e. merge while bit h
    of i is set, carrying left-to-right. The stack is the ordered peak
    list; peaks(A ++ B) is reproducible by resuming the counter at
    |A| — that boundary stability is what makes a seeded sliver
    replay expressible at all.
    """
    h = 0
    node = leaf
    while i & (1 << h):
        node = _h(stack.pop() + node)
        h += 1
    stack.append(node)


def _peaks(leaves: list[bytes]) -> list[bytes]:
    """Ordered peak list for a from-genesis insert of every leaf."""
    stack: list[bytes] = []
    for i, leaf in enumerate(leaves):
        _push(stack, i, leaf)
    return stack


def _bag(peaks: list[bytes], count: int) -> bytes:
    return _h(b"".join(peaks) + str(count).encode())


def mmr_root(leaves: list[bytes]) -> bytes:
    """Bagged-peaks MMR root over sha256 leaves (append-order matters).

    Peaks are the binary-counter subtree decomposition (one subtree per
    set bit of the leaf count, left to right); the bagged root is
    sha256(concat(peaks) || count). Not a security MMR — same doctrine
    as the fleet's rate limiter: integrity, not adversaries.

    v2 note (verify_tail proposal): the peak-merging rule changed from
    "greedy full subtrees + unmerged stragglers" to the binary-counter
    rule so that peaks are boundary-stable: a sliver seeded onto a
    checkpoint's peaks reproduces the from-genesis root. Behavioral
    invariants (determinism, order-sensitivity, empty constant) are
    unchanged; absolute root values change, which is the point — a
    checkpoint must commit to a structure continuations can extend.
    """
    if not leaves:
        return _h(b"mmr:empty")
    return _bag(_peaks(leaves), len(leaves))


@dataclass
class Checkpoint:
    upto_tick: int            # prefix [1..upto] is folded away
    root: bytes               # MMR root over the prefix's delta hashes
    state: dict               # minimal sufficient state vector (counts, last hash)
    leaf_count: int
    peaks: list = field(default_factory=list)  # ordered prefix peaks (binary-
                              # counter decomposition) — sufficient to seed a
                              # sliver replay and prove the sliver continues
                              # the chain (verify_tail)


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
            peaks=_peaks([self.leaf(e) for e in prefix]),
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

    def verify_tail(self, book, expected: "bytes | None" = None) -> bool:
        """The sliver after the fold must continue the chain honestly.

        V1 fix (proposal; found by hard/r2 properties, PR #26): the
        previous check compared a recomputed bag against b"" — a sha256
        digest is never empty, so any non-empty sliver passed, tampered
        or not. The docstring's law is now implemented literally:
        replay the sliver seeded from the checkpoint's peaks (binary-
        counter carries resume at leaf_count) and require the result to
        equal the root over the full chain. This catches:

          * a checkpoint spliced from a different chain (peaks disagree
            with the retained chain's genesis-to-now recomputation);
          * structural sliver edits — non-contiguous ticks after
            upto_tick (inserted/duplicated/dropped receipts).

        Honest boundary, same class as verify()'s "delta hashes, not
        annotations": with a single fold and no external head-root
        anchor, post-hoc CONTENT edits inside an otherwise consistent
            (checkpoint, sliver) pair recompute consistently on both
            sides — no commitment to the sliver existed at fold time,
            so content honesty is unprovable until a later fold (or an
            externally carried head root) anchors it. The anchor hook
            is `expected` below; fleet wiring of a stamped head root is
            deliberately out of scope for this proposal.
        """
        if not self.folds:
            # Nothing folded: no checkpoint to continue. The only honest
            # claim available is that the book carries any commitment.
            return bool(book.entries)
        cp = self.folds[-1]
        if len(book.entries) < cp.leaf_count:
            return False              # checkpoint claims more than the book holds
        sliver = book.entries[cp.leaf_count:]
        # structural gate: the sliver's ticks must continue the folded
        # prefix exactly (no inserted / dropped / duplicated receipts)
        if any(e.tick != cp.upto_tick + 1 + j for j, e in enumerate(sliver)):
            return False
        # Replay ≡ Live for the join: seeded sliver replay must equal
        # the from-genesis root over the full chain.
        stack = list(cp.peaks)
        for j, e in enumerate(sliver):
            _push(stack, cp.leaf_count + j, self.leaf(e))
        seeded = _bag(stack, len(book.entries))
        if expected is not None:
            # externally anchored mode (prefix deleted, head root carried
            # out-of-band): the seeded replay must reproduce the anchor.
            return seeded == expected
        return seeded == mmr_root([self.leaf(e) for e in book.entries])
