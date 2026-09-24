"""Vendored BLAKE3 (pure python, stdlib-only).

Scope honesty: this build implements the SINGLE-CHUNK path (inputs of
up to 1024 bytes), which covers everything the receipt envelope ever
signs (canonical receipt preimage + chain head << 1 KiB). Longer inputs
are refused loudly, never hashed silently — the same refusal-polarity
doctrine as the rest of the fleet.

Reference: the BLAKE3 specification (github.com/BLAKE3-team/BLAKE3).
The compression function is the BLAKE2s round with the BLAKE3 message
permutation; flags are the spec's constants.
"""

from __future__ import annotations

_IV = (
    0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
    0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19,
)

_MSG_PERMUTATION = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)

_CHUNK_LEN = 1024
_BLOCK_LEN = 64

_CHUNK_START = 1
_CHUNK_END = 2
_ROOT = 8


def _rotr(x: int, n: int) -> int:
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF


def _g(v: list, a: int, b: int, c: int, d: int, x: int, y: int) -> None:
    v[a] = (v[a] + v[b] + x) & 0xFFFFFFFF
    v[d] = _rotr(v[d] ^ v[a], 16)
    v[c] = (v[c] + v[d]) & 0xFFFFFFFF
    v[b] = _rotr(v[b] ^ v[c], 12)
    v[a] = (v[a] + v[b] + y) & 0xFFFFFFFF
    v[d] = _rotr(v[d] ^ v[a], 8)
    v[c] = (v[c] + v[d]) & 0xFFFFFFFF
    v[b] = _rotr(v[b] ^ v[c], 7)


def _round(v: list, m: list) -> None:
    _g(v, 0, 4, 8, 12, m[0], m[1])
    _g(v, 1, 5, 9, 13, m[2], m[3])
    _g(v, 2, 6, 10, 14, m[4], m[5])
    _g(v, 3, 7, 11, 15, m[6], m[7])
    _g(v, 0, 5, 10, 15, m[8], m[9])
    _g(v, 1, 6, 11, 12, m[10], m[11])
    _g(v, 2, 7, 8, 13, m[12], m[13])
    _g(v, 3, 4, 9, 14, m[14], m[15])


def _compress(cv: list, block_words: list, counter: int, block_len: int, flags: int) -> list:
    v = list(cv) + list(_IV)
    v[12] = counter & 0xFFFFFFFF
    v[13] = (counter >> 32) & 0xFFFFFFFF
    v[14] = block_len
    v[15] = flags
    m = list(block_words)
    for r in range(7):
        _round(v, m)
        if r != 6:
            m = [m[i] for i in _MSG_PERMUTATION]
    return [(v[i] ^ v[i + 8]) & 0xFFFFFFFF for i in range(8)] + [
        (v[i + 8] ^ cv[i]) & 0xFFFFFFFF for i in range(8)
    ]


def _words(block: bytes) -> list:
    assert len(block) == _BLOCK_LEN
    return [int.from_bytes(block[i:i + 4], "little") for i in range(0, _BLOCK_LEN, 4)]


def blake3(data: bytes) -> bytes:
    """BLAKE3-256 over a single chunk (<= 1024 bytes).

    Raises ValueError beyond one chunk: this vendored build refuses
    rather than silently implementing a half-tree. Receipt envelopes
    never exceed one chunk; if that changes, implement the chunk/parent
    tree per spec instead of widening this refusal quietly.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("blake3 hashes bytes, not str — encode first")
    if len(data) > _CHUNK_LEN:
        raise ValueError(
            f"vendored single-chunk BLAKE3 refuses {len(data)} bytes "
            f"(limit {_CHUNK_LEN}); implement the parent tree per spec"
        )
    cv = list(_IV)
    if len(data) == 0:
        blocks, last_len = [_words(bytes(_BLOCK_LEN))], 0
    else:
        body = bytes(data)
        n_full, rem = divmod(len(body), _BLOCK_LEN)
        blocks = [_words(body[i:i + _BLOCK_LEN]) for i in range(0, n_full * _BLOCK_LEN, _BLOCK_LEN)]
        if rem:
            blocks.append(_words(body[n_full * _BLOCK_LEN:] + bytes(_BLOCK_LEN - rem)))
            last_len = rem
        else:
            last_len = _BLOCK_LEN
    for i, blk in enumerate(blocks):
        last = i == len(blocks) - 1
        flags = 0
        if i == 0:
            flags |= _CHUNK_START
        if last:
            flags |= _CHUNK_END | _ROOT
        out = _compress(cv, blk, 0, last_len if last else _BLOCK_LEN, flags)
        if not last:
            cv = out[:8]
    return b"".join(w.to_bytes(4, "little") for w in out)[:32]
