"""The echogram: an instrument, not a snapshot.

Companion to philosophy/THE-ECHOGRAM.md (AI-Writings PR #54, Casey's
12:17 ideation). Two channels, per the essay:

  BRIGHTNESS (JEV) = the depth return itself, quantized by the VERTICAL
    knob: V=1 gate (shallow/deep), V=2 lumen, V=4, V=10 full spectrum.
  MOTION (JEV)    = surprise above floor -> '!' : did the bottom MOVE.
  COLOR (JEPA)    = which reading explained the return (per-reader exact
    error, pre-update): d=rift m=ean p=eriod P=ersist.

The world hides a ridge that DRIFTS at row 20 (wobble included) — the
array must image a moving bottom. Fidelity = per-row L1 closeness of the
normalized render to the normalized depth (imaging quality, not argmax),
so a gate is structurally unable to score what a spectrum can.

Run: python3 examples/echogram.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import (Q16, Engine, Cell, Hook, Projection, MeanPredictor,
                       ConstReading, NgramReading, DriftReading,
                       ReadingEnsemble, WitnessRng, seed_from_state)
from jev_quilt.predictor import surprise

WIDTH, ROWS = 15, 40
SHIFT_AT, SHIFT_BY = 20, 2
FLOOR = Q16(15, 100)


def ridge_col(y: int) -> int:
    return 7 + (SHIFT_BY if y >= SHIFT_AT else 0) + (1 if y % 6 == 0 else 0)


def depth(x: int, y: int, rng: WitnessRng) -> Q16:
    d = Q16(6, 2) - Q16(abs(x - ridge_col(y)), 1) / Q16(2, 1)   # 3.0 at ridge
    n = Q16(rng._carve() % 40, 400)                             # +-0.1 dyadic
    return d + n if (x + y) % 2 == 0 else d - n


def quantize(v: Q16, levels: int) -> int:
    rungs = 1 if levels <= 1 else (2 if levels == 2 else (4 if levels == 4 else 10))
    if rungs == 1:
        return 1 if v.num * 2 >= v.den * 5 else 0      # gate: ridge-flank threshold 2.5
    idx = (v.num * rungs) // (v.den * 4)               # full rational, [0,4) -> rung
    return max(0, min(rungs - 1, idx))


BRIGHT = " .:-=+*#%@"
COLORMAP = {"drift": "d", "mean": "m", "period": "p", "persist": "P"}


def main():
    eng = Engine()
    eng.register(Cell("world.row", (-1, 0)))
    cells = []
    for x in range(WIDTH):
        c = Cell(f"sonar.{x:02d}", (x, 0), input_hooks=[Hook("world.row")],
                 decision={"rule": "identity", "value": Q16(3, 1)},
                 predictor=ReadingEnsemble({
                     "mean": MeanPredictor(k=4), "persist": ConstReading(),
                     "period": NgramReading(k=3), "drift": DriftReading(k=4)}),
                 surprise_floor=FLOOR,
                 outputs=[Projection(f"felt.{x:02d}", "q16")])
        eng.register(c)
        cells.append(c)

    def color_of(cell, v: Q16) -> str:
        best, bn = "?", None
        for name, r in sorted(cell.predictor.readings.items()):
            p = r.predict()
            e = abs((v - p).num) if p is not None else 10 ** 9
            if bn is None or e < bn:
                best, bn = COLORMAP.get(name, "?"), e
        return best

    def sweep(levels: int, stagger: int, tag: str, seed: int):
        for c in cells:
            c.predictor = ReadingEnsemble({
                "mean": MeanPredictor(k=4), "persist": ConstReading(),
                "period": NgramReading(k=3), "drift": DriftReading(k=4)})
        rng = WitnessRng(seed)
        rungs = 1 if levels <= 1 else (2 if levels == 2 else (4 if levels == 4 else 10))
        bright_rows, color_rows, alarms_front = [], [], 0
        err_sum = 0.0
        for y in range(ROWS):
            vals = [depth(x, y, rng) for x in range(WIDTH)]
            rung = []
            for x, c in enumerate(cells):
                on = (not stagger) or ((y + x) % stagger == 0)
                c.decision = {"rule": "identity", "value": vals[x]} if on else None
            eng.emit("world.row", {"mag": Q16(1)}, state={"y": y})
            brow, crow = [], []
            for x, c in enumerate(cells):
                rung.append(quantize(vals[x], levels))
                last = eng.books[f"sonar.{x:02d}"].entries[-1] \
                    if eng.books[f"sonar.{x:02d}"].entries else None
                alarmed = last and '"alarmed": "true"' in last.payload
                if alarmed and SHIFT_AT - 2 <= y <= SHIFT_AT + 4:
                    alarms_front += 1
                brow.append(BRIGHT[rung[-1]])
                crow.append(color_of(c, vals[x]) if c.decision else ".")
            bright_rows.append("".join(brow))
            color_rows.append("".join(crow))
            # imaging fidelity: normalized render vs normalized depth (L1)
            dmin = min(v.num / v.den for v in vals)
            dmax = max(v.num / v.den for v in vals)
            for x in range(WIDTH):
                truth = (vals[x].num / vals[x].den - dmin) / max(dmax - dmin, 1e-9)
                err_sum += abs(rung[x] / (rungs - 1 or 1) - truth)
        fid = 1.0 - err_sum / (ROWS * WIDTH)
        print(f"\n== {tag}: imaging fidelity {fid:.3f} "
              f"(motion alarms at the front: {alarms_front}) ==")
        mark = ridge_col(SHIFT_AT + 2)
        for i in range(0, ROWS, 4):
            flag = " <R" if i >= SHIFT_AT - 2 else ""
            print(f"   |{bright_rows[i]}| |{color_rows[i]}|{flag}")
        return fid

    print(f"ECHORGRAM — ridge at col ~7, drifts +{SHIFT_BY} at row {SHIFT_AT}")
    base = seed_from_state({"instrument": "echogram"})
    r = {}
    r["gate   /sync  "] = sweep(1, 0, "V=1 gate, synchronized", base + 1)
    r["lumen  /sync  "] = sweep(2, 0, "V=2 lumen, synchronized", base + 2)
    r["V4     /sync  "] = sweep(4, 0, "V=4, synchronized", base + 4)
    r["spectrm/sync  "] = sweep(10, 0, "V=10 spectrum, synchronized", base + 10)
    r["spectrm/fugue3"] = sweep(10, 3, "V=10 spectrum, fugue stagger=3", base + 13)
    r["gate   /rerun "] = sweep(1, 0, "V=1 gate, reseeded (per-sweep worlds)", base + 1)
    print("\n== fidelity table (1 - mean L1 vs true depth) ==")
    for k, v in r.items():
        print(f"   {k}  {v:.3f}")
    ok = all(b.verify() for b in eng.books.values())
    n = sum(len(b.entries) for b in eng.books.values())
    print(f"receipts: {n}; chain verifies: {ok}")


if __name__ == "__main__":
    main()
