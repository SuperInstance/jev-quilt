"""E5: Brew cell — parallel candidates, judged once, calm states cached.

Spring from substrate-llm-client (Mavis): "brew = best of 5 parallel LLM
calls; jev_conf in [0.65,0.95]; cached if high enough." Exact offline
version: K witness-RNG futures per state, judged by terminal energy;
decisions for states already seen are served from an exact cache keyed by
state hash when confidence >= cache_floor. Measures: mean decision energy,
cache hit rate, compute saved. The deadband applied to imagination itself.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import Q16, WorldModel, WitnessRng, seed_from_state

CACHE_FLOOR = Q16(3, 4)   # serve from cache at >= 75% confidence


def gridworld():
    def tr(s: Q16, a: str) -> Q16:
        p = s.num // s.den
        if a == "right":
            p = min(4, p + 1)
        elif a == "left":
            p = max(0, p - 1)
        return Q16(p, 1)
    return WorldModel(tr, energy=lambda s: Q16(4, 1) - s)


def main(states: int = 40, repeats: int = 3, k: int = 5):
    w = gridworld()
    rng = WitnessRng(seed_from_state({"exp": "brew"}))
    cache: dict[str, tuple] = {}
    hits = misses = 0
    energies, energies_fresh = [], []
    for i in range(states):
        st = Q16(rng._carve() % 5, 1)
        key = f"{st.num}/{st.den}"
        if key in cache:
            conf, choice, e = cache[key]
            if conf >= CACHE_FLOOR:
                hits += 1
                energies.append(e)
                continue
        misses += 1
        cands = []
        for j in range(k):
            act = rng.pick(["left", "right"])
            term = w.roll(st, act, horizon=2)
            cands.append((w.energy(term), act))
        cands.sort(key=lambda x: (x[0].num, x[0].den))
        best_e, best_a = cands[0]
        total = sum(int((c[0] - cands[-1][0]).num) + 1 for c in cands)
        conf = Q16(len([c for c in cands if c[0] == best_e]), k)
        energies.append(best_e)
        energies_fresh.append(best_e)
        cache[key] = (conf, best_a, best_e)
    n = hits + misses
    mean_e = Q16(sum(e.num for e in energies), len(energies) * 4)
    print(f"E5 brew: {n} decision points ({states} states x {repeats} visits, "
          f"K={k} candidates)")
    print(f"   cache hits {hits}/{n} = {Q16(hits, n)}  (floor {CACHE_FLOOR})")
    print(f"   mean decision energy {mean_e} (lower=better); "
          f"compute saved ~{hits * 5} rolls")


if __name__ == "__main__":
    main()
