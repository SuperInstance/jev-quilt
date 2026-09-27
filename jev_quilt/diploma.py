"""Portable diploma (G13) + sea-graded transfer (G14): standing that survives
a kernel change.

`standing.py` lets one cell earn the right to stop asking, from its own book.
`commons.py` lets a fresh cell inherit a *fleet's* pooled evidence. Neither
answers the question G13 files: can standing cross a kernel boundary at
all — a different implementation, a different process, a different
language — and still be trusted? A `Diploma` is the answer: a signed,
content-addressed envelope over one Standing's deposits, so a *different*
kernel can confer standing by replay rather than by trust in the network
that carried it.

Two properties carried over from the family's oldest instincts, restated
for a portable artifact instead of a live WAL:

  * **Conferred, never self-granted, even in transit.** A Diploma is only
    ever *issued* from a real Standing (built by replaying a real book); the
    receiving kernel does not take the deposits on faith — it re-derives the
    root and checks the Ed25519 signature (`verify_diploma`, verify-only,
    never raises) before it will build anything from them. A tampered
    diploma is a refusal (`root_mismatch` / `bad_signature` /
    `unknown_signer`), never a silent forgery.
  * **Withheld ≠ conferred, on the receiving side too.** The receiving
    kernel applies its OWN `diploma_n` threshold to the transferred
    deposits (`standing_from_diploma(..., diploma_n=...)`), independent of
    whatever threshold the issuing kernel used. A streak that transfers
    faithfully is not automatically *earned* elsewhere — earning is a
    property of the deposit's streak against a threshold, decided locally,
    same as it always was.

G14 (sea-graded transfer) is the diploma's payload put to work: a diploma
may additionally carry an `earned_floor` — an exact ℚ surprise ceiling
(`Q16`, `"num/den"` on the wire) above which even earned standing may not
autopilot. `sea_graded_verdict` is `standing.verdict` with one more gate:
earned AND (no floor, or this outcome's surprise is within it) → ANSWER;
earned but surprise blew the floor → CONFIRM, not ANSWER (recall is
available, but conditions have moved outside what was graded); not earned →
the base verdict, unchanged. Revocable exactly as `standing.py` already is:
one booked-wrong observation on the receiver tears the streak down, and the
next call answers from the base verdict again.

Bytes law: `canonical_diploma_bytes` is pipe-joined UTF-8 over the sorted
deposits, the diploma threshold, and the floor — no json, no repr, no
pickle — so a byte-exact port (Rust, TS, ...) reproduces the same root and
the same signed message. `diploma_root` folds the threshold and the floor
into the MMR root via a `__meta__` leaf, so neither can be edited in
transit without breaking the root the signature seals.

STRETCH note: the tests below run both "kernels" as the same Python
implementation, so they prove cross-*instance* transfer (two independent
Standing/Diploma objects, two independent verifications) — not literally
cross-language. The true cross-language morphism rests entirely on the
byte-canonical discipline above (`canonical_diploma_bytes` / `diploma_root`
touch nothing but UTF-8 pipe-joined text and sha256/MMR, exactly the
family's existing cross-language contract in `signed_receipts.py`); it is
pinned here by a hard-coded expected-root vector a non-Python port can
reproduce and check itself against.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional, Union

from .fold import mmr_root
from .q16 import Q16
from .standing import Standing, DEFAULT_DIPLOMA
from .signed_receipts import seal_bytes, verify_bytes, chain_head_hex


def _leaf(key: str, answer: str, streak: int) -> bytes:
    """A 32-byte content-addressed leaf for one deposit — same \\x1f-delimited
    shape as commons._leaf, so no key/answer/streak collision can forge
    another deposit's leaf."""
    canon = f"{key}\x1f{answer}\x1f{streak}"
    return hashlib.sha256(canon.encode("utf-8")).digest()


def _floor_to_str(earned_floor: Union[Q16, str, None]) -> Optional[str]:
    """Normalize an earned_floor to the wire form: an exact "num/den" string,
    or None. Accepts a Q16 (the exact form) or an already-stringified floor;
    floats never enter — identity stays exact."""
    if earned_floor is None:
        return None
    if isinstance(earned_floor, Q16):
        return f"{earned_floor.num}/{earned_floor.den}"
    return str(earned_floor)


def parse_floor(floor: Optional[str]) -> Optional[Q16]:
    """The small helper the spec calls for: parse a diploma's "num/den"
    floor back into an exact Q16. None stays None. Never touches float."""
    if floor is None:
        return None
    num_str, den_str = floor.split("/")
    return Q16(int(num_str), int(den_str))


def canonical_diploma_bytes(deposits: list, diploma_n: int,
                            earned_floor: Optional[str] = None) -> bytes:
    """Cross-language canonical form: pipe-joined UTF-8 over the SORTED
    deposits, then diploma_n, then the floor (or '' if none). No json, no
    repr, no pickle — a Rust/TS port reproduces this byte-for-byte from the
    same (deposits, diploma_n, earned_floor)."""
    deps_sorted = sorted(deposits)
    dep_part = "|".join(f"{k}\x1f{a}\x1f{s}" for k, a, s in deps_sorted)
    return f"{dep_part}|{diploma_n}|{earned_floor or ''}".encode("utf-8")


def diploma_root(deposits: list, diploma_n: int,
                 earned_floor: Optional[str] = None) -> str:
    """MMR root over the sorted deposit leaves PLUS a meta-leaf folding in
    diploma_n and the floor — so neither the threshold nor the floor can be
    edited in transit without breaking the root the signature seals."""
    deps_sorted = sorted(deposits)
    leaves = [_leaf(k, a, s) for (k, a, s) in deps_sorted]
    meta = hashlib.sha256(
        f"__meta__\x1f{diploma_n}\x1f{earned_floor or ''}".encode("utf-8")
    ).digest()
    leaves.append(meta)
    return mmr_root(leaves).hex()


@dataclass(frozen=True)
class Diploma:
    """A signed, content-addressed envelope over one Standing's deposits.
    `root` is the diploma's chain tip (fed to seal_bytes as chain_tip, same
    role bk.replay() plays for a SignedReceipt) — recomputing it from
    (deposits, diploma_n, earned_floor) and comparing is the first check
    `verify_diploma` makes, before it ever asks the signature a question."""

    deposits: list  # list[tuple[str, str, int]] — (key, answer, streak)
    diploma_n: int
    earned_floor: Optional[str]  # exact "num/den", or None
    root: str        # hex MMR root over deposits + meta-leaf
    signer: str
    signature: str   # 128-hex Ed25519

    def to_dict(self) -> dict:
        return {
            "deposits": [list(d) for d in self.deposits],
            "diploma_n": self.diploma_n,
            "earned_floor": self.earned_floor,
            "root": self.root,
            "signer": self.signer,
            "signature": self.signature,
        }

    @staticmethod
    def from_dict(d: dict) -> "Diploma":
        return Diploma(
            deposits=[tuple(x) for x in d["deposits"]],
            diploma_n=d["diploma_n"],
            earned_floor=d.get("earned_floor"),
            root=d["root"],
            signer=d["signer"],
            signature=d["signature"],
        )


def issue(standing: Standing, *, signer: str, seed_hex: str,
         earned_floor: Union[Q16, str, None] = None) -> Diploma:
    """Mint a Diploma over `standing`'s current deposits. The diploma's own
    root is used as the chain_tip sealed by the signature — same layering
    signed_receipts uses for a Bookkeeper's replay() tip, here over a
    content-addressed deposit set instead of a WAL."""
    deps = standing.deposits()
    floor = _floor_to_str(earned_floor)
    root = diploma_root(deps, standing.diploma, floor)
    canonical = canonical_diploma_bytes(deps, standing.diploma, floor)
    _, signature = seal_bytes(canonical, chain_tip=root, signer=signer,
                              seed_hex=seed_hex)
    return Diploma(deposits=deps, diploma_n=standing.diploma,
                   earned_floor=floor, root=root, signer=signer,
                   signature=signature)


def verify_diploma(diploma: Diploma, pubkeys: dict) -> dict:
    """Permissionless verification, never raises. Recomputes the root first
    (catches ANY edited deposit, threshold, or floor — the meta-leaf makes
    those indistinguishable from an edited deposit) then checks the
    signature exactly as verify_bytes always has.

    Returns the same verdict shape as verify_bytes/verify_envelope:
      ok: bool
      reasons: [] | ["root_mismatch"] | ["unknown_signer"] |
               ["bad_signature"] | ["malformed:..."]
    """
    recomputed = diploma_root(diploma.deposits, diploma.diploma_n,
                              diploma.earned_floor)
    if recomputed != diploma.root:
        return {"ok": False, "reasons": ["root_mismatch"], "signer": diploma.signer}
    canonical = canonical_diploma_bytes(diploma.deposits, diploma.diploma_n,
                                        diploma.earned_floor)
    # The diploma's root plays chain_tip's role; the actual chain_head fed
    # to the signed message is chain_head_hex(root), exactly as seal_bytes
    # derived it at issue() time (see signed_receipts.seal_bytes).
    chain_head = chain_head_hex(diploma.root)
    return verify_bytes(canonical, chain_head, diploma.signer,
                        diploma.signature, pubkeys,
                        expected_chain_tip=diploma.root)


def standing_from_diploma(diploma: Diploma, pubkeys: dict, *,
                          diploma_n: int = DEFAULT_DIPLOMA) -> Standing:
    """Confer standing from a verified diploma. Refusal polarity: an
    unverifiable diploma yields an EMPTY Standing (earned False everywhere)
    — never partial trust, never an exception. `diploma_n` is the
    RECEIVING kernel's own threshold, independent of whatever threshold the
    issuing kernel used to build the diploma — withheld ≠ conferred applies
    on this side too."""
    verdict = verify_diploma(diploma, pubkeys)
    if not verdict["ok"]:
        return Standing(diploma_n)
    return Standing.from_deposits(diploma.deposits, diploma_n=diploma_n)


def sea_graded_verdict(standing: Standing, key: str, base_verdict: str, *,
                       surprise: Q16, earned_floor: Optional[Q16]
                       ) -> tuple:
    """G14: the fourth verdict, gated by a sea-graded floor. Earned standing
    autopilots (ANSWER) only while this outcome's surprise stays within the
    floor the diploma carried; past it, standing is held but withheld
    (CONFIRM) — conditions have moved outside what was graded. Unearned
    keys are untouched: (base_verdict, None), same as standing.verdict."""
    if not standing.earned(key):
        return (base_verdict, None)
    if earned_floor is not None and surprise > earned_floor:
        return ("CONFIRM", None)
    return ("ANSWER", standing.recall(key))
