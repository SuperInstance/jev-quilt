"""The deposit commons: many cells' earned standing, glued into one verifiable
shared memory (FRONTIER R2, the other half).

`standing.py` lets a cell earn the right to stop asking *from its own book*.
The commons is how a **fresh** cell inherits what the fleet already proved: read
the commons, answer from it, skip the re-deriving. It is the radio channel
un-jammed — nobody re-asks what is already aboard.

Built on `fold.mmr_root`, deliberately. The same content-addressed root that
proves *replay ≡ live* for one cell's WAL here proves that two nodes' copies of
the commons **agree** — the sheaf gluing condition PRODUCTS.md filed for
`sheaf-gossip`. Two properties make that real:

  • **Content-addressed.** `Commons.root()` is an MMR root over the canonical,
    sorted deposit leaves. Same deposits ⇒ same root, on any node. A peer can
    prove agreement by comparing one 32-byte root, not the whole table.
  • **Confluent (order-free).** Deposits are sorted before rooting and merges add
    weights commutatively, so `A.merge(B)` and `B.merge(A)` yield the *same* root.
    Federation can gossip in any order and still converge — glue, don't fight.

Pooled evidence is the commons superpower: ten cells each with a streak of 1 on
the same (key→answer) sum to a fleet weight of 10, so a route no single cell had
yet *earned* can still be fleet-earned. Exact and deterministic throughout — no
float touches identity.
"""

from __future__ import annotations
import hashlib
from dataclasses import dataclass

from .fold import mmr_root
from .standing import Standing, DEFAULT_DIPLOMA


@dataclass(frozen=True)
class Deposit:
    key: str
    answer: str
    weight: int   # aggregate booked-correct evidence backing this (key → answer)


def _leaf(key: str, answer: str, weight: int) -> bytes:
    """A 32-byte content-addressed leaf for one deposit (\\x1f-delimited, so no
    key/answer collision can forge another's leaf)."""
    canon = f"{key}\x1f{answer}\x1f{weight}"
    return hashlib.sha256(canon.encode("utf-8")).digest()


class Commons:
    """A shared, content-addressed, confluent store of proven (key → answer)
    routes with pooled evidence weights."""

    def __init__(self, quorum: int = DEFAULT_DIPLOMA):
        self.quorum = max(1, quorum)
        self._w: dict[tuple[str, str], int] = {}   # (key, answer) -> aggregate weight

    # ── building ────────────────────────────────────────────────────
    def deposit(self, key: str, answer: str, weight: int = 1) -> None:
        if weight <= 0:
            return
        self._w[(key, answer)] = self._w.get((key, answer), 0) + weight

    def absorb_standing(self, standing: Standing) -> None:
        """Fold one cell's earned standing into the commons."""
        for key, answer, streak in standing.deposits():
            self.deposit(key, answer, streak)

    @classmethod
    def from_books(cls, books: dict, *, diploma: int = DEFAULT_DIPLOMA,
                   quorum: int = DEFAULT_DIPLOMA, **standing_kw) -> "Commons":
        """Build the commons by replaying every contributing cell's book."""
        c = cls(quorum=quorum)
        for _name, book in books.items():
            c.absorb_standing(Standing.from_book(book, diploma=diploma, **standing_kw))
        return c

    def merge(self, other: "Commons") -> "Commons":
        """Confluent union: weights add, so order and grouping never matter.
        Returns self for chaining."""
        for (key, answer), w in other._w.items():
            self.deposit(key, answer, w)
        return self

    # ── reading ─────────────────────────────────────────────────────
    def recall(self, key: str) -> str | None:
        """The fleet's best proven answer for a key, or None. Best = highest
        pooled weight; ties broken by answer (deterministic). Absence is honest —
        the commons never fabricates a route it has no evidence for."""
        best, best_w = None, 0
        for (k, answer), w in self._w.items():
            if k != key:
                continue
            if w > best_w or (w == best_w and best is not None and answer < best):
                best, best_w = answer, w
        return best

    def weight(self, key: str, answer: str | None = None) -> int:
        """Pooled evidence for a (key, answer), or the max over answers for a key."""
        if answer is not None:
            return self._w.get((key, answer), 0)
        return max((w for (k, _a), w in self._w.items() if k == key), default=0)

    def earned(self, key: str) -> bool:
        """Fleet-earned: the best answer for this key clears the quorum of pooled
        evidence — a route the whole fleet stands behind, even if no single cell
        had earned it alone."""
        return self.weight(key) >= self.quorum

    def deposits(self) -> list[Deposit]:
        """All deposits, in canonical (key, answer) order."""
        return [Deposit(k, a, w) for (k, a), w in sorted(self._w.items())]

    # ── proving agreement ───────────────────────────────────────────
    def root(self) -> bytes:
        """Content-addressed MMR root over the canonical deposit leaves. Two
        commons with the same deposits return the same root, regardless of the
        order they were built or merged in."""
        return mmr_root([_leaf(d.key, d.answer, d.weight) for d in self.deposits()])

    def agrees_with(self, other: "Commons") -> bool:
        """Do two nodes hold the same commons? One 32-byte comparison, not a
        table diff — the gluing check."""
        return self.root() == other.root()
