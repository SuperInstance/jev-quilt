"""E2: GAN-cell — generator proposes, JEV judge scores, best kept, data grows.

Spring from substrate-gan (Mavis): "generator proposes -> JEV (judge)
scores -> best kept -> training data grows -> coherence strengthens."
Quilt version, fully exact: the generator is a witness-RNG sampler over a
Q16 alphabet; the judge is imagine_score against an exact rubric; kept
receipts are the growing training set. Coherence = mean kept energy,
tracked per round and booked.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import (Cell, Hook, Q16, Engine, WorldModel, imagine_score,
                       WitnessRng, seed_from_state)

ALPHABET = [Q16(i, 16) for i in range(16)]         # finer than rubric: no free hits
RUBRIC = [Q16(1, 10), Q16(3, 10), Q16(5, 10)]       # judge's taste


def main(rounds: int = 20, proposals: int = 6):
    eng = Engine()
    eng.register(Cell("gan.judge", (0, 0)))
    seed = seed_from_state({"gan": "cell", "round": 0})
    kept_dists, coherence = [], []
    kept_ledger: list[Q16] = []

    for rnd in range(rounds):
        rng = WitnessRng(seed + rnd)
        best = None   # (terminal, dist_Q16, nearest)
        for _ in range(proposals):
            # generator that LEARNS: half the proposals are resampled from
            # the kept ledger (the growing training data), half explore fresh
            if kept_ledger and rng._carve() % 2 == 0:
                cand = rng.pick(kept_ledger)
            else:
                cand = rng.pick(ALPHABET)
            d = imagine_score(WorldModel(lambda s, a: s, lambda s: s),
                              cand, RUBRIC, horizon=0)
            if d.kind == "score":
                delta = cand - d.value
                dist = Q16(abs(delta.num), delta.den)
                if best is None or dist < best[1]:
                    best = (cand, dist, d.value)
        if best is None:
            continue
        kept_ledger.append(best[0])
        eng.books["gan.judge"].book(
            state={"round": rnd}, delta={"mag": best[0]},
            decision_kind="gan_keep",
            payload={"round": rnd, "kept": str(best[0]),
                     "dist_to_rubric": str(best[1]),
                     "nearest_rubric": str(best[2])})
        kept_dists.append(best[1])
        s = kept_dists[0]
        for x in kept_dists[1:]:
            s = s + x
        coherence.append(Q16(s.num, s.den * len(kept_dists)))  # exact mean

    ok = all(b.verify() for b in eng.books.values())
    print(f"E2 gan-cell: {rounds} rounds x {proposals} proposals, "
          f"{len(kept_ledger)} kept")
    print(f"   coherence (mean |kept-nearest|): start {coherence[0]} "
          f"-> end {coherence[-1]}  (lower = tighter fit to rubric)")
    print(f"   judge receipts verify: {ok}")


if __name__ == "__main__":
    main()
