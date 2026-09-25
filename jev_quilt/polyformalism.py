"""Polyformalism: the substrate's cross-language canary, callable.

The fleet canary string must hash to the same FNV-1a-64 value in every
substrate port (Python here; the Rust/C siblings live in the repo's
top-level polyformalism/ directory). tests/test_fleet_canary.py pins
the value with a local reimplementation; this module gives the
substrate its OWN canary surface so any cell, sibling, or audit lane
can verify the bytes-law without re-deriving it — one import, one call.

Bytes-law: UTF-8 encoding, byte-level FNV-1a, never ord() iteration
(same rule as bookkeeper.fnv1a — which is what this module calls).
"""

from .bookkeeper import fnv1a

CANARY_STRING = "café Δ 日本語"
CANARY_VALUE = 0x024a555471370b18d
_CANARY_HEX = f"0x{CANARY_VALUE:017x}"   # pinned spelling: 0x0-prefixed


def fleet_canary() -> str:
    """The fleet canary value, 0x-prefixed lowercase hex.

    Computed live from the substrate's own fnv1a over the UTF-8 bytes
    of CANARY_STRING — asserted equal to the pinned CANARY_VALUE at
    import time so a broken hash implementation fails loudly, here,
    instead of silently in a faraway sibling port.
    """
    live = f"0x{fnv1a(CANARY_STRING.encode('utf-8')):017x}"
    assert live == _CANARY_HEX, (
        f"fleet canary broken in this substrate: {live} != {_CANARY_HEX} — "
        "the bytes-law is violated; do not trust cross-language receipts"
    )
    return live
"""Fleet polyformalism canary.

One hash, every substrate. FNV-1a 64-bit over the UTF-8 bytes of
"café Δ 日本語" must equal 0x024a555471370b18d in Python, Rust, C,
WASM, and every other port (see repo-root polyformalism/ for the
reference implementations and assets/06_canary_0x024a.png for the pin).

CI gates on this value byte-exact; do not change the string.
"""
from __future__ import annotations

FLEET_CANARY_STRING = "café Δ 日本語"
FLEET_CANARY_VALUE = 0x024a555471370b18d

_FNV1A_OFFSET_BASIS = 0xCBF29CE484222325
_FNV1A_PRIME = 0x100000001B3
_MASK64 = 0xFFFFFFFFFFFFFFFF


def fnv1a_64(s: str) -> int:
    """FNV-1a 64-bit hash, byte-level over UTF-8."""
    h = _FNV1A_OFFSET_BASIS
    for b in s.encode("utf-8"):
        h ^= b
        h = (h * _FNV1A_PRIME) & _MASK64
    return h


def fleet_canary() -> str:
    """The fleet-wide polyformalism canary, pinned byte-exact.

    Returns the canonical 0x-prefixed, 16-digit lowercase hex form.
    """
    # Canonical fleet pin is 0x-prefixed with a leading zero: 19 chars
    # total (0x + 17 hex digits). Pinned byte-exact in assets/06_canary_0x024a.png
    # and .github/workflows/test.yml — do not "fix" the width.
    return format(FLEET_CANARY_VALUE, "#019x")
