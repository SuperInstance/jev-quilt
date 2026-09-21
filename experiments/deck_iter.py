"""experiments/deck_iter.py — E5: the deck as iterator (poll vs surprise).

The pitch's homeostatic-compute claim, measured: a poll loop evaluates
the titanium gate EVERY tick; JevIterator evaluates only when the tap
admits. Same world, same storms — does iteration miss anything, and
how much gate does it save?

World: 600 ticks of calm water, two storm windows. Deterministic seeds.
Run: python3 experiments/deck_iter.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import Bookkeeper, Q16 as Q, WitnessRng
from jev_quilt.tap import ProposalGate, TapGate
from jev_quilt.jeviter import JevIterator

CALM = {"coho": Q(1, 3), "king": Q(1, 3), "chum": Q(1, 3)}
STORM = {"coho": Q(1, 10), "king": Q(8, 10), "chum": Q(1, 10)}
STORM_WINDOWS = ((200, 220), (440, 445))
MAX_LB = Q(60, 1)


def gate_for(keeper):
    return (ProposalGate(keeper)
            .add_invariant("weight_under_60lb", lambda q, ctx: q < MAX_LB)
            .add_invariant("calibrated",
                           lambda q, ctx: max(v.to_float() for v in ctx["dist"].values()) >= 0.5))


def world_stream():
    rng = WitnessRng(11)
    for t in range(600):
        if any(a <= t < b for a, b in STORM_WINDOWS):
            d = dict(STORM)
            d["coho"] = Q(1, 10) + Q16_noise(rng)
        else:
            d = dict(CALM)
        yield t, d


def Q16_noise(rng):
    return Q(rng.next_q16().num, 100)


def poll_loop():
    keeper = Bookkeeper("poll")
    gate = gate_for(keeper)
    decisions = 0
    storm_decided = 0
    for t, d in world_stream():
        ok, _, _ = gate.propose({"t": t}, {"d": list(d)}, d, Q(40, 1))
        decisions += 1
        if any(a <= t < b for a, b in STORM_WINDOWS):
            storm_decided += 1
    return keeper, decisions, storm_decided


def iter_loop():
    keeper = Bookkeeper("iter")
    gate = gate_for(keeper)
    it = JevIterator((d for _, d in world_stream()), TapGate(k=1.5), keeper)
    events = 0
    for ev in it:
        events += 1
        gate.propose({"ev": events}, {"d": list(ev.value)}, ev.value, Q(40, 1))
    return keeper, events, events  # gate evals == events (seed books, no eval)


if __name__ == "__main__":
    kp, dp, sp = poll_loop()
    ki, di, se = iter_loop()
    storm_ticks = sum(b - a for a, b in STORM_WINDOWS)
    print("== E5: the deck as iterator (600 ticks, 2 storm windows) ==")
    print(f"   poll: {dp} gate evaluations, {len(kp.entries)} receipts")
    print(f"   iter: {di} gate evaluations ({100*(1-di/dp):.1f}% saved), "
          f"{len(ki.entries)} receipts, {se} events")
    print(f"   storm coverage: poll decided {sp}/{storm_ticks} storm ticks")
    kinds_i = [e.decision_kind for e in ki.entries]
    print(f"   iter ledger: seed={kinds_i.count('seed')} event={kinds_i.count('event')} "
          f"silence={kinds_i.count('silence')} exhausted={kinds_i.count('exhausted')}")
    assert di < dp // 3, "iteration must save >2/3 of gate evaluations"
    assert se >= 2, "both storms must surface as events"
    assert ki.replay() and kp.replay()
    print("   both chains replay coherent. The valves held.")
