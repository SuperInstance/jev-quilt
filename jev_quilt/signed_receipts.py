"""Receipts v2: verify-only Ed25519/BLAKE3 signature envelope.

Implements docs/RECEIPTS-V2.md (design note, jev-quilt PR #9):

    SignedReceipt = {
      receipt:    <existing Receipt, unchanged>,
      chain_head: fnv1a-64 of the chain tip this receipt seals (16-hex),
      signer:     <node/agent identity key id>,
      signature:  Ed25519.sign(signer_sk, BLAKE3(canonical_bytes || chain_head)),
    }

Laws carried over from the design note:

- **Sign, don't replace.** The sha256/FNV-1a chain stays the in-ledger
  truth; the envelope strips cleanly (old verifiers reproduce today's
  behavior bit-for-bit — that is a pinned test, not a hope).
- **Verify-only receipts for cross-node claims.** Verification is
  permissionless (public keys suffice); minting requires the seed, which
  this module never prints, logs, or serializes.
- **One key per node identity.** Rotation books a retirement payload
  signed by the NEW key (`rotation_payload`); a stolen key writes until
  rotation — named honest gap in the design note, unchanged.
- **Non-repudiation is a cross-node property only.** Inside one WAL the
  chain already settles disputes; the envelope earns its cost exactly
  where the chain cannot: two nodes, two bookkeepers, one argument.

Refusal polarity: `verify_envelope` / `verify_bytes` never raise on bad
material. They return a verdict with reasons (unknown_signer /
bad_signature / wrong_chain_head / malformed:...) so the caller can
book a `v2-refused` row in the WAL — refusal is booked, never silent
(family doctrine: refusal polarity is a first-class ledger row).

Primitive scope (honest): the vendored BLAKE3 refuses >1024-byte inputs;
a signed receipt message is ~150 bytes, so the single-chunk path covers
the envelope forever unless the receipt shape changes — in which case
implement the parent tree per spec rather than widening the refusal.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass

from .blake3 import blake3
from .bookkeeper import Receipt, fnv1a
from . import ed25519


def canonical_bytes(receipt: Receipt) -> bytes:
    """The receipt's canonical form: EXACTLY the sha() preimage.

    The envelope binds what the chain binds — same fields, same
    re-derivation rule (a non-empty payload re-derives payload_hash
    from the retained residue text; empty payload keeps the stored
    hash, the historical back-compat formula). Cross-language form so
    Rust/TS ports reproduce it byte-for-byte: pipe-joined UTF-8, no
    JSON, no pickle, no repr.
    """
    payload_hash = (
        f"{fnv1a(receipt.payload.encode('utf-8')):016x}"
        if receipt.payload else receipt.payload_hash
    )
    raw = (
        f"{receipt.tick}|{receipt.state_hash}|{receipt.delta_hash}|"
        f"{receipt.decision_kind}|{payload_hash}"
    )
    return raw.encode("utf-8")


def chain_head_hex(chain_tip: str) -> str:
    """fnv1a-64 over the chain tip's hex, as 16 lowercase hex chars.

    The chain tip is substrate-specific (Python bookkeeper: replay()
    sha256-hex; Rust bookkeeper: the fnv1a-64 chain value hex). Hashing
    the tip's hex keeps the envelope substrate-neutral: any sibling that
    can name its tip can be sealed. Bytes rule, as always: UTF-8, never
    ord().
    """
    return f"{fnv1a(chain_tip.encode('utf-8')):016x}"


def message_bytes(canonical: bytes, chain_head: str) -> bytes:
    """BLAKE3 input: canonical_bytes || chain_head (16-hex ASCII).

    The '||' is byte concatenation; the chain_head encoding is pinned as
    lowercase ASCII hex — an 8-byte LE integer encoding would differ and
    is exactly the kind of silent cross-language drift the bytes-law
    exists to prevent.
    """
    if not isinstance(canonical, bytes):
        raise TypeError("canonical must be bytes — canonical_bytes() first")
    return canonical + chain_head.encode("ascii")


@dataclass(frozen=True)
class SignedReceipt:
    """Envelope around an unchanged Receipt. Fields beyond `receipt`
    are the signature layer; stripping them yields the v1 receipt
    bit-for-bit (pinned test)."""
    receipt: Receipt
    chain_head: str
    signer: str
    signature: str  # 128-hex Ed25519 over blake3(message_bytes)

    def to_dict(self) -> dict:
        r = self.receipt
        return {
            "receipt": {
                "tick": r.tick, "state_hash": r.state_hash,
                "delta_hash": r.delta_hash, "decision_kind": r.decision_kind,
                "payload_hash": r.payload_hash, "payload": r.payload,
            },
            "chain_head": self.chain_head,
            "signer": self.signer,
            "signature": self.signature,
        }

    @staticmethod
    def from_dict(d: dict) -> "SignedReceipt":
        r = d["receipt"]
        return SignedReceipt(
            receipt=Receipt(
                tick=r["tick"], state_hash=r["state_hash"],
                delta_hash=r["delta_hash"], decision_kind=r["decision_kind"],
                payload_hash=r["payload_hash"], payload=r.get("payload", ""),
            ),
            chain_head=d["chain_head"], signer=d["signer"],
            signature=d["signature"],
        )

    def to_canonical_json(self) -> str:
        """Family canonical JSON: sorted keys, compact separators, UTF-8.
        This is the interchange/transport form (persisted or shipped);
        the SIGNATURE is over canonical_bytes || chain_head, not over
        this JSON — authorization and interchange stay layered (v2
        positioning claim 5; see docs/RECEIPTS-V2.md)."""
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))


def generate_identity(node: str, generation: int) -> tuple:
    """Mint a node identity. Returns (signer_id, seed_hex, pubkey_hex).

    The seed is secret material: the caller persists it (file mode 0600
    or an env var), this module NEVER prints or logs it. verify_envelope
    needs only pubkey_hex — a verify-only node holds no secret at all.
    """
    seed = secrets.token_bytes(32)
    signer_id = f"{node}.k{generation}"
    return signer_id, seed.hex(), ed25519.publickey(seed).hex()


def seal_bytes(canonical: bytes, chain_tip: str, signer: str, seed_hex: str) -> tuple:
    """Low-level seal over caller-supplied canonical bytes — the path
    for FOREIGN/sibling receipts whose canonical form is their own
    substrate's rule (e.g. twist-engine: body||hash UTF-8). jev_quilt
    Receipts should use `seal`, which derives canonical_bytes per this
    repo's law. Returns (chain_head_hex, signature_hex)."""
    seed = bytes.fromhex(seed_hex)
    ch = chain_head_hex(chain_tip)
    msg = message_bytes(canonical, ch)
    return ch, ed25519.sign(seed, msg).hex()


def verify_bytes(canonical: bytes, chain_head: str, signer: str,
                 signature_hex: str, pubkeys: dict,
                 expected_chain_tip: str | None = None) -> dict:
    """verify_envelope's twin for caller-supplied canonical bytes.
    Same verdict shape, same refusal polarity."""
    reasons: list = []
    pk_hex = pubkeys.get(signer)
    if pk_hex is None:
        return {"ok": False, "reasons": ["unknown_signer"], "signer": signer}
    if expected_chain_tip is not None and chain_head_hex(expected_chain_tip) != chain_head:
        return {"ok": False, "reasons": ["wrong_chain_head"], "signer": signer}
    try:
        pk = bytes.fromhex(pk_hex)
        sig = bytes.fromhex(signature_hex)
    except ValueError as e:
        return {"ok": False, "reasons": [f"malformed:{e}"], "signer": signer}
    if not ed25519.verify(pk, message_bytes(canonical, chain_head), sig):
        reasons.append("bad_signature")
    return {"ok": not reasons, "reasons": reasons, "signer": signer}


def seal(receipt: Receipt, chain_tip: str, signer: str, seed_hex: str) -> SignedReceipt:
    """Sign a receipt against the current chain tip. The chain tip is
    named (and checked by verifiers against wrong_chain_head) so a
    signature cannot be lifted onto a different fork of the ledger."""
    ch, sig = seal_bytes(canonical_bytes(receipt), chain_tip, signer, seed_hex)
    return SignedReceipt(receipt=receipt, chain_head=ch, signer=signer,
                         signature=sig)


def verify_envelope(signed: SignedReceipt,
                    pubkeys: dict,
                    expected_chain_tip: str | None = None) -> dict:
    """Permissionless verification. `pubkeys` maps signer id -> pubkey
    hex (a verify-only node holds exactly this and nothing else).

    Returns a verdict dict, never raises on bad material:
      ok: bool
      reasons: [] | ["unknown_signer"] | ["bad_signature"] |
               ["wrong_chain_head"] | ["malformed:..."]
    A False verdict is a REFUSAL with evidence — book it, don't swallow
    it (family doctrine: refusal polarity is a first-class ledger row).
    """
    return verify_bytes(canonical_bytes(signed.receipt), signed.chain_head,
                        signed.signer, signed.signature, pubkeys,
                        expected_chain_tip)


def rotation_payload(old_signer: str, old_pubkey_hex: str,
                     new_signer: str, new_pubkey_hex: str,
                     note: str = "") -> bytes:
    """Canonical retirement payload: the NEW key signs the OLD key's
    retirement (design note rule — rotation books a receipt of its own
    or the chain forks socially). Pipe-joined UTF-8, bytes-law clean."""
    raw = f"retire|{old_signer}|{old_pubkey_hex}|{new_signer}|{new_pubkey_hex}|{note}"
    return raw.encode("utf-8")


def sign_rotation(payload: bytes, new_signer: str, new_seed_hex: str) -> str:
    """Ed25519 signature (128-hex) over the retirement payload with the
    NEW key — the new key attests the old key is done."""
    sig = ed25519.sign(bytes.fromhex(new_seed_hex), payload)
    return sig.hex()


def verify_rotation(payload: bytes, new_pubkey_hex: str, signature_hex: str) -> bool:
    try:
        return ed25519.verify(bytes.fromhex(new_pubkey_hex), payload,
                              bytes.fromhex(signature_hex))
    except ValueError:
        return False  # malformed material is a refusal, not an exception
