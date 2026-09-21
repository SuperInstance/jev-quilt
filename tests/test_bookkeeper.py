import sys
sys.path.insert(0, "/workspace/repos/jev-quilt")

from jev_quilt.bookkeeper import Bookkeeper


def test_book_ticks_increase():
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
