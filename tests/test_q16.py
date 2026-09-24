import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))



from jev_quilt.q16 import Q16, commensurate, SCALE


import unittest


class TestConverted(unittest.TestCase):
    def test_q16_exact_decimal(self):
        assert Q16.from_float(0.1) + Q16.from_float(0.2) == Q16.from_float(0.3)


    def test_q16_rejects_non_dyadic5(self):
        with self.assertRaises(ValueError):
            Q16.from_float(1 / 3)


    def test_q16_reduction(self):
        assert Q16(2, 4) == Q16(1, 2)
        assert Q16(-2, -4) == Q16(1, 2)


    def test_q16_zero_denominator(self):
        with self.assertRaises(ZeroDivisionError):
            Q16(1, 0)


    def test_q16_arithmetic_exact(self):
        a = Q16(1, 3) if False else Q16(3, 10)   # 0.3
        b = Q16(7, 10)                            # 0.7
        assert (a + b) == Q16(1, 1)
        assert (a * b) == Q16(21, 100)


    def test_commensurate_true(self):
        assert commensurate(Q16.from_float(0.5), Q16.from_float(0.25))
        assert commensurate(Q16(1, 4), Q16(1, 2))


    def test_commensurate_ternary_ghost(self):
        # 1/3 vs 1: not on a common decimal lattice → False
        assert not commensurate(Q16(1, 3), Q16(1, 1))


    def test_commensurate_zero(self):
        assert commensurate(Q16(0), Q16(5))
        assert not commensurate(Q16(1), Q16(0))
