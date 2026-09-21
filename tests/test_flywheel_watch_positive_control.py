"""Pins for the positive control: the watch must FIRE on this harness
when a mean-unrepresentable world is present, and must keep its honest
negative on the real domains at the same time."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from examples.flywheel_watch_positive_control import (
    run_with_synthetic, SYNTH, SYNTH_TICKS,
)
from examples.flywheel_watch import run_flywheel
from jev_quilt.jepa_slot import scan


def test_grafted_periodic_cell_is_named():
    books = run_with_synthetic(SYNTH_TICKS)
    candidates, problems = scan(books, min_wakes=10)
    assert problems == []
    assert [c.cell for c in candidates] == [SYNTH]
    c = candidates[0]
    assert 2 * c.alarms >= c.wakes  # majority bar, exact integer compare
    assert books[SYNTH].verify()


def test_real_domains_stay_negative_alongside():
    """The graft must not launder the real reading: with the synthetic
    cell removed from the result set, no production domain may be a
    candidate — positive control and honest negative hold together."""
    books = run_with_synthetic(SYNTH_TICKS)
    real = {k: v for k, v in books.items() if k != SYNTH}
    candidates, problems = scan(real, min_wakes=10)
    assert candidates == []
    assert problems == []


def test_control_is_tied_to_production_reading():
    """The grafted harness must agree with the plain production run on
    the four real domains, entry for entry — if run_flywheel's wiring
    drifts, the control is no longer controlling the production loop."""
    plain = run_flywheel(ticks=SYNTH_TICKS)
    grafted = run_with_synthetic(SYNTH_TICKS)
    for name, bk in plain.items():
        assert name in grafted
        assert [e.payload for e in grafted[name].entries] == \
               [e.payload for e in bk.entries], f"{name} drifted"
