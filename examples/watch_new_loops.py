"""Watch reading on main's new loops: jeviter and deck_sim.

The flywheel watch (#10) read the production flywheel and reported an
honest negative; the positive control (#11) proved the instrument
cannot stay deaf. Main has since grown two NEW loops — jeviter (JEV as
an iterator: a for-loop driven by information gain, not index) and
deck_sim (the proving ground: vision cell + hanging scale vs the
ProposalGate). The instrument's standing order is to keep reading the
ledgers, so this is the first reading on those loops.

Same construction as flywheel_watch.py: the loop's own signal
sequences, verbatim shapes, sensed by cells with the MeanPredictor
class and surprise_floor — the question is never "is there surprise"
but "is the surprise MAJORITARIAN" (scan(): >= 50% of wakes alarmed,
exact integer compare).

Reading (pinned by tests/test_watch_new_loops.py):

  jeviter.static    low alarms   a constant stream is mean-representable;
                                the tap's silences are booked as refusals,
                                not alarmed wakes
  jeviter.periodic  MAJORITY     period-8 alternation — a running mean
                    ALARMS       converges to the midpoint and is wrong
                                on EVERY wake. scan() NAMES this cell:
                                the predictor class is structurally blind
                                here; this is the JEPA plug seam, arrived
                                naturally on a production-adjacent loop
  deck.vision       low alarms   the glare window (t=20..35) is a
                                TRANSITION the mean absorbs, like
                                game.confidence's t=60 step on the
                                flywheel — not a structure
  deck.scale        low alarms   38/52 lb landings as fractions of the
                                60 lb invariant; the refused float
                                (Law 1) never reaches a sense cell —
                                refusals are booked by the gate, not
                                alarmed by the predictor

  scan() -> exactly ONE candidate: jeviter.periodic. The periodic
  world's structure (its period) is the thing a running mean cannot
  represent at ANY K — the same shape the slot watch named
  synthetically, now named on the loop the fleet actually built. The
  instrument earns its keep: it stays quiet on three honest domains
  and speaks once, where the speaking is true.

Run: python3 examples/watch_new_loops.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import Bookkeeper, Cell, Hook, Q16, Engine, MeanPredictor, Projection, WitnessRng
from jev_quilt.jepa_slot import scan

ALARM_FLOOR = Q16(15, 100)
TICKS = 120
PERIOD = 8
GLARE = (20, 35)          # deck_sim's sun-off-the-water window, verbatim
MAX_LB = Q16(60, 1)       # deck_sim's physical invariant


def jeviter_stream(periodic: bool, ticks: int = TICKS) -> list[dict]:
    """The stream shapes jeviter consumes. NOTE the normalizer: jeviter
    divides every reading by its exact Q16 sum, so a single-key stream
    degenerates to 1/1 always — real streams need >= 2 keys (this is
    worth knowing before feeding the iterator)."""
    out = []
    for t in range(ticks):
        if periodic and (t % PERIOD) < PERIOD // 2:
            out.append({"x": 0.8, "y": 0.2})
        else:
            out.append({"x": 0.2, "y": 0.8})
    return out


def deck_vision_stream(ticks: int = TICKS) -> list[float]:
    """deck_sim's vision organ output (p_king), same re-read policy:
    re-read on glare change or every 10 ticks."""
    rng = WitnessRng(7)
    stream, last_glare = [], None
    for t in range(ticks):
        glare = 0.9 if GLARE[0] <= t < GLARE[1] else 0.25
        if glare != last_glare or t % 10 == 0:
            p = (0.15 + 0.20 * rng.next_q16().to_float()) if glare > 0.5 \
                else min(0.75 + 0.15 * rng.next_q16().to_float(), 0.95)
            last_glare, last_p = glare, p
        stream.append(last_p)
    return stream


def deck_scale_stream(ticks: int = TICKS) -> list[float]:
    """deck_sim's landing weights as a fraction of the 60 lb invariant
    (normalization keeps deviations on the same scale as the alarm
    floor — 38/60 vs 52/60 straddle 0.75 at +-0.117, under floor)."""
    return [(52 if t % 5 == 0 else 38) / MAX_LB.to_float()
            for t in range(ticks)]


def run_watch() -> dict[str, Bookkeeper]:
    eng = Engine()
    eng.register(Cell("world", (0, 0)))
    streams = {
        "jeviter.static": [row["x"] for row in jeviter_stream(False)],
        "jeviter.periodic": [row["x"] for row in jeviter_stream(True)],
        "deck.vision": deck_vision_stream(),
        "deck.scale": deck_scale_stream(),
    }
    for i, (name, _) in enumerate(streams.items()):
        eng.register(Cell(
            name, (1, i),
            input_hooks=[Hook("world")],
            decision={"rule": "identity", "value": Q16(0, 1)},
            predictor=MeanPredictor(k=4),
            surprise_floor=ALARM_FLOOR,
            outputs=[Projection(f"felt.{name}", "q16")],
        ))
    for t in range(TICKS):
        for name, sig in streams.items():
            eng.cells[name].decision = {
                "rule": "identity", "value": Q16.from_float(round(sig[t], 4))}
        eng.emit("world", {"tick": t + 1}, state={"t": t + 1})
    return eng.books


def main() -> None:
    books = run_watch()
    receipts = sum(len(b.entries) for b in books.values())
    assert all(b.verify() for b in books.values())

    print(f"== watch on new loops — {receipts} receipts, all chain-verified ==")
    for name in books:
        bk = books[name]
        alarms = sum(1 for e in bk.entries if '"alarmed": "true"' in e.payload)
        print(f"  {name:18s} alarms={alarms}/{len(bk.entries)}")

    candidates, problems = scan(books, min_wakes=10)
    print("\n== JEPA slot candidates ==")
    for c in candidates:
        print(f"  {c}")
    if not candidates:
        print("  (none — honest negative)")
    for p in problems:
        print(f"  PROBLEM: {p}")


if __name__ == "__main__":
    main()
