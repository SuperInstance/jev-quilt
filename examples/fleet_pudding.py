"""The pudding: jev-quilt deciding a real fleet lane — receipts, not vibes.

Dogfood protocol (Casey 2026-09-21: "practice using quilt yourself"):
encode the actual open-lane decision as cells, let the engine decide,
then HONESTLY compare against the operator's gut call recorded BEFORE
running. The comparison is the deliverable, not the decision.

Run: python3 examples/fleet_pudding.py

DOGFOOD RECORD (2026-09-21): gut call recorded before running = "ak-slice2
first, it's stalled and valuable." Fabric ranking: ak-slice2 0.74,
jev-quilt-v03 0.71, ideation-wave2 0.60, lane-ad-hnsim 0.53, canon-pnpm
0.49 → MATCH, with one honest upgrade over the gut: the near-tie exposed
that the answer is sensitive to `unblocked` — when the AK driver proved
alive mid-hour, ownership of ak-slice2 left main and the ranking flipped
to jev-quilt-v03. Receipts: 20 wakes, 4 books per candidate, chain
verified. Verdict: useful as a forcing function for declared weights + a
re-runnable, diffable decision record — NOT yet a replacement for judgment
(the scores were still mine; the fabric made them argue in the open).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import Cell, Hook, Projection, Q16, Engine

DEN = 10 ** 8  # all score×weight products share this denominator exactly

# criteria weights — declared, exact, arguable (argue by changing them)
WEIGHTS = {
    "merge_value": Q16(4, 10),    # advances a front / shrinks Casey's queue
    "unblocked":   Q16(3, 10),    # main can ship it this hour
    "ownership":   Q16(2, 10),    # main is the best owner (crons can't)
    "small":       Q16(1, 10),    # committable unit < 1h
}

# candidates scored per criterion, 0..10 (integers are exact in ℚ×10⁸)
CANDIDATES = {
    "ak-slice2":      {"merge_value": 7, "unblocked": 9, "ownership": 6, "small": 7},
    "jev-quilt-v03":  {"merge_value": 5, "unblocked": 9, "ownership": 9, "small": 6},
    "ideation-wave2": {"merge_value": 3, "unblocked": 8, "ownership": 8, "small": 8},
    "lane-ad-hnsim":  {"merge_value": 6, "unblocked": 5, "ownership": 5, "small": 4},
    "canon-pnpm":     {"merge_value": 6, "unblocked": 4, "ownership": 4, "small": 5},
}


def product(cand: str, criterion: str) -> Q16:
    """score(0..10 → ℚ tenths) × weight(ℚ tenths) = exact."""
    return Q16(CANDIDATES[cand][criterion], 10) * WEIGHTS[criterion]


def main() -> None:
    eng = Engine()
    for i, c in enumerate(WEIGHTS):
        eng.register(Cell(f"criterion.{c}", (0, i)))
    for i, cand in enumerate(CANDIDATES):
        eng.register(Cell(
            f"score.{cand}", (1, i),
            input_hooks=[Hook(f"criterion.{c}") for c in WEIGHTS],
            decision={"rule": "sum",
                      "terms": [(product(cand, c).num, product(cand, c).den)
                                for c in WEIGHTS]},
            outputs=[Projection("choice.next_lane", "score")],
        ))

    for c in WEIGHTS:
        eng.emit(f"criterion.{c}", {"mag": Q16(1)}, state={"criterion": c})

    totals = {cand: sum((product(cand, c) for c in WEIGHTS), Q16(0))
              for cand in CANDIDATES}
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    print("== jev-quilt lane ranking (exact q16 weighted scores) ==")
    for cand, t in ranked:
        print(f"  {cand:18s} {t.to_float():.4f}")
    woke = [r for r in eng.log if r.reason == "decided"]
    print(f"\nwake events: {len(eng.log)} ({len(woke)} decided, "
          f"{len(eng.log) - len(woke)} silent/refused)")
    bk = eng.books["score.ak-slice2"]
    print(f"receipts booked per candidate: {bk._tick} "
          f"(= {len(WEIGHTS)} criteria; chain-verify={bk.verify()})")


if __name__ == "__main__":
    main()
