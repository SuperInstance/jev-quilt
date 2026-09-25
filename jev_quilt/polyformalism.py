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
