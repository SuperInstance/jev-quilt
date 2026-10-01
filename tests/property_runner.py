"""Minimal stdlib-only property-based test harness (round R2).

Each property is a callable::

    def prop_something(rng: random.Random) -> tuple[bool, dict | None]:
        ...
        return ok, counterexample_or_None

The runner executes N iterations per property with a ``random.Random``
seeded deterministically from a master seed plus the property's qualified
name (str seeding hashes via sha512, so it is stable across processes and
immune to PYTHONHASHSEED). On failure it prints the counterexample dict
returned by the property. ``run_suite`` returns the list of failures so a
``__main__`` can exit non-zero when any property fails.

Determinism contract: same master seed -> same per-property seed ->
same random sequence -> same verdicts and the same counterexample.

No third-party deps (Hypothesis is deliberately NOT used — this package
is stdlib-only and the properties must run in the same `python3 -m
unittest discover` pass as everything else).
"""

from __future__ import annotations

import random
import sys

DEFAULT_N = 200
DEFAULT_MASTER_SEED = "jev-quilt-r2-properties-v1"


def run_property(fn, n=DEFAULT_N, master_seed=DEFAULT_MASTER_SEED):
    """Run ``fn(rng)`` n times. Returns (ok, counterexample_dict|None)."""
    name = getattr(fn, "__qualname__", repr(fn))
    rng = random.Random(f"{master_seed}:{name}")
    for i in range(n):
        ok, cx = fn(rng)
        if not ok:
            cx = dict(cx or {})
            cx.setdefault("property", name)
            cx.setdefault("iteration", i)
            cx.setdefault("n", n)
            return False, cx
    return True, None


def run_suite(properties, n=DEFAULT_N, master_seed=DEFAULT_MASTER_SEED, out=None):
    """Run every property in `properties`; print status lines to `out`.

    Returns a list of (property_name, counterexample) for the failures.
    """
    out = out if out is not None else sys.stdout
    failures = []
    for fn in properties:
        name = getattr(fn, "__qualname__", repr(fn))
        ok, cx = run_property(fn, n=n, master_seed=master_seed)
        if ok:
            print(f"[PASS] {name} (N={n}, seed={master_seed!r})", file=out)
        else:
            print(f"[FAIL] {name} (N={n}, seed={master_seed!r})", file=out)
            print(f"       counterexample: {cx!r}", file=out)
            failures.append((name, cx))
    return failures


def _load_suites():
    """Import the property suites, tolerating both `python3 tests/property_runner.py`
    (sys.path[0] == tests/) and `python3 -m tests.property_runner` from repo root."""
    mods = []
    for name in (
        "test_props_cell",
        "test_props_fold",
        "test_props_q16",
        "test_props_witness_rng",
        "test_props_predictor",
    ):
        try:
            mod = __import__(name)
        except ImportError:
            mod = __import__(f"tests.{name}", fromlist=[name])
        mods.append(mod)
    return mods


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    n = DEFAULT_N
    master_seed = DEFAULT_MASTER_SEED
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--n":
            n = int(argv[i + 1]); i += 2
        elif a == "--seed":
            master_seed = argv[i + 1]; i += 2
        else:
            i += 1
    properties = []
    for mod in _load_suites():
        properties.extend(getattr(mod, "PROPERTIES", ()))
    failures = run_suite(properties, n=n, master_seed=master_seed)
    total = len(properties)
    print(f"--- {total - len(failures)}/{total} properties passed "
          f"(N={n}, seed={master_seed!r}) ---")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
