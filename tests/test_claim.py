"""Reproducibility as `mmr_root` (G16): a claim earns standing iff N independent
witnesses reproduce it — their books fold to a single agreed root, confluent
across gossip order, and a drifting instrument is excluded rather than
silently averaged in. The heart of the rung is the discriminator: a witness
that disagrees but stays WITHIN the calibrated floor is an honest
disagreement (halt — not reproducible); a witness whose surprise CLEARS the
floor is a flagged instrument drift (excluded, not averaged in).
"""
import json
import unittest

from jev_quilt.bookkeeper import Bookkeeper
from jev_quilt.q16 import Q16
from jev_quilt.calibrate import CalibratedFloor
from jev_quilt.claim import Claim, Reading, claim_standing


def _witness_book(value: str, magnitude: int):
    """A single-entry book for one witness: it reads `value` at `magnitude`."""
    bk = Bookkeeper("witness")
    bk.book({}, {}, value, {"value": value, "magnitude": magnitude})
    return bk


def _reading_fn(book) -> tuple:
    """Mirror test_commons.py/test_standing.py's residue read: pull (value,
    magnitude) straight off the one booked receipt."""
    res = json.loads(book.entries[-1].payload)
    return res["value"], Q16(int(res["magnitude"]))


def _swarm(n_agree: int, agree_value: str, agree_mag: int,
           dissent_value: str = None, dissent_mag: int = None):
    """n_agree witnesses reporting (agree_value, agree_mag); optionally one more
    ('dissenter') reporting (dissent_value, dissent_mag)."""
    books = {f"w{i}": _witness_book(agree_value, agree_mag) for i in range(n_agree)}
    if dissent_value is not None:
        books["dissenter"] = _witness_book(dissent_value, dissent_mag)
    return books


class TestConverted(unittest.TestCase):
    def test_reproduced_claim_earns_standing(self):
        # 5 witnesses all "42", quorum 3, no drift -> earns_standing True; two
        # independent from_books runs over the same evidence agree bit-for-bit.
        books = _swarm(5, "42", 100)
        a = Claim.from_books(books, reading_fn=_reading_fn, quorum=3)
        assert a.earns_standing()
        assert a.consensus() == "42"

        books2 = _swarm(5, "42", 100)
        b = Claim.from_books(books2, reading_fn=_reading_fn, quorum=3)
        assert a.agrees_with(b)

    def test_single_delta_divergence_breaks_reproducibility(self):
        # 4 witnesses "42"@100, one dissenter "43"@101 (surprise=1). A floor
        # with floor_min=2 stays wider than the delta -> honest disagreement,
        # NOT flagged as drift -> the dissenter stays in the trusted set ->
        # not unanimous -> earns_standing False. Its changed reading also
        # changes the root, so this claim does not agree with the canonical
        # all-"42" one.
        canonical_books = _swarm(5, "42", 100)
        canonical = Claim.from_books(canonical_books, reading_fn=_reading_fn, quorum=3)

        diverged_books = _swarm(4, "42", 100, dissent_value="43", dissent_mag=101)
        floor = CalibratedFloor(k=5, slack=Q16(5, 2), floor_min=Q16(2))
        diverged = Claim.from_books(diverged_books, reading_fn=_reading_fn, quorum=3, floor=floor)

        assert not diverged.earns_standing()
        assert diverged.consensus() is None
        assert diverged.drifters() == set()               # not flagged: honest disagreement
        assert not diverged.agrees_with(canonical)         # single delta -> different root

    def test_confluent_across_gossip_order(self):
        ordered_books = _swarm(4, "42", 100, dissent_value="43", dissent_mag=101)
        # same content, different (gossip) arrival order
        shuffled_books = {}
        for k in reversed(list(ordered_books.keys())):
            shuffled_books[k] = ordered_books[k]

        ordered = Claim.from_books(ordered_books, reading_fn=_reading_fn, quorum=3)
        shuffled = Claim.from_books(shuffled_books, reading_fn=_reading_fn, quorum=3)
        assert ordered.root() == shuffled.root()
        assert ordered.agrees_with(shuffled)

    def test_drifting_float_is_downweighted_not_averaged(self):
        # 4 witnesses "42"@100, one dissenter "43"@150 (surprise=50). A tiny
        # floor_min lets the mean-scaled floor (50/5 * 5/2 = 25) clear well
        # below the dissenter's own surprise (50) -> flagged as drifting,
        # excluded from consensus, absent from readings() by default, but
        # still present in root() and drifters().
        books = _swarm(4, "42", 100, dissent_value="43", dissent_mag=150)
        floor = CalibratedFloor(k=5, slack=Q16(5, 2), floor_min=Q16(1, 1000))
        claim = Claim.from_books(books, reading_fn=_reading_fn, quorum=3, floor=floor)

        assert claim.drifters() == {"dissenter"}
        assert claim.consensus() == "42"
        assert claim.earns_standing()                      # remaining 4 unanimous, >= quorum
        assert all(r.witness != "dissenter" for r in claim.readings())
        all_readings = claim.readings(include_drifting=True)
        assert any(r.witness == "dissenter" and r.drifting for r in all_readings)
        assert isinstance(all_readings[0], Reading)
        # the drifter's actual reading still counts toward the content-addressed root
        canonical = Claim.from_books(_swarm(5, "42", 100), reading_fn=_reading_fn, quorum=3)
        assert not claim.agrees_with(canonical)

    def test_honest_disagreement_vs_drift_are_distinguished(self):
        # The SAME numeric divergence (surprise=10: dissenter magnitude 110
        # vs consensus magnitude 100), judged by two different floors,
        # produces opposite outcomes -- proving the floor, not the delta, is
        # what decides "real disagreement, halt" vs "bad instrument, exclude".
        books = _swarm(4, "42", 100, dissent_value="43", dissent_mag=110)

        wide_floor = CalibratedFloor(k=5, slack=Q16(5, 2), floor_min=Q16(15))
        honest = Claim.from_books(books, reading_fn=_reading_fn, quorum=3, floor=wide_floor)
        assert honest.drifters() == set()                   # within the floor: honest disagreement
        assert not honest.earns_standing()                  # genuinely not reproducible: halt

        narrow_floor = CalibratedFloor(k=5, slack=Q16(5, 2), floor_min=Q16(1, 1000))
        drifted = Claim.from_books(books, reading_fn=_reading_fn, quorum=3, floor=narrow_floor)
        assert drifted.drifters() == {"dissenter"}           # clears the floor: flagged drift
        assert drifted.earns_standing()                      # excluded -> the rest are unanimous
        assert drifted.consensus() == "42"

    def test_content_addressed_root_vector(self):
        # Cross-language pin (fixed small swarm, no drift machinery in play):
        # computed once from this module's own _leaf + fold.mmr_root and
        # pasted here as the byte-canonical contract, mirroring
        # test_diploma.py's style.
        books = {
            "alpha": _witness_book("42", 100),
            "beta": _witness_book("42", 100),
            "gamma": _witness_book("43", 105),
        }
        claim = Claim.from_books(books, reading_fn=_reading_fn, quorum=2)
        expected = "1dd4c6d70860d469d304c2cab9e100c8a4555137c2ffdb5ffcdaaad7df8459aa"
        assert claim.root().hex() == expected

    def test_claim_standing_bridge_confers_the_fourth_verdict(self):
        earned_books = _swarm(5, "42", 100)
        earned = Claim.from_books(earned_books, reading_fn=_reading_fn, quorum=3)
        assert claim_standing(earned, "k", "ESCALATE") == ("ANSWER", "42")

        unearned_books = _swarm(4, "42", 100, dissent_value="43", dissent_mag=101)
        floor = CalibratedFloor(k=5, slack=Q16(5, 2), floor_min=Q16(2))
        unearned = Claim.from_books(unearned_books, reading_fn=_reading_fn, quorum=3, floor=floor)
        assert claim_standing(unearned, "k", "ESCALATE") == ("ESCALATE", None)


if __name__ == "__main__":
    unittest.main()
