import unittest
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

from jev_quilt.bookkeeper import Bookkeeper




class TestConverted(unittest.TestCase):

    def test_book_ticks_increase(self):
        bk = Bookkeeper("c")
        r1 = bk.book({"s": 1}, {"d": 1}, "choice", {"v": "a"})
        r2 = bk.book({"s": 2}, {"d": 2}, "choice", {"v": "b"})
        assert (r1.tick, r2.tick) == (1, 2)
        assert bk.verify()




def test_replay_deterministic():
    bk = Bookkeeper("c")
    bk.book({"s": 1}, {"d": 1}, "noul", {"p": 0.5})
    bk.book({"s": 2}, {"d": 2}, "noul", {"p": 0.7})
    assert bk.replay() == bk.replay()
    assert len(bk.replay()) == 64  # sha256 hex


def test_replay_diverges_on_tamper():
    bk = Bookkeeper("c")
    bk.book({"s": 1}, {"d": 1}, "choice", {"v": "a"})
    h = bk.replay()
    bk.entries[0] = type(bk.entries[0])(1, "0" * 64, bk.entries[0].delta_hash,
                                         bk.entries[0].decision_kind, bk.entries[0].payload_hash)
    assert bk.replay() != h


def test_verify_catches_gap():
    bk = Bookkeeper("c")
    bk.book({}, {}, "q16", {})
    bk.entries[0] = type(bk.entries[0])(5, "", "", "", "")
    assert not bk.verify()


def test_wake_state_shape():
    bk = Bookkeeper("c")
    ws = bk.wake_state()
    assert ws["cell"] == "c" and ws["booked_ticks"] == 0 and ws["chain"] is None


def test_fnv1a_reference_vectors():
    from jev_quilt.bookkeeper import fnv1a
    assert fnv1a(b"") == 0xcbf29ce484222325
    assert fnv1a(b"a") == 0xaf63dc4c8601ec8c
    # non-ASCII: hash the UTF-8 ENCODING, never ord() — this vector is
    # pinned in polyform/rust/src/lib.rs too; both languages must agree.
    assert fnv1a("café Δ 日本語".encode("utf-8")) == 0x024a555471370b18d


def test_payload_hash_matches_rust_substrate():
    # Rust book_with_payload("choice", 0, '{"v": "a"}').payload_hash
    # == 0x654e3ae949abedfa — pinned in the rust suite. Same residue,
    # same rule (fnv1a-64 over UTF-8), same hash. Cross-language
    # receipt compare is now real, not "self-consistent per cell".
    bk = Bookkeeper("c")
    r = bk.book({"s": 1}, {"d": 1}, "choice", {"v": "a"})
    assert r.payload_hash == "654e3ae949abedfa"
    assert r.payload == '{"v": "a"}'


def test_payload_tamper_breaks_replay():
    bk = Bookkeeper("c")
    bk.book({"s": 1}, {"d": 1}, "choice", {"v": "a"})
    h = bk.replay()
    e = bk.entries[0]
    bk.entries[0] = type(e)(e.tick, e.state_hash, e.delta_hash,
                            e.decision_kind, e.payload_hash, payload='{"v": "EVIL"}')
    assert bk.replay() != h


# ── G20a: typed, uncapped decision fields (closes C9) ──────────────────

def test_book_without_typed_fields_is_byte_for_byte_unchanged():
    """A booking that never sets a typed decision field hashes IDENTICALLY
    to the historical formula -- the declared G20a pin change is scoped to
    callers that opt in (orgbook.py), never to the fleet's other cells."""
    bk = Bookkeeper("c")
    r = bk.book({"s": 1}, {"d": 1}, "choice", {"v": "a"})
    assert r.decision_bytes() == b""
    raw = f"1|{r.state_hash}|{r.delta_hash}|choice|{r.payload_hash}"
    import hashlib
    assert r.sha() == hashlib.sha256(raw.encode()).hexdigest()


def test_book_accepts_typed_decision_fields_uncapped():
    """A decision field far longer than the 200-char residue cap is
    carried EXACTLY -- the render may still be capped; the decision never
    is (Law 1/3: identity never floats, decide from the typed field)."""
    bk = Bookkeeper("c")
    long_reason = "x" * 500
    r = bk.book({"s": 1}, {"d": 1}, "ACT", {"reason": long_reason},
               dispatch_id="d1", runner="r1", key="k1", correct=False,
               base_verdict="CONFIRM", answer="k1")
    assert r.runner == "r1" and r.key == "k1" and r.correct is False
    assert r.base_verdict == "CONFIRM" and r.dispatch_id == "d1"
    assert len(r.payload) <= 200          # the render stays capped ...
    assert r.decision_bytes() != b""      # ... the decision does not


def test_book_refuses_a_decision_field_that_is_not_a_bool_or_str():
    bk = Bookkeeper("c")
    try:
        bk.book({}, {}, "ACT", {}, runner="r1", correct="yes")  # not a bool
        assert False, "expected a refusal"
    except ValueError:
        pass
    assert bk.entries == []   # refused at book() -- never a partial land


def test_book_refuses_a_decision_field_containing_the_reserved_delimiter():
    bk = Bookkeeper("c")
    try:
        bk.book({}, {}, "ACT", {}, runner="r1\x1fEVIL")
        assert False, "expected a refusal"
    except ValueError:
        pass
    assert bk.entries == []
