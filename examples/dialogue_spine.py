"""Dialogue spine demo: essay 001's instrument, made measurable.

A tiny NPC spine — 3 branch nodes, each holding a Choice over candidate
next-moves with exact integer weights. Player utterances arrive as deltas
with a `touched` set and a magnitude. Deadband: below the floor a node does
NOT re-decide (silence is booked). spine_share = woke nodes / total nodes —
the creepiness dial from ideation/dialogue-fractals/001.

Run: python3 examples/dialogue_spine.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import Cell, Hook, Projection, Q16, Engine


def cares(node):
    return lambda s: node in s.get("touched", set())

# The pre-computed spine: node -> candidate next-moves with exact weights.
SPINE = {
    "greeting":      {"warm_hello": 60, "curt_nod": 30, "ignore": 10},
    "accusation":    {"deny": 25, "justify_price": 45, "offer_discount": 30},
    "aftermath":     {"change_subject": 50, "wait": 35, "escalate": 15},
}

FLOOR = Q16(2, 100)  # utterance magnitude below 0.02 → deadband silence

# (text, magnitude, touched nodes)
UTTERANCES = [
    ("hey",                          Q16(1, 1000), {"greeting"}),          # tiny
    ("you're overcharging me",       Q16(8, 10),   {"accusation", "greeting"}),
    ("hm",                           Q16(1, 1000), {"aftermath"}),         # below floor
    ("fine, whatever",               Q16(5, 10),   {"aftermath", "accusation"}),
    ("actually, why IS it priced so high?", Q16(9, 10), {"accusation", "aftermath", "greeting"}),
]


def main() -> None:
    eng = Engine()
    eng.register(Cell("player.utterance", (0, 0)))
    for i, node in enumerate(SPINE):
        eng.register(Cell(
            f"spine.{node}", (1, i),
            input_hooks=[Hook("player.utterance", floor=FLOOR, when=cares(node))],
            decision={"rule": "argmax", "options": SPINE[node]},
            outputs=[Projection("voice.line", "choice")],
        ))

    print(f"{'utterance':38s} woke/total  spine_share  deadband_beats  line picked")
    for text, mag, touched in UTTERANCES:
        state = {"touched": sorted(touched), "utterance": text}
        results = eng.emit("player.utterance", {"mag": mag}, state=state)
        woke = [r for r in results if r.reason == "decided"]
        silent = [r for r in results if r.reason == "silent_deadband"]
        share = len(woke) / len(SPINE)
        beats = len(silent)
        picked = ", ".join(f"{r.cell.split('.')[1]}→{r.decision.value}" for r in woke)
        print(f"{text!r:38s} {len(woke)}/{len(SPINE)}        "
              f"{share:.2f}         {beats}               {picked}")

    bk = eng.books["spine.accusation"]
    print(f"\nreceipts booked (accusation node): {bk._tick}, "
          f"chain-verify={bk.verify()}")
    print("doctrine check: 'hm' below floor → booked silence, no re-decision:"
          f" {'PASS' if any(r.reason=='silent_deadband' for r in eng.log) else 'FAIL'}")


if __name__ == "__main__":
    main()
