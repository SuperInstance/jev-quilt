"""experiments/deck_sim.py — the proving ground from the sheaf pitch.

Pitching back-deck: a vision cell (stochastic, emits exact-rational
Choice Distributions over species) and a hanging scale (exact Q16
weight) propose landings; the ProposalGate disposes against physical
invariants. The TapGate throttles the vision cell: static water =
silence, a boil of fish = valves open. A hallucinated float weight is
refused before any invariant runs (Law 1).

Experiments (deterministic seeds; every decision booked + replayed):
  E1 tap sweep      k x drift-rate -> emits (the valves)
  E2 species id     vision dist under glare vs clean water -> refusals
  E3 law 1          float identity refused, booked, replayed
  E4 ledger         transition/refusal counts, chain coherence
Run: python3 experiments/deck_sim.py
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import Bookkeeper, Q16, WitnessRng
from jev_quilt.tap import TapGate, ProposalGate

Q = Q16
SPECIES = ("coho", "king", "chum")
MAX_LB = Q(60, 1)            # physical invariant: scale tops out at 60 lb
KNOWN = {s: Q(1, 1) for s in SPECIES}


def vision_dist(rng: WitnessRng, glare: float) -> dict:
    """Stochastic organ: samples a distribution, exact rationals out."""
    p_king = (0.15 + 0.20 * rng.next_q16().to_float()) if glare > 0.5 \
        else min(0.75 + 0.15 * rng.next_q16().to_float(), 0.95)
    p_coho = (1.0 - p_king) * 0.7
    p_chum = 1.0 - p_king - p_coho
    return {"king": Q.from_float(round(p_king, 4)),
            "coho": Q.from_float(round(p_coho, 4)),
            "chum": Q.from_float(round(p_chum, 4))}


def e1_tap_sweep():
    print("== E1: tap valves (k x drift -> emits of 120 ticks) ==")
    for k in (0.5, 1.0, 2.0, 4.0):
        row = []
        for drift in (0.0, 0.01, 0.05, 0.2):
            rng = WitnessRng(41)
            gate = TapGate(k=k)
            prev = {"x": Q(1, 2), "y": Q(1, 2)}
            emits = 0
            for t in range(120):
                new = prev
                if drift and rng.below(Q.from_float(drift)):
                    f = rng.next_q16().to_float()
                    new = {"x": Q.from_float(round(0.2 + 0.6 * f, 4)),
                           "y": Q.from_float(round(0.8 - 0.6 * f, 4))}
                if gate.admit(prev, new)[0]:
                    emits += 1
                prev = new
            row.append(f"{drift}:{emits:3d}")
        print(f"   k={k:<4} " + "  ".join(row))
    print("   (static 0-drift must be ~silent at every k; valves open with drift)")


def e2_e4_landing():
    print("\n== E2-E4: the deck (vision + scale vs the titanium gate) ==")
    keeper = Bookkeeper("deck")
    gate = (ProposalGate(keeper)
            .add_invariant("weight_under_60lb", lambda q, ctx: q < MAX_LB)
            .add_invariant("calibrated_confidence",
                           lambda q, ctx: max(v.to_float() for v in ctx["dist"].values()) >= 0.5))
    rng = WitnessRng(7)
    tap = TapGate(k=1.5)
    prev_dist = {"king": Q(1, 3), "coho": Q(1, 3), "chum": Q(1, 3)}

    n_transition = n_refusal = n_silenced = 0
    dist = prev_dist
    last_glare = None
    for t in range(60):
        glare = 0.9 if 20 <= t < 35 else 0.25      # sun off the water
        if glare != last_glare or t % 10 == 0:     # the organ re-reads on
            dist = vision_dist(rng, glare)         # change, not on a poll
            last_glare = glare
        emit, gain, th = tap.admit(prev_dist, dist)
        if emit:
            prev_dist = dist
        if not emit:
            n_silenced += 1
            continue
        weight = Q(38, 1) if t % 5 else Q(52, 1)  # kings hit the deck
        top = max(dist.items(), key=lambda kv: kv[1].to_float())[0]
        ok, reason, _ = gate.propose({"t": t}, {"species": top},
                                     KNOWN | {"king": dist["king"]}, weight)
        n_transition += ok
        n_refusal += (not ok)
        if 20 <= t < 35 and not ok:
            print(f"   t={t:2d} glare-window refusal: {reason} (the titanium earns it)")

    # E3: hallucinated float identity
    ok, reason, r = gate.propose({"t": 99}, {"species": "king"},
                                 KNOWN, 41.7)      # a float. Law 1.
    print(f"\n   E3 law1: float identity -> accepted={ok} reason={reason} "
          f"receipt={r.decision_kind}")

    kinds = [e.decision_kind for e in keeper.entries]
    print(f"\n   E4 ledger: transitions={kinds.count('transition')} "
          f"refusals={kinds.count('refusal')} silenced_by_tap={n_silenced}")
    print(f"   replay(): {'coherent' if keeper.replay() else 'DIVERGED'}")


if __name__ == "__main__":
    e1_tap_sweep()
    e2_e4_landing()
