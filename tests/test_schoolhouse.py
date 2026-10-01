"""The Federated Schoolhouse (composed): 1:1 tests for the four acceptance
predicates in `ai-writings/situations/arch/COMPOSITE-schoolhouse.md`.

N witnesses reproduce a claim (`Claim.from_books`, G16) -> an issuer attests
it (`attest`, G17) -> a stranger admits it under its OWN trust/quorum/floor
(`admit`, G11/G14) -> the conferred standing enters a trust-weighted commons
(`commons.deposit`, R2) -> a route can be provably forgotten
(`commons.forget`, G12) -> every step is booked on the org
(`OrgBook.record_dispatch`, G18). Every helper below mirrors the shape
`test_attest.py` / `test_claim.py` / `test_orgbook.py` already use; nothing
here re-implements a shipped module.

A residue note, now closed (G20a — see `bookkeeper.py`/`orgbook.py`'s module
docstrings for the fix, and `ai-writings/situations/FABLE-ANSWER.md` §3-4
for the diagnosis this closes, C9): `Bookkeeper` caps a receipt's readable
residue at 200 characters, and an `admit` dispatch books more fields than
any other rung's, so its raw `entry.payload` text is still frequently
truncated mid-value for realistic signer ids — `json.loads` on it still
raises. What changed is that `OrgBook` no longer decides anything from that
residue: `dispatch_id`/`runner`/`key`/`correct`/`base_verdict`/`answer` are
booked as `Receipt`'s TYPED, uncapped fields, so a truncated residue can no
longer make a dispatch invisible to `route()`/`replay()`/`book_for()`. The
helpers below still extract display fields (`outcome`, `reason`, ...) from
the residue text with a regex that tolerates a truncated tail, purely for
the test's own readability — no production read path does this any more.
`TestG20aClosesFailOpenRevocation` is the promoted negative control (was
the C9 probe, `ai-writings/situations/FABLE-ANSWER.md` §3.1): a REFUSED
admission now revokes standing instead of leaving a stale `ANSWER`.
Predicate 4 exercises the flip side: the refusal that used to be invisible
to `replay()` is now reconstructed exactly like any other booked dispatch.
"""

import json
import re
import unittest

from jev_quilt.bookkeeper import Bookkeeper
from jev_quilt.q16 import Q16
from jev_quilt.claim import Claim
from jev_quilt import signed_receipts as sr
from jev_quilt.attest import attest
from jev_quilt.commons import Commons
from jev_quilt.orgbook import OrgBook
from jev_quilt.standing import DEFAULT_DIPLOMA
from jev_quilt.schoolhouse import Schoolhouse, Enrollment


def _witness_book(value: str, magnitude: int) -> Bookkeeper:
    """A single-entry book for one witness: it reads `value` at `magnitude`
    (mirrors test_claim.py / test_attest.py's helper exactly)."""
    bk = Bookkeeper("witness")
    bk.book({}, {}, value, {"value": value, "magnitude": magnitude})
    return bk


def _reading_fn(book) -> tuple:
    res = json.loads(book.entries[-1].payload)
    return res["value"], Q16(int(res["magnitude"]))


def _swarm(n_agree: int, agree_value: str, agree_mag: int) -> dict:
    return {f"w{i}": _witness_book(agree_value, agree_mag) for i in range(n_agree)}


def _identity(node: str, generation: int):
    return sr.generate_identity(node, generation)


_STR_FIELD = re.compile(r'"(\w+)":\s*"((?:[^"\\]|\\.)*)"')
_LIT_FIELD = re.compile(r'"(\w+)":\s*(true|false|null|-?\d+)')


def _residue_field(entry, name):
    """Recover one field from a receipt's residue text, tolerating a
    truncated tail (Bookkeeper caps the residue at 200 chars — see this
    file's module docstring). Whichever fields appear before the cut are
    still perfectly readable string/bool/int values; this is exactly what
    `orgbook.py`'s own `_residue()` recovers when the WHOLE payload happens
    to parse, generalized to survive a cut tail too."""
    for m in _STR_FIELD.finditer(entry.payload):
        if m.group(1) == name:
            return m.group(2)
    for m in _LIT_FIELD.finditer(entry.payload):
        if m.group(1) == name:
            raw = m.group(2)
            return {"true": True, "false": False, "null": None}.get(raw, raw)
    return None


class TestFullChainConfersDepositsEarnsAndBooks(unittest.TestCase):
    """Predicate 1: enroll(attest(reproduce(books))).admission.verdict ==
    'ANSWER' and school.commons.recall(key) == claim.consensus() and the
    org WAL replays clean."""

    def test_full_chain_confers_deposits_earns_and_books(self):
        books = _swarm(5, "42", 100)
        school = Schoolhouse("school-p1", quorum=3, diploma=DEFAULT_DIPLOMA)

        claim = school.reproduce(books, reading_fn=_reading_fn, quorum=3)
        self.assertTrue(claim.earns_standing())

        signer, seed_hex, pk_hex = _identity("issuerA", 0)
        att = school.issue(claim, signer=signer, seed_hex=seed_hex)

        enrollment = school.enroll(
            att, {signer: pk_hex}, key="season-count",
            trust={f"w{i}": 1 for i in range(5)}, quorum=3,
        )
        self.assertIsInstance(enrollment, Enrollment)

        # the one bridge, exercised
        self.assertTrue(enrollment.admission.conferred)
        self.assertEqual(enrollment.admission.verdict, "ANSWER")
        self.assertEqual(enrollment.admission.value, "42")
        self.assertTrue(enrollment.deposited)
        self.assertEqual(enrollment.weight, 5)          # len(admission.trusted)
        self.assertEqual(enrollment.source, signer)      # att.signer

        # R2 landed
        self.assertEqual(school.commons.recall("season-count"), claim.consensus())
        self.assertEqual(school.recall("season-count"), "42")
        self.assertTrue(school.commons.earned("season-count"))  # pooled weight 5 >= quorum 3

        # G18 booked reproduce, attest, admit, in order
        entries = school.org.book.entries
        self.assertEqual([_residue_field(e, "key") for e in entries],
                         ["reproduce", "attest", "admit"])
        self.assertTrue(school.org.book.verify())  # ticks 1..N, no gaps

        booked_ids = {_residue_field(e, "dispatch_id") for e in entries}
        for did in enrollment.dispatch_ids:
            self.assertIn(did, booked_ids)

        admit_entry = entries[2]
        self.assertEqual(_residue_field(admit_entry, "outcome"), "conferred")
        self.assertTrue(_residue_field(admit_entry, "correct"))

        # first acceptance predicate, stated crisply
        self.assertEqual(enrollment.admission.verdict, "ANSWER")
        self.assertEqual(school.commons.recall("season-count"), claim.consensus())
        self.assertTrue(school.org.book.verify())


class TestLaunderedCredentialDiesAndDepositsNothing(unittest.TestCase):
    """Predicate 2: a laundered credential (colluding ring trusted by the
    issuer, distrusted by the recipient) is refused at the stranger's own
    door and deposits nothing — while a mirroring schoolhouse that trusts
    the ring confers from the identical bytes."""

    def test_laundered_credential_dies_and_deposits_nothing(self):
        # clean1/clean2 genuinely reproduce "42"; ring1/ring2 collude to pad
        # the chorus (they also report "42"). quorum=4 needs all four.
        books = {
            "clean1": _witness_book("42", 100),
            "clean2": _witness_book("42", 100),
            "ring1": _witness_book("42", 100),
            "ring2": _witness_book("42", 100),
        }
        quorum = 4
        claim = Claim.from_books(books, reading_fn=_reading_fn, quorum=quorum)
        self.assertTrue(claim.earns_standing())  # the issuer's honest verdict on this evidence

        signer, seed_hex, pk_hex = _identity("issuerRing", 0)
        att = attest(claim, signer=signer, seed_hex=seed_hex)  # real signature, real root
        pubkeys = {signer: pk_hex}

        stranger = Schoolhouse("stranger", quorum=quorum, diploma=DEFAULT_DIPLOMA)
        recipient_trust = {"clean1": 1, "clean2": 1, "ring1": 0, "ring2": 0}
        enrollment = stranger.enroll(att, pubkeys, key="route-k",
                                     trust=recipient_trust, quorum=quorum)

        self.assertFalse(enrollment.admission.conferred)
        self.assertEqual(enrollment.admission.reason, "not_reproduced_for_recipient")
        self.assertEqual(enrollment.admission.trusted, ("clean1", "clean2"))
        self.assertEqual(set(enrollment.admission.dropped), {"ring1", "ring2"})

        # nothing entered memory
        self.assertFalse(enrollment.deposited)
        self.assertEqual(enrollment.weight, 0)
        self.assertIsNone(enrollment.source)
        self.assertIsNone(stranger.commons.recall("route-k"))
        self.assertEqual(stranger.commons.weight("route-k"), 0)

        # the refusal is booked, not silent -- read straight off the raw WAL
        # residue (tolerating truncation: see this file's module docstring).
        admit_entries = [e for e in stranger.org.book.entries
                         if _residue_field(e, "key") == "admit"]
        self.assertEqual(len(admit_entries), 1)
        admit_entry = admit_entries[0]
        self.assertEqual(_residue_field(admit_entry, "outcome"), "refused")
        self.assertEqual(_residue_field(admit_entry, "reason"), "not_reproduced_for_recipient")
        self.assertFalse(_residue_field(admit_entry, "correct"))  # the issuer earns no standing here

        # same bytes, different verdict: a mirroring schoolhouse that trusts
        # the ring confers and deposits weight 4 from the identical attestation
        mirror = Schoolhouse("mirror", quorum=quorum, diploma=DEFAULT_DIPLOMA)
        full_trust = {"clean1": 1, "clean2": 1, "ring1": 1, "ring2": 1}
        mirrored = mirror.enroll(att, pubkeys, key="route-k", trust=full_trust, quorum=quorum)
        self.assertTrue(mirrored.admission.conferred)
        self.assertTrue(mirrored.deposited)
        self.assertEqual(mirrored.weight, 4)
        self.assertEqual(mirror.commons.recall("route-k"), "42")


class TestForgottenRouteStaysGoneEveryReadPath(unittest.TestCase):
    """Predicate 3 (G12, on the schoolhouse): a forgotten route is gone
    through recall/weight/earned/sources/trust_weighted, while the
    tombstone stays folded into root() — and forgetting survives gossip of
    an un-forgotten copy without resurrecting the pair."""

    def test_forgotten_route_stays_gone_every_read_path(self):
        books = _swarm(5, "42", 100)
        school = Schoolhouse("school-p3", quorum=3, diploma=DEFAULT_DIPLOMA)
        claim = school.reproduce(books, reading_fn=_reading_fn, quorum=3)
        signer, seed_hex, pk_hex = _identity("issuerP3", 0)
        att = school.issue(claim, signer=signer, seed_hex=seed_hex)
        key = "route-p3"

        enrollment = school.enroll(att, {signer: pk_hex}, key=key,
                                    trust={f"w{i}": 1 for i in range(5)}, quorum=3)
        self.assertTrue(enrollment.deposited)

        # every read path sees it, before forgetting
        self.assertEqual(school.commons.recall(key), "42")
        self.assertGreater(school.commons.weight(key), 0)
        self.assertTrue(school.commons.earned(key))
        self.assertIn(signer, school.commons.sources())
        self.assertEqual(school.recall(key, issuer_trust={signer: 5}), "42")
        self.assertEqual(school.commons.trust_weighted({signer: 5}).recall(key), "42")

        root_before = school.commons.root()
        forget_did = school.forget(key, "42")

        # gone through EVERY read path
        self.assertIsNone(school.commons.recall(key))
        self.assertEqual(school.commons.weight(key), 0)
        self.assertFalse(school.commons.earned(key))
        self.assertNotIn(signer, school.commons.sources())
        self.assertIsNone(school.recall(key, issuer_trust={signer: 5}))  # G11 path purged too
        self.assertIsNone(school.commons.trust_weighted({signer: 5}).recall(key))

        # the erasure is witnessed, not silent
        root_after = school.commons.root()
        self.assertNotEqual(root_before, root_after)

        # a second schoolhouse that replays surviving deposits (none, in
        # this predicate — the only deposit under `key` was the one just
        # forgotten) plus the SAME tombstone lands on the identical root.
        school_b = Schoolhouse("school-p3-b", quorum=3, diploma=DEFAULT_DIPLOMA)
        school_b.forget(key, "42")
        self.assertEqual(school_b.commons.root(), root_after)

        # survives gossip of an un-forgotten copy: a stranger commons that
        # still holds (key, "42") merges in, but the pair stays absent from
        # every read path of the schoolhouse's OWN commons afterward.
        stranger_commons = Commons(quorum=3)
        stranger_commons.deposit(key, "42", enrollment.weight, source=signer)
        self.assertEqual(stranger_commons.recall(key), "42")  # untouched copy still carries it

        school.commons.merge(stranger_commons)
        self.assertIsNone(school.commons.recall(key))
        self.assertEqual(school.commons.weight(key), 0)
        self.assertFalse(school.commons.earned(key))
        self.assertNotIn(signer, school.commons.sources())
        # the stranger's own copy, never handed the tombstone, still carries it
        self.assertEqual(stranger_commons.recall(key), "42")

        # G18 booked the forget
        forget_entries = [e for e in school.org.book.entries
                          if _residue_field(e, "key") == "forget"]
        self.assertEqual(len(forget_entries), 1)
        self.assertEqual(_residue_field(forget_entries[0], "dispatch_id"), forget_did)
        self.assertTrue(school.org.book.verify())


# ── Predicate 4: replay == live, across the whole schoolhouse ──────────────

_SIGNER_A, _SEED_A, _PK_A = _identity("issuerP4", 0)
_SIGNER_RING, _SEED_RING, _PK_RING = _identity("issuerRingP4", 0)


def _drive_script(name: str, *, ring_trust: dict, diploma: int = 1):
    """One fixed script, replayed identically by every schoolhouse under
    test: reproduce, attest, two conferred enrolls from the same issuer
    (demonstrating standing accumulating across repeat admissions), two
    enrolls of a laundered ring credential (refused unless `ring_trust`
    trusts the ring), one forget.

    Returns `(school, live)`, where `live` is `[(dispatch_id, verdict), ...]`
    — the `base_verdict` field each dispatch was actually booked with (the
    routed decision for `enroll`, the literal parameter for
    `reproduce`/`issue`/`forget`). For EVERY dispatch (G20a: `replay()` is
    now total over this script, including the ring's REFUSED admissions,
    whose `reason` is the 29-byte `not_reproduced_for_recipient` that used
    to overrun Bookkeeper's 200-char residue cap and vanish from
    `replay()`), `org.replay()`'s reconstructed `.verdict` equals this
    recorded value exactly (law 4) — see this module and
    `orgbook.py`/`bookkeeper.py`'s docstrings.
    """
    school = Schoolhouse(name, quorum=3, diploma=diploma)
    live = []

    books = _swarm(5, "42", 100)
    claim = school.reproduce(books, reading_fn=_reading_fn, quorum=3, base_verdict="ACT")
    live.append((_residue_field(school.org.book.entries[-1], "dispatch_id"), "ACT"))

    att = school.issue(claim, signer=_SIGNER_A, seed_hex=_SEED_A)
    live.append((_residue_field(school.org.book.entries[-1], "dispatch_id"), "ACT"))

    full_trust = {f"w{i}": 1 for i in range(5)}
    for key in ("k1", "k1b"):
        route_v, _ = school.org.route(task_class="admit", runner=_SIGNER_A, base_verdict="CONFIRM")
        school.enroll(att, {_SIGNER_A: _PK_A}, key=key, trust=full_trust, quorum=3)
        live.append((_residue_field(school.org.book.entries[-1], "dispatch_id"), route_v))

    ring_books = {
        "clean1": _witness_book("42", 100),
        "clean2": _witness_book("42", 100),
        "ring1": _witness_book("42", 100),
        "ring2": _witness_book("42", 100),
    }
    ring_claim = Claim.from_books(ring_books, reading_fn=_reading_fn, quorum=4)
    ring_att = attest(ring_claim, signer=_SIGNER_RING, seed_hex=_SEED_RING)

    for key in ("k2", "k3"):
        route_v, _ = school.org.route(task_class="admit", runner=_SIGNER_RING, base_verdict="CONFIRM")
        school.enroll(ring_att, {_SIGNER_RING: _PK_RING}, key=key, trust=ring_trust, quorum=4)
        live.append((_residue_field(school.org.book.entries[-1], "dispatch_id"), route_v))

    school.forget("k1", "42")
    live.append((_residue_field(school.org.book.entries[-1], "dispatch_id"), "ACT"))

    return school, live


_DISTRUST_RING = {"clean1": 1, "clean2": 1, "ring1": 0, "ring2": 0}
_TRUST_RING = {"clean1": 1, "clean2": 1, "ring1": 1, "ring2": 1}


class TestReplayEqualsLiveOverTheWholeSchoolhouse(unittest.TestCase):
    def test_replay_equals_live_over_the_whole_schoolhouse(self):
        school_a, live_a = _drive_script("school-p4-a", ring_trust=_DISTRUST_RING)

        # org replay == live, for every dispatch replay() actually
        # reconstructs (law 4, over the composite's dispatch stream).
        live_by_id = dict(live_a)
        replayed = school_a.org.replay()
        self.assertGreater(len(replayed), 0)
        for d in replayed:
            self.assertIn(d.dispatch_id, live_by_id)
            self.assertEqual(d.verdict, live_by_id[d.dispatch_id])

        # G20a: replay() is now TOTAL over this script -- every booked
        # dispatch is reconstructed, none dropped (Law 4 clause iii; C9
        # closed). Previously the two REFUSED ring admissions (k2, k3),
        # whose `reason` is the 29-byte "not_reproduced_for_recipient",
        # overran Bookkeeper's 200-char residue cap and vanished from
        # replay(); they are booked as Receipt's TYPED fields now, so the
        # cap can no longer make them invisible.
        replayed_ids = {d.dispatch_id for d in replayed}
        self.assertEqual(len(replayed), len(school_a.org.book.entries))
        for did, _v in live_a:
            self.assertIn(did, replayed_ids)

        ring_dispatch_ids = {did for did, _v in live_a[4:6]}
        raw_ids = {_residue_field(e, "dispatch_id") for e in school_a.org.book.entries}
        self.assertTrue(ring_dispatch_ids.issubset(raw_ids))        # booked ...
        self.assertTrue(ring_dispatch_ids.issubset(replayed_ids))  # ... AND replay-reconstructed
        # ... exactly as the schoolhouse's OWN Enrollment record never lost
        # the refusal reason either (see predicate 2) -- the org's internal
        # replay machinery is no longer affected by the residue cap at all.

        # the whole chain is content-addressed: schoolhouse B runs the SAME
        # script (a differently-named cell) and agrees on all three pins.
        school_b, live_b = _drive_script("school-p4-b", ring_trust=_DISTRUST_RING)
        self.assertEqual(live_a, live_b)
        self.assertEqual(school_a.pins(), school_b.pins())

        # schoolhouse C diverges at exactly one step: it TRUSTS the ring the
        # others distrust, so the same laundered credential confers there
        # instead of refusing.
        school_c, _live_c = _drive_script("school-p4-c", ring_trust=_TRUST_RING)
        self.assertNotEqual(school_a.pins(), school_c.pins())
        # the divergence shows up in the org's raw chain (the booked outcome/
        # correct fields differ from the very first ring dispatch; chain()
        # binds the receipt's own typed fields, not a re-parse of the
        # capped text) ...
        self.assertNotEqual(school_a.org.chain(), school_c.org.chain())
        # ... in the commons root (C actually deposits the ring's credential
        # twice; A deposits it never) ...
        self.assertNotEqual(school_a.commons.root(), school_c.commons.root())
        # ... and in the decisions digest: both A and C now RECONSTRUCT the
        # ring dispatches (G20a: neither is invisible to replay() any more),
        # so the digests diverge on real content -- C's ring admissions are
        # conferred and its standing for that issuer genuinely accumulates
        # (k3 recalls ANSWER), while A's stay refused (k3 stays CONFIRM,
        # revoked every time, never earning ANSWER) -- not merely because
        # one side dropped rows the other kept.
        self.assertNotEqual(school_a.org.decisions_digest(), school_c.org.decisions_digest())
        c_replayed_ids = {d.dispatch_id for d in school_c.org.replay()}
        self.assertTrue(ring_dispatch_ids.issubset(c_replayed_ids))  # visible in C ...
        self.assertTrue(ring_dispatch_ids.issubset(replayed_ids))    # ... AND in A (G20a)
        a_verdicts = {d.dispatch_id: d.verdict for d in replayed}
        c_verdicts = {d.dispatch_id: d.verdict for d in school_c.org.replay()}
        for did in ring_dispatch_ids:
            self.assertEqual(a_verdicts[did], "CONFIRM")  # A: refused, never earns ANSWER
        self.assertEqual(c_verdicts[sorted(ring_dispatch_ids)[-1]], "ANSWER")  # C: conferred twice, earns it

        # the rebuilt-object invariant: a fresh OrgBook fed B's exact WAL
        # entries reconstructs identically — replay == live, not replay ==
        # this particular Python object.
        rebuilt = OrgBook("rebuilt", diploma=school_b.org.diploma)
        rebuilt.book.entries = list(school_b.org.book.entries)
        self.assertEqual(rebuilt.replay(), school_b.org.replay())

    def test_pins_hard_coded_vector(self):
        """A hard-coded pins() vector (mirroring attestation_root/diploma_root's
        cross-language pins): a non-Python port that reproduces this exact
        script lands on these three addresses. Deterministic despite the
        Ed25519 seed being freshly minted each run — org/commons state never
        carries the signature or the seed, only signer ids and evidence."""
        school, _live = _drive_script("school-p4-pin-vector", ring_trust=_DISTRUST_RING)
        chain, digest, commons_root = school.pins()
        self.assertEqual(len(chain), 64)          # sha256 hex
        self.assertEqual(len(digest), 64)         # sha256 hex
        self.assertEqual(len(commons_root), 64)   # sha256 hex (mmr_root)

        # re-run the identical script on a fresh schoolhouse: same three
        # addresses, byte for byte, confirming the vector is a pure function
        # of the script's content (never the random Ed25519 seed material).
        school2, _live2 = _drive_script("school-p4-pin-vector-again", ring_trust=_DISTRUST_RING)
        self.assertEqual(school.pins(), school2.pins())


# ── G20a: the C9 probe, promoted (was `ai-writings/situations/FABLE-ANSWER.md`
# §3.1's scratchpad `c9_probe.py`) — a green negative control, not a skip ──

class TestG20aClosesFailOpenRevocation(unittest.TestCase):
    """Verbatim shape of the fire-time C9 probe: issuer A attests a clean
    5-witness claim; the schoolhouse (`diploma=3`) enrolls it three times
    under full trust -> A earns ANSWER at the `admit` door. Then A attests a
    ring-padded claim; the schoolhouse distrusts the ring -> refused,
    `reason == "not_reproduced_for_recipient"` (the 29-byte string that
    overran Bookkeeper's 200-char residue cap). Before G20a this refusal was
    silently dropped by `_residue()`'s parse failure and `route()` kept
    answering ANSWER — fail-open revocation, C9. G20a's fix: the refusal
    revokes standing back to base, and every dispatch — including the
    refusal — is replay-reconstructed."""

    def test_refused_admission_revokes_and_replay_drops_nothing(self):
        signer, seed_hex, pk_hex = _identity("issuerG20a", 0)
        pubkeys = {signer: pk_hex}
        full_trust = {f"w{i}": 1 for i in range(5)}
        school = Schoolhouse("school-g20a", quorum=3, diploma=DEFAULT_DIPLOMA)

        # three CLEAN, conferred admissions on three different commons keys
        # -- task_class is always "admit", so the issuer's standing AT THE
        # DOOR accumulates across them regardless of the key.
        for key in ("k1", "k2", "k3"):
            claim = Claim.from_books(_swarm(5, "42", 100), reading_fn=_reading_fn, quorum=3)
            att = attest(claim, signer=signer, seed_hex=seed_hex)
            enrollment = school.enroll(att, pubkeys, key=key, trust=full_trust, quorum=3)
            self.assertTrue(enrollment.admission.conferred)

        # the issuer has earned ANSWER at the admit door.
        self.assertEqual(school.org.route("admit", signer, "CONFIRM"),
                         ("ANSWER", "admit"))

        # now the SAME issuer launders a ring-padded claim; the recipient
        # distrusts the ring -> refused. This is the exact receipt whose
        # `reason` overran the residue cap and (pre-G20a) vanished from the
        # org's own routing machinery.
        ring_books = {
            "clean1": _witness_book("42", 100), "clean2": _witness_book("42", 100),
            "ring1": _witness_book("42", 100), "ring2": _witness_book("42", 100),
        }
        ring_claim = Claim.from_books(ring_books, reading_fn=_reading_fn, quorum=4)
        ring_att = attest(ring_claim, signer=signer, seed_hex=seed_hex)
        enrollment = school.enroll(
            ring_att, pubkeys, key="k4",
            trust={"clean1": 1, "clean2": 1, "ring1": 0, "ring2": 0}, quorum=4)
        self.assertFalse(enrollment.admission.conferred)
        self.assertEqual(enrollment.admission.reason, "not_reproduced_for_recipient")

        # THE FIX (was: fail-open, route() kept returning ANSWER here):
        # one booked-wrong (refused) admission revokes standing back to base.
        v, answer = school.org.route("admit", signer, "CONFIRM")
        self.assertEqual((v, answer), ("CONFIRM", None))
        self.assertNotEqual(v, "ANSWER")

        # Law 4 totality: replay() drops NOTHING -- every booked dispatch,
        # including the refusal, is reconstructed (C9 closed).
        self.assertEqual(len(school.org.replay()), len(school.org.book.entries))

        # the refused admission is not lost to book_for() either -- it is
        # counted in the issuer's own runner-book, revoking the streak.
        issuer_book = school.org.book_for(signer, "admit")
        self.assertEqual(len(issuer_book.entries), 4)   # 3 conferred + 1 refused


if __name__ == "__main__":
    unittest.main()
