"""Two mirrors: JEV simulating JEPA; JEPA simulating JEV.

One engine, one world, two fabrics watching it:

  mirror.ensemble  — JEV managing a variety of JEPA readings (mean,
                     persistence, period, drift). A Choice by integer
                     weights picks the trusted reading per tick; the
                     receipt books which reading spoke.
  mirror.imagination — JEPA rolling candidate futures in a tiny world
                     whose state IS the signal; the surface act re-enacts
                     JEV (typed Choice, exact probabilities, bookable).

The disagreement ledger takes |surprise_ensemble - surprise_imagination|
each tick: where both mirrors are calm, confidence compounds; where they
split, the split itself is booked and named. That is the two-way
simulation Casey asked for (2026-09-21 11:34), run wide.

Run: python3 examples/two_mirrors.py --ticks 60
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import (Cell, Hook, Q16, Engine, MeanPredictor, Projection,
                       ConstReading, NgramReading, DriftReading,
                       ReadingEnsemble, WorldModel, imagine_choice)
from jev_quilt.predictor import surprise

SIG_PERIOD = [Q16(1, 10), Q16(5, 10), Q16(9, 10)]   # periodic world
STEP_AT = 40                                        # ...then a regime step
POST_STEP = [Q16(8, 10), Q16(8, 10), Q16(8, 10)]


def signal(t: int) -> Q16:
    if t < STEP_AT:
        return SIG_PERIOD[t % 3]
    return POST_STEP[t % 3]


def world_of(pos: Q16):
    def transition(s: Q16, a: str) -> Q16:
        p = s.num // s.den
        if a == "up":
            p = min(3, p + 1)
        elif a == "hold":
            pass
        elif a == "down":
            p = max(0, p - 1)
        else:
            raise ValueError(a)
        return Q16(p, 1)
    return WorldModel(transition, energy=lambda s: Q16(3, 1) - s)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticks", type=int, default=60)
    a = ap.parse_args()

    eng = Engine()
    eng.register(Cell("world.signal", (0, 0)))
    eng.register(Cell(
        "mirror.ensemble", (1, 0), input_hooks=[Hook("world.signal")],
        decision={"rule": "identity", "value": SIG_PERIOD[0]},
        predictor=ReadingEnsemble({
            "mean": MeanPredictor(k=4),
            "persist": ConstReading(),
            "period": NgramReading(k=3),
            "drift": DriftReading(k=4),
        }),
        surprise_floor=Q16(15, 100),
        outputs=[Projection("felt.ensemble", "q16")],
    ))
    eng.register(Cell(
        "mirror.imagination", (2, 0), input_hooks=[Hook("world.signal")],
        decision={"rule": "identity", "value": SIG_PERIOD[0]},
        predictor=MeanPredictor(k=4),   # feels the rolled-choice outcomes
        surprise_floor=Q16(15, 100),
        outputs=[Projection("acted.imagination", "choice")],
    ))

    w = world_of(Q16(0, 1))
    imagination_pos = Q16(1, 1)
    print(f"{'t':>3} {'signal':>7} {'reading':>8} {'ens_surp':>9} "
          f"{'img_choice':>10} {'img_surp':>9} {'|disagree|':>10}")
    disagreements = []
    for t in range(1, a.ticks + 1):
        v = signal(t)
        eng.cells["mirror.ensemble"].decision = {"rule": "identity", "value": v}
        eng.cells["mirror.imagination"].decision = {"rule": "identity", "value": v}
        eng.emit("world.signal", {"mag": Q16(1)}, state={"t": t})

        # JEPA-sim-JEV act: roll futures from the world-state = signal level
        d = imagine_choice(w, v, ["up", "hold", "down"], horizon=1)
        imagination_pos = w.roll(imagination_pos, str(d.value), 1)

        ens_r = json.loads(eng.books["mirror.ensemble"].entries[-1].payload)
        img_r = json.loads(eng.books["mirror.imagination"].entries[-1].payload)
        es = Q16(*[int(x) for x in ens_r.get("surprise", "0/1").split("/")]) \
            if "surprise" in ens_r else None
        ims = Q16(*[int(x) for x in img_r.get("surprise", "0/1").split("/")]) \
            if "surprise" in img_r else None
        if es is not None and ims is not None:
            dd = es - ims
            dd = Q16(abs(dd.num), dd.den)
            disagreements.append((t, dd))
        if t % 5 == 0 or (STEP_AT - 2) <= t <= (STEP_AT + 3):
            print(f"{t:>3} {v.to_float():>7.3f} {ens_r.get('reading', '—'):>8} "
                  f"{ens_r.get('surprise', '—'):>9} {str(d.value):>10} "
                  f"{img_r.get('surprise', '—'):>9} "
                  f"{str(dd) if es is not None and ims is not None else '—':>10}")

    # book the disagreement ledger into its own receipts (law 4: even the
    # comparison between fabrics is booked, not just asserted)
    eng.register(Cell("meta.disagreement", (3, 0)))
    for t, dd in disagreements:
        eng.books["meta.disagreement"].book(
            state={"t": t}, delta={"mag": dd},
            decision_kind="disagreement",
            payload={"tick": t, "abs_surprise_delta": str(dd)})

    ens_alarms = sum(1 for e in eng.books["mirror.ensemble"].entries
                     if '"alarmed": "true"' in e.payload)
    img_alarms = sum(1 for e in eng.books["mirror.imagination"].entries
                     if '"alarmed": "true"' in e.payload)
    print(f"\nensemble alarms: {ens_alarms}   imagination alarms: {img_alarms}   "
          f"disagreement receipts: {len(disagreements)}")
    print(f"chain verifies: "
          f"{all(b.verify() for b in eng.books.values())}")


if __name__ == "__main__":
    main()
