"""Tests for jev_quilt.polyformalism — the substrate's own canary surface.

Before this audit the fleet canary value (tests/test_fleet_canary.py)
was only checkable via a local reimplementation inside that test. This
module exposes fleet_canary() from the substrate itself; these tests
pin its contract so the surface cannot silently rot.
"""

import unittest

from jev_quilt.bookkeeper import fnv1a
from jev_quilt.polyformalism import (
    CANARY_STRING, CANARY_VALUE, _CANARY_HEX, fleet_canary,
)


class TestPolyformalismCanary(unittest.TestCase):

    def test_pinned_value_matches_fleet_canary_test(self):
        self.assertEqual(CANARY_VALUE, 0x024a555471370b18d)
        self.assertEqual(fleet_canary(), "0x024a555471370b18d")

    def test_canary_computed_from_substrate_fnv1a(self):
        live = fnv1a(CANARY_STRING.encode("utf-8"))
        self.assertEqual(live, CANARY_VALUE)
        self.assertEqual(fleet_canary(), f"0x{live:017x}")

    def test_canary_hex_shape(self):
        h = fleet_canary()
        self.assertTrue(h.startswith("0x0"))
        self.assertEqual(len(h), len("0x") + 17)
        int(h, 16)  # parses


if __name__ == "__main__":
    unittest.main()
