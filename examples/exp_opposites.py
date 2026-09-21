"""E6: Opposites cell — polarity as a first-class fabric law.

Spring from substrate-opposites (Mavis): canonical opposites, with
JEV <-> JEPA as a substrate-native pair. Quilt version: a cell that
senses categorical names and emits their canonical opposite, booked.
Proof-of-concept self-construction angle: the opposites table IS the
fabric's polarity memory — every pairing is a tiny two-state world
whose transition law is invertible; the cell is that law, worn.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import Cell, Hook, Engine, opposite, is_canonical, OPPOSITES


def main():
    names = ["witness", "jev", "bind", "calm", "predict", "ensemble",
             "unregistered-name"]
    eng = Engine()
    eng.register(Cell("opp.in", (0, 0)))
    eng.register(Cell("opp.out", (1, 0), input_hooks=[Hook("opp.in")],
                      decision={"rule": "identity", "value": None}))
    for n in names:
        eng.cells["opp.in"].decision = {"rule": "identity", "value": n}
        eng.cells["opp.out"].decision = {"rule": "identity",
                                         "value": opposite(n)}
        eng.emit("opp.in", {"name": n}, state={"name": n})
    known = sum(1 for n in names if is_canonical(n))
    inv = all(opposite(opposite(x)) == x or opposite(x) == "gap"
              for x in ["jev", "witness", "calm"])
    print(f"E6 opposites: {len(names)} names, {known} canonical, "
          f"{len(names) - known} -> gap (honest absence)")
    print(f"   sample polarity: " + ", ".join(
        f"{n}->{opposite(n)}" for n in names[:6]))
    print(f"   involution holds on canonical names: {inv}")
    print(f"   jev<->jepa pair present: {OPPOSITES.get('jev') == 'jepa'}")
    print(f"   receipts verify: {all(b.verify() for b in eng.books.values())}")


if __name__ == "__main__":
    main()
