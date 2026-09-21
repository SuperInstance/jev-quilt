"""E: rough seas — the ripple in the flat calm a fixed floor sleeps through.

The bored-middle failure, on the water. A long flat calm (tiny surprises), then
one small anomaly — the rogue ripple. A FIXED alarm floor tuned for normal seas
misses it; the calibrated floor, which tightens in the calm, catches it — without
crying wolf on the ordinary chop. Everything is exact ℚ, so the toy on the table
and the gear on the boat run the same law.

Run:  python examples/rough_seas.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import Q16, surprise, alarm
from jev_quilt.calibrate import CalibratedFloor, alarm_calibrated

CALM = Q16(1, 100)          # ambient surprise on a flat sea: 0.01
RIPPLE = Q16(3, 100)        # the small real anomaly: 0.03
FIXED_FLOOR = Q16(5, 100)   # a floor a person would pick for "normal" seas: 0.05


def sea():
    """80 beats of calm, one ripple at beat 60, calm again."""
    for t in range(80):
        yield RIPPLE if t == 60 else CALM


def main():
    cal = CalibratedFloor(k=8, slack=Q16(5, 2))     # → floor settles at 0.01×2.5 = 0.025
    fixed_hits, cal_hits, fixed_false, cal_false = 0, 0, 0, 0
    ripple_seen_by = {"fixed": False, "calibrated": False}

    for t, s in enumerate(sea()):
        out, pred = s, Q16(0)                        # surprise == s
        f_alarm = alarm(out, pred, FIXED_FLOOR)
        c_alarm = alarm_calibrated(out, pred, cal)   # learns as it goes
        if t == 60:                                  # the ripple
            ripple_seen_by["fixed"] = f_alarm
            ripple_seen_by["calibrated"] = c_alarm
        else:                                        # the ordinary calm
            fixed_false += f_alarm
            cal_false += c_alarm
        fixed_hits += f_alarm
        cal_hits += c_alarm

    print("rough seas — one small ripple at beat 60")
    print(f"  fixed floor {FIXED_FLOOR}:  ripple caught = {ripple_seen_by['fixed']}   "
          f"false alarms in calm = {fixed_false}")
    print(f"  calibrated floor (now {cal.floor()}):  ripple caught = {ripple_seen_by['calibrated']}   "
          f"false alarms in calm = {cal_false}")
    print()
    if ripple_seen_by["calibrated"] and not ripple_seen_by["fixed"]:
        print("  → the calibrated floor caught the ripple the fixed floor slept through,")
        print("    and never cried wolf on the ordinary chop. Legality is not calibration.")
    return ripple_seen_by


if __name__ == "__main__":
    main()
