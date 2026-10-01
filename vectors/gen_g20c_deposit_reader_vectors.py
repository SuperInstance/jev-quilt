"""G20c — the Deposit Reader: cross-language vector generator.

G20b's own STRETCH note (`ports/rust/src/g20b.rs`'s module docstring):
`Commons.root()`'s MMR/leaf mechanics were reproduced in Rust, but the
commons **deposit table itself** (which `(key, answer, weight)` triples
exist at all) was taken from the fixture as ground truth — deriving it
independently means re-implementing `Schoolhouse.enroll`'s whole bridge:
`Claim.from_books` (G16) -> `attest` (G17) -> `admit` (G11/G14) ->
`Commons.deposit` (R2). This script drives that REAL pipeline (via the
shipped `Schoolhouse` class — reproduce/issue/enroll/forget — never a
hand-written `Commons.deposit` call) and exports every raw input a second,
independent reader needs to re-derive the same table from scratch:

  * every witness's reported `(value, Q16 magnitude)` — the raw claim
    inputs `Claim.from_books` folds through `CalibratedFloor`/`surprise`;
  * the recipient's OWN trust map, quorum, and a fresh `CalibratedFloor`,
    plus the `reading_magnitude` lookup `admit()` needs to re-judge drift
    independently of the issuer's advisory flags;
  * the resulting `Attestation`'s carried readings/consensus/quorum/floor
    (so a reader can recompute `attestation_root` and its own
    `canonical_attestation_bytes` and check the ROOT the signature seals —
    the one root-integrity check that needs no cryptography at all);
  * the final `Commons.deposits()` table and `Commons.root()`, plus one
    `forget()` (G12 tombstone) so the reader exercises both leaf groups.

Scope (see `ports/rust/src/g20c.rs`'s module docstring for the full
reproduced-vs-STRETCH accounting): the Ed25519/BLAKE3 SIGNATURE itself is
NOT re-derived here (no crypto crate, no hand-rolled bignum curve — see
G20b's own precedent). Everything downstream of "the signature verified"
IS re-derived: `Q16` exact-rational arithmetic, `surprise`, the swarm-drift
`CalibratedFloor` judgment (both the issuer's advisory pass inside `Claim.
from_books` and the recipient's OWN re-judgment inside `admit`), the
trust/quorum/unanimity gate, the `attestation_root` integrity check, the
`enroll` bridge (`weight = len(admission.trusted)`, `source = att.signer`),
and `Commons.deposits()` / `Commons.root()` over the resulting table.

Run from the repo root:

    python3 vectors/gen_g20c_deposit_reader_vectors.py

Writes `vectors/g20c_deposit_reader_vectors.json`. Every "expected_*" field
is read directly off the REAL objects this repo's own code produces
(`Schoolhouse`/`Claim`/`Attestation`/`Admission`/`Commons`) — never
hand-computed.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jev_quilt.q16 import Q16
from jev_quilt.calibrate import CalibratedFloor
from jev_quilt.schoolhouse import Schoolhouse
from jev_quilt import ed25519

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "g20c_deposit_reader_vectors.json")

CLAIM_QUORUM = 3     # Claim.earns_standing()'s quorum (non-drifting witnesses)
ADMIT_QUORUM = 3     # the recipient's OWN quorum, passed fresh to every enroll()
COMMONS_QUORUM = 5   # Schoolhouse.commons' earned() threshold (not exercised by root)
DIPLOMA = 3           # Schoolhouse's OrgBook diploma (unused by this rung's pins)
FLOOR_K = 4           # CalibratedFloor window — smallest EXACT_K entry that lets a
                      # 4-8 witness scenario actually warm the floor


def _seed_hex(signer: str) -> str:
    """Deterministic (not random) 32-byte Ed25519 seed, so the fixture is
    reproducible byte-for-byte across runs — same discipline as every other
    fixed scenario in this family."""
    return hashlib.sha256(f"g20c-seed::{signer}".encode()).hexdigest()[:64]


def _q16_wire(q: Q16) -> dict:
    return {"num": q.num, "den": q.den}


class _Question:
    """One (key, issuer) reproduction: a fixed set of witnesses, each
    reporting a (value, Q16 magnitude), reproduced/issued/enrolled through
    the REAL `Schoolhouse` pipeline."""

    def __init__(self, key: str, issuer: str, readings: dict,
                 recipient_trust: dict, base_verdict: str = "CONFIRM",
                 sea_floor: "Q16 | None" = None, admit_quorum: "int | None" = None,
                 expect_conferred: bool = True):
        self.key = key
        self.issuer = issuer
        self.readings = readings              # witness -> (value, Q16 magnitude)
        self.recipient_trust = recipient_trust  # witness -> int trust (default 0)
        self.base_verdict = base_verdict
        # G14: an issue-time sea (earned_floor) so `admit`'s sea-grading gate
        # (earned but outside what the reproduction was graded under ->
        # CONFIRM, not ANSWER) is exercised too, not just the ANSWER path.
        self.sea_floor = sea_floor
        self.admit_quorum = admit_quorum if admit_quorum is not None else ADMIT_QUORUM
        self.expect_conferred = expect_conferred


def build_scenario():
    """Three questions: two independent issuers pooling evidence for the
    SAME key (`route-north`, exercising `Commons.deposit`'s weight-pooling
    across sources), one for a second key (`route-south`), and one for a
    THIRD key (`route-west`) that is deposited then `forget()`-ten (G12),
    so the reader independently derives both a live pooled deposit and a
    tombstone leaf from the same real pipeline."""
    questions = [
        _Question(
            key="route-north", issuer="issuer-north-1",
            readings={
                # "n0" sorts FIRST and reports a wildly-off magnitude; the
                # calibrated floor's k=4 window (the last 4 witnesses in
                # sorted order) is built from n2..n5's calm surprises, so
                # n0 is judged against a floor it never got to pollute —
                # a real drift-based exclusion, not a hand-picked flag.
                "n0": ("shallow", Q16(500)),
                "n1": ("shallow", Q16(40)), "n2": ("shallow", Q16(41)),
                "n3": ("shallow", Q16(39)), "n4": ("shallow", Q16(42)),
                "n5": ("shallow", Q16(38)),
            },
            recipient_trust={"n0": 1, "n1": 1, "n2": 1, "n3": 1, "n4": 1, "n5": 1},
        ),
        _Question(
            key="route-north", issuer="issuer-north-2",
            readings={
                "n2": ("shallow", Q16(41)), "n3": ("shallow", Q16(39)),
                "n4": ("shallow", Q16(42)), "n7": ("shallow", Q16(40)),
                "n8": ("shallow", Q16(37)),
            },
            # n8 is DISTRUSTED by the recipient — a trust-based drop, distinct
            # from n6's drift-based drop above (admit()'s `dropped` unions both).
            recipient_trust={"n2": 1, "n3": 1, "n4": 1, "n7": 1, "n8": 0},
        ),
        _Question(
            key="route-south", issuer="issuer-south-1",
            readings={
                "s1": ("deep", Q16(80)), "s2": ("deep", Q16(81)),
                "s3": ("deep", Q16(79)), "s4": ("deep", Q16(82)),
            },
            recipient_trust={"s1": 1, "s2": 1, "s3": 1, "s4": 1},
            # a TIGHT issue-time sea (0.1): the recipient's own re-graded
            # surprise (its magnitudes are the same spread, surprise ~2.5)
            # blows well past it, so `admit` still CONFERS (unanimous,
            # quorum met) but downgrades ANSWER -> CONFIRM (G14).
            sea_floor=Q16(1, 10),
        ),
        _Question(
            key="route-west", issuer="issuer-west-1",
            readings={
                "w1": ("gone", Q16(10)), "w2": ("gone", Q16(11)),
                "w3": ("gone", Q16(9)), "w4": ("gone", Q16(12)),
            },
            recipient_trust={"w1": 1, "w2": 1, "w3": 1, "w4": 1},
        ),
        _Question(
            # Negative-space coverage (never touches `commons` — refused
            # admissions deposit nothing, `schoolhouse.py`'s bridge): four
            # witnesses reproduce and agree cleanly, but the RECIPIENT's own
            # quorum (5) exceeds how many it ever trusts (4) — `admit`
            # refuses with `reason="not_reproduced_for_recipient"` even
            # though every trusted witness agreed. A reader that always
            # confers would pass every question above for the wrong
            # reason; this one only passes if `conferred=False` is
            # independently derived too.
            key="route-refused", issuer="issuer-ghost-1",
            readings={
                "r1": ("shadow", Q16(20)), "r2": ("shadow", Q16(21)),
                "r3": ("shadow", Q16(19)), "r4": ("shadow", Q16(22)),
            },
            recipient_trust={"r1": 1, "r2": 1, "r3": 1, "r4": 1},
            admit_quorum=5, expect_conferred=False,
        ),
    ]
    return questions


def run(questions):
    sh = Schoolhouse("schoolhouse.g20c", quorum=COMMONS_QUORUM, diploma=DIPLOMA)
    reading_fn = lambda book: book   # `book` IS the (value, Q16) tuple directly

    pubkeys = {}
    exported = []

    for q in questions:
        books = dict(q.readings)
        issuer_floor = CalibratedFloor(k=FLOOR_K)
        claim = sh.reproduce(books, reading_fn=reading_fn, quorum=CLAIM_QUORUM,
                             floor=issuer_floor, runner=q.issuer, base_verdict="ACT")
        assert claim.earns_standing(), f"{q.key}/{q.issuer}: claim failed to earn standing — fixture design error"

        seed_hex = _seed_hex(q.issuer)
        pubkeys[q.issuer] = ed25519.publickey(bytes.fromhex(seed_hex)).hex()
        att = sh.issue(claim, signer=q.issuer, seed_hex=seed_hex, floor=q.sea_floor)

        recipient_floor = CalibratedFloor(k=FLOOR_K)
        magnitudes = {w: mag for w, (_v, mag) in q.readings.items()}
        enrollment = sh.enroll(
            att, pubkeys, key=q.key, trust=q.recipient_trust, quorum=q.admit_quorum,
            floor=recipient_floor, reading_magnitude=lambda r: magnitudes[r.witness],
            base_verdict=q.base_verdict,
        )
        assert enrollment.admission.conferred == q.expect_conferred, (
            f"{q.key}/{q.issuer}: expected conferred={q.expect_conferred}, "
            f"got {enrollment.admission.conferred} — fixture design error")

        exported.append({
            "key": q.key,
            "issuer": q.issuer,
            "claim_quorum": CLAIM_QUORUM,
            "admit_quorum": q.admit_quorum,
            "floor_k": FLOOR_K,
            "witnesses": {
                w: {"value": v, "magnitude": _q16_wire(mag)}
                for w, (v, mag) in sorted(q.readings.items())
            },
            "recipient_trust": dict(sorted(q.recipient_trust.items())),
            "expected": {
                "claim_readings": [
                    {"witness": r.witness, "value": r.value, "drifting": r.drifting}
                    for r in claim.readings(include_drifting=True)
                ],
                "claim_consensus": claim.consensus(),
                "attestation": {
                    "readings": [
                        {"witness": r.witness, "value": r.value, "drifting": r.drifting}
                        for r in att.readings
                    ],
                    "consensus": att.consensus,
                    "quorum": att.quorum,
                    "earned_floor": att.earned_floor,
                    "root": att.root,
                    "signer": att.signer,
                },
                "admission": {
                    "conferred": enrollment.admission.conferred,
                    "verdict": enrollment.admission.verdict,
                    "value": enrollment.admission.value,
                    "reason": enrollment.admission.reason,
                    "trusted": list(enrollment.admission.trusted),
                    "dropped": list(enrollment.admission.dropped),
                },
                "deposit": {
                    "deposited": enrollment.deposited,
                    "key": q.key,
                    "answer": enrollment.admission.value,
                    "weight": enrollment.weight,
                    "source": enrollment.source,
                },
            },
        })

    # G12: route-west is deposited through the REAL pipeline above, then
    # forgotten — the tombstone leaf must fold into `commons.root()` exactly
    # as it does for a hand-written deposit (G20b already proved the leaf
    # mechanics; this proves the DERIVED deposit forgets the same way).
    # Exported as raw scenario data (`forgets`, below), not left for a
    # reader to infer, so the independent derivation never has to hardcode
    # this script's own choice of which route to forget.
    forgets = [("route-west", "gone")]
    for key, answer in forgets:
        sh.forget(key, answer)

    commons_root_hex = sh.commons.root().hex()
    deposits_table = [{"key": d.key, "answer": d.answer, "weight": d.weight}
                      for d in sh.commons.deposits()]
    tombstones = sorted([list(p) for p in sh.commons._tombstones])

    return {
        "comment": (
            "G20c cross-language vectors (jev-quilt/ports/rust/src/g20c.rs "
            "MUST derive every 'expected*' field byte-for-byte from the raw "
            "witness readings/trust/quorum/floor above it — never from "
            "copying the deposit table itself. Ed25519/BLAKE3 signature "
            "verification is the one honest STRETCH, documented in g20c.rs's "
            "module docstring). Generated by "
            "vectors/gen_g20c_deposit_reader_vectors.py."
        ),
        "commons_quorum": COMMONS_QUORUM,
        "questions": exported,
        "forgets": [list(p) for p in forgets],
        "commons": {
            "deposits": deposits_table,
            "tombstones": tombstones,
            "expected_root_hex": commons_root_hex,
        },
        "pins": {
            "commons_root": commons_root_hex,
        },
    }


def main():
    out = run(build_scenario())
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print("wrote", OUT)
    print("deposits:", out["commons"]["deposits"])
    print("tombstones:", out["commons"]["tombstones"])
    print("commons_root:", out["commons"]["expected_root_hex"])
    for q in out["questions"]:
        print(q["key"], q["issuer"], "->", q["expected"]["admission"],
              "deposit:", q["expected"]["deposit"])


if __name__ == "__main__":
    main()
