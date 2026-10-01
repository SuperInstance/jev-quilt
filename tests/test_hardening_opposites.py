"""Hardening tests: jev_quilt.opposites.

Invariants promised by the module docstring, previously enforced by a
single test (total + involutive on 4 sampled keys):

  * opposite() is TOTAL and NORMALIZING: input is stripped + lowered,
    so "  WITNESS  ", "Witness", "witness" are the same name.
  * Unknown names map to GAP — the honest opposite of an unnamed thing
    is a named absence; GAP itself is canonical and maps to "proof".
  * The WHOLE table is an involution on canonical names (antisymmetric
    property over every pair, not a 4-key sample).
  * Involution is a canonical-names-only law: double-opposite of an
    unknown is "proof", not the unknown — pinned so nobody "fixes" the
    total function into a lie.
  * is_canonical uses the same normalization as opposite().

Stdlib unittest only; deterministic; no network.
"""

import unittest

from jev_quilt.opposites import GAP, TABLE, is_canonical, opposite


class TestNormalization(unittest.TestCase):

    def test_strips_and_lowercases(self):
        self.assertEqual(opposite("  WITNESS  "), "forget")
        self.assertEqual(opposite("Witness"), "forget")
        self.assertEqual(opposite("jEv"), "jepa")

    def test_is_canonical_uses_same_normalization(self):
        self.assertTrue(is_canonical("  WITNESS "))
        self.assertTrue(is_canonical("Jev"))
        self.assertFalse(is_canonical("unknown-thing"))
        self.assertFalse(is_canonical("  "))


class TestTotality(unittest.TestCase):

    def test_unknown_names_map_to_gap(self):
        for name in ("quilt", "zzz-not-a-pair", "", "  ", "GAPLESS"):
            self.assertEqual(opposite(name), GAP)

    def test_gap_is_canonical_and_maps_to_proof(self):
        self.assertEqual(GAP, "gap")
        self.assertEqual(opposite(GAP), "proof")
        self.assertEqual(opposite("proof"), GAP)


class TestTableLaws(unittest.TestCase):

    def test_whole_table_is_involution(self):
        # every canonical name inverts and re-inverts to itself
        for k in TABLE:
            self.assertEqual(opposite(opposite(k)), k, f"breaks at {k!r}")

    def test_table_is_antisymmetric(self):
        for k, v in TABLE.items():
            self.assertEqual(TABLE.get(v), k, f"pair {k!r}->{v!r} not mirrored")

    def test_double_opposite_of_unknown_is_proof_not_unknown(self):
        # totality before involution: absence inverts to a NAME
        self.assertEqual(opposite(opposite("unregistered")), "proof")


if __name__ == "__main__":
    unittest.main()
