"""The Federated Schoolhouse: the shipped rung-spine composed into one
walkable path (bootstrap-gate #1 — "the spine is composed, not just
shipped").

Every rung below is shipped and untouched; this module re-implements none
of them. It is the *sentence*, not a new word: N witnesses reproduce a
claim (`Claim.from_books`, G16) -> an issuer attests it (`attest`, G17) ->
a stranger admits it under its OWN trust/quorum/floor (`admit`, G11/G14)
-> the conferred standing enters a trust-weighted commons (`commons.
deposit`, R2) -> a route can be provably forgotten (`commons.forget`,
G12) -> every step is booked on the org (`OrgBook.record_dispatch`, G18).

The one genuinely new surface is the `Admission` -> `Commons.deposit`
bridge (see `Schoolhouse.enroll`): *when a stranger's attestation confers
standing on this node, what enters the commons, at what weight, tagged as
whose?* Resolved here, at dispatch altitude:

  * **Answer = `admission.value`** — the recipient's own recomputed
    consensus, never the issuer's advisory `att.consensus`.
  * **Weight = `len(admission.trusted)`** — the count of trusted,
    non-drifting witnesses THIS recipient actually counted. Integer,
    exact, and it is the recipient's own honest measure of the evidence.
  * **Source = `att.signer`** (the issuer) — so the commons can be read a
    SECOND time through `trust_weighted`, over issuers rather than
    witnesses: G11 applied twice, once at the witness layer (inside
    `admit`) and once at the credential layer (over the commons).
  * **Refused => deposit nothing.** The org still books the refusal, with
    its reason — refusal is a first-class ledger row, never a silent gap.
  * **Correct = `conferred`** for the admission dispatch's org receipt
    (Law 5): the acceptance test of "admit this credential" is "did it
    confer standing for me?" An issuer whose padded credentials keep
    being refused never accrues booked-correct runs here.

Additive only. No import from this module reaches into another module's
internals; every call below is a call to a shipped public function,
followed by a `record_dispatch`.

Honest limits (inherited, not resolved here — see
`ai-writings/situations/arch/COMPOSITE-schoolhouse.md` for the full
discussion): both "kernels" exercised anywhere near this module are the
same Python implementation (cross-*instance*, not cross-*language*
federation); forgetting is local-until-gossiped (`commons.merge`'s
tombstone rule, unchanged); whether trust should compose as a single
associative algebra across the witness/issuer/org layers, rather than the
serial, gated composition built here, is filed as an open law-level
question (candidate C8), not answered by this build.

**Closed (G20a — was a newly discovered honest limit, found composing this
module: C9, fail-open revocation).** The `admit` dispatch books more fields
for this rung (tier/task_class/runner/verdict/outcome/correct/key/
base_verdict) than any other rung's, plus this module's own `reason` extra
on a refusal; a REFUSED admission's `reason` is `attest.admit`'s
`"not_reproduced_for_recipient"` (29 bytes) — carrying it still pushes the
JSON-encoded RESIDUE (the capped, human-readable audit render;
`bookkeeper.py`'s docstring) over 200 characters for *any* signer id
length. That render staying capped is fine now: `record_dispatch` also
hands `Bookkeeper.book()` this dispatch's identity as TYPED, uncapped
fields (`dispatch_id`, `runner`, `key`, `correct`, `base_verdict`,
`answer` — see `bookkeeper.py`/`orgbook.py`'s module docstrings), and
`OrgBook.route()`/`replay()`/`book_for()` read those, never the residue.
A REFUSED admission is therefore booked, replay-reconstructed, and
revokes the issuer's standing exactly like any other booked-wrong
outcome — no longer invisible to the org's own routing machinery just
because its human-readable render overran a display cap.
`tests/test_schoolhouse.py`'s `TestG20aClosesFailOpenRevocation` is the
promoted negative control (was the fire-time C9 probe); predicate 4
exercises the flip side (`replay()` is now total over a script that
includes a refusal).
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional

from .claim import Claim
from .attest import Attestation, Admission, attest, admit
from .commons import Commons
from .orgbook import OrgBook
from .calibrate import CalibratedFloor
from .q16 import Q16
# NOTE: no re-implementation of reproduction, signing, admission, deposit,
# forgetting, or routing. This file is the *sentence*, not a new word.


@dataclass(frozen=True)
class Enrollment:
    """One credential's walk of the whole spine, as the schoolhouse booked it.

    `admission` is the recipient's OWN verdict (attest.admit) — never the
    issuer's. `deposited`/`weight` record what entered the commons (R2). Nothing
    here is a second decision procedure: every field is a value some shipped
    function returned, plus the org rows this enrollment wrote."""
    key: str
    admission: Admission
    deposited: bool
    weight: int                      # pooled evidence deposited = len(admission.trusted); 0 if refused
    source: Optional[str]            # the issuer id the deposit is tagged with (provenance for L2 trust)
    dispatch_ids: tuple              # tuple[str, ...] — the org receipts this enrollment booked


class Schoolhouse:
    """A node that admits strangers' credentials on its own authority and keeps
    a living, forgettable, replay-verifiable memory of what it came to trust.

    Holds exactly two pieces of durable state, both already replay-verifiable
    on their own: an `OrgBook` (the WAL of every schoolhouse action, G18) and a
    `Commons` (the trust-weighted, forgettable memory of admitted routes, R2/G11/
    G12). It adds no third store and no float."""

    def __init__(self, name: str = "schoolhouse", *, quorum: int, diploma: int):
        self.org = OrgBook(name, diploma=diploma)
        self.commons = Commons(quorum=quorum)
        self._n = 0                  # monotonic dispatch counter, for stable ids

    def _next_id(self, phase: str) -> str:
        self._n += 1
        return f"{phase}-{self._n:04d}"

    # ── G16: reproduce, booked ──────────────────────────────────────────
    def reproduce(self, books: dict, *, reading_fn: Callable, quorum: int,
                  floor: Optional[CalibratedFloor] = None,
                  runner: str = "swarm", base_verdict: str = "ACT") -> Claim:
        claim = Claim.from_books(books, reading_fn=reading_fn, quorum=quorum, floor=floor)
        did = self._next_id("reproduce")
        self.org.record_dispatch(did, tier="claim", task_class="reproduce",
                                 runner=runner, verdict=base_verdict,
                                 outcome=("viable" if claim.earns_standing() else "halt"),
                                 base_verdict=base_verdict, answer=base_verdict)
        return claim

    # ── G17: issue, booked ──────────────────────────────────────────────
    def issue(self, claim: Claim, *, signer: str, seed_hex: str,
              floor: Optional[Q16] = None) -> Attestation:
        att = attest(claim, signer=signer, seed_hex=seed_hex, floor=floor)  # refuses if unreproduced
        did = self._next_id("attest")
        self.org.record_dispatch(did, tier="attest", task_class="attest",
                                 runner=signer, verdict="ACT", outcome="viable",
                                 base_verdict="ACT", answer="ACT")
        return att

    # ── G11 + G14 + R2 + G18: admit under OWN trust, deposit if conferred, book ──
    def enroll(self, att: Attestation, pubkeys: dict, *, key: str,
               trust: dict, quorum: int,
               floor: Optional[CalibratedFloor] = None,
               reading_magnitude: Optional[Callable] = None,
               base_verdict: str = "CONFIRM") -> Enrollment:
        """Admit `att` on the SCHOOLHOUSE's own authority, and — iff conferred —
        deposit the conferred standing into the commons, tagged by the issuer.
        The org books the admission dispatch, routed by the ISSUER's standing at
        this door: correct = conferred, so an issuer whose credentials keep being
        refused (padded with untrusted rings) never earns a fast path here."""
        a = admit(att, pubkeys, trust=trust, quorum=quorum, floor=floor,
                  reading_magnitude=reading_magnitude, base_verdict=base_verdict)
        dids = []

        # THE ONE BRIDGE (see module docstring): a conferred admission becomes
        # R2 memory.
        deposited, weight, source = False, 0, None
        if a.conferred:
            weight = len(a.trusted)                        # integer, exact: how many trusted witnesses reproduced
            source = att.signer                             # provenance → second-layer G11 over issuers
            self.commons.deposit(key, a.value, weight, source=source)
            deposited = True

        # G18: book the admission, routed by the issuer's own booked history here.
        did = self._next_id("admit")
        route_v, _ = self.org.route(task_class="admit", runner=att.signer,
                                    base_verdict=base_verdict)
        # NOTE (residue budget — see the module docstring's honest limit):
        # `answer` is left to record_dispatch's own default (= tier) rather
        # than repeated as `a.verdict`, a pure duplicate of `verdict` just
        # below; `reason` is added ONLY when refused (`a.reason is None` on
        # every conferred admission already, so adding a `"reason": null`
        # extra there would cost bytes for zero information — `_residue`
        # reads an absent key and a null-valued key identically). Both are
        # real bytes saved, not cosmetic: Bookkeeper caps the readable
        # residue at 200 chars (immutable, bookkeeper.py), and this
        # dispatch already books more fields than any other rung's. The
        # trims keep every CONFERRED admission comfortably under the cap
        # for any reasonably-named signer. They cannot save the one case
        # that remains genuinely over budget: a REFUSED admission whose
        # `reason` is the 29-byte "not_reproduced_for_recipient" overruns
        # the cap regardless of signer-id length (the other eight mandatory
        # fields alone already consume it), so that specific dispatch stays
        # invisible to `OrgBook.replay()`/`route()`/`book_for()` — though
        # it remains, truthfully, in the raw WAL and in this call's own
        # `Enrollment`.
        extra = {"reason": a.reason} if a.reason is not None else {}
        self.org.record_dispatch(
            did, tier="admit", task_class="admit", runner=att.signer,
            verdict=a.verdict, outcome=("conferred" if a.conferred else "refused"),
            base_verdict=route_v, correct=a.conferred,
            **extra)                                          # refusal reason is a booked field, never silent
        dids.append(did)
        return Enrollment(key=key, admission=a, deposited=deposited,
                          weight=weight, source=source, dispatch_ids=tuple(dids))

    # ── G12: forget, booked, through every read path ───────────────────
    def forget(self, key: str, answer: Optional[str] = None, *,
               runner: str = "custodian") -> str:
        self.commons.forget(key, answer)                    # tombstone folded into commons.root()
        did = self._next_id("forget")
        self.org.record_dispatch(did, tier="custodian", task_class="forget",
                                 runner=runner, verdict="ACT", outcome="viable",
                                 base_verdict="ACT", answer="ACT")
        return did

    # ── reading the memory, optionally through a SECOND layer of trust ──
    def recall(self, key: str, *, issuer_trust: Optional[dict] = None) -> Optional[str]:
        """The schoolhouse's best admitted answer for `key`. With `issuer_trust`,
        the commons is first re-scaled by each ISSUER's earned trust (a stranger
        issuer defaults to 0) — G11 applied a second time, at the credential layer
        rather than the witness layer. Without it, a plain pooled-weight recall."""
        c = self.commons.trust_weighted(issuer_trust) if issuer_trust is not None else self.commons
        return c.recall(key)

    # ── the three pins (content-addressed agreement over the whole chain) ──
    def pins(self) -> tuple:
        """(org WAL chain, org decisions digest, commons root) — the three
        32-byte-ish content addresses that make the WHOLE schoolhouse
        replay-verifiable. Two schoolhouses fed the same script agree on all
        three; a forgotten route changes the commons root and nothing silently."""
        return (self.org.chain(), self.org.decisions_digest(), self.commons.root().hex())
