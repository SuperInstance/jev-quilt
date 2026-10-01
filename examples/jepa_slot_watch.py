"""The JEPA slot watch: prove the alarm ledger can NAME the hole.

Two worlds, one predictor class (exact MeanPredictor), one scanner:

  periodic — the world cycles with period 10; a running mean of K=4 is
      structurally blind to a cycle longer than its window. Every wake
      is a surprise the predictor class cannot fix by tuning K.
  constant — the world holds still; the same predictor converges and
      the scanner honestly reports NO candidate.

Run: python3 examples/jepa_slot_watch.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import Cell, Hook, Q16, Engine, MeanPredictor, Projection
from jev_quilt.jepa_slot import scan

FLOOR = Q16(1, 10)   # alarm when surprise > 0.1
TICKS = 40


def run_world(name: str, signal) -> dict:
    eng = Engine()
    eng.register(Cell("world", (0, 0)))
    eng.register(Cell(
        f"sense.{name}", (1, 0),
        input_hooks=[Hook("world")],
        decision={"rule": "identity", "value": signal(0)},
        predictor=MeanPredictor(k=4),
        surprise_floor=FLOOR,
        outputs=[Projection(f"felt.{name}", "q16")],
    ))
    for t in range(1, TICKS + 1):
        eng.cells[f"sense.{name}"].decision = {
            "rule": "identity", "value": signal(t)}
        eng.emit("world", {"tick": t}, state={"t": t})
    return eng.books


def periodic(t: int) -> Q16:
    """Period-10 cycle. A K=4 running mean is blind BY CONSTRUCTION to a
    cycle longer than its window — this is a predictor-CLASS failure,
    not a tuning failure."""
    return Q16(t % 10 + 1, 10)


def constant(t: int) -> Q16:
    return Q16(3, 10)


def main() -> None:
    books = {}
    books.update(run_world("periodic", periodic))
    books.update(run_world("constant", constant))

    candidates, problems = scan(books)
    receipts = sum(len(b.entries) for b in books.values())

    print(f"== {receipts} receipts, all chain-verified: "
          f"{all(b.verify() for b in books.values())} ==\n")
    for name, bk in books.items():
        alarms = sum(1 for e in bk.entries if '"alarmed": "true"' in e.payload)
        print(f"  {name:22s} wakes={len(bk.entries):4d} alarms={alarms:3d}")

    print("\n== JEPA slot candidates ==")
    if candidates:
        for c in candidates:
            print(f"  {c}")
    else:
        print("  (none — predictor class covers every watched cell)")
    for p in problems:
        print(f"  PROBLEM: {p}")

    print("\nreading: the periodic cell alarms on a STRUCTURE the mean "
          "cannot represent.\nThat is the JEPA-shaped hole: not more "
          "tuning, a different predictor class behind the same "
          "predict()/update() seam.")


if __name__ == "__main__":
    main()
