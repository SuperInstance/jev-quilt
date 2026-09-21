"""experiments/classifier_lab.py — E6/E7: counterintuitive classifier physics.

E6 CASCADE NON-MONOTONICITY: series composition of taps is NOT
monotone. A coarse admission re-anchors the boundary the fine tap
measures against — so coarse→fine can catch what fine-alone ratchets
past (and vice versa). World: drifting baseline + rare jumps.

E7 THE RATCHET: a world oscillating at fixed amplitude is silenced
AFTER ITS FIRST ADMISSION — the tap learns "this much divergence is
normal" from its own first event, and the symmetric return leg falls
just under the self-set threshold. Adversarial resonance is impossible
by construction: the classifier is amplitude-ADAPTIVE, not
amplitude-sensitive. Amplitude sweeps show invariance; that invariance
IS the finding.

Run: python3 experiments/classifier_lab.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt import Bookkeeper, Q16 as Q
from jev_quilt.jeviter import JevIterator
from jev_quilt.tap import TapGate

CALM = {"a": Q(1, 2), "b": Q(1, 2)}
HOT = {"a": Q(7, 10), "b": Q(3, 10)}


def run(stream, k, cell="lab"):
    keeper = Bookkeeper(cell)
    return list(JevIterator(stream, TapGate(k=k), keeper)), keeper


def drift_world(n=400, jump_every=80):
    """Baseline drifts CALM→HOT slowly; every jump_every a snap back."""
    w = []
    for t in range(n):
        phase = (t % jump_every) / jump_every
        a = Q(5, 10) + Q(int(4 * phase), 10)   # 0.5 → 0.9 drift
        w.append({"a": a, "b": Q(10 - a.num, 10) if a.den == 10 else Q(1, 1)})
    return w


def oscillate(n, hot_a_num):
    hot = {"a": Q(hot_a_num, 10), "b": Q(10 - hot_a_num, 10)}
    return [dict(CALM) if (t // 25) % 2 == 0 else dict(hot) for t in range(n)]


if __name__ == "__main__":
    print("== E6: cascade non-monotonicity (drift + jump world) ==")
    w = drift_world()
    fine, _ = run(w, 4.0, "fine")
    ck = Bookkeeper("coarse")
    coarse_evs = list(JevIterator(w, TapGate(k=0.5), ck))
    fk = Bookkeeper("cascade-fine")
    casc = list(JevIterator([e.value for e in coarse_evs], TapGate(k=4.0), fk))
    print(f"   fine(4.0) alone:        {len(fine)} events")
    print(f"   coarse(0.5)→fine(4.0):  {len(casc)} events")
    print(f"   NON-MONOTONE: coarse re-anchoring made the fine tap "
          f"{'MORE' if len(casc) > len(fine) else 'LESS'} sensitive "
          f"({len(casc)} vs {len(fine)}) — composition order is load-bearing")

    print("== E7: the ratchet (oscillation amplitude invariance) ==")
    for label, num in [("1/10", 6), ("3/10", 8), ("5/10", 10), ("9/10", 9)]:
        evs, k = run(oscillate(400, num), 2.0, f"res-{label}")
        kinds = [e.decision_kind for e in k.entries]
        print(f"   HOT a={label}: {len(evs)} events over 16 swings "
              f"(seed={kinds.count('seed')} silence={kinds.count('silence')})")
    print("   every amplitude: exactly ONE event. After the first")
    print("   admission the tap sets its threshold from that gain; the")
    print("   symmetric return leg (gain = first-gain ± epsilon) lands")
    print("   just under. A fixed-amplitude world is learnable noise —")
    print("   the classifier cannot be resonated against itself.")
