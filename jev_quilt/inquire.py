"""Inquiry: receipts -> open-ended questions -> the next battery.

The experimentation flywheel Casey asked for (2026-09-21): every battery
books its receipts; inquiry reads the books and SYNTHESIZES the next
round of questions. The loop is: experiment -> understand -> ask ->
experiment. v0 heuristics are deliberately small and honest; each
returned question names the experiment that would answer it.
"""

from __future__ import annotations
import json

from .bookkeeper import Bookkeeper


def _residues(book: Bookkeeper) -> list[dict]:
    out = []
    for e in book.entries:
        try:
            out.append(json.loads(e.payload))
        except Exception:
            out.append({})
    return out


def next_questions(books: dict[str, Bookkeeper]) -> list[dict]:
    """Read the fleet's books; emit (cell, question, experiment) triples."""
    qs = []
    for name, book in books.items():
        if not isinstance(book, Bookkeeper) or not book.entries:
            continue
        res = _residues(book)
        n_alarm_total = sum(1 for r in res if r.get("alarmed") == "true")
        surprises = [r["surprise"] for r in res if "surprise" in r]

        if n_alarm_total >= 3:
            qs.append({
                "cell": name,
                "question": f"{name} was alarmed {n_alarm_total} times across "
                            f"{len(res)} wakes — is the signal non-stationary "
                            f"(drift) or is the predictor underfitted?",
                "experiment": "split the book at the largest surprise; replay both "
                              "halves with K=4 and K=16; whichever half stops alarming "
                              "tells you which failure mode it was.",
            })
        elif res and n_alarm_total == 0 and len(res) >= 8:
            qs.append({
                "cell": name,
                "question": f"{name} has never alarmed in {len(res)} wakes — "
                            f"is its deadband finer than its true signal?",
                "experiment": "coarsen the hook floor one notch until the first "
                              "silent_deadband appears, then back off one notch: the "
                              "largest floor that never silences a real wake.",
            })
        if len(surprises) >= 5:
            qs.append({
                "cell": name,
                "question": f"{name}'s surprise series ({', '.join(surprises[-4:])}) — "
                            f"trending toward the floor (intuition maturing) or "
                            f"pinned above it (model class wrong)?",
                "experiment": "compare the exact means of the two halves of the "
                              "surprise series. Maturing = second < first. If pinned, "
                              "the predictor class itself is wrong — a JEPA-shaped "
                              "hole, not a tuning knob.",
            })
    return qs
