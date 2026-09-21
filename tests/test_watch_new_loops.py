"""Pin the watch reading on jeviter + deck_sim (examples/watch_new_loops.py)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from examples.watch_new_loops import run_watch
from jev_quilt.jepa_slot import scan


def test_all_books_verify():
    books = run_watch()
    assert set(books) == {"world", "jeviter.static", "jeviter.periodic",
                          "deck.vision", "deck.scale"}
    assert all(b.verify() for b in books.values())


def test_periodic_world_names_candidate():
    books = run_watch()
    candidates, problems = scan(books, min_wakes=10)
    assert problems == []
    named = [c.cell for c in candidates]
    # the period-8 world is the one structure a running mean cannot
    # represent at ANY K — the watch must name it and ONLY it
    assert "jeviter.periodic" in named
    assert len(named) == 1


def test_majority_alarm_share_is_exact():
    books = run_watch()
    candidates, _ = scan(books, min_wakes=10)
    c = next(c for c in candidates if c.cell == "jeviter.periodic")
    assert 2 * c.alarms >= c.wakes


def test_honest_domains_stay_quiet():
    books = run_watch()
    for name in ("jeviter.static", "deck.vision", "deck.scale"):
        bk = books[name]
        alarms = sum(1 for e in bk.entries if '"alarmed": "true"' in e.payload)
        # transitions and warm-up transients exist but are far under
        # the majority bar — a bad week is not a slot
        assert 2 * alarms < len(bk.entries)
