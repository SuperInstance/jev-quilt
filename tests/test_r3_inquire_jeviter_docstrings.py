"""R3 docstring-vs-behavior pins — inquire + jeviter lane.

The R3 sweep of inquire.py and jeviter.py found one silent-coercion
hazard and one implicit cross-module contract:

* `JevIterator` carries readings on the exact Q16 integer lattice, and
  any non-integer value silently coerces to Q16(0, 1) — zero. The class
  docstring named neither the lattice nor the coercion, and a fully
  fractional reading degrades further: the sum-normalization guard
  (`total.num > 0`) skips, so the all-zero belief is seeded/compared as
  zeros. The docstring now says so; these pins keep it said.
* `inquire.next_questions` counts alarms with `r.get("alarmed") ==
  "true"` — a STRING match that is only correct because engine.py
  happens to book the payload that way. If the producer ever switches to
  a JSON boolean (`true`, not `"true"`), every alarm heuristic in
  inquiry silently reads zero. The contract is pinned end-to-end: book
  exactly what engine books, assert the alarm question fires; book the
  boolean form, assert the drift would be caught (the heuristic does not
  count it — documented behavior, not a fix, per the audit's honest
  scope).
"""

import inspect
import json

from jev_quilt import jeviter as jeviter_mod
from jev_quilt.bookkeeper import Bookkeeper
from jev_quilt.inquire import next_questions
from jev_quilt.jeviter import JevIterator
from jev_quilt.q16 import Q16


def test_jeviter_docstring_pins_fractional_coercion():
    """R3 audit pin: the Q16 lattice coercion must stay documented."""
    doc = inspect.getsource(jeviter_mod.JevIterator)
    assert "integer lattice" in doc
    assert "Q16(0, 1)" in doc
    assert "silently coerces" in doc


def test_jeviter_fractional_reading_becomes_zero_belief():
    """A fully fractional reading seeds an all-zero belief, un-normalized."""
    keeper = Bookkeeper("r3-frac")
    it = JevIterator([{"a": 1.5, "b": 2.5}], gate=_Gate(), keeper=keeper)
    events = list(it)
    assert events == []
    seeded = [e for e in keeper.entries if e.decision_kind == "seed"]
    assert len(seeded) == 1
    # The seeded belief is zeros: coercion, then normalization skipped.
    assert it.last == {"a": Q16(0, 1), "b": Q16(0, 1)}


def test_inquire_counts_engine_string_alarm_form():
    """The alarm heuristic sees exactly what engine.py books (string 'true')."""
    book = Bookkeeper("r3-alarm")
    for _ in range(3):
        book.book({}, {}, "decided", {"alarmed": "true"})
    qs = next_questions({"r3-alarm": book})
    assert any("alarmed 3 times" in q["question"] for q in qs), qs


def test_inquire_boolean_alarm_form_is_documented_drift():
    """JSON boolean true (not the string) is NOT counted — pinned drift site."""
    book = Bookkeeper("r3-bool")
    for _ in range(3):
        book.book({}, {}, "decided",
                  json.loads('{"alarmed": true}'))
    qs = next_questions({"r3-bool": book})
    assert not any("alarmed 3 times" in q["question"] for q in qs)


class _Gate:
    """Minimal gate: admit nothing — the coercion test only needs the seed."""

    def admit(self, last, reading):
        return False, 0.0, 1.0
