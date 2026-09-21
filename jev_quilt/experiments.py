"""Experiment battery: massive, honest, booked.

Runs typed-decision experiments across the genres and writes every receipt
(state hash, decision, latency, calibration fields) into a bookkeeper WAL.
Offline by default (q16 + scripted probes); --live fires the real
TypeSafe API for every question.

Usage:
  python3 -m jev_quilt.experiments [--live] [--n N]
"""

from __future__ import annotations
import argparse
import json
import sys

from .backends import Q16Backend, resolve_backend
from .bookkeeper import Bookkeeper
from .typesafe_client import TypeSafeBackend

# --- experiment domains: (name, state, questions) -------------------------

DIALOGUE_STATE = {
    "scene": "tavern", "npc": "quartermaster", "player_tone": "suspicious",
    "spine": ["greeting", "player_accuses_price_gouging"],
    "trust": 0.31,
}

GAME_STATE = {
    "game": "chess", "board_fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
    "player_color": "white", "clock_s": [312, 298],
}

ROBOT_STATE = {
    "env": "warehouse", "battery": 0.62, "payload": None,
    "obstacles": [{"kind": "human", "dist_m": 2.1, "velocity": [0.4, 0.0]}],
    "task_queue": ["pick:A-12", "drop:B-07"],
}

DOMAINS = [
    ("dialogue.tone_routing", DIALOGUE_STATE, [
        {"type": "choice", "id": "tone", "options": ["warm", "neutral", "guarded", "defensive"],
         "context": "player just accused the npc of price gouging"},
        {"type": "score", "id": "trust_shift", "rubric": [-2, -1, 0, 1, 2],
         "context": "how does this exchange move trust"},
        {"type": "noul", "id": "offer_discount",
         "context": "should the npc offer a discount to de-escalate"},
    ]),
    ("game.chess_move", GAME_STATE, [
        {"type": "choice", "id": "move_class", "options": ["develop", "castle", "capture", "push_pawn", "tactic"],
         "context": "opening principles + clock pressure"},
        {"type": "score", "id": "position_confidence", "rubric": [0, 1, 2, 3, 4, 5],
         "context": "confidence the current position is better for white"},
    ]),
    ("robotics.route", ROBOT_STATE, [
        {"type": "choice", "id": "reflex", "options": ["proceed", "slow", "stop", "reroute", "yield"],
         "context": "human obstacle at 2.1m moving slowly"},
        {"type": "noul", "id": "need_reasoner",
         "context": "does this situation need the L2 reasoning loop"},
        {"type": "score", "id": "urgency", "rubric": [0, 1, 2, 3],
         "context": "how time-critical is pick:A-12"},
    ]),
]


def run(live: bool, n: int, out_path: str | None) -> int:
    bk = Bookkeeper("experiments")
    ts = TypeSafeBackend()
    q16 = Q16Backend()
    total_q = 0
    rows = []

    for i in range(n):
        for domain, state, questions in DOMAINS:
            if live:
                if not ts.available():
                    print("FATAL: --live but no JEV_API_KEY/TYPESAFE_API_KEY in env", file=sys.stderr)
                    return 2
                try:
                    decisions, meta = ts.decide_batch(state, questions)
                except RuntimeError as e:
                    print(f"live call failed: {e}", file=sys.stderr)
                    return 1
                for q, d in zip(questions, decisions):
                    bk.book(state, {"domain": domain, "q": q["id"]}, d.kind,
                            {"value": str(d.value), "probs": d.probabilities})
                    rows.append({"domain": domain, "q": q["id"], "kind": d.kind,
                                 "value": d.value, "probabilities": d.probabilities,
                                 "confidence": d.confidence, **meta, "round": i})
                    total_q += 1
            else:
                # Offline probe: book the state shape + a deterministic viability
                # decision so the battery exercises the full receipt path.
                d = q16.decide({"rule": "threshold", "value": (7, 10), "threshold": (1, 2)}, None)
                bk.book(state, {"domain": domain, "probe": "offline"}, "q16",
                        {"value": d.value, "note": "offline probe; live backend not wired to this run"})
                for q in questions:
                    rows.append({"domain": domain, "q": q["id"], "kind": q["type"],
                                 "value": None, "offline": True, "round": i})
                    total_q += 1

    verify_ok = bk.verify()
    report = {
        "mode": "live" if live else "offline",
        "rounds": n, "questions": total_q,
        "booked": bk._tick, "book_verify": verify_ok,
        "chain": bk.replay(),
        "sample_rows": rows[:6],
    }
    text = json.dumps(report, indent=2, default=str)
    if out_path:
        with open(out_path, "w") as f:
            f.write(text + "\n")
    print(text[:1200])
    print(f"\n... full report {'written to ' + out_path if out_path else 'elided'}")
    return 0 if verify_ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="use the real TypeSafe Jev API")
    ap.add_argument("--n", type=int, default=3, help="rounds (each round = all domains)")
    ap.add_argument("--out", default=None, help="write JSON report to path")
    a = ap.parse_args()
    sys.exit(run(a.live, a.n, a.out))


if __name__ == "__main__":
    main()
