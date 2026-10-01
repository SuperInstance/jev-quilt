#!/usr/bin/env python3
"""R7 — performance regression harness. Times hot ops, enforces budgets.
Stdlib only. Budgets are generous (CI-noisy-room); they pin ORDER OF MAGNITUDE,
not micro-benchmarks. FAIL = >3x budget, so flakes don't false-positive.
Run: python3 tests/r7_perf_harness.py  (exit non-zero on breach)"""
import json, os, sys, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jev_quilt.bookkeeper import fnv1a as fnv1a_64

FLEET_CANARY_STRING = "café Δ 日本語"
FLEET_CANARY_VALUE = 0x024a555471370b18d

BUDGETS_MS = {  # calibrated on-node 2026-09-25; CI gets 3x headroom
    "fnv1a_64_x10k":      {"budget_ms": 250,  "note": "10k single hashes ~21us/call, call-overhead bound"},
    "fnv1a_batch_100k":   {"budget_ms": 60,   "note": "one 100k-byte batch"},
    "canary_call_x1k":    {"budget_ms": 20,   "note": "1k canary format calls"},
}

def bench(name, fn):
    t0 = time.perf_counter()
    fn()
    ms = (time.perf_counter() - t0) * 1000
    b = BUDGETS_MS[name]["budget_ms"]
    ok = ms <= b * 3
    print(f"  {'PASS' if ok else 'FAIL'} {name}: {ms:.1f}ms (budget {b}ms, fail >{b*3:.0f}ms)")
    return {"name": name, "ms": round(ms, 2), "budget_ms": b, "ok": ok}

def main():
    results = []
    results.append(bench("fnv1a_64_x10k", lambda: [fnv1a_64(FLEET_CANARY_STRING.encode()) for _ in range(10_000)]))
    data = FLEET_CANARY_STRING.encode() * 2000  # ~86KB
    results.append(bench("fnv1a_batch_100k", lambda: fnv1a_64(data)))
    results.append(bench("canary_call_x1k",
        lambda: [format(FLEET_CANARY_VALUE, "#019x") for _ in range(1_000)]))

    bad = [r for r in results if not r["ok"]]
    print(f"\n{'BREACH' if bad else 'ALL WITHIN BUDGET'} — {len(results)-len(bad)}/{len(results)}")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
