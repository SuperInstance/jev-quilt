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


def _tombstone_leaf(key: str, answer: str) -> bytes:
    """A 32-byte content-addressed leaf for a forgotten (key, answer) pair.

    `__tomb__` is a namespace prefix no deposit leaf can ever produce (a
    deposit leaf's canonical string always starts with the deposit's own
    key), so a tombstone can never collide with, or be forged as, a live
    deposit leaf."""
    canon = f"__tomb__\x1f{key}\x1f{answer}"
    return hashlib.sha256(canon.encode("utf-8")).digest()


class Commons:
    """A shared, content-addressed, confluent store of proven (key → answer)
    routes with pooled evidence weights.

    G12 — provable forgetting: a person has a right to leave, and a fleet has
    a right to shed a route that encoded someone's private ground. But the
    commons is append-only and content-addressed on doctrine — the
    witness-referenced is never destroyed. The resolution is the same trick
    as everywhere else here: you do not *mutate the past out*, you *fold the
    erasure in*. `forget()` does not edit history invisibly; it books a
    tombstone leaf, a witnessed, content-addressed record that a pair was
    removed. `root()` folds tombstones in alongside deposits, so forgetting
    is itself a real, provable state change — a peer can replay the delta
    (surviving deposits + the new tombstone) and land on the same root. A
    commons that has never called `forget` roots byte-identically to the
    pre-G12 commons (empty tombstone set ⇒ unchanged behavior): forgetting
    is purely additive.

    STRETCH / honest limit: `merge()`'s tombstone rule is gossip-safe, not
    magically global. A tombstone suppresses a pair's weight on merge only
    where the tombstone itself has propagated — see `merge()`'s docstring.
    Nothing here can force every node to forget instantaneously without
    delivering the tombstone to it; that would require a surveillance
    archive of all copies, which is exactly what the right to leave is
    against.
    """

    ANON = "__anon__"   # source tag for deposits with no named provenance

    def __init__(self, quorum: int = DEFAULT_DIPLOMA):
        self.quorum = max(1, quorum)
        self._w: dict[tuple[str, str], int] = {}   # (key, answer) -> aggregate weight
        # provenance: (key, answer) -> {source -> weight}. Kept alongside _w so a
        # trust-free reading (recall/root) is unchanged, but a trust-weighted
        # gluing (G11) can down-weight a source the fleet has not earned to trust.
        self._prov: dict[tuple[str, str], dict[str, int]] = {}
        # G12: pairs whose forgetting has been booked locally. Sorted before
        # rooting (see root()) so tombstone order never affects the root.
        self._tombstones: set[tuple[str, str]] = set()

    # ── building ────────────────────────────────────────────────────
    def deposit(self, key: str, answer: str, weight: int = 1, source: str | None = None) -> None:
        if weight <= 0:
            return
        self._w[(key, answer)] = self._w.get((key, answer), 0) + weight
        src = source or self.ANON
        pm = self._prov.setdefault((key, answer), {})
        pm[src] = pm.get(src, 0) + weight

    def absorb_standing(self, standing: Standing, source: str | None = None) -> None:
        """Fold one cell's earned standing into the commons, tagged by source."""
        for key, answer, streak in standing.deposits():
            self.deposit(key, answer, streak, source=source)

    # ── forgetting (G12) ────────────────────────────────────────────
    def forget(self, key: str, answer: str | None = None) -> None:
        """Book the removal of a deposit — the right to leave, witnessed.

        Removes `(key, answer)` (or, if `answer` is None, every answer
        deposited under `key`) from `self._w` and `self._prov`, and adds
        each removed pair to `self._tombstones`. After this call
        `recall(key)` / `weight(key, ...)` read as if the pair had never
        been deposited (they read `self._w`, which this emptied) — but the
        forgetting itself is not silent: it is folded into `root()` as a
        tombstone leaf, so a peer can replay the erasure and land on the
        same root, and no one can quietly claim the pair was simply never
        there.

        Idempotent, and books the tombstone even when the pair was already
        absent — the *intent* to forget is itself witnessed, regardless of
        whether there was anything live to remove.

        No silent resurrection: because this deletes `self._w[(k, a)]`
        outright (not merely masks it), a later `deposit(key, answer, ...)`
        starts counting from 0. The tombstone stays folded into the root
        even after re-deposit — that is correct: the ledger then shows *it
        was forgotten, then re-learned*, not that it was never forgotten.
        """
        if answer is not None:
            pairs = [(key, answer)]
        else:
            pairs = [k for k in self._w if k[0] == key]
        for pair in pairs:
            self._w.pop(pair, None)
            self._prov.pop(pair, None)
            self._tombstones.add(pair)

    @classmethod
    def from_books(cls, books: dict, *, diploma: int = DEFAULT_DIPLOMA,
                   quorum: int = DEFAULT_DIPLOMA, **standing_kw) -> "Commons":
        """Build the commons by replaying every contributing cell's book. The
        book's name is its provenance — so trust can later be applied per source."""
        c = cls(quorum=quorum)
        for name, book in books.items():
            c.absorb_standing(Standing.from_book(book, diploma=diploma, **standing_kw), source=name)
        return c

    def merge(self, other: "Commons") -> "Commons":
        """Confluent union: weights add (and per-source provenance adds), so order
        and grouping never matter. Returns self for chaining.

        G12 merge rule for tombstones (the one real judgment call — see the
        class docstring's STRETCH note): `_tombstones` is unioned like
        `_prov`, and afterward every read path is purged of any pair in the
        unioned tombstone set — not just `_w`, but `_prov` too, so a
        forgotten pair cannot resurface through the provenance-keyed G11
        reads (`trust_weighted` / `provenance_merge` / `sources`), which
        index `_prov` directly and never consult `_w`. Without purging
        `_prov` as well, a stranger's un-forgotten copy of a pair could be
        merged in, re-populate `_prov`, and then a `trust_weighted` read of
        the *merged* commons would resurrect weight for a pair this node has
        explicitly forgotten — a real leak, since `forget()` already scrubs
        `_prov` locally but a merge was re-adding it from the other side.
        Now both `_w` and `_prov` are dropped for every tombstoned pair
        after each merge, so a forgotten pair is absent from every read
        path (`recall`, `weight`, `earned`, `sources`, `trust_weighted`,
        `provenance_merge`) the moment its tombstone is present, while the
        tombstone leaf itself still stays folded into `root()` — the
        erasure remains witnessed even though the pair reads as gone.

        This still means forgetting only suppresses a pair's weight in the
        merge result where the tombstone has actually propagated to it — a
        node that has not yet received a given tombstone will still
        contribute that pair's weight (and provenance) into the merge, and
        only stops once the tombstone itself is gossiped in. That is
        deliberately *not* instantaneous global erasure (that would require
        a surveillance archive tracking every copy); it is the honest,
        gossip-safe semantics: forgetting is local unless gossiped as its
        own tombstone. The rule stays confluent — union is commutative and
        associative for both `_prov` and `_tombstones`, and the drop step is
        a deterministic function of the unioned sets, so `A.merge(B)` and
        `B.merge(A)` still converge to the same root (and the same purged
        `_prov`).
        """
        for (key, answer), srcmap in other._prov.items():
            for src, w in srcmap.items():
                self.deposit(key, answer, w, source=(None if src == self.ANON else src))
        self._tombstones |= other._tombstones
        for pair in self._tombstones:
            self._w.pop(pair, None)
            self._prov.pop(pair, None)
        return self

    # ── trust-weighted gluing (G11) ──────────────────────────────────
    def sources(self) -> set:
        """Every named source that has deposited (excludes anonymous)."""
        return {s for pm in self._prov.values() for s in pm if s != self.ANON}

    def trust_weighted(self, trust: dict[str, int], default: int = 0) -> "Commons":
        """A new commons whose weights are re-scaled by each source's EARNED trust:
        effective(key,answer) = Σ_source trust.get(source, default) · raw_weight.

        This is the gluing a fleet can survive a stranger joining. Blind weight-sum
        (the base merge) is buyable — an adversary inflates a weight and steers the
        commons. Here an unseen source defaults to trust 0: it contributes nothing
        until the fleet has earned reason to trust it, so a lie deposited at weight
        1000 by a stranger is scaled to 0 and cannot outvote a small, trusted
        truth. Trust is the lever; weight alone is not. Confluent and
        content-addressed like any commons (it *is* one). Integer-exact — no float
        touches identity."""
        c = Commons(quorum=self.quorum)
        for (key, answer), srcmap in self._prov.items():
            eff = sum(trust.get(src, default) * w for src, w in srcmap.items())
            if eff > 0:
                # deposit the effective weight, preserving provenance for re-gluing
                for src, w in srcmap.items():
                    tw = trust.get(src, default) * w
                    if tw > 0:
                        c.deposit(key, answer, tw, source=(None if src == self.ANON else src))
        return c

    def provenance_merge(self, *others: "Commons", trust: dict[str, int], default: int = 0) -> "Commons":
        """Glue self with other fleets' commons, then read through trust. Order-free
        (confluent): the raw union commutes, and trust is applied deterministically
        after — so no arrival order lets a stranger win."""
        raw = Commons(quorum=self.quorum).merge(self)
        for o in others:
            raw.merge(o)
        return raw.trust_weighted(trust, default=default)

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
        """Content-addressed MMR root over the canonical deposit leaves,
        followed by the canonical tombstone leaves (G12). Two commons with
        the same deposits AND the same forgets return the same root,
        regardless of the order they were built, forgotten from, or merged
        in — both leaf groups are sorted before rooting.

        Backward-compat pin: an empty tombstone set (no `forget` ever
        called) makes this byte-identical to the pre-G12 root — tombstone
        leaves are strictly appended after all deposit leaves, so a commons
        that never forgets anything roots exactly as it did before G12.
        """
        leaves = [_leaf(d.key, d.answer, d.weight) for d in self.deposits()]
        leaves += [_tombstone_leaf(k, a) for (k, a) in sorted(self._tombstones)]
        return mmr_root(leaves)

    def agrees_with(self, other: "Commons") -> bool:
        """Do two nodes hold the same commons? One 32-byte comparison, not a
        table diff — the gluing check."""
        return self.root() == other.root()
