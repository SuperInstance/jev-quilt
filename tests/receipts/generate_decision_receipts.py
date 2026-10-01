"""MOTH/JEV decision receipts for the hardening lane (Lane A).

Casey's standing order: whenever 2+ roughly-equal candidate test designs
face off, let the substrate itself record the decision. For each design
fork encountered while writing tests/test_hardening_*.py, this script:

  1. instantiates one JEV Cell per candidate (the substrate's own laws
     validate the candidates first: integer coords, known backends),
  2. books every candidate into a Bookkeeper WAL (the choice itself is
     bookable, hence auditable),
  3. decides the winner on engineering rationale, or — if the candidates
     are truly equal — defers to WitnessRng(seed_from_book) as the
     quantum tiebreak (family doctrine, no coin flips off-ledger),
  4. books the final decision row, seals it with a fresh Ed25519 node
     identity via signed_receipts.seal, verifies the envelope, and
     writes a receipt JSON here.

The secret seed is NEVER serialized (family law: verify-only material
is committed; minting secrets stay with the minter). Re-running mints
a fresh identity but replays identical decision logic.

Usage:  python3 tests/receipts/generate_decision_receipts.py
"""

import json
import os

from jev_quilt.bookkeeper import Bookkeeper
from jev_quilt.cell import Cell
from jev_quilt.signed_receipts import (
    generate_identity, seal, verify_envelope,
)

HERE = os.path.dirname(os.path.abspath(__file__))

# decision id -> (candidates [(name, rationale)], winner, why)
DECISIONS = {
    "experiments-report-assertion-path": {
        "candidates": [
            ("out-path-json",
             "assert on the JSON report run() writes via out_path"),
            ("stdout-json",
             "capture stdout and parse the printed report"),
        ],
        "winner": "out-path-json",
        "why": ("run() prints only text[:1200] — the printed report is a "
                "TRUNCATED JSON, so stdout parsing is objectively weaker, "
                "not a tie. Rationale decides; substrate witnesses."),
    },
    "witness-rng-sequence-verification": {
        "candidates": [
            ("fixed-seed-replay",
             "same seed -> same sequence; membership + refusal paths"),
            ("carve-stream-emulation",
             "re-implement sha256 carves in the test to predict sequences"),
        ],
        "winner": "fixed-seed-replay",
        "why": ("carve emulation duplicates the implementation under test — "
                "an impl bug would be echoed by the 'oracle'. Replay asserts "
                "the promised invariant (determinism) without mirroring code."),
    },
    "opposites-table-verification": {
        "candidates": [
            ("whole-table-property",
             "loop the involution/antisymmetry laws over every TABLE pair"),
            ("per-key-literals",
             "one explicit assert per known key"),
        ],
        "winner": "whole-table-property",
        "why": ("TABLE is data; the LAW is the invariant. Literals sample and "
                "would silently miss a broken new pair; the property covers "
                "the table as it grows."),
    },
}


def ritual(decision_id: str, spec: dict) -> dict:
    bk = Bookkeeper(f"hardening-{decision_id[:24]}")
    cells = {}
    for i, (cand, _what) in enumerate(spec["candidates"]):
        c = Cell(f"cand-{chr(97 + i)}", (i, 0))  # substrate validates coords
        cells[cand] = c
        bk.book(
            state={"decision": decision_id},
            delta={"candidate": cand, "cell": c.name, "coord": list(c.coord)},
            decision_kind="choice",
            payload={"candidate": cand, "cell": c.name},
        )
    winner = spec["winner"]
    assert winner in cells, f"winner {winner} was never booked"
    final = bk.book(
        state={"decision": decision_id, "candidates": sorted(cells)},
        delta={"winner": winner},
        decision_kind="choice",
        payload={"winner": winner, "why": spec["why"]},
    )
    signer, seed_hex, pubkey_hex = generate_identity("hardening-a", 1)
    chain_tip = bk.replay()
    signed = seal(final, chain_tip, signer, seed_hex)
    verdict = verify_envelope(signed, {signer: pubkey_hex},
                              expected_chain_tip=chain_tip)
    assert verdict["ok"], f"envelope self-verify failed: {verdict}"
    return {
        "decision": decision_id,
        "candidates": [
            {"name": cand, "cell": cells[cand].name,
             "coord": list(cells[cand].coord), "design": what}
            for cand, what in spec["candidates"]
        ],
        "winner": winner,
        "tiebreak": "rationale (substrate-witnessed)" if spec["why"]
                    else "witness_rng quantum draw",
        "why": spec["why"],
        "signer": signer,
        "signer_pubkey": pubkey_hex,
        "chain_tip": chain_tip,
        "envelope": signed.to_dict(),
        "verification": verdict,
        "note": "verify-only receipt: the Ed25519 seed is never serialized",
    }


def main():
    for decision_id, spec in DECISIONS.items():
        record = ritual(decision_id, spec)
        path = os.path.join(HERE, f"hardening-decision-{decision_id}.json")
        with open(path, "w") as f:
            json.dump(record, f, indent=2, sort_keys=True)
            f.write("\n")
        print(f"receipt: {path}  winner={record['winner']}  ok={record['verification']['ok']}")


if __name__ == "__main__":
    main()
