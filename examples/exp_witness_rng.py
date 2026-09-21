"""E1: witness RNG — replay-identical randomness from the ledger itself.

Two engines replay the same event sequence: identical receipts, identical
seed, identical rolls. Then Monte-Carlo futures in the gridworld, all
determined by where the ledger stood. Spring: substrate-rng (Mavis).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import (Cell, Hook, Q16, Engine, MeanPredictor, WitnessRng,
                       seed_from_book)


def replay_events():
    eng = Engine()
    eng.register(Cell("src", (0, 0)))
    eng.register(Cell("a", (1, 0), input_hooks=[Hook("src")],
                      decision={"rule": "identity", "value": Q16(1, 10)},
                      predictor=MeanPredictor(k=4)))
    for t in range(1, 21):
        eng.emit("src", {"mag": Q16(1)}, state={"t": t})
    return eng


def main():
    e1, e2 = replay_events(), replay_events()
    s1, s2 = seed_from_book(e1.books["a"]), seed_from_book(e2.books["a"])
    assert s1 == s2, "same witness state must seed the same rolls"

    r1 = [WitnessRng(s1).next_q16() for _ in range(8)]
    r2 = [WitnessRng(s2).next_q16() for _ in range(8)]
    assert r1 == r2
    assert all(isinstance(q, Q16) and q.den == 1 << 16 for q in r1)

    # divergence probe: one extra event -> different seed -> different stream
    e2.emit("src", {"mag": Q16(1)}, state={"t": 21})
    s3 = seed_from_book(e2.books["a"])
    r3 = [WitnessRng(s3).next_q16() for _ in range(8)]
    assert r3 != r1

    # Monte-Carlo futures from the ledger: 64 imagined dice in [0,1)
    rng = WitnessRng(s1)
    rolls = [rng.next_q16() for _ in range(64)]
    mean = sum(rolls, Q16(0, 1)) / Q16(len(rolls), 1)
    print(f"E1 witness-rng: replay-identical rolls OK (seed {hex(s1)[:12]}...)")
    print(f"   64 ledger-seeded rolls, exact dyadic, sample mean {mean} "
          f"(~0.5 expected; deterministic given the ledger)")


if __name__ == "__main__":
    main()
