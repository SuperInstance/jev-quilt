"""The elephant under the ledger: intuition maturing, measured.

A sense cell (identity rule) is fed a signal that steps from 0.1 to 0.7.
Its MeanPredictor feels each value before it lands. Watch the alarms:
surprise is large on the step (the world changed), then shrinks to zero
as the window fills with the new regime — shorter and shorter delays,
more confidence, exactly as booked.

Run: python3 examples/elephant.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import Cell, Hook, Projection, Q16, Engine, MeanPredictor

SIGNAL = [Q16(1, 10)] * 6 + [Q16(7, 10)] * 10  # step at t=7
FLOOR = Q16(15, 100)   # alarm if surprise > 0.15


def main() -> None:
    eng = Engine()
    eng.register(Cell("world.signal", (0, 0)))
    eng.register(Cell(
        "sense.elephant", (1, 0),
        input_hooks=[Hook("world.signal")],
        decision={"rule": "identity", "value": SIGNAL[0]},
        predictor=MeanPredictor(k=4),
        surprise_floor=FLOOR,
        outputs=[Projection("felt.value", "q16")],
    ))

    print(f"{'t':>3} {'signal':>7} {'predicted':>10} {'surprise':>9}  alarm")
    for t, v in enumerate(SIGNAL, 1):
        eng.cells["sense.elephant"].decision = {"rule": "identity", "value": v}
        eng.emit("world.signal", {"mag": Q16(1)}, state={"t": t})
        bk = eng.books["sense.elephant"]
        last = bk.entries[-1]
        import json
        r = json.loads(last.payload)
        print(f"{t:>3} {v.to_float():>7.3f} {r.get('predicted', '—'):>10} "
              f"{r.get('surprise', '—'):>9}  {'ALARM' if r.get('alarmed') else ''}")

    alarms = sum(1 for e in eng.books["sense.elephant"].entries
                 if '"alarmed": "true"' in e.payload)
    print(f"\nalarm count: {alarms} (the step is one surprise; the rest is the "
          f"window filling — intuition is the booked absence of further alarms)")
    print(f"chain verify: {eng.books['sense.elephant'].verify()}")


if __name__ == "__main__":
    main()
