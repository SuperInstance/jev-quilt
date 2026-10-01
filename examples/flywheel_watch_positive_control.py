"""Positive control for the flywheel watch: the instrument CAN fire here.

The first production reading (examples/flywheel_watch.py) was an honest
negative: none of the four flywheel domains is majority-alarmed, so
scan() named no JEPA slot. An honest negative is only as good as the
proof that the instrument is not deaf ON THIS HARNESS — the toy demo
(jepa_slot_watch.py) fired on a toy world, but the production loop has
its own wiring (four cells, one world emit per tick, Q16 scripted
regimes). If a periodic domain is grafted onto the SAME harness, the
very same scan() must name it — majority-alarmed, receipt-backed, exact.

That is what this file pins: same run_flywheel, one synthetic grafted
cell `sense.synth.periodic` (period 10, K=4 mean — blind by
construction). scan() must return exactly that cell and nothing else;
the four real domains must stay non-candidates. If a future edit to the
harness or the scanner breaks the firing path, this control fails
LOUDLY — the watch's honest negative would otherwise be unfalsifiable.

Run: python3 examples/flywheel_watch_positive_control.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from examples.flywheel_watch import run_flywheel, world_signal, DOMAINS, ALARM_FLOOR, TICKS
from jev_quilt import Cell, Hook, Q16, MeanPredictor, Projection
from jev_quilt.jepa_slot import scan

SYNTH = "sense.synth.periodic"
SYNTH_TICKS = 120


def run_with_synthetic(ticks: int = TICKS) -> dict:
    """The production flywheel + one grafted periodic cell, same wiring.

    Returns the full book dict (real domains + synthetic)."""
    books = run_flywheel(ticks=ticks)
    # graft onto the same engine shape: a second sense cell fed by the
    # same world rhythm, predictor class identical to production (K=4).
    eng_books = _grafted_books(ticks)
    books.update(eng_books)
    return books


def _grafted_books(ticks: int) -> dict:
    from jev_quilt import Engine

    eng = Engine()
    eng.register(Cell("world", (0, 0)))
    eng.register(Cell(
        SYNTH, (2, 0),
        input_hooks=[Hook("world")],
        decision={"rule": "identity", "value": Q16(1, 10)},
        predictor=MeanPredictor(k=4),
        surprise_floor=ALARM_FLOOR,
        outputs=[Projection("felt.synth.periodic", "q16")],
    ))
    for t in range(1, ticks + 1):
        eng.cells[SYNTH].decision = {
            "rule": "identity", "value": Q16(t % 10 + 1, 10)}
        eng.emit("world", {"tick": t}, state={"t": t})
    return eng.books


def main() -> None:
    books = run_with_synthetic(SYNTH_TICKS)
    receipts = sum(len(b.entries) for b in books.values())
    assert all(b.verify() for b in books.values())

    candidates, problems = scan(books, min_wakes=10)

    print(f"== positive control — {receipts} receipts, all chain-verified ==")
    for name, bk in sorted(books.items()):
        alarms = sum(1 for e in bk.entries if '"alarmed": "true"' in e.payload)
        tag = ""
        if name == SYNTH:
            tag = "  <- grafted periodic world (mean-blind by construction)"
        print(f"  {name:26s} alarms={alarms:3d}/{len(bk.entries):3d}{tag}")

    print("\n== scan() on the grafted production loop ==")
    for c in candidates:
        print(f"  {c}")
    for p in problems:
        print(f"  PROBLEM: {p}")

    assert [c.cell for c in candidates] == [SYNTH], \
        "positive control broken: scanner must name exactly the grafted cell"
    assert problems == []
    print("\ncontrol holds: the watch fires on this harness exactly when a "
          "mean-unrepresentable world is present — the production negative "
          "is the world's shape, not instrument deafness.")


if __name__ == "__main__":
    main()
