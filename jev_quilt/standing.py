"""Earned standing: the fourth verdict, learned from the book (FRONTIER R2).

`ACT / CONFIRM / ESCALATE` route a cell's ignorance — they are what it does when
it is not sure. They give a cell no way to say the most human thing: *I have done
this, correctly, so many times that I have earned the right to stop asking.* So a
fleet of cells re-asks the commons what it already knows cold — a radio channel
jammed with questions whose answers are aboard.

Standing is the move that ends that: after a cell has booked `diploma` correct
decisions in a row on the same residue-key, it may **ANSWER** — recall the proven
decision from its own book instead of re-deciding. Two properties keep it honest,
both the fleet's oldest instincts:

  • **Conferred, never self-granted.** Standing is *derived by replaying the
    Bookkeeper* (law 4: replay ≡ live). A cell cannot vote itself standing; only
    a run of booked-correct receipts confers it. The book is the training corpus
    (PRODUCTS.md self-training) — the learner is just this replay.
  • **Revocable.** One booked-wrong outcome for a key resets its streak and drops
    the recalled answer. A reflex whose world has drifted loses the fast path the
    instant it is wrong, and must re-earn it. No permanent, stale confidence — the
    calibration lesson (R1) carried into memory.

Exact and deterministic: standing is a pure function of the book, so two identical
books yield identical standing, on deck or in a datacenter.
"""

from __future__ import annotations
import json
from typing import Callable, Optional

from .bookkeeper import Bookkeeper

DEFAULT_DIPLOMA = 3


def _residue(entry) -> dict:
    """The booked residue as a dict (same read inquire.next_questions uses)."""
    try:
        r = json.loads(entry.payload)
        return r if isinstance(r, dict) else {}
    except Exception:
        return {}


def _default_key(res: dict) -> Optional[str]:
    """Which situation this receipt is about — the neighborhood standing is per."""
    for f in ("key", "trigger", "intent", "residue"):
        if res.get(f) is not None:
            return str(res[f])
    return None


def _default_correct(res: dict) -> bool:
    """Was the booked decision confirmed correct? (truthy 'correct' field)."""
    c = res.get("correct")
    return c is True or c == "true" or c == 1


class Standing:
    """Standing over a set of residue-keys, derived by replaying a book.

    A key holds standing once its consecutive booked-correct streak reaches
    `diploma`. Any booked-wrong outcome revokes it. `recall(key)` returns the
    proven decision to reuse — only while standing is held (a fabricated answer
    is never returned)."""

    def __init__(self, diploma: int = DEFAULT_DIPLOMA):
        self.diploma = max(1, diploma)
        self._streak: dict[str, int] = {}
        self._answer: dict[str, str] = {}

    @classmethod
    def from_book(cls, book: Bookkeeper, *, diploma: int = DEFAULT_DIPLOMA,
                  key_fn: Callable[[dict], Optional[str]] = _default_key,
                  correct_fn: Callable[[dict], bool] = _default_correct) -> "Standing":
        s = cls(diploma)
        for e in book.entries:
            res = _residue(e)
            k = key_fn(res)
            if k is None:
                continue
            answer = res.get("answer") if res.get("answer") is not None else e.decision_kind
            s.observe(k, correct_fn(res), str(answer))
        return s

    def observe(self, key: str, correct: bool, answer: str) -> None:
        """Fold one booked outcome into standing. A miss tears standing up."""
        if correct:
            self._streak[key] = self._streak.get(key, 0) + 1
            self._answer[key] = answer
        else:
            self._streak[key] = 0
            self._answer.pop(key, None)

    def streak(self, key: str) -> int:
        return self._streak.get(key, 0)

    def earned(self, key: str) -> bool:
        return self._streak.get(key, 0) >= self.diploma

    def recall(self, key: str) -> Optional[str]:
        """The proven decision to reuse — only while standing is held, else None."""
        return self._answer.get(key) if self.earned(key) else None

    @property
    def count(self) -> int:
        return sum(1 for k, v in self._streak.items() if v >= self.diploma)


def verdict(standing: Standing, key: str, base_verdict: str) -> tuple[str, Optional[str]]:
    """The fourth verdict. Returns ('ANSWER', proven_answer) when standing is held
    for `key`, else (base_verdict, None) — the ACT/CONFIRM/ESCALATE the cell would
    otherwise take. Legal by construction: ANSWER appears only when earned, and
    only ever names an answer the book already proved correct."""
    if standing.earned(key):
        return ("ANSWER", standing.recall(key))
    return (base_verdict, None)
