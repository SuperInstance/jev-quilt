"""OrgBook (G18 — the Org on the Quilt, replay-verifiable half): book the
dispatch org on the kernel it builds. Routing is wiring over `standing.py`,
never a second decision procedure; the org's WAL is replay ≡ live exactly as
a single cell's book is (law 4), and two org-books built from the same
dispatch sequence agree on their pins — the WAL chain and a decisions digest
— without comparing a table row by row.
"""
import unittest

from jev_quilt.standing import Standing, verdict as standing_verdict, DEFAULT_DIPLOMA
from jev_quilt.orgbook import OrgBook


def _run(org, dispatch_id, task_class, runner, tier, outcome, *, base_verdict="ACT"):
    """Live-simulate one dispatch: decide the route, then book what happened
    — exactly the shape a real dispatcher call takes (decide once, then
    record what came of it)."""
    v, answer = org.route(task_class, runner, base_verdict)
    org.record_dispatch(dispatch_id, tier, task_class, runner, v, outcome,
                        base_verdict=base_verdict, answer=tier)
    return v, answer


class TestOrgBook(unittest.TestCase):

    def test_route_is_exactly_standing_verdict_over_the_runner_book(self):
        org = OrgBook("org.test")
        for i in range(DEFAULT_DIPLOMA):
            _run(org, f"d{i}", "grep-sweep", "haiku-1", "haiku", "correct")

        # cross-check against a bare Standing built the standing.py way, over
        # the SAME receipts (filtered to this runner) — route() must not
        # diverge by so much as one bit from what standing.py itself says.
        book = org.book_for("haiku-1")
        s = Standing.from_book(book, diploma=org.diploma)
        expected = standing_verdict(s, "grep-sweep", "ACT")
        assert org.route("grep-sweep", "haiku-1", "ACT") == expected
        assert expected == ("ANSWER", "haiku")

    def test_route_does_not_earn_before_the_diploma_streak(self):
        org = OrgBook("org.test")
        for i in range(DEFAULT_DIPLOMA - 1):
            _run(org, f"d{i}", "lint", "haiku-2", "haiku", "correct")
        v, answer = org.route("lint", "haiku-2", "ACT")
        assert v == "ACT"                 # N-1 correct: standing not yet earned
        assert answer is None

    def test_one_booked_wrong_run_revokes_answer_back_to_base(self):
        org = OrgBook("org.test")
        for i in range(DEFAULT_DIPLOMA):
            _run(org, f"d{i}", "format-check", "haiku-3", "haiku", "correct")
        assert org.route("format-check", "haiku-3", "ACT") == ("ANSWER", "haiku")

        # the world drifted: one booked-wrong run on the SAME class
        _run(org, "d-miss", "format-check", "haiku-3", "haiku", "wrong")
        v, answer = org.route("format-check", "haiku-3", "ACT")
        assert v == "ACT"                 # revoked — dropped straight back to base
        assert answer is None

        # a fresh unrelated class for the same runner is unaffected
        _run(org, "d-other", "unit-tests", "haiku-3", "haiku", "correct")
        assert org.route("unit-tests", "haiku-3", "ACT") == ("ACT", None)

    def test_different_runners_earn_standing_independently(self):
        org = OrgBook("org.test")
        for i in range(DEFAULT_DIPLOMA):
            _run(org, f"a{i}", "grep-sweep", "haiku-1", "haiku", "correct")
        # haiku-4 has never run this class — no standing leaks across runners
        v, answer = org.route("grep-sweep", "haiku-4", "ESCALATE")
        assert v == "ESCALATE"
        assert answer is None

    def test_replay_reproduces_every_routing_decision_bit_for_bit(self):
        org = OrgBook("org.replay")
        live = []
        plan = [
            ("d1", "grep-sweep", "haiku-1", "haiku", "correct", "ACT"),  # streak 0 -> ACT
            ("d2", "grep-sweep", "haiku-1", "haiku", "correct", "ACT"),  # streak 1 -> ACT
            ("d3", "grep-sweep", "haiku-1", "haiku", "correct", "ACT"),  # streak 2 -> ACT
            ("d4", "grep-sweep", "haiku-1", "haiku", "correct", "ACT"),  # streak 3 -> earns ANSWER here
            ("d5", "grep-sweep", "haiku-1", "haiku", "wrong",   "ACT"),  # streak 4 -> still ANSWER; this run misses
            ("d6", "grep-sweep", "haiku-1", "haiku", "correct", "ACT"),  # the miss revoked it -> back to ACT
            ("d7", "unit-tests", "sonnet-1", "sonnet", "correct", "ESCALATE"),
        ]
        for dispatch_id, task_class, runner, tier, outcome, base in plan:
            v, answer = _run(org, dispatch_id, task_class, runner, tier, outcome, base_verdict=base)
            live.append((dispatch_id, runner, task_class, base, v, answer))

        replayed = [(d.dispatch_id, d.runner, d.task_class, d.base_verdict, d.verdict, d.answer)
                    for d in org.replay()]
        assert replayed == live
        # exactly the earn-then-revoke-then-rebuild shape
        assert [row[4] for row in live] == ["ACT", "ACT", "ACT", "ANSWER", "ANSWER", "ACT", "ESCALATE"]

    def test_replay_equals_live_on_a_freshly_rebuilt_orgbook_too(self):
        """The org's WAL is portable: replaying it on a brand-new OrgBook fed
        the exact same receipts (not just re-reading the live object) lands
        on the identical reconstructed decisions — replay ≡ live, not
        replay ≡ this particular Python object."""
        org = OrgBook("org.a")
        plan = [
            ("d1", "route", "runner-x", "sonnet", "correct", "ACT"),
            ("d2", "route", "runner-x", "sonnet", "correct", "ACT"),
            ("d3", "route", "runner-x", "sonnet", "correct", "ACT"),
        ]
        for dispatch_id, task_class, runner, tier, outcome, base in plan:
            _run(org, dispatch_id, task_class, runner, tier, outcome, base_verdict=base)

        rebuilt = OrgBook("org.b")
        rebuilt.book.entries = list(org.book.entries)   # same WAL, fresh object
        assert rebuilt.replay() == org.replay()

    def test_deterministic_pin_two_identical_orgbooks_agree(self):
        def build(name):
            org = OrgBook(name)
            for i in range(DEFAULT_DIPLOMA):
                _run(org, f"d{i}", "grep-sweep", "haiku-1", "haiku", "correct")
            _run(org, "d-extra", "grep-sweep", "haiku-1", "haiku", "correct")
            _run(org, "d-x", "unit-tests", "sonnet-1", "sonnet", "correct", base_verdict="ESCALATE")
            return org

        a = build("org.pin.a")
        b = build("org.pin.b")

        # same dispatch sequence, differently-named cells -> identical chain
        # and identical decisions digest: the pin is over the BOOKED
        # CONTENT, not the object identity or the cell's own name.
        assert a.chain() == b.chain()
        assert a.decisions_digest() == b.decisions_digest()

        # a divergent booked-wrong somewhere in the sequence, once a LATER
        # dispatch actually observes the revoked standing, changes both pins
        def build_with_a_miss(name):
            org = OrgBook(name)
            for i in range(DEFAULT_DIPLOMA):
                _run(org, f"d{i}", "grep-sweep", "haiku-1", "haiku", "correct")
            _run(org, "d-extra", "grep-sweep", "haiku-1", "haiku", "wrong")   # revokes standing
            _run(org, "d-x", "unit-tests", "sonnet-1", "sonnet", "correct", base_verdict="ESCALATE")
            return org

        c = build_with_a_miss("org.pin.c")
        assert c.chain() != a.chain()
        assert c.decisions_digest() == a.decisions_digest()   # the miss itself isn't yet OBSERVED by a later route()

        # now let each org route grep-sweep once more: the observed decision
        # (ANSWER for a/b, ACT for c — the revocation finally shows up) is
        # exactly what diverges the decisions digest, not the raw WAL alone
        _run(a, "d-observe", "grep-sweep", "haiku-1", "haiku", "correct")
        _run(c, "d-observe", "grep-sweep", "haiku-1", "haiku", "correct")
        assert a.decisions_digest() != c.decisions_digest()
        last_a = a.replay()[-1]
        last_c = c.replay()[-1]
        assert last_a.verdict == "ANSWER"
        assert last_c.verdict == "ACT"

    def test_record_dispatch_books_a_real_receipt_law4(self):
        org = OrgBook("org.test")
        r = org.record_dispatch("d001", "haiku", "grep-sweep", "haiku-1", "ACT", "correct")
        assert r.tick == 1
        assert r.decision_kind == "ACT"
        assert org.book.entries == [r]
        assert org.book.verify()   # structurally sound WAL: ticks 1..N, no gaps


if __name__ == "__main__":
    unittest.main()
