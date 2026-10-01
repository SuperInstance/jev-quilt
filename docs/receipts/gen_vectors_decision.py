"""MOTH/JEV instrumentation for the release-0.1.0 vectors-shipping decision.

Standing order (Casey): every non-obvious release tradeoff gets JEV cells
with signed receipts before the build ships. This generator books one
ledger cell per option, then a verdict cell, seals the tip with the
repo's own receipts-v2 envelope (eat our own cooking), and persists the
signed rows. Run from the repo root:

    python3 docs/receipts/gen_vectors_decision.py

The seed is TEST/decision material, never a real node key (same standing
as vectors/signed_receipt_vectors.json's all-zero seed). The pubkey is
written into the ledger doc — a verify-only reader holds exactly that.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))  # repo root, so `import jev_quilt` works

from jev_quilt.bookkeeper import Bookkeeper
from jev_quilt import signed_receipts as sr

HERE = os.path.dirname(os.path.abspath(__file__))

OPTIONS = [
    ("A.move_into_package",
     "vectors/ -> jev_quilt/vectors/ + package-data; ships in wheel; "
     "loader path updated in runtime with env/repo-root fallback"),
    ("B.keep_at_root_exclude",
     "vectors/ stays at repo root; wheel ships NO test pins; "
     "tests reference repo-relative path (status quo, made explicit)"),
    ("C.drop",
     "delete vectors/signed_receipt_vectors.json and the cross-language "
     "byte pins in tests/test_receipts_v2.py"),
]

VERDICT = (
    "B.keep_at_root_exclude WINS. The vectors file is a TEST-ONLY "
    "cross-language contract pin (docs/RECEIPTS-V2.md): 2006 bytes of "
    "known-answer material for the receipts-v2 envelope that Rust "
    "ports/ and TS twist-engine MUST reproduce byte-for-byte. Runtime "
    "code (jev_quilt/signed_receipts.py) never loads it — grep-verified. "
    "Shipping it would install test fixtures into site-packages and "
    "create a false runtime dependency; dropping it would break the "
    "pinned cross-language contract. No tie: A and C each fail one hard "
    "gate (site-packages hygiene / contract survival), B passes both. "
    "Quantum tiebreak not invoked."
)


def main() -> None:
    bk = Bookkeeper("release-0.1.0.vectors-shipping")
    for name, claim in OPTIONS:
        bk.book({"cell": name}, {"option": claim},
                "cell_booked", {"tradeoff": "vectors-shipping"})
    bk.book({"verdict": "B"}, {"rationale": VERDICT},
            "decided", {"decision": "keep_at_root_exclude"})

    tip = bk.replay()
    node = "lane-b.releaser"
    signer, seed_hex, pubkey_hex = sr.generate_identity(node, 1)
    signed = sr.seal(bk.entries[-1], tip, signer, seed_hex)

    out = {
        "ledger": "release-0.1.0.vectors-shipping",
        "chain_tip": tip,
        "verify_only_pubkey": pubkey_hex,
        "signer": signer,
        "note": "Seed intentionally NOT persisted (module law: seeds are "
                "never serialized). Decision material, not a real node key.",
        "options": [n for n, _ in OPTIONS],
        "verdict": VERDICT,
        "sealed_tip_receipt": signed.to_canonical_json(),
    }
    path = os.path.join(HERE, "release-0.1.0-vectors-decision.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")

    verdict = sr.verify_envelope(signed, {signer: pubkey_hex},
                                 expected_chain_tip=tip)
    print("wrote", path)
    print("verify:", verdict)


if __name__ == "__main__":
    main()
