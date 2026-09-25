"""Property suite: jev_quilt/cell.py (typed decision surface).

Docstring claims pinned here (quoted in the property comments):
  - module: "Law 1: identity never floats (coord is integer (k, s))."
  - module: "Law 5: viability is binary; above the floor deltas are graded."
  - Cell.viability_floor: "default = decisions carry confidence
    and confidence > 0 is viable."
  - Cell.__post_init__ (code): unknown backend -> ValueError.

Cell carries no version counter of its own; the version counter behind
`cell.bookkeeper = True` is Bookkeeper._tick, so monotonicity of the
ledger a cell writes to is pinned here as the cell-side counter law.
"""

from __future__ import annotations

import dataclasses
import sys
from types import SimpleNamespace

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from jev_quilt.cell import Cell, Hook, Projection, DEADBAND
from jev_quilt.bookkeeper import Bookkeeper

from tests.property_runner import run_property, DEFAULT_N


# ---------------------------------------------------------------- generators

def _good_coord(rng):
    return (rng.randint(-(1 << 31), 1 << 31), rng.randint(0, 1 << 16))


def _bad_coord(rng):
    kind = rng.randrange(4)
    if kind == 0:
        return (rng.random(), rng.randint(0, 10))          # float member
    if kind == 1:
        return (rng.randint(0, 10),)                        # too short
    if kind == 2:
        return [rng.randint(0, 10), rng.randint(0, 10)]     # list, not tuple
    return (rng.randint(0, 10), rng.randint(0, 10), rng.randint(0, 10))  # too long


# ---------------------------------------------------------------- properties

def prop_coord_accepts_integer_pairs(rng):
    """Law 1: "identity never floats (coord is integer (k, s))" — the
    accepting half: any 2-tuple of ints must construct."""
    for _ in range(20):
        k, s = _good_coord(rng)
        c = Cell(name="p", coord=(k, s))
        if c.coord != (k, s):
            return False, {"coord": (k, s), "stored": c.coord}
    return True, None


def prop_coord_rejects_non_integer_identity(rng):
    """Law 1 (the rejecting half): floats, wrong arity, non-tuple all raise."""
    for _ in range(20):
        bad = _bad_coord(rng)
        try:
            Cell(name="p", coord=bad)
        except TypeError:
            continue
        return False, {"bad_coord": bad, "accepted": True}
    return True, None


def prop_backend_allowlist(rng):
    """__post_init__: backend must be one of auto|q16|openjev-local|typesafe-api."""
    known = ("auto", "q16", "openjev-local", "typesafe-api")
    for b in known:
        Cell(name="p", coord=(0, 0), backend=b)
    for _ in range(20):
        junk = "".join(rng.choice("abcdefghijklmnopqrstuvwxyz_-") for _ in range(rng.randint(1, 12)))
        if junk in known:
            continue
        try:
            Cell(name="p", coord=(0, 0), backend=junk)
        except ValueError:
            continue
        return False, {"backend": junk, "accepted": True}
    return True, None


def prop_viability_floor_confidence_rule(rng):
    """viability_floor docstring: "default = decisions carry confidence
    and confidence > 0 is viable."  No confidence attr -> viable;
    confidence > 0 -> viable; confidence <= 0 -> not viable."""
    for _ in range(30):
        cell = Cell(name="p", coord=(0, 0))
        mode = rng.randrange(3)
        if mode == 0:
            d = SimpleNamespace()                      # no confidence attr
            if cell.viability_floor(d) is not True:
                return False, {"mode": "no-attr", "got": cell.viability_floor(d)}
        elif mode == 1:
            conf = rng.choice([rng.random() + 1e-9, 1e-12, 1.0])
            d = SimpleNamespace(confidence=conf)
            if cell.viability_floor(d) is not True:
                return False, {"mode": "positive", "conf": conf}
        else:
            conf = rng.choice([0.0, -rng.random() - 1e-9])
            d = SimpleNamespace(confidence=conf)
            if cell.viability_floor(d) is not False:
                return False, {"mode": "nonpositive", "conf": conf,
                               "got": cell.viability_floor(d)}
    return True, None


def prop_hook_projection_frozen_and_roundtrip(rng):
    """Hook/Projection are frozen dataclasses: construction is idempotent
    (equal inputs -> equal value), and an asdict round-trip reconstructs
    an equal value when no callable predicate is present (dataclasses.asdict
    cannot carry the `when` callable, so this pins the no-predicate path)."""
    for _ in range(20):
        src = f"src{rng.randint(0, 10)}"
        h1 = Hook(source=src, on="delta", floor=DEADBAND)
        h2 = Hook(source=src, on="delta", floor=DEADBAND)
        if h1 != h2 or hash(h1) != hash(h2):
            return False, {"hook": src}
        h3 = Hook(**dataclasses.asdict(h1))
        if h3 != h1:
            return False, {"hook_roundtrip": dataclasses.asdict(h1)}
        to, ty = f"cell{rng.randint(0, 5)}", rng.choice(["json", "coefficient", "choice", "bytes"])
        p1 = Projection(to=to, as_type=ty)
        p2 = Projection(**dataclasses.asdict(p1))
        if p1 != p2:
            return False, {"projection_roundtrip": dataclasses.asdict(p1)}
    return True, None


def prop_frozen_dataclass_rejects_mutation(rng):
    """frozen=True: setattr on Hook/Projection must raise FrozenInstanceError
    (an AttributeError subclass) — hooks are immutable subscriptions."""
    for obj in (Hook(source="s"), Projection(to="t", as_type="json")):
        try:
            obj.new_field = 1
        except AttributeError:
            continue
        return False, {"mutated": obj}
    return True, None


def prop_ledger_version_counter_monotonic(rng):
    """The version counter behind a cell's ledger: Bookkeeper ticks are
    strictly increasing from 1 and Bookkeeper.verify() (ticks == 1..N)
    holds for any random book a cell could write."""
    for _ in range(10):
        bk = Bookkeeper(f"c{rng.randint(0, 99)}")
        n = rng.randint(1, 40)
        for i in range(n):
            bk.book({"v": rng.randint(0, 10 ** 6)}, {"d": rng.randint(0, 10 ** 6)},
                    rng.choice(["a", "b", "c"]), {"p": rng.randint(0, 100)})
        if [e.tick for e in bk.entries] != list(range(1, n + 1)):
            return False, {"n": n, "ticks": [e.tick for e in bk.entries][:8]}
        if not bk.verify():
            return False, {"n": n, "verify": False}
        if bk.wake_state()["booked_ticks"] != n:
            return False, {"n": n, "wake": bk.wake_state()}
    return True, None


def prop_replay_is_deterministic(rng):
    """Law 4 (bookkeeper.py): "replay ≡ live" — replay() is a pure
    function of the entries: two books built with the same operations
    replay to the same chain hash, and chain is a 64-hex string."""
    for _ in range(5):
        bk = Bookkeeper("p")
        n = rng.randint(1, 20)
        ops = [({"v": i}, {"d": i}, "k", {"p": i}) for i in range(n)]
        for state, delta, kind, payload in ops:
            bk.book(state, delta, kind, payload)
        again = Bookkeeper("p")
        for state, delta, kind, payload in ops:
            again.book(state, delta, kind, payload)
        if bk.replay() != again.replay():
            return False, {"divergence": True}
        if len(bk.replay()) != 64:
            return False, {"chain": bk.replay()[:16]}
    return True, None


PROPERTIES = [
    prop_coord_accepts_integer_pairs,
    prop_coord_rejects_non_integer_identity,
    prop_backend_allowlist,
    prop_viability_floor_confidence_rule,
    prop_hook_projection_frozen_and_roundtrip,
    prop_frozen_dataclass_rejects_mutation,
    prop_ledger_version_counter_monotonic,
    prop_replay_is_deterministic,
]


# ------------------------------------------------------- unittest wiring

import unittest  # noqa: E402


class TestCellProperties(unittest.TestCase):
    def _check(self, fn):
        ok, cx = run_property(fn)
        self.assertTrue(ok, f"property {fn.__qualname__} failed: {cx!r}")

    def test_coord_law_accept(self): self._check(prop_coord_accepts_integer_pairs)
    def test_coord_law_reject(self): self._check(prop_coord_rejects_non_integer_identity)
    def test_backend_allowlist(self): self._check(prop_backend_allowlist)
    def test_viability_floor(self): self._check(prop_viability_floor_confidence_rule)
    def test_hook_projection_roundtrip(self): self._check(prop_hook_projection_frozen_and_roundtrip)
    def test_frozen_rejects_mutation(self): self._check(prop_frozen_dataclass_rejects_mutation)
    def test_ledger_version_counter(self): self._check(prop_ledger_version_counter_monotonic)
    def test_replay_deterministic(self): self._check(prop_replay_is_deterministic)


if __name__ == "__main__":
    unittest.main()
