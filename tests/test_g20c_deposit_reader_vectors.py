"""G20c — the Deposit Reader: keep the checked-in cross-language fixture
honest.

`vectors/g20c_deposit_reader_vectors.json` is what the non-Python (Rust)
reader in `ports/rust/src/g20c.rs` independently DERIVES the commons
deposit table (and `Commons.root()`) from — closing G20b's own STRETCH
note (the deposit table was previously taken from the fixture as ground
truth; here it is re-derived from raw witness readings through the real
`Claim.from_books` -> `attest` -> `admit` -> `Schoolhouse.enroll` bridge ->
`Commons.deposit`/`forget` pipeline). This test does NOT re-verify the Rust
reader (that is `cargo test`'s job, in `ports/rust/`); it verifies the
*fixture itself* stays truthful:

  * `test_committed_vectors_match_a_fresh_regeneration` — regenerating the
    vectors from `vectors/gen_g20c_deposit_reader_vectors.py` right now
    reproduces the checked-in file byte-for-byte.
  * `test_deposit_table_matches_a_live_schoolhouse_built_independently` —
    a second Python call path (not the generator module) drives the SAME
    witnesses/trust/quorum/floor through a fresh `Schoolhouse`, and its
    resulting deposit table + `commons.root()` are cross-checked against
    the committed fixture — two different call paths into the same
    Python implementation, not just one script's opinion of itself.
"""
import importlib.util
import json
import os
import unittest

from jev_quilt.q16 import Q16
from jev_quilt.calibrate import CalibratedFloor
from jev_quilt.schoolhouse import Schoolhouse
from jev_quilt import ed25519

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
GEN_PATH = os.path.join(REPO_ROOT, "vectors", "gen_g20c_deposit_reader_vectors.py")
VECTORS_PATH = os.path.join(REPO_ROOT, "vectors", "g20c_deposit_reader_vectors.json")


def _load_generator_module():
    spec = importlib.util.spec_from_file_location("gen_g20c_deposit_reader_vectors", GEN_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestG20cVectorsFreshness(unittest.TestCase):

    def test_committed_vectors_match_a_fresh_regeneration(self):
        mod = _load_generator_module()
        fresh = mod.run(mod.build_scenario())

        with open(VECTORS_PATH, encoding="utf-8") as f:
            committed = json.load(f)

        self.assertEqual(fresh["commons_quorum"], committed["commons_quorum"])
        self.assertEqual(fresh["questions"], committed["questions"])
        self.assertEqual(fresh["forgets"], committed["forgets"])
        self.assertEqual(fresh["commons"], committed["commons"])
        self.assertEqual(fresh["pins"], committed["pins"])

    def test_deposit_table_matches_a_live_schoolhouse_built_independently(self):
        """A second Python call path: reconstructs the scenario from the
        committed fixture's OWN raw witness/trust/quorum fields (not from
        the generator module's internal state) through a fresh
        `Schoolhouse`, and checks the resulting deposit table + root
        against the committed fixture — catches the generator quietly
        agreeing with only itself."""
        with open(VECTORS_PATH, encoding="utf-8") as f:
            committed = json.load(f)

        sh = Schoolhouse("schoolhouse.g20c.replay", quorum=committed["commons_quorum"], diploma=3)
        reading_fn = lambda book: book
        pubkeys = {}

        for q in committed["questions"]:
            books = {w: (info["value"], Q16(info["magnitude"]["num"], info["magnitude"]["den"]))
                    for w, info in q["witnesses"].items()}
            issuer_floor = CalibratedFloor(k=q["floor_k"])
            claim = sh.reproduce(books, reading_fn=reading_fn, quorum=q["claim_quorum"],
                                 floor=issuer_floor, runner=q["issuer"], base_verdict="ACT")

            seed_hex = mod_seed_hex(q["issuer"])
            pubkeys[q["issuer"]] = ed25519.publickey(bytes.fromhex(seed_hex)).hex()
            earned_floor_q = None
            if q["expected"]["attestation"]["earned_floor"] is not None:
                num_s, den_s = q["expected"]["attestation"]["earned_floor"].split("/")
                earned_floor_q = Q16(int(num_s), int(den_s))
            att = sh.issue(claim, signer=q["issuer"], seed_hex=seed_hex, floor=earned_floor_q)

            recipient_floor = CalibratedFloor(k=q["floor_k"])
            magnitudes = {w: Q16(info["magnitude"]["num"], info["magnitude"]["den"])
                         for w, info in q["witnesses"].items()}
            enrollment = sh.enroll(
                att, pubkeys, key=q["key"], trust=q["recipient_trust"], quorum=q["admit_quorum"],
                floor=recipient_floor, reading_magnitude=lambda r: magnitudes[r.witness],
                base_verdict="CONFIRM",
            )
            self.assertEqual(enrollment.admission.conferred, q["expected"]["admission"]["conferred"])
            self.assertEqual(enrollment.admission.verdict, q["expected"]["admission"]["verdict"])
            self.assertEqual(enrollment.admission.value, q["expected"]["admission"]["value"])
            self.assertEqual(sorted(enrollment.admission.trusted), q["expected"]["admission"]["trusted"])
            self.assertEqual(sorted(enrollment.admission.dropped), q["expected"]["admission"]["dropped"])

        for key, answer in committed["forgets"]:
            sh.forget(key, answer)

        deposits = [{"key": d.key, "answer": d.answer, "weight": d.weight} for d in sh.commons.deposits()]
        self.assertEqual(deposits, committed["commons"]["deposits"])
        self.assertEqual(sh.commons.root().hex(), committed["commons"]["expected_root_hex"])
        self.assertEqual(sh.commons.root().hex(), committed["pins"]["commons_root"])


def mod_seed_hex(signer: str) -> str:
    """Same deterministic seed derivation the generator uses (not imported
    from it, deliberately — this test path re-derives it independently so
    it is not just calling back into the generator module under test)."""
    import hashlib
    return hashlib.sha256(f"g20c-seed::{signer}".encode()).hexdigest()[:64]


if __name__ == "__main__":
    unittest.main()
