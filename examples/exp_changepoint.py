"""E4: change-point detection benchmark — disagreement vs raw surprise.

Parallel simulations: each run flips a periodic world to constant at a
random step time (witness-RNG chosen, exact). Two detectors race:
  A) raw surprise on a mean reader (classic)
  B) |ensemble surprise - imagination surprise| (the two-mirrors fabric)
Detection = first tick a detector's signal exceeds its floor after the
true step. Latency and false-alarms (pre-step triggers) are counted.
This is the 'parallel simulations' arm — N runs, independent, exact.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import (Q16, MeanPredictor, ConstReading, NgramReading,
                       DriftReading, ReadingEnsemble, WitnessRng,
                       seed_from_state, surprise)

PERIOD = [Q16(1, 10), Q16(5, 10), Q16(9, 10)]
FLOOR = Q16(15, 100)


def one_run(step_at: int, ticks: int, seed: int):
    ens = ReadingEnsemble({"mean": MeanPredictor(k=4), "persist": ConstReading(),
                           "period": NgramReading(k=3), "drift": DriftReading(k=4)})
    mean = MeanPredictor(k=4)
    det_raw = det_dis = None
    alarm_raw_pre = alarm_dis_pre = 0   # pre-step alarm TICKS (per-tick rate)
    pre_ticks = 0
    for t in range(1, ticks + 1):
        v = PERIOD[t % 3] if t < step_at else Q16(8, 10)
        pe, pi_ = ens.predict(), mean.predict()
        ens.update(v); mean.update(v)
        se = surprise(v, pe) if pe is not None else None
        si = surprise(v, pi_) if pi_ is not None else None
        if se is not None and si is not None:
            dd = se - si
            dd = Q16(abs(dd.num), dd.den)
            if t < step_at:
                pre_ticks += 1
                if se > FLOOR:
                    alarm_raw_pre += 1
                if dd > FLOOR:
                    alarm_dis_pre += 1
            else:
                if det_raw is None and se > FLOOR:
                    det_raw = t - step_at
                if det_dis is None and dd > FLOOR:
                    det_dis = t - step_at
    return det_raw, det_dis, alarm_raw_pre, alarm_dis_pre, pre_ticks


def main(runs: int = 200, ticks: int = 80):
    rng = WitnessRng(seed_from_state({"exp": "changepoint", "n": runs}))
    steps = [3 + rng._carve() % (ticks - 20) for _ in range(runs)]
    lat_raw, lat_dis = [], []
    arm_raw = arm_dis = pre_total = 0
    missed_raw = missed_dis = 0
    for i, st in enumerate(steps):
        dr, dd_, ar, ad, pt = one_run(st, ticks, i)
        arm_raw += ar; arm_dis += ad; pre_total += pt
        if dr is None:
            missed_raw += 1
        else:
            lat_raw.append(dr)
        if dd_ is None:
            missed_dis += 1
        else:
            lat_dis.append(dd_)
    def stat(xs):
        if not xs:
            return "n/a"
        m = Q16(sum(xs), len(xs))
        return f"mean {m} over {len(xs)} detections"
    print(f"E4 changepoint: {runs} runs, random step in [3,{ticks - 20}], "
          f"floor {FLOOR}")
    print(f"   raw-surprise detector : latency {stat(lat_raw)}, "
          f"missed {missed_raw}, pre-step alarms {arm_raw}/{pre_total} "
          f"ticks (= {Q16(arm_raw, max(pre_total,1))})")
    print(f"   disagreement detector : latency {stat(lat_dis)}, "
          f"missed {missed_dis}, pre-step alarms {arm_dis}/{pre_total} "
          f"ticks (= {Q16(arm_dis, max(pre_total,1))})")
    print(f"   honest read: on periodic worlds both signals sit near/above "
          f"the floor pre-step; disagreement's value is naming the split, "
          f"not speed here")


if __name__ == "__main__":
    main()
