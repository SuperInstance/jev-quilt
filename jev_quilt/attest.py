"""The Attestation (G17): a credential earned by reproduction, re-verifiable
by the recipient from scratch — anti-credential-laundering.

`claim.py` (G16) proves reproduction to the node holding the books; it
cannot leave that node as a trusted object. `diploma.py` (G13/G14) leaves a
node signed, but it seals one cell's streak and the receiver re-checks only
that the streak transferred — never whether the evidence behind it came
from witnesses worth believing. An `Attestation` closes that loop: it is a
signed, content-addressed envelope over a reproduced `Claim` — every
witness's reading (drifters included), the issuer's consensus, quorum, and
the calibrated floor the reproduction held under. A stranger kernel does
NOT admit it on the issuer's word. It verifies the signature, re-derives the
reproduction root from the carried readings, then applies its OWN trust
weights (G11), its OWN quorum, and its OWN floor (G14) and RECOMPUTES
consensus itself before conferring anything.

The capability this makes possible: **the recipient can honestly reach a
different verdict than the issuer from the very same bytes.** An issuer who
trusts a colluding witness ring signs a validly-reproduced attestation; a
recipient who assigns that ring trust 0 gets `conferred=False` from the
identical attestation — and that is correct, not a failure. That is why the
issuer's `earns_standing` boolean is deliberately never on the wire: there
is no "it's earned" field to forge, only the evidence and a signature over
it, and the recipient always recomputes the verdict itself.

The one real design fork (resolved at dispatch altitude, see
../ai-writings/situations/arch/NEW-DIRECTIONS.md § A): the Attestation
carries every witness's reading, not just the consensus + a reproduction
proof. Carrying only the consensus would be O(1) but would not let a
recipient drop a distrusted witness and watch the answer change — which is
the entire capability G17 exists to provide. The cost (O(N) in the witness
count) is the correct trade.

Same law as `claim.py`, carried into the portable artifact: `attestation_
root` is taken over ALL witnesses' readings (drifters included — the full
content address of what the swarm reported, so a single-delta edit still
changes the root even for a witness later excluded); consensus (both the
issuer's carried, advisory value AND the recipient's own recomputation) is
taken over the trusted, non-drifting subset only.

Byte/root discipline mirrors `diploma.py` exactly: `canonical_attestation_
bytes` is pipe-joined UTF-8 over the sorted readings, the consensus, the
quorum and the floor — no json, no repr, no pickle; `attestation_root` folds
that same meta (consensus|quorum|floor) into an extra MMR leaf, so none of
it can be edited in transit without breaking the root the signature seals.

One deliberate addition beyond the architecture sketch's literal dataclass:
`Attestation` carries a stored `root` field (hex), exactly as `Diploma`
does. The sketch's code block omits it, but the spec prose requires a
distinct `root_mismatch` refusal reason ("re-derives the reproduction root
... and checks it equals the SEALED root") — that requires a root value
carried in the envelope to compare against, the same shape `diploma.py`
already uses (`verify_diploma` recomputes and compares against `diploma.
root` before it ever asks the signature a question). Without a stored root,
any edit to a reading or to the consensus/quorum/floor meta would only ever
surface as `bad_signature` (the recomputed message no longer matches what
was signed), collapsing the `root_mismatch` / `bad_signature` distinction
the predicate calls for. This is additive to the sketch, not a redesign: no
field is removed, and `earns_standing` is still never carried (see below).

Verify-only refusal polarity throughout: `verify_attestation` never raises;
`admit` never raises; only `attest` refuses at ISSUE time (raises, mirroring
the family's other constructors — `CalibratedFloor`, `MeanPredictor`, `Q16`
— that refuse to build a lying object rather than build one silently).

STRETCH / honest limits (carried from `claim.py` and `diploma.py`):

  * Cross-*language* reproducibility is asserted via the byte-canonical
    `_leaf` / `canonical_attestation_bytes` / sorted `mmr_root`, pinned by a
    hard-coded expected-root vector; the "issuer" and "recipient" kernels
    exercised in this module's tests are both this same Python
    implementation (cross-*instance*, not literally cross-language) — same
    STRETCH carried by G13/G14/G16.
  * The recipient's drift re-judgment (`admit`'s `floor` +
    `reading_magnitude`) mirrors `Claim.from_books`'s swarm-drift algorithm
    exactly (fold every surprise in the trusted set into the floor, THEN
    grade every witness against the resulting floor) so the two rungs share
    one law; a recipient who supplies neither argument honors the carried
    `drifting` flags instead — an honest, weaker fallback (it trusts the
    issuer's floor judgment, but never the issuer's trust judgment or its
    consensus), noted, not hidden.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Callable, Optional

from .claim import Claim
from .calibrate import CalibratedFloor
from .diploma import parse_floor, _floor_to_str
from .fold import mmr_root
from .predictor import surprise
from .q16 import Q16
from .signed_receipts import seal_bytes, verify_bytes, chain_head_hex


@dataclass(frozen=True)
class WitnessReading:
    """One witness's carried reading. `drifting` is the ISSUER's floor
    judgment at issue time — advisory; the recipient may re-judge it
    (`admit`'s `floor` + `reading_magnitude`) rather than take it on
    faith."""
    witness: str        # the witness's signer id
    value: str           # its canonical reading
    drifting: bool        # flagged by the issuer's floor at issue time


@dataclass(frozen=True)
class Attestation:
    """A signed, content-addressed envelope over a reproduced `Claim`.

    Deliberately carries NO `earns_standing` field: there is nothing here
    for the issuer to assert that a recipient must take on faith. Every
    other field is either raw evidence (`readings`) or the issuer's
    ADVISORY judgment over that evidence (`consensus`, `quorum`,
    `earned_floor`) — advisory because `admit` always recomputes them
    against the recipient's own trust, quorum and floor before conferring
    anything."""
    readings: tuple        # tuple[WitnessReading, ...] — ALL witnesses, sorted by witness id
    consensus: str          # issuer's consensus value (advisory; recipient recomputes)
    quorum: int              # issuer's quorum (advisory)
    earned_floor: Optional[str]  # "num/den" Q16 wire form, or None (G14 carry)
    root: str                 # hex MMR root over readings + meta-leaf (the sealed root)
    signer: str                # issuer id
    signature: str               # Ed25519 over canonical_attestation_bytes || chain_head(root)


def _leaf(r: WitnessReading) -> bytes:
    """A 32-byte content-addressed leaf for one witness's carried reading
    (\\x1f-delimited, same shape as claim._leaf/diploma._leaf, so no
    witness/value/drifting collision can forge another witness's leaf)."""
    canon = f"{r.witness}\x1f{r.value}\x1f{int(r.drifting)}"
    return hashlib.sha256(canon.encode("utf-8")).digest()


def canonical_attestation_bytes(readings, consensus: Optional[str], quorum: int,
                                earned_floor: Optional[str]) -> bytes:
    """Cross-language canonical form: pipe-joined UTF-8 over the SORTED
    readings, then consensus, then quorum, then the floor (or '' if none).
    No json, no repr, no pickle — a Rust/TS port reproduces this byte-for-
    byte from the same (readings, consensus, quorum, earned_floor)."""
    rs_sorted = sorted(readings, key=lambda r: r.witness)
    rs_part = "|".join(f"{r.witness}\x1f{r.value}\x1f{int(r.drifting)}" for r in rs_sorted)
    return f"{rs_part}|{consensus or ''}|{quorum}|{earned_floor or ''}".encode("utf-8")


def attestation_root(readings, consensus: Optional[str], quorum: int,
                     earned_floor: Optional[str]) -> bytes:
    """MMR root over the sorted witness leaves PLUS a meta-leaf folding in
    consensus, quorum and the floor — so none of the three can be edited in
    transit without breaking the root the signature seals. Mirrors `claim.
    root()` in taking the root over EVERY carried reading (drifters
    included — the full content address of what the swarm reported)."""
    rs_sorted = sorted(readings, key=lambda r: r.witness)
    leaves = [_leaf(r) for r in rs_sorted]
    meta = hashlib.sha256(
        f"__meta__\x1f{consensus or ''}\x1f{quorum}\x1f{earned_floor or ''}".encode("utf-8")
    ).digest()
    leaves.append(meta)
    return mmr_root(leaves)


def attest(claim: Claim, *, signer: str, seed_hex: str,
          floor: Optional[Q16] = None) -> Attestation:
    """Mint an Attestation over a reproduced `claim`. REFUSES (raises
    ValueError) if the claim does not `earns_standing()` — a certificate of
    an unreproduced claim would be a lie at the source, not a lenient
    default. Carries `claim.readings(include_drifting=True)` (ALL
    witnesses, sorted), `claim.consensus()`, `claim.quorum`, and the
    (optional) sea the reproduction held under. Signs the attestation's own
    root, same layering `diploma.issue` uses over a Standing's deposit
    root."""
    if not claim.earns_standing():
        raise ValueError(
            "attest: claim does not earn standing — refusing to issue a "
            "certificate of an unreproduced claim"
        )
    readings = tuple(
        WitnessReading(witness=r.witness, value=r.value, drifting=r.drifting)
        for r in claim.readings(include_drifting=True)
    )
    consensus = claim.consensus()
    quorum = claim.quorum
    earned_floor = _floor_to_str(floor)
    root = attestation_root(readings, consensus, quorum, earned_floor).hex()
    canonical = canonical_attestation_bytes(readings, consensus, quorum, earned_floor)
    _, signature = seal_bytes(canonical, chain_tip=root, signer=signer, seed_hex=seed_hex)
    return Attestation(readings=readings, consensus=consensus, quorum=quorum,
                       earned_floor=earned_floor, root=root, signer=signer,
                       signature=signature)


def verify_attestation(att: Attestation, pubkeys: dict) -> dict:
    """Permissionless verification, never raises. Recomputes the root
    FIRST (catches any edited reading, consensus, quorum or floor — the
    meta-leaf makes those indistinguishable from an edited reading) then
    checks the signature exactly as `verify_diploma` does.

    Returns the same verdict shape as `verify_bytes`/`verify_diploma`:
      ok: bool
      reasons: [] | ["root_mismatch"] | ["unknown_signer"] |
               ["bad_signature"] | ["malformed:..."]
    A False verdict is a REFUSAL with evidence, never a silent forgery."""
    recomputed = attestation_root(att.readings, att.consensus, att.quorum,
                                  att.earned_floor).hex()
    if recomputed != att.root:
        return {"ok": False, "reasons": ["root_mismatch"], "signer": att.signer}
    canonical = canonical_attestation_bytes(att.readings, att.consensus,
                                            att.quorum, att.earned_floor)
    chain_head = chain_head_hex(att.root)
    return verify_bytes(canonical, chain_head, att.signer, att.signature,
                        pubkeys, expected_chain_tip=att.root)


@dataclass(frozen=True)
class Admission:
    """The recipient's OWN verdict over an Attestation — never the
    issuer's. `trusted`/`dropped` are the audit trail: which witnesses the
    recipient actually counted, and which it dropped (by its own trust==0,
    or by its own re-judged/carried drift), and why."""
    conferred: bool
    verdict: str                 # 'ANSWER' | 'CONFIRM' | base_verdict
    value: Optional[str]
    reason: Optional[str]        # refusal reason, for the booked v2-refused row
    trusted: tuple                 # tuple[str, ...] — witnesses the recipient counted
    dropped: tuple                  # tuple[str, ...] — dropped by trust==0 or drift


def _recompute_drift(readings, cal: CalibratedFloor,
                     reading_magnitude: Callable[[WitnessReading], Q16]) -> set:
    """Mirror `Claim.from_books`'s swarm-drift algorithm exactly, but over
    the RECIPIENT's own `CalibratedFloor` and the recipient's own reading of
    each witness's magnitude: modal value, consensus magnitude of the
    witnesses agreeing with it, every witness's surprise against that,
    the WHOLE set folded into the floor before anyone is judged against the
    resulting reading (a swarm is a set, not a time series — same law as
    claim.py). Returns the witness ids the recipient's floor flags."""
    if not readings:
        return set()
    names = sorted(r.witness for r in readings)
    by_name = {r.witness: r for r in readings}
    mags = {name: reading_magnitude(by_name[name]) for name in names}

    counts: dict = {}
    for name in names:
        v = by_name[name].value
        counts[v] = counts.get(v, 0) + 1
    top = max(counts.values())
    modal_value = min(v for v, c in counts.items() if c == top)

    agreeing_mags = [mags[name] for name in names if by_name[name].value == modal_value]
    consensus_mag = sum(agreeing_mags, Q16(0)) * Q16(1, len(agreeing_mags))

    surprises = {name: surprise(mags[name], consensus_mag) for name in names}
    for name in names:
        cal.update(surprises[name])
    f = cal.floor()
    return {name for name in names if f is not None and surprises[name] > f}


def admit(att: Attestation, pubkeys: dict, *, trust: dict, quorum: int,
         floor: Optional[CalibratedFloor] = None,
         reading_magnitude: Optional[Callable[[WitnessReading], Q16]] = None,
         base_verdict: str = "CONFIRM") -> Admission:
    """Confer standing from an Attestation using ONLY the recipient's own
    trust weights, quorum and floor. The issuer's `consensus`/`quorum` are
    never trusted — they are advisory fields the recipient may disagree
    with, and does not even need to inspect to reach a verdict.

    1. `verify_attestation` — on failure, refuse (booked reason), no
       witness is ever consulted.
    2. Recipient's trusted set = readings whose witness has
       `trust.get(w, 0) > 0`, MINUS any the recipient's own floor re-flags
       as drifting (needs BOTH `floor` and `reading_magnitude`; with either
       missing, the carried `drifting` flags are honored instead — a
       weaker, explicit fallback, never silent).
    3. `conferred` iff the trusted, non-drifting witnesses are UNANIMOUS on
       one value AND there are at least the recipient's own `quorum` of
       them — the recipient recomputes consensus itself; the issuer's
       carried `consensus` plays no role in this decision.
    4. Sea-grading (G14): if `att.earned_floor` is set and the recipient's
       OWN floor reading is rougher than it, conferred standing degrades to
       `CONFIRM` rather than `ANSWER` — earned, but outside what the
       reproduction was graded under, from the recipient's own conditions.
    5. Otherwise: `Admission(conferred=False, verdict=base_verdict,
       value=None, reason='not_reproduced_for_recipient', ...)`.
    """
    v = verify_attestation(att, pubkeys)
    if not v["ok"]:
        reason = v["reasons"][0] if v["reasons"] else "verification_failed"
        return Admission(conferred=False, verdict=base_verdict, value=None,
                         reason=reason, trusted=(), dropped=())

    trust_passed = [r for r in att.readings if trust.get(r.witness, 0) > 0]
    trust_dropped = {r.witness for r in att.readings} - {r.witness for r in trust_passed}

    if floor is not None and reading_magnitude is not None:
        drift_dropped = _recompute_drift(trust_passed, floor, reading_magnitude)
    else:
        drift_dropped = {r.witness for r in trust_passed if r.drifting}

    trusted = [r for r in trust_passed if r.witness not in drift_dropped]
    dropped = tuple(sorted(trust_dropped | drift_dropped))
    trusted_ids = tuple(sorted(r.witness for r in trusted))

    values = {r.value for r in trusted}
    conferred = len(trusted) >= quorum and len(values) == 1
    if not conferred:
        return Admission(conferred=False, verdict=base_verdict, value=None,
                         reason="not_reproduced_for_recipient",
                         trusted=trusted_ids, dropped=dropped)

    value = next(iter(values))

    earned_floor_q = parse_floor(att.earned_floor)
    recipient_sea = floor.floor() if floor is not None else None
    if earned_floor_q is not None and recipient_sea is not None and recipient_sea > earned_floor_q:
        return Admission(conferred=True, verdict="CONFIRM", value=value,
                         reason=None, trusted=trusted_ids, dropped=dropped)
    return Admission(conferred=True, verdict="ANSWER", value=value,
                     reason=None, trusted=trusted_ids, dropped=dropped)
