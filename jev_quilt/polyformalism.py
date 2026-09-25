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
