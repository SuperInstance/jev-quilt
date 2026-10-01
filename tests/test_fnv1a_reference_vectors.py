"""R8 pin: bind the LIBRARY fnv1a (jev_quilt.bookkeeper) to external
reference vectors — not to a local reimplementation.

Why this test exists (Goodhart red-team R8):
  tests/test_fleet_canary.py reimplements fnv1a_64 LOCALLY and asserts
  against a constant also defined in that file. That only proves the
  test file is self-consistent: bookkeeper.fnv1a could be gutted (or
  made to return a constant) and the fleet-canary unit test would stay
  green. The only binding was the CI "canary check" step — which
  imports jev_quilt.polyformalism, a module that DOES NOT EXIST on
  main (as of 2026-09-25, every recent main CI run fails at that step).

  This test pins the REAL library implementation to vectors published
  outside this repo (http://www.isthe.com/chongo/tech/comp/fnv/ —
  FNV-1a 64-bit: "" -> 0xcbf29ce484222325, "a" -> 0xaf63dc4c8601ec8c,
  "foobar" -> 0x85944171f73967e8) plus the fleet canary string, and
  includes differential checks that ANY constant-return hack fails.
"""
import unittest

from jev_quilt.bookkeeper import fnv1a

FLEET_CANARY_STRING = "café Δ 日本語"
FLEET_CANARY_VALUE = 0x024a555471370b18d


class TestFnv1aLibraryReferenceVectors(unittest.TestCase):
    def test_offset_basis_empty_input(self):
        self.assertEqual(fnv1a(b""), 0xcbf29ce484222325)

    def test_chongo_vector_a(self):
        # External reference vector (chongo/isthe.com FNV page).
        self.assertEqual(fnv1a(b"a"), 0xaf63dc4c8601ec8c)

    def test_chongo_vector_foobar(self):
        # External reference vector (chongo/isthe.com FNV page).
        self.assertEqual(fnv1a(b"foobar"), 0x85944171f73967e8)

    def test_fleet_canary_via_library(self):
        # The fleet canary MUST fall out of the library implementation,
        # not merely out of a test-local copy of the algorithm.
        self.assertEqual(
            fnv1a(FLEET_CANARY_STRING.encode("utf-8")), FLEET_CANARY_VALUE
        )

    def test_differential_distinct_inputs_distinct_outputs(self):
        # Anti-constant hack: a gutted fnv1a returning a pinned value
        # fails here even if it fools the canary assertion.
        outs = {fnv1a(s) for s in (b"x", b"y", b"zz", b"fleet", b"canary")}
        self.assertEqual(len(outs), 5)

    def test_differential_single_bit_flip_changes_output(self):
        base = fnv1a(b"fleet")
        for i in range(8):
            flipped = bytearray(b"fleet")
            flipped[0] ^= 1 << i
            self.assertNotEqual(fnv1a(bytes(flipped)), base)


if __name__ == "__main__":
    unittest.main()
