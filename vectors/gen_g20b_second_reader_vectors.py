"""G20b — the Second Reader: cross-language vector generator.

`ai-writings/situations/FABLE-ANSWER.md` (G20b): today `OrgBook.chain()`,
`OrgBook.decisions_digest()`, `Commons.root()`, and `Schoolhouse.pins()`
have exactly ONE witness — Python reading itself. This script exports a
FIXED, deterministic scenario (raw dict inputs, not just Python's own
output hexes) so an independent, non-Python reader can recompute every
pin from the bytes-law alone and assert byte-for-byte agreement.

Run from the repo root:

    python3 vectors/gen_g20b_second_reader_vectors.py

Writes `vectors/g20b_second_reader_vectors.json`. Every "expected_*" field
is read directly off the REAL objects this repo's own code produces
(`Bookkeeper`/`OrgBook`/`Commons`/`fold.mmr_root`) — never hand-computed —
and the reconstructed raw inputs (`state`/`delta`/`payload` dicts) are
cross-checked in this same script against those real objects' stored
hashes before anything is written, so the fixture cannot silently drift
from the code it claims to describe (see `_selfcheck` calls below).

Scope (see `ports/rust/src/g20b.rs` module docstring for the full
reproduced-vs-STRETCH accounting):

  * `OrgBook.chain()` — FULLY reproduced from raw `state`/`delta`/`payload`
    dicts + typed decision fields (own JSON canonicalization + fnv1a-64 +
    sha256, no Python involved).
  * `OrgBook.decisions_digest()` — FULLY reproduced by replaying the
    diploma/streak machinery (`standing.py`'s rule) purely from each
    entry's typed fields (runner/key/correct/base_verdict/answer).
  * `fold.mmr_root()` — FULLY reproduced and exercised generically (not
    just on this fixture's own leaves).
  * `Commons.root()` — the MMR/leaf MECHANICS are fully reproduced; the
    deposit/tombstone table itself is exported as ground truth (deriving
    it from scratch requires re-implementing the attest/admit/claim
    trust-and-quorum pipeline — Ed25519, BLAKE3, Q16, CalibratedFloor —
    which is out of scope here and flagged as STRETCH).

ASCII-only by construction: Python's `json.dumps(..., sort_keys=True)`
defaults to `ensure_ascii=True` (non-ASCII becomes `\\uXXXX`), which this
generator's minimal cross-language JSON canonicalizer does not attempt to
match in general — every string in this fixture is plain ASCII so the
question never arises. Flagged, not silently sidestepped.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jev_quilt.bookkeeper import Bookkeeper, fnv1a
from jev_quilt.orgbook import OrgBook
from jev_quilt.commons import Commons
from jev_quilt.fold import mmr_root
from jev_quilt.schoolhouse import Schoolhouse
from jev_quilt.calibrate import CalibratedFloor  # noqa: F401 (documents the STRETCH boundary)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "g20b_second_reader_vectors.json")


# ── rebuild the exact state/delta/payload dicts OrgBook.record_dispatch
#    hands to Bookkeeper.book() (mirrors orgbook.py's construction 1:1) ──
def _build_state(dispatch_id):
    return {"dispatch_id": dispatch_id}


def _build_delta(outcome, correct):
    return {"outcome": outcome, "correct": bool(correct)}


def _build_payload(dispatch_id, runner, tier, verdict, outcome, correct,
                    task_class, answer_value, base_verdict, extra):
    payload = {
        "dispatch_id": dispatch_id, "runner": runner, "tier": tier,
        "verdict": verdict, "outcome": outcome, "correct": bool(correct),
        "key": task_class, "answer": answer_value,
    }
    if base_verdict is not None:
        payload["base_verdict"] = base_verdict
    payload.update(extra)
    return payload


def _selfcheck_hash(d: dict, expected_hex: str, label: str) -> None:
    got = hashlib.sha256(json.dumps(d, sort_keys=True, default=str).encode()).hexdigest()
    assert got == expected_hex, f"fixture drift ({label}): {got} != {expected_hex}"


# ── the driven scenario ──────────────────────────────────────────────
DIPLOMA = 3


def build_orgbook():
    """A scenario that exercises: earning a diploma streak, one booked-wrong
    revocation, re-earning it, a runner that never earns it, AND — the G20a
    fire-time probe itself — a refusal whose freeform `reason` overruns the
    200-char residue cap, to prove the typed fields survive that cap
    (C9)."""
    org = OrgBook("org.g20b", diploma=DIPLOMA)
    calls = []  # (dispatch_id, tier, task_class, runner, verdict, outcome, base_verdict, correct, answer, extra)

    def record(dispatch_id, tier, task_class, runner, verdict, outcome, *,
               base_verdict="ACT", correct=None, answer=None, **extra):
        calls.append(dict(dispatch_id=dispatch_id, tier=tier, task_class=task_class,
                          runner=runner, verdict=verdict, outcome=outcome,
                          base_verdict=base_verdict, correct=correct, answer=answer,
                          extra=extra))
        return org.record_dispatch(dispatch_id, tier, task_class, runner, verdict,
                                    outcome, base_verdict=base_verdict, correct=correct,
                                    answer=answer, **extra)

    # alpha/grep-sweep: 3 correct (earns ANSWER), then a booked-wrong
    # (revokes), then 3 more correct (re-earns) — exercises streak-earn,
    # revoke, and re-earn in decisions_digest.
    for i in range(DIPLOMA):
        record(f"a{i}", "haiku", "grep-sweep", "alpha", "ACT", "correct", base_verdict="ACT")
    record("a-bad", "haiku", "grep-sweep", "alpha", "ACT", "wrong", base_verdict="ACT")
    for i in range(DIPLOMA):
        record(f"a2-{i}", "haiku", "grep-sweep", "alpha", "ACT", "correct", base_verdict="ACT")

    # beta/lint: only 2 correct — never clears the diploma.
    for i in range(DIPLOMA - 1):
        record(f"b{i}", "sonnet", "lint", "beta", "ACT", "correct", base_verdict="ACT")

    # the G20a fire-time probe: a REFUSED admission whose `reason` overruns
    # the 200-char residue cap. Booked with a long freeform `reason` extra —
    # the typed fields (dispatch_id/runner/key/correct/base_verdict/answer)
    # must still be exactly recoverable (that is the whole point of C9's
    # fix), even though the JSON residue truncates mid-string.
    long_reason = "not_reproduced_for_recipient: " + ("padding-ring-witness-" * 12)
    assert len(long_reason) > 200
    record("refused-1", "admit", "admit", "gamma.issuer", "CONFIRM", "refused",
           base_verdict="CONFIRM", correct=False, answer="admit",
           reason=long_reason)

    return org, calls


def export_orgbook_entries(org: OrgBook, calls: list) -> list:
    out = []
    for call, e in zip(calls, org.book.entries):
        answer_value = call["answer"] if call["answer"] is not None else call["tier"]
        correct = call["correct"]
        if correct is None:
            correct = str(call["outcome"]).lower() in {
                "correct", "pass", "passed", "viable", "ok", "done"}
        state = _build_state(call["dispatch_id"])
        delta = _build_delta(call["outcome"], correct)
        payload = _build_payload(call["dispatch_id"], call["runner"], call["tier"],
                                 call["verdict"], call["outcome"], correct,
                                 call["task_class"], answer_value, call["base_verdict"],
                                 call["extra"])
        _selfcheck_hash(state, e.state_hash, f"state[{e.tick}]")
        _selfcheck_hash(delta, e.delta_hash, f"delta[{e.tick}]")
        residue = json.dumps(payload, sort_keys=True, default=str)[:200]
        assert residue == e.payload, f"residue mismatch at tick {e.tick}"
        assert f"{fnv1a(residue.encode('utf-8')):016x}" == e.payload_hash
        decision_fields = (e.dispatch_id, e.runner, e.key, e.correct, e.base_verdict, e.answer)
        assert e.dispatch_id == call["dispatch_id"]
        out.append({
            "tick": e.tick,
            "state": state,
            "delta": delta,
            "decision_kind": e.decision_kind,
            "payload": payload,
            "typed": {
                "dispatch_id": e.dispatch_id, "runner": e.runner, "key": e.key,
                "correct": e.correct, "base_verdict": e.base_verdict, "answer": e.answer,
            },
            "expected": {
                "state_hash": e.state_hash,
                "delta_hash": e.delta_hash,
                "payload_residue": e.payload,
                "payload_hash": e.payload_hash,
                "sha": e.sha(),
            },
        })
    return out


def build_mmr_vectors():
    vecs = []
    for n in (0, 1, 2, 3, 4, 5, 7, 8, 13, 16):
        leaves = [hashlib.sha256(f"g20b-leaf-{i}".encode()).digest() for i in range(n)]
        vecs.append({
            "leaves_hex": [l.hex() for l in leaves],
            "expected_root_hex": mmr_root(leaves).hex(),
        })
    return vecs


def build_commons():
    """A commons scenario exercising deposits from multiple sources AND a
    forget (G12 tombstone) — `root()`'s two leaf groups, both exercised."""
    c = Commons(quorum=3)
    c.deposit("route-a", "left", 2, source="witness-1")
    c.deposit("route-a", "left", 1, source="witness-2")
    c.deposit("route-a", "right", 4, source="witness-3")
    c.deposit("route-b", "up", 5, source="witness-1")
    c.forget("route-b", "up")             # tombstoned: absent from deposits, present in root
    c.deposit("route-c", "steady", 3, source=None)  # anonymous source
    return c


def main():
    org, calls = build_orgbook()
    entries = export_orgbook_entries(org, calls)
    expected_chain = org.chain()
    expected_digest = org.decisions_digest()

    commons = build_commons()
    expected_commons_root = commons.root().hex()

    out = {
        "comment": (
            "G20b cross-language vectors (jev-quilt/ports/rust/src/g20b.rs "
            "MUST reproduce every 'expected*' field byte-for-byte from the "
            "raw dicts/fields above it — never from copying the hex "
            "itself). Generated by vectors/gen_g20b_second_reader_vectors.py."
        ),
        "diploma": DIPLOMA,
        "orgbook": {
            "cell_name": org.book.cell_name,
            "entries": entries,
            "expected_chain": expected_chain,
        },
        "decisions_digest": {
            "expected": expected_digest,
        },
        "mmr_vectors": build_mmr_vectors(),
        "commons": {
            "quorum": commons.quorum,
            "deposits": [{"key": d.key, "answer": d.answer, "weight": d.weight}
                        for d in commons.deposits()],
            "tombstones": sorted([list(p) for p in commons._tombstones]),
            "expected_root_hex": expected_commons_root,
        },
        "pins": {
            "chain": expected_chain,
            "decisions_digest": expected_digest,
            "commons_root": expected_commons_root,
        },
    }

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print("wrote", OUT)
    print("pins:", out["pins"])


if __name__ == "__main__":
    main()
