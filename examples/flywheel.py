"""The flywheel: experiment -> booked understanding -> synthesized questions.

One driver. Ticks a synthetic world through the ENGINE (not the raw
battery) so every probe is a hooked wake with a pre-committed prediction,
an exact surprise, and a chain-verified receipt. When the run ends,
inquiry reads the books and prints the NEXT experiments as questions.

This is the loop Casey described (2026-09-21): iteratively improving
experiments that build on each other's understanding and lead to open-
ended research questions that come back for more massive experimentation.

Run: python3 examples/flywheel.py --ticks 200
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import Cell, Hook, Q16, Engine, MeanPredictor, Projection
from jev_quilt.inquire import next_questions

DOMAINS = ["dialogue.trust", "game.confidence", "robotics.battery", "sheet.margin"]
ALARM_FLOOR = Q16(15, 100)


def world_signal(t: int, domain_idx: int) -> Q16:
    """Deterministic synthetic regime per domain: each drifts at a
    different rate, with one step change at t = ticks//3. Exact rationals
    throughout — the world is scripted, not random, so surprise has a
    known ground truth."""
    base = [1, 3, 2, 4][domain_idx]
    step_at = 60
    ramp = t // 20
    if domain_idx == 1 and t >= step_at:   # game.confidence steps late
        ramp += 3
    v = (base + ramp) % 10
    return Q16(v + 1, 10)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", type=int, default=120)
    a = ap.parse_args()

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

    for t in range(1, a.ticks + 1):
        for i, d in enumerate(DOMAINS):
            eng.cells[f"sense.{d}"].decision = {
                "rule": "identity", "value": world_signal(t, i)}
        eng.emit("world", {"tick": t}, state={"t": t})

    print("== alarm ledger ==")
    for d in DOMAINS:
        bk = eng.books[f"sense.{d}"]
        alarms = sum(1 for e in bk.entries if '"alarmed": "true"' in e.payload)
        print(f"  {d:22s} wakes={len(bk.entries):4d} alarms={alarms:3d} "
              f"verify={bk.verify()}")

    print("\n== inquiry: next experiments ==")
    for q in next_questions(eng.books):
        print(f"  [{q['cell']}] {q['question']}")
        print(f"      -> {q['experiment']}")

    print(f"\n{sum(len(b.entries) for b in eng.books.values())} receipts, "
          f"all chain-verified: "
          f"{all(b.verify() for b in eng.books.values())}")


if __name__ == "__main__":
    main()
