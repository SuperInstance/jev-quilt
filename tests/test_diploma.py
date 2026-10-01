"""G13 (portable diploma) + G14 (sea-graded transfer): standing that
survives a kernel change.

A Diploma is a signed, content-addressed envelope over one Standing's
deposits, so a DIFFERENT kernel can confer standing by replay rather than
by trust in whatever carried the bytes. G14 puts the diploma's optional
earned_floor to work: earned standing autopilots only while the outcome's
surprise stays inside the floor the diploma carried.

STRETCH: both "kernels" below are the same Python implementation, so these
tests prove cross-INSTANCE transfer (independent Standing/Diploma objects,
independent verification), not literally cross-language. The true
cross-language morphism rests on the byte-canonical discipline in
diploma.py (UTF-8 pipe-joined text, sha256/MMR — nothing else touches
identity); it is pinned here by a hard-coded expected-root vector any
non-Python port can reproduce and check itself against
(test_content_addressed_root_matches_pinned_vector).
"""

import unittest

from jev_quilt.standing import Standing, DEFAULT_DIPLOMA
from jev_quilt.q16 import Q16
from jev_quilt import signed_receipts as sr
from jev_quilt.diploma import (
    Diploma, issue, verify_diploma, standing_from_diploma,
    sea_graded_verdict, canonical_diploma_bytes, diploma_root, parse_floor,
)

PINNED_ROOT = "16feb37a53737f2d7fe28fd74be827c5fa9a0ac68dd8cbce6505538a51038906"


def _standing(rows, diploma_n=DEFAULT_DIPLOMA):
    """Build a Standing by folding (key, correct, answer) rows in order."""
    s = Standing(diploma_n)
    for key, correct, answer in rows:
        s.observe(key, correct, answer)
    return s


def _identity(seed_byte=0):
    seed = bytes([seed_byte]) * 32
    from jev_quilt import ed25519
    return f"kernelA{seed_byte}.k0", seed.hex(), ed25519.publickey(seed).hex()


class TestG13ValidTransfer(unittest.TestCase):
    def test_valid_diploma_confers_earned_standing_on_a_fresh_kernel(self):
        s = _standing([("open", True, "warm")] * DEFAULT_DIPLOMA)
        self.assertTrue(s.earned("open"))
        signer, seed_hex, pk_hex = sr.generate_identity("toykernel", 0)
        dip = issue(s, signer=signer, seed_hex=seed_hex)

        v = verify_diploma(dip, {signer: pk_hex})
        self.assertTrue(v["ok"], v)
        self.assertEqual(v["reasons"], [])

        fresh = standing_from_diploma(dip, {signer: pk_hex})
        self.assertTrue(fresh.earned("open"))
        self.assertEqual(fresh.recall("open"), "warm")


class TestG13Tamper(unittest.TestCase):
    def setUp(self):
        self.s = _standing([("open", True, "warm")] * DEFAULT_DIPLOMA)
        self.signer, self.seed_hex, self.pk_hex = sr.generate_identity("toykernel", 1)
        self.dip = issue(self.s, signer=self.signer, seed_hex=self.seed_hex)
        self.pubkeys = {self.signer: self.pk_hex}

    def test_inflated_streak_is_root_mismatch(self):
        tampered_deposits = [(k, a, streak + 100) for (k, a, streak) in self.dip.deposits]
        tampered = Diploma(deposits=tampered_deposits, diploma_n=self.dip.diploma_n,
                           earned_floor=self.dip.earned_floor, root=self.dip.root,
                           signer=self.dip.signer, signature=self.dip.signature)
        v = verify_diploma(tampered, self.pubkeys)
        self.assertFalse(v["ok"])
        self.assertEqual(v["reasons"], ["root_mismatch"])
        fresh = standing_from_diploma(tampered, self.pubkeys)
        self.assertFalse(fresh.earned("open"))

    def test_flipped_signature_byte_is_bad_signature(self):
        flipped_hex = ("0" if self.dip.signature[0] != "0" else "1") + self.dip.signature[1:]
        tampered = Diploma(deposits=self.dip.deposits, diploma_n=self.dip.diploma_n,
                           earned_floor=self.dip.earned_floor, root=self.dip.root,
                           signer=self.dip.signer, signature=flipped_hex)
        v = verify_diploma(tampered, self.pubkeys)
        self.assertFalse(v["ok"])
        self.assertEqual(v["reasons"], ["bad_signature"])
        fresh = standing_from_diploma(tampered, self.pubkeys)
        self.assertFalse(fresh.earned("open"))

    def test_unknown_signer_no_pubkeys(self):
        v = verify_diploma(self.dip, {})
        self.assertFalse(v["ok"])
        self.assertEqual(v["reasons"], ["unknown_signer"])
        fresh = standing_from_diploma(self.dip, {})
        self.assertFalse(fresh.earned("open"))

    def test_unknown_signer_wrong_id(self):
        v = verify_diploma(self.dip, {"someone.else": self.pk_hex})
        self.assertFalse(v["ok"])
        self.assertEqual(v["reasons"], ["unknown_signer"])
        fresh = standing_from_diploma(self.dip, {"someone.else": self.pk_hex})
        self.assertFalse(fresh.earned("open"))


class TestG13WithheldNotConferred(unittest.TestCase):
    def test_transferred_streak_below_threshold_is_not_earned(self):
        s = _standing([("route", True, "left")])  # streak 1, not yet earned
        self.assertFalse(s.earned("route"))
        signer, seed_hex, pk_hex = sr.generate_identity("toykernel", 2)
        dip = issue(s, signer=signer, seed_hex=seed_hex)
        v = verify_diploma(dip, {signer: pk_hex})
        self.assertTrue(v["ok"], v)

        received = standing_from_diploma(dip, {signer: pk_hex}, diploma_n=3)
        # the deposit transferred faithfully (streak = 1) ...
        self.assertEqual(received.streak("route"), 1)
        self.assertEqual(received.recall("route"), None)
        # ... but is NOT earned at threshold 3: withheld != conferred
        self.assertFalse(received.earned("route"))


class TestG14SeaGradedVerdict(unittest.TestCase):
    def setUp(self):
        self.s = _standing([("open", True, "warm")] * DEFAULT_DIPLOMA)
        signer, seed_hex, pk_hex = sr.generate_identity("toykernel", 3)
        self.floor = Q16(1, 10)
        self.dip = issue(self.s, signer=signer, seed_hex=seed_hex, earned_floor=self.floor)
        self.pubkeys = {signer: pk_hex}
        self.standing = standing_from_diploma(self.dip, self.pubkeys)
        self.parsed_floor = parse_floor(self.dip.earned_floor)
        self.assertEqual(self.parsed_floor, self.floor)

    def test_surprise_within_floor_answers(self):
        v = sea_graded_verdict(self.standing, "open", "ACT",
                               surprise=Q16(1, 20), earned_floor=self.parsed_floor)
        self.assertEqual(v, ("ANSWER", "warm"))

    def test_surprise_past_floor_confirms_not_answers(self):
        v = sea_graded_verdict(self.standing, "open", "ACT",
                               surprise=Q16(1, 2), earned_floor=self.parsed_floor)
        self.assertEqual(v, ("CONFIRM", None))

    def test_revocable_wrong_observe_falls_back_to_base(self):
        self.assertTrue(self.standing.earned("open"))
        self.standing.observe("open", False, "warm")  # the world drifted
        v = sea_graded_verdict(self.standing, "open", "ACT",
                               surprise=Q16(1, 20), earned_floor=self.parsed_floor)
        self.assertEqual(v, ("ACT", None))

    def test_unearned_key_untouched(self):
        v = sea_graded_verdict(self.standing, "never-seen", "ESCALATE",
                               surprise=Q16(0), earned_floor=self.parsed_floor)
        self.assertEqual(v, ("ESCALATE", None))


class TestContentAddressed(unittest.TestCase):
    def test_same_deposits_and_floor_same_root_across_instances(self):
        deps = [("open", "warm", 3), ("route", "left", 5)]
        a = diploma_root(list(deps), 3, "1/10")
        b = diploma_root(list(reversed(deps)), 3, "1/10")
        self.assertEqual(a, b)

    def test_changing_a_streak_changes_the_root(self):
        deps = [("open", "warm", 3)]
        base = diploma_root(deps, 3, None)
        changed = diploma_root([("open", "warm", 4)], 3, None)
        self.assertNotEqual(base, changed)

    def test_changing_the_floor_changes_the_root(self):
        deps = [("open", "warm", 3)]
        no_floor = diploma_root(deps, 3, None)
        with_floor = diploma_root(deps, 3, "1/10")
        self.assertNotEqual(no_floor, with_floor)

    def test_content_addressed_root_matches_pinned_vector(self):
        # Cross-language pin: computed once from canonical_diploma_bytes /
        # diploma_root over this exact (deposits, diploma_n, floor) tuple.
        # A byte-exact port (Rust, TS, ...) must reproduce this value.
        deps = [("open", "warm", 3), ("route", "left", 5)]
        self.assertEqual(
            canonical_diploma_bytes(deps, 3, None),
            b"open\x1fwarm\x1f3|route\x1fleft\x1f5|3|",
        )
        self.assertEqual(diploma_root(deps, 3, None), PINNED_ROOT)


class TestDiplomaRoundTrip(unittest.TestCase):
    def test_to_dict_from_dict_round_trips(self):
        s = _standing([("open", True, "warm")] * DEFAULT_DIPLOMA)
        signer, seed_hex, pk_hex = sr.generate_identity("toykernel", 4)
        dip = issue(s, signer=signer, seed_hex=seed_hex, earned_floor=Q16(1, 10))
        d = dip.to_dict()
        self.assertEqual(d["deposits"], [list(x) for x in dip.deposits])
        back = Diploma.from_dict(d)
        self.assertEqual(back, dip)
        v = verify_diploma(back, {signer: pk_hex})
        self.assertTrue(v["ok"], v)


if __name__ == "__main__":
    unittest.main()
