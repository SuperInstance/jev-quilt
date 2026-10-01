"""Vendored Ed25519 (RFC 8032 reference arithmetic, pure python, stdlib-only).

Chosen over a binding so the receipts-v2 envelope keeps jev-quilt's zero
-runtime-dependency law; the arithmetic below is the RFC 8032 reference
form, validated against known answer vectors and cross-checked fuzzily
against a bindings build in CI-equivalent runs (see tests).

Speed is not the point: signing happens at cross-node boundaries
(<<1/sec), not per-tick. Correctness + auditability is the point.
"""

from __future__ import annotations

import hashlib

_Q = 2 ** 255 - 19
_L = 2 ** 252 + 27742317777372353535851937790883648493


def _inv(x: int) -> int:
    return pow(x, _Q - 2, _Q)


_D = (-121665 * _inv(121666)) % _Q
_I = pow(2, (_Q - 1) // 4, _Q)


def _xrecover(y: int) -> int:
    xx = (y * y - 1) * _inv(_D * y * y + 1) % _Q
    x = pow(xx, (_Q + 3) // 8, _Q)
    if (x * x - xx) % _Q != 0:
        x = (x * _I) % _Q
    if x % 2 != 0:
        x = _Q - x
    return x


_BY = (4 * _inv(5)) % _Q
_BX = _xrecover(_BY) % _Q
_B = (_BX, _BY)
_IDENTITY = (0, 1)


def _isoncurve(p: tuple) -> bool:
    x, y = p
    return (-x * x + y * y - 1 - _D * x * x * y * y) % _Q == 0


def _edwards(p: tuple, q: tuple) -> tuple:
    x1, y1 = p
    x2, y2 = q
    x3 = (x1 * y2 + x2 * y1) * _inv(1 + _D * x1 * x2 * y1 * y2) % _Q
    y3 = (y1 * y2 + x1 * x2) * _inv(1 - _D * x1 * x2 * y1 * y2) % _Q
    return (x3, y3)


def _scalarmult(p: tuple, e: int) -> tuple:
    q = _IDENTITY
    while e > 0:
        if e & 1:
            q = _edwards(q, p)
        p = _edwards(p, p)
        e >>= 1
    return q


def _encodeint(y: int) -> bytes:
    return y.to_bytes(32, "little")


def _encodepoint(p: tuple) -> bytes:
    x, y = p
    return (y | ((x & 1) << 255)).to_bytes(32, "little")


def _decodeint(s: bytes) -> int:
    return int.from_bytes(s, "little")


def _decodepoint(s: bytes) -> tuple:
    if len(s) != 32:
        raise ValueError("point encoding is 32 bytes")
    y = int.from_bytes(s, "little") & ((1 << 255) - 1)
    x = _xrecover(y)
    if (x & 1) != ((s[31] >> 7) & 1):
        x = _Q - x
    p = (x, y)
    if not _isoncurve(p):
        raise ValueError("point is not on curve")
    return p


def _hint(m: bytes) -> int:
    return int.from_bytes(hashlib.sha512(m).digest(), "little")


def _clamp(h32: bytes) -> int:
    a = int.from_bytes(h32, "little")
    a &= (1 << 254) - 8
    a |= 1 << 254
    return a


def publickey(seed: bytes) -> bytes:
    """Derive the 32-byte public key from a 32-byte secret seed."""
    if len(seed) != 32:
        raise ValueError("Ed25519 secret seed is 32 bytes")
    h = hashlib.sha512(seed).digest()
    a = _clamp(h[:32])
    return _encodepoint(_scalarmult(_B, a))


def sign(seed: bytes, msg: bytes) -> bytes:
    """Ed25519 signature (64 bytes) over msg with a 32-byte secret seed."""
    if len(seed) != 32:
        raise ValueError("Ed25519 secret seed is 32 bytes")
    if not isinstance(msg, (bytes, bytearray)):
        raise TypeError("sign bytes, not str — canonical bytes discipline")
    h = hashlib.sha512(seed).digest()
    a = _clamp(h[:32])
    pk = _encodepoint(_scalarmult(_B, a))
    r = _hint(h[32:] + msg) % _L
    R = _scalarmult(_B, r)
    k = _hint(_encodepoint(R) + pk + msg) % _L
    S = (r + k * a) % _L
    return _encodepoint(R) + _encodeint(S)


def verify(pk: bytes, msg: bytes, sig: bytes) -> bool:
    """True iff sig is a valid Ed25519 signature of msg under pk.

    Malformed points, non-canonical S, and wrong-length inputs all
    return False — a refusal, never an exception leak. (RFC 8032 §5.1.7
    check-then-verify, compressed for our envelope's use.)
    """
    if len(pk) != 32 or len(sig) != 64 or not isinstance(msg, (bytes, bytearray)):
        return False
    try:
        A = _decodepoint(pk)
        R = _decodepoint(sig[:32])
    except ValueError:
        return False
    S = _decodeint(sig[32:])
    if S >= _L:
        return False
    k = _hint(sig[:32] + pk + bytes(msg)) % _L
    return _scalarmult(_B, S) == _edwards(R, _scalarmult(A, k))
