"""Earned standing (FRONTIER R2): the fourth verdict, derived from the book.

Standing is conferred by a run of booked-correct receipts and revoked by a single
booked-wrong one. It is a pure function of the Bookkeeper (law 4: replay ≡ live),
never self-granted, and ANSWER never names an answer the book didn't prove.
"""
from jev_quilt.bookkeeper import Bookkeeper
from jev_quilt.standing import Standing, verdict, DEFAULT_DIPLOMA


def _book(rows):
    """Book a sequence of (key, correct, answer) residues into a fresh WAL."""
    bk = Bookkeeper("cell.test")
    for key, correct, answer in rows:
        bk.book({}, {}, answer, {"key": key, "correct": correct, "answer": answer})
    return bk


def test_standing_is_earned_after_N_correct_not_before():
    bk = _book([("open", True, "warm")] * (DEFAULT_DIPLOMA - 1))
    s = Standing.from_book(bk)
    assert not s.earned("open")                 # N-1 correct: not yet
    assert s.recall("open") is None             # so no answer to recall
    bk.book({}, {}, "warm", {"key": "open", "correct": True, "answer": "warm"})
    s = Standing.from_book(bk)
    assert s.earned("open")                     # the Nth correct confers standing
    assert s.recall("open") == "warm"


def test_standing_is_revocable_one_miss_tears_it_up():
    bk = _book([("ping", True, "pong")] * 4)
    assert Standing.from_book(bk).earned("ping")
    bk.book({}, {}, "pong", {"key": "ping", "correct": False, "answer": "pong"})  # the world drifted
    s = Standing.from_book(bk)
    assert not s.earned("ping")
    assert s.recall("ping") is None             # must be re-earned


def test_never_self_granted_no_correct_run_no_standing():
    bk = _book([("q", False, "a"), ("q", True, "a"), ("q", False, "a"), ("q", True, "a")])
    s = Standing.from_book(bk)                   # never 3 in a row
    assert not s.earned("q")


def test_recall_only_names_a_proven_answer():
    bk = _book([("route", True, "left"), ("route", True, "left"), ("route", True, "left")])
    s = Standing.from_book(bk)
    assert s.recall("route") == "left"          # exactly what the book proved
    assert s.recall("never-seen") is None


def test_verdict_is_the_fourth_only_when_earned():
    bk = _book([("x", True, "go")] * DEFAULT_DIPLOMA)
    s = Standing.from_book(bk)
    assert verdict(s, "x", "ACT") == ("ANSWER", "go")        # earned → the fourth verdict
    assert verdict(s, "y", "ESCALATE") == ("ESCALATE", None)  # unseen → route ignorance


def test_derived_from_book_replay_equals_live():
    rows = [("k", True, "v"), ("k", True, "v"), ("k", True, "v")]
    a = Standing.from_book(_book(rows))
    b = Standing.from_book(_book(rows))
    assert a.earned("k") == b.earned("k")
    assert a.recall("k") == b.recall("k")
    assert a.count == b.count == 1
