"""Pins for the first flywheel watch reading.

The honest negative must STAY honest: if a future edit to the flywheel
worlds makes a domain majority-alarmed, or breaks a receipt chain, these
tests fail — the watch reading has to be re-taken, not silently stale.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from examples.flywheel_watch import run_flywheel, DOMAINS
from jev_quilt.jepa_slot import scan


def test_flywheel_books_all_verify():
    books = run_flywheel(ticks=40)
    assert all(b.verify() for b in books.values())


def test_flywheel_watch_honest_negative():
    """No flywheel domain is majority-alarmed: the predictor class is
    not the binding constraint on these worlds. Pinned so the printed
    reading can never drift from the books."""
    books = run_flywheel(ticks=60)
    candidates, problems = scan(books, min_wakes=10)
    assert candidates == []
    assert problems == []


def test_step_change_is_transition_not_structure():
    """game.confidence alarms at the t=60 step (density well under the
    majority bar): a transition the mean absorbs is NOT a JEPA slot.
    This is the discipline that keeps tuning-scale surprise from being
    mistaken for a predictor-class failure."""
    books = run_flywheel(ticks=120)
    bk = books["sense.game.confidence"]
    alarms = sum(1 for e in bk.entries if '"alarmed": "true"' in e.payload)
    assert 0 < alarms < len(bk.entries) / 2  # real, but far from majority
    # and post-step wakes converge again — the mean re-represents the world
    last_alarm_idx = max(
        i for i, e in enumerate(bk.entries) if '"alarmed": "true"' in e.payload)
    assert last_alarm_idx < len(bk.entries) - 10  # quiet tail = absorbed


def test_quiet_domains_stay_quiet():
    books = run_flywheel(ticks=120)
    for d in ("sense.dialogue.trust", "sense.robotics.battery"):
        bk = books[d]
        alarms = sum(1 for e in bk.entries if '"alarmed": "true"' in e.payload)
        assert alarms == 0, f"{d} drifted from its pinned reading"
