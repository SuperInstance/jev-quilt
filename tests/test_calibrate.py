"""Calibrated floor: the bored-middle / rough-seas failure, and its fix.

A fixed alarm floor set generous enough for 'normal' conditions sleeps through a
small anomaly hiding in a long calm. On a boat that is the rogue ripple in a flat
sea you never turn to look at. The calibrated floor tightens in the calm, so the
small real thing still clears it — without crying wolf on the ordinary chop.
Everything stays exact ℚ so it runs the same on deck as on a datacenter.
"""
from jev_quilt import Q16, surprise, alarm
from jev_quilt.calibrate import CalibratedFloor, alarm_calibrated


def _s(x_num, den=100):
    """A surprise of x_num/den, built from an outcome vs a zero prediction."""
    return Q16(x_num, den), Q16(0)   # (outcome, predicted) → surprise = x_num/den


import unittest


class TestConverted(unittest.TestCase):
    def test_floor_is_exact_not_close(self):
        cal = CalibratedFloor(k=8, slack=Q16(5, 2))
        for _ in range(8):
            cal.update(Q16(1, 100))            # a flat, calm sea
        # mean 1/100 × slack 5/2 = 1/40, exactly
        assert cal.floor() == Q16(1, 40)


    def test_warmup_is_honest(self):
        cal = CalibratedFloor(k=8)
        cal.update(Q16(1, 100))
        assert cal.floor() is None             # a floor before evidence is a lie
        out, pred = _s(50)
        assert alarm_calibrated(out, pred, cal, learn=False) is False


    def test_bored_middle_the_fixed_floor_sleeps_through_it(self):
        # a long calm: ambient surprise ~0.01
        cal = CalibratedFloor(k=8, slack=Q16(5, 2))
        for _ in range(8):
            cal.update(Q16(1, 100))
        # a small anomaly appears: surprise 0.03
        out, pred = _s(3)                       # 0.03
        fixed_floor = Q16(5, 100)              # 0.05 — a floor tuned for 'normal' seas
        assert alarm(out, pred, fixed_floor) is False        # FIXED floor sleeps through it
        assert alarm_calibrated(out, pred, cal, learn=False) is True   # calibrated catches it
        # because the calibrated floor is 1/40 = 0.025, and 0.03 > 0.025


    def test_no_alarm_storm_on_the_ordinary_chop(self):
        cal = CalibratedFloor(k=8, slack=Q16(5, 2))
        for _ in range(8):
            cal.update(Q16(1, 100))
        out, pred = _s(1)                       # 0.01, an ordinary calm sample
        assert alarm_calibrated(out, pred, cal, learn=False) is False   # 0.01 < 0.025


    def test_floor_relaxes_after_a_spike_no_permanent_deafness(self):
        cal = CalibratedFloor(k=8, slack=Q16(5, 2))
        for _ in range(8):
            cal.update(Q16(1, 100))
        before = cal.floor()
        cal.update(Q16(50, 100))               # one big spike enters the window
        raised = cal.floor()
        assert raised > before                  # the floor rises a little...
        for _ in range(8):                      # ...then a calm run flushes the spike out
            cal.update(Q16(1, 100))
        assert cal.floor() == before            # back to sensitive — the sea forgets


    def test_inexact_k_and_float_slack_refused(self):
        _cm = self.assertRaises(ValueError)
        try:
            CalibratedFloor(k=3)
        except ValueError as _e:
            self.assertIn("exact family", str(_e))
        else:
            self.fail("expected ValueError")
        with self.assertRaises(TypeError):
            CalibratedFloor(slack=2.5)          # a float where identity matters


    def test_deterministic(self):
        a = CalibratedFloor(k=8); b = CalibratedFloor(k=8)
        for _ in range(10):
            a.update(Q16(2, 100)); b.update(Q16(2, 100))
        assert a.floor() == b.floor()
