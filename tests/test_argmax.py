from jev_quilt.backends import Q16Backend


import unittest


class TestConverted(unittest.TestCase):
    def test_argmax_picks_highest_weight(self):
        d = Q16Backend().decide({"rule": "argmax", "options": {"a": 10, "b": 70, "c": 20}}, None)
        assert d.kind == "choice"
        assert d.value == "b"
        assert abs(d.probabilities["b"] - 0.7) < 1e-12
        assert abs(d.probabilities["a"] - 0.1) < 1e-12


    def test_argmax_empty_options_refuses(self):
        _cm = self.assertRaises(ValueError)
        try:
            Q16Backend().decide({"rule": "argmax", "options": {}}, None)
        except ValueError as _e:
            self.assertIn("empty", str(_e))
        else:
            self.fail("expected ValueError")


    def test_argmax_zero_total_refuses(self):
        _cm = self.assertRaises(ValueError)
        try:
            Q16Backend().decide({"rule": "argmax", "options": {"a": 0, "b": 0}}, None)
        except ValueError as _e:
            self.assertIn("positive", str(_e))
        else:
            self.fail("expected ValueError")
