#!/usr/bin/env python3
"""R4 — replay determinism: bookkeeper WAL invariants the docs already claim.

Pins (from bookkeeper.py docstrings, quoted inline):
- Law 4: "replay ≡ live" — replay() is byte-identical across simulated
  restarts (JSON persistence round-trip) and across processes (subprocess
  cold-start booking of the same payloads from the same seeds).
- Receipt.sha(): "editing payload alone breaks replay" — tamper evidence:
  a one-character payload edit diverges the chain; verify() catches tick
  corruption. (Referee validated by positive detection, not absence.)
- fnv1a docstring: "a Rust receipt and a Python receipt for the same
  residue must agree, non-ASCII included" — pin the exact fnv1a-64 hex for
  a non-ASCII residue so a Rust-side test can assert the same number.
- Empty-payload back-compat: "Empty payload keeps the stored hash — the
  historical formula, back-compat pinned."

Stdlib unittest only. Fixed seeds. No network.
"""
import hashlib, json, subprocess, sys, tempfile, unittest
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from jev_quilt.bookkeeper import Bookkeeper, Receipt, fnv1a

# Fixed payloads — a non-trivial booking script shared with the subprocess pin.
PAYLOADS = [
    {"kind": "spawn", "name": "scout-alpha", "params": {"depth": 1, "seed": 42}},
    {"kind": "book", "domains": ["mesh", "wal", "canon"], "drift": 0.03125},
    {"kind": "verdict", "text": "café Δ 日本語 — non-ASCII residue", "score": 0.875},
    {"kind": "forget", "reason": "ttl", "tick_budget": 128},
]

SUBPROCESS_BOOKER = r'''
import hashlib, json, sys
sys.path.insert(0, sys.argv[1])
from jev_quilt.bookkeeper import Bookkeeper
payloads = json.loads(sys.argv[2])
bk = Bookkeeper("replay-test-cell")
for p in payloads:
    bk.book(state={"seq": p["kind"], "len": len(payloads)},
            delta={"op": p["kind"]}, decision_kind=p["kind"], payload=p)
print(bk.replay())
'''


def book_script(payloads):
    """Book PAYLOADS into a fresh Bookkeeper; return (bookkeeper, chain)."""
    bk = Bookkeeper("replay-test-cell")
    for p in payloads:
        bk.book(state={"seq": p["kind"], "len": len(payloads)},
                delta={"op": p["kind"]}, decision_kind=p["kind"], payload=p)
    return bk, bk.replay()


class TestReplayDeterminism(unittest.TestCase):
    def test_replay_identical_across_simulated_restarts(self):
        # Law 4: "replay ≡ live". Serialize the book, rebuild in a fresh
        # Bookkeeper (as a restarted cell would from persisted storage),
        # replay must be byte-identical.
        bk, chain = book_script(PAYLOADS)
        persisted = json.dumps([asdict(e) for e in bk.entries])
        rebuilt = Bookkeeper("replay-test-cell")
        for d in json.loads(persisted):
            rebuilt.entries.append(Receipt(**d))
        self.assertEqual(rebuilt.replay(), chain)
        self.assertTrue(rebuilt.verify())

    def test_replay_identical_across_processes(self):
        # Cold-start pin: a subprocess that imports the package fresh and
        # books the same payloads must produce the same chain hash. Guards
        # against import-order, time-, or global-state dependence.
        _, chain = book_script(PAYLOADS)
        repo = str(Path(__file__).resolve().parent.parent)
        out = subprocess.run(
            [sys.executable, "-c", SUBPROCESS_BOOKER, repo, json.dumps(PAYLOADS)],
            capture_output=True, text=True, timeout=60, cwd=repo)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stdout.strip(), chain)

    def test_tampered_payload_diverges_chain(self):
        # Receipt.sha(): "editing payload alone breaks replay"
        bk, chain = book_script(PAYLOADS)
        victim = bk.entries[2]
        bk.entries[2] = Receipt(**{**asdict(victim), "payload": victim.payload + "X"})
        self.assertNotEqual(bk.replay(), chain)

    def test_tampered_tick_fails_verify(self):
        bk, _ = book_script(PAYLOADS)
        d = asdict(bk.entries[1]); d["tick"] = 99
        bk.entries[1] = Receipt(**d)
        self.assertFalse(bk.verify())

    def test_fnv1a_nonascii_cross_language_pin(self):
        # fnv1a docstring: "a Rust receipt and a Python receipt for the same
        # residue must agree, non-ASCII included." This hex IS the contract;
        # a Rust-side test must assert the same value.
        residue = "café Δ 日本語"
        self.assertEqual(fnv1a(residue.encode("utf-8")), 0x024A555471370B18D)

    def test_empty_payload_backcompat(self):
        # "Empty payload keeps the stored hash — the historical formula"
        r = Receipt(tick=1, state_hash="a" * 64, delta_hash="b" * 64,
                    decision_kind="noop", payload_hash="c" * 16, payload="")
        raw = f"1|{'a'*64}|{'b'*64}|noop|{'c'*16}"
        self.assertEqual(r.sha(), hashlib.sha256(raw.encode()).hexdigest())

    def test_wake_state_shape(self):
        bk, chain = book_script(PAYLOADS)
        ws = bk.wake_state()
        self.assertEqual(ws["cell"], "replay-test-cell")
        self.assertEqual(ws["booked_ticks"], len(PAYLOADS))
        self.assertEqual(ws["chain"], chain)


if __name__ == "__main__":
    unittest.main()
