from jev_quilt import Q16, MeanPredictor, surprise, alarm
from jev_quilt.predictor import Predictor


import unittest


class TestConverted(unittest.TestCase):
    def test_mean_is_exact_not_close(self):
        p = MeanPredictor(k=4)
        for v in (Q16(1, 10), Q16(2, 10), Q16(3, 10), Q16(4, 10)):
            p.update(v)
        assert p.predict() == Q16(1, 4)  # exactly 0.25, not 0.24999...


    def test_warmup_returns_none_honestly(self):
        p = MeanPredictor(k=4)
        p.update(Q16(1, 10))
        assert p.predict() is None  # a feeling before evidence is a lie


    def test_inexact_k_refused(self):
        _cm = self.assertRaises(ValueError)
        try:
            MeanPredictor(k=3)  # 1/3 not representable in Z[1/10^6]
        except ValueError as _e:
            self.assertIn("exact family", str(_e))
        else:
            self.fail("expected ValueError")


    def test_surprise_exact_and_alarm_binary(self):
        out = Q16(7, 10)
        pred = Q16(1, 4)
        s = surprise(out, pred)
        assert s == Q16(9, 20)  # 0.7 - 0.25 = 0.45 exactly
        assert alarm(out, pred, Q16(1, 2)) is False   # binary: below floor
        assert alarm(out, pred, Q16(2, 5)) is True    # 0.45 > 0.4, exact floor
        # (an earlier draft of this test used Q16(1,3) as the floor — inexact
        # in Z[1/10^6]; the predictor refuses such K, and floors should come
        # from the exact family too. Seam documented, not hidden.)


    def test_intuition_matures_after_a_step(self):
        p = MeanPredictor(k=4)
        for _ in range(4):
            p.update(Q16(1, 10))          # old regime 0.1 — window fills
        alarms = []
        for _ in range(5):
            pred = p.predict()
            out = Q16(7, 10)              # new regime 0.7
            alarms.append(alarm(out, pred, Q16(15, 100)))
            p.update(out)
        # step is felt for exactly 3 beats; then the window is full of the
        # new regime and the elephant is calm — shorter delays, more confidence
        assert alarms == [True, True, True, False, False]
