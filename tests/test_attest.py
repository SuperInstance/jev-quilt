"""The Attestation (G17): a credential earned by reproduction, re-verifiable
by the recipient from scratch.

`claim.py` (G16) proves reproduction to the node holding the books.
`diploma.py` (G13/G14) lets a Standing's streak leave that node signed, but
never re-checks the trustworthiness of the evidence behind it. An
Attestation is a signed, content-addressed envelope over a reproduced
`Claim` — every witness's reading (drifters included), the issuer's
consensus/quorum, and the calibrated floor the reproduction held under. The
receiving kernel never takes the issuer's word: it re-derives the
reproduction root, applies its OWN trust weights, quorum and floor, and
RECOMPUTES the verdict itself.

The headline property under test (`test_recipient_reweights_laundered_
credential`): the recipient can honestly reach a DIFFERENT verdict than the
issuer from the exact same signed bytes, because the issuer's
`earns_standing` is never on the wire — there is nothing to forge, only
evidence to re-weigh.
"""

import json
import unittest

from jev_quilt.bookkeeper import Bookkeeper
from jev_quilt.q16 import Q16
from jev_quilt.calibrate import CalibratedFloor
from jev_quilt.claim import Claim
from jev_quilt import signed_receipts as sr
from jev_quilt.attest import (
    Attestation, WitnessReading, Admission,
    attest, verify_attestation, admit,
    attestation_root, canonical_attestation_bytes,
)


def _witness_book(value: str, magnitude: int):
    """A single-entry book for one witness: it reads `value` at `magnitude`
    (mirrors test_claim.py's helper exactly)."""
    bk = Bookkeeper("witness")
    bk.book({}, {}, value, {"value": value, "magnitude": magnitude})
    return bk


def _reading_fn(book) -> tuple:
    res = json.loads(book.entries[-1].payload)
    return res["value"], Q16(int(res["magnitude"]))


def _swarm(n_agree: int, agree_value: str, agree_mag: int):
    return {f"w{i}": _witness_book(agree_value, agree_mag) for i in range(n_agree)}


def _identity(node: str, generation: int):
    return sr.generate_identity(node, generation)


class TestReproducedClaimIssuesAdmissibleAttestation(unittest.TestCase):
    def test_reproduced_claim_issues_admissible_attestation(self):
        # 5 unanimous witnesses, quorum 3, full recipient trust.
        books = _swarm(5, "42", 100)
        claim = Claim.from_books(books, reading_fn=_reading_fn, quorum=3)
        self.assertTrue(claim.earns_standing())

        signer, seed_hex, pk_hex = _identity("issuerA", 0)
        att = attest(claim, signer=signer, seed_hex=seed_hex)

        v = verify_attestation(att, {signer: pk_hex})
        self.assertTrue(v["ok"], v)
        self.assertEqual(v["reasons"], [])
        self.assertEqual(len(att.readings), 5)
        self.assertTrue(all(isinstance(r, WitnessReading) for r in att.readings))

        trust = {f"w{i}": 1 for i in range(5)}
        a = admit(att, {signer: pk_hex}, trust=trust, quorum=3)
        self.assertIsInstance(a, Admission)
        self.assertTrue(a.conferred)
        self.assertEqual(a.verdict, "ANSWER")
        self.assertEqual(a.value, claim.consensus())
        self.assertEqual(a.value, "42")


class TestTamperedAttestationRefused(unittest.TestCase):
    def setUp(self):
        books = _swarm(5, "42", 100)
        self.claim = Claim.from_books(books, reading_fn=_reading_fn, quorum=3)
        self.signer, self.seed_hex, self.pk_hex = _identity("issuerB", 0)
        self.att = attest(self.claim, signer=self.signer, seed_hex=self.seed_hex)
        self.pubkeys = {self.signer: self.pk_hex}
        self.trust = {f"w{i}": 1 for i in range(5)}

    def test_edited_reading_is_root_mismatch(self):
        tampered_readings = tuple(
            WitnessReading(witness=r.witness, value="99", drifting=r.drifting) if i == 0 else r
            for i, r in enumerate(self.att.readings)
        )
        tampered = Attestation(readings=tampered_readings, consensus=self.att.consensus,
                               quorum=self.att.quorum, earned_floor=self.att.earned_floor,
                               root=self.att.root, signer=self.att.signer,
                               signature=self.att.signature)
        v = verify_attestation(tampered, self.pubkeys)
        self.assertFalse(v["ok"])
        self.assertEqual(v["reasons"], ["root_mismatch"])
        a = admit(tampered, self.pubkeys, trust=self.trust, quorum=3)
        self.assertFalse(a.conferred)
        self.assertEqual(a.reason, "root_mismatch")

    def test_edited_meta_is_root_mismatch(self):
        # consensus / quorum / floor are all folded into the meta leaf; any
        # edit to any of the three is caught the same way as an edited
        # reading -- none of them may be changed in transit either.
        for field, value in (("consensus", "99"), ("quorum", 999), ("earned_floor", "1/2")):
            with self.subTest(field=field):
                kwargs = dict(readings=self.att.readings, consensus=self.att.consensus,
                              quorum=self.att.quorum, earned_floor=self.att.earned_floor,
                              root=self.att.root, signer=self.att.signer,
                              signature=self.att.signature)
                kwargs[field] = value
                tampered = Attestation(**kwargs)
                v = verify_attestation(tampered, self.pubkeys)
                self.assertFalse(v["ok"])
                self.assertEqual(v["reasons"], ["root_mismatch"])
                a = admit(tampered, self.pubkeys, trust=self.trust, quorum=3)
                self.assertFalse(a.conferred)
                self.assertEqual(a.reason, "root_mismatch")

    def test_flipped_signature_byte_is_bad_signature(self):
        flipped_hex = ("0" if self.att.signature[0] != "0" else "1") + self.att.signature[1:]
        tampered = Attestation(readings=self.att.readings, consensus=self.att.consensus,
                               quorum=self.att.quorum, earned_floor=self.att.earned_floor,
                               root=self.att.root, signer=self.att.signer,
                               signature=flipped_hex)
        v = verify_attestation(tampered, self.pubkeys)
        self.assertFalse(v["ok"])
        self.assertEqual(v["reasons"], ["bad_signature"])
        a = admit(tampered, self.pubkeys, trust=self.trust, quorum=3)
        self.assertFalse(a.conferred)
        self.assertEqual(a.reason, "bad_signature")

    def test_unknown_signer_refused(self):
        v = verify_attestation(self.att, {})
        self.assertFalse(v["ok"])
        self.assertEqual(v["reasons"], ["unknown_signer"])
        a = admit(self.att, {}, trust=self.trust, quorum=3)
        self.assertFalse(a.conferred)
        self.assertEqual(a.reason, "unknown_signer")


class TestRecipientReweightsLaunderedCredential(unittest.TestCase):
    def test_recipient_reweights_laundered_credential(self):
        # clean1/clean2 genuinely reproduce "42". ring1/ring2 collude to pad
        # the chorus -- they ALSO report "42" (Claim's law requires full
        # unanimity among non-drifters, so an outright false VALUE the
        # genuine witnesses would dissent from could only "earn standing" by
        # the issuer's floor excluding the genuine witnesses as drifters;
        # here the laundering is cheaper still -- the ring fabricates
        # INDEPENDENT agreement it never actually witnessed, padding the
        # quorum). Quorum=4 needs all four; the two genuine witnesses alone
        # are short of it.
        books = {
            "clean1": _witness_book("42", 100),
            "clean2": _witness_book("42", 100),
            "ring1": _witness_book("42", 100),
            "ring2": _witness_book("42", 100),
        }
        quorum = 4
        claim = Claim.from_books(books, reading_fn=_reading_fn, quorum=quorum)
        self.assertEqual(claim.drifters(), set())
        self.assertEqual(claim.consensus(), "42")
        self.assertTrue(claim.earns_standing())  # the issuer's honest verdict on this evidence

        signer, seed_hex, pk_hex = _identity("issuerRing", 0)
        att = attest(claim, signer=signer, seed_hex=seed_hex)
        pubkeys = {signer: pk_hex}
        v = verify_attestation(att, pubkeys)
        self.assertTrue(v["ok"], v)  # real signature, real root -- nothing here is forged

        # A recipient who mirrors the issuer's trust reaches the same verdict.
        full_trust = {"clean1": 1, "clean2": 1, "ring1": 1, "ring2": 1}
        mirrored = admit(att, pubkeys, trust=full_trust, quorum=quorum)
        self.assertTrue(mirrored.conferred)
        self.assertEqual(mirrored.verdict, "ANSWER")
        self.assertEqual(mirrored.value, "42")

        # The SAME bytes, re-weighed by a recipient who assigns the ring
        # trust 0: the trusted set loses the padding and falls below the
        # recipient's own quorum. conferred flips to False -- and that is
        # correct, not a failure, even though the issuer reproduced and
        # signed this exact attestation.
        recipient_trust = {"clean1": 1, "clean2": 1, "ring1": 0, "ring2": 0}
        reweighed = admit(att, pubkeys, trust=recipient_trust, quorum=quorum)
        self.assertFalse(reweighed.conferred)
        self.assertEqual(reweighed.reason, "not_reproduced_for_recipient")
        self.assertEqual(reweighed.trusted, ("clean1", "clean2"))
        self.assertEqual(set(reweighed.dropped), {"ring1", "ring2"})

        # Same verify_attestation.ok -- the difference is entirely in the
        # recipient's own re-weighing, not in anything the issuer could hide.
        self.assertTrue(verify_attestation(att, pubkeys)["ok"])


class TestRecipientStricterQuorum(unittest.TestCase):
    def test_recipient_stricter_quorum(self):
        books = _swarm(5, "42", 100)
        claim = Claim.from_books(books, reading_fn=_reading_fn, quorum=3)
        signer, seed_hex, pk_hex = _identity("issuerC", 0)
        att = attest(claim, signer=signer, seed_hex=seed_hex)
        trust = {f"w{i}": 1 for i in range(5)}

        stricter = admit(att, {signer: pk_hex}, trust=trust, quorum=len(att.readings) + 1)
        self.assertFalse(stricter.conferred)
        self.assertEqual(stricter.reason, "not_reproduced_for_recipient")

        # the recipient's own (looser) quorum still confers, over the same bytes
        looser = admit(att, {signer: pk_hex}, trust=trust, quorum=3)
        self.assertTrue(looser.conferred)


class TestSeaGradedAdmission(unittest.TestCase):
    def test_sea_graded_admission(self):
        books = _swarm(5, "42", 100)
        claim = Claim.from_books(books, reading_fn=_reading_fn, quorum=3)
        signer, seed_hex, pk_hex = _identity("issuerD", 0)
        earned_floor = Q16(1, 10)
        att = attest(claim, signer=signer, seed_hex=seed_hex, floor=earned_floor)
        self.assertEqual(att.earned_floor, "1/10")
        trust = {f"w{i}": 1 for i in range(5)}

        # a calm recipient floor (never warmed -> floor() is None) does not
        # gate ANSWER at all.
        calm = admit(att, {signer: pk_hex}, trust=trust, quorum=3,
                    floor=CalibratedFloor())
        self.assertTrue(calm.conferred)
        self.assertEqual(calm.verdict, "ANSWER")

        # a recipient floor whose OWN current reading is rougher than the
        # sea the reproduction was earned under: conferred, but held to
        # CONFIRM, not ANSWER.
        rough = CalibratedFloor(k=1, slack=Q16(1), floor_min=Q16(1, 1000))
        rough.update(Q16(1))  # floor() == 1, well past earned_floor (1/10)
        self.assertGreater(rough.floor(), earned_floor)
        graded = admit(att, {signer: pk_hex}, trust=trust, quorum=3, floor=rough)
        self.assertTrue(graded.conferred)
        self.assertEqual(graded.verdict, "CONFIRM")
        self.assertEqual(graded.value, "42")


class TestConfluentAdmission(unittest.TestCase):
    def test_confluent_admission(self):
        books = _swarm(5, "42", 100)
        claim = Claim.from_books(books, reading_fn=_reading_fn, quorum=3)
        signer, seed_hex, pk_hex = _identity("issuerE", 0)
        att = attest(claim, signer=signer, seed_hex=seed_hex)
        trust = {f"w{i}": 1 for i in range(5)}

        shuffled = Attestation(readings=tuple(reversed(att.readings)),
                               consensus=att.consensus, quorum=att.quorum,
                               earned_floor=att.earned_floor, root=att.root,
                               signer=att.signer, signature=att.signature)
        self.assertTrue(verify_attestation(shuffled, {signer: pk_hex})["ok"])

        a1 = admit(att, {signer: pk_hex}, trust=trust, quorum=3)
        a2 = admit(shuffled, {signer: pk_hex}, trust=trust, quorum=3)
        self.assertEqual(a1, a2)


class TestContentAddressedRootVector(unittest.TestCase):
    def test_content_addressed_root_vector(self):
        # Cross-language pin: computed once from this module's own _leaf +
        # fold.mmr_root and pasted here as the byte-canonical contract,
        # mirroring test_claim.py / test_diploma.py's style.
        readings = (
            WitnessReading(witness="alpha", value="42", drifting=False),
            WitnessReading(witness="beta", value="42", drifting=False),
            WitnessReading(witness="gamma", value="43", drifting=False),
        )
        consensus = "42"
        quorum = 2
        earned_floor = None
        self.assertEqual(
            canonical_attestation_bytes(readings, consensus, quorum, earned_floor),
            b"alpha\x1f42\x1f0|beta\x1f42\x1f0|gamma\x1f43\x1f0|42|2|",
        )
        expected = "b2df4dc148cce54bbc13190b2dab3417feda6b681fd49970873f39c0f90e51ce"
        self.assertEqual(attestation_root(readings, consensus, quorum, earned_floor).hex(),
                        expected)

        # order-independence: the function itself sorts before rooting.
        reordered = tuple(reversed(readings))
        self.assertEqual(
            attestation_root(reordered, consensus, quorum, earned_floor),
            attestation_root(readings, consensus, quorum, earned_floor),
        )


class TestIssuerRefusesUnreproducedClaim(unittest.TestCase):
    def test_issuer_refuses_unreproduced_claim(self):
        diverged_books = _swarm(4, "42", 100)
        diverged_books["dissenter"] = _witness_book("43", 101)
        floor = CalibratedFloor(k=5, slack=Q16(5, 2), floor_min=Q16(2))
        claim = Claim.from_books(diverged_books, reading_fn=_reading_fn, quorum=3, floor=floor)
        self.assertFalse(claim.earns_standing())

        signer, seed_hex, _ = _identity("issuerF", 0)
        with self.assertRaises(ValueError):
            attest(claim, signer=signer, seed_hex=seed_hex)


if __name__ == "__main__":
    unittest.main()
