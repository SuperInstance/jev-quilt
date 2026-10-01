"""First flywheel watch reading: the instrument meets the real loop.

The slot watch shipped with a synthetic demonstration (jepa_slot_watch.py:
period-10 world vs K=4 mean -> named candidate). This is the first
reading on the PRODUCTION loop — the flywheel's four domains — asking:
does the alarm ledger of the actual experiment cycle name a JEPA-shaped
hole, or does the mean predictor class cover these worlds?

Reading (pinned by tests/test_flywheel_watch.py):

  dialogue.trust      0 alarms   mean-representable drift
  game.confidence     7 alarms   the t=60 step change — a TRANSITION,
                                not a structure; density 7/120 is far
                                under the majority bar
  robotics.battery    0 alarms   mean-representable
  sheet.margin        1 alarm    warm-up transient

  scan() -> NO candidates, NO problems. Honest negative: on the current
  flywheel worlds the predictor class is not the binding constraint. The
  hole the watch names is real but elsewhere — a world whose structure
  (periodicity, regime memory) a running mean cannot represent at ANY K.
  The instrument's job is to keep watching the ledgers until such a
  world shows up in production, not to manufacture a candidate from
  tuning-scale surprise.

Run: python3 examples/flywheel_watch.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import Cell, Hook, Q16, Engine, MeanPredictor, Projection
from jev_quilt.jepa_slot import scan

DOMAINS = ["dialogue.trust", "game.confidence", "robotics.battery", "sheet.margin"]
ALARM_FLOOR = Q16(15, 100)
TICKS = 120


def world_signal(t: int, domain_idx: int) -> Q16:
    """The flywheel's scripted regimes, verbatim from flywheel.py —
    same world, so the reading is about the loop, not a new toy."""
    base = [1, 3, 2, 4][domain_idx]
    ramp = t // 20
    if domain_idx == 1 and t >= 60:
        ramp += 3
    return Q16((base + ramp) % 10 + 1, 10)


def run_flywheel(ticks: int = TICKS) -> dict:
    eng = Engine()
    eng.register(Cell("world", (0, 0)))
    for i, d in enumerate(DOMAINS):
        eng.register(Cell(
            f"sense.{d}", (1, i),
            input_hooks=[Hook("world")],
            decision={"rule": "identity", "value": Q16(1, 10)},
            predictor=MeanPredictor(k=4),
            surprise_floor=ALARM_FLOOR,
            outputs=[Projection(f"felt.{d}", "q16")],
        ))
    for t in range(1, ticks + 1):
        for i, d in enumerate(DOMAINS):
            eng.cells[f"sense.{d}"].decision = {
                "rule": "identity", "value": world_signal(t, i)}
        eng.emit("world", {"tick": t}, state={"t": t})
    return eng.books


def main() -> None:
    books = run_flywheel()
    receipts = sum(len(b.entries) for b in books.values())
    assert all(b.verify() for b in books.values())

    print(f"== flywheel watch — {receipts} receipts, all chain-verified ==")
    for d in DOMAINS:
        bk = books[f"sense.{d}"]
        alarms = sum(1 for e in bk.entries if '"alarmed": "true"' in e.payload)
        share = f"{alarms}/{len(bk.entries)}"
        note = ""
        if d == "game.confidence":
            note = "  <- step-change transition, not a structure"
        print(f"  {d:22s} alarms={share:>8s}{note}")

    candidates, problems = scan(books, min_wakes=10)
    print("\n== JEPA slot candidates ==")
    if candidates:
        for c in candidates:
            print(f"  {c}")
    else:
        print("  (none — honest negative: the mean predictor class covers")
        print("   every flywheel domain today; the watch keeps reading the")
        print("   ledgers until a world arrives that it cannot represent)")
    for p in problems:
        print(f"  PROBLEM: {p}")


if __name__ == "__main__":
    main()
