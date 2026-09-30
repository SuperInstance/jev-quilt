"""KAT bridge pins — characterisation gate for the JEV oracle instrument.

Commissioned item (queue 2026-09-30): bridge AI-Writings' jev_kat.mjs (known-answer
control, PR #70 merged 2026-09-29T21:26:53Z) into jev-quilt as
tools/jev_kat_bridge.mjs + a characterisation gate in this suite. NO VERDICT MUTATION:
these pins never touch jev_quilt verdicts, receipts, or ledgers; they pin only the
gate's evaluation logic offline (fixture receipts, no key, no network).
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BRIDGE = REPO / "tools" / "jev_kat_bridge.mjs"

PASSING = {
    "schema": "fleet/jev-kat@v1",
    "noul": {
        "regimeA1": {"passes": True},
        "regimeA2": {"passes": True},
        "regimeB": {"passes": True, "spread": 0.61},
    },
    "choice": {"correct": True, "discriminates": True, "verdict": "PASS"},
    "score": {"spread": 0.55, "discriminates": True, "verdict": "PASS"},
}

DEGRADED_REGIMEB = json.loads(json.dumps(PASSING))
DEGRADED_REGIMEB["noul"]["regimeB"]["passes"] = False

DEGRADED_SCORE_ONLY = json.loads(json.dumps(PASSING))
DEGRADED_SCORE_ONLY["score"] = {
    "spread": 0.02, "discriminates": False, "verdict": "FAIL_DISCRIMINATION",
}


def run_gate(fixture):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(fixture, f)
        path = f.name
    return subprocess.run(
        ["node", str(BRIDGE), "gate", path],
        capture_output=True, text=True, timeout=60,
    )


class TestKatBridgeExists(unittest.TestCase):
    def test_bridge_file_present(self):
        # FAIL-first surface: on main-tip (pre-bridge) this file does not exist.
        self.assertTrue(BRIDGE.is_file(), "tools/jev_kat_bridge.mjs must exist")

    def test_canonical_instrument_pin(self):
        # The instrument stays canonical in AI-Writings; the pin must name repo,
        # commit, and sha256 so a drifted upstream cannot be bridged silently.
        src = BRIDGE.read_text()
        self.assertIn("SuperInstance/AI-Writings", src)
        self.assertIn("3f8405888366e3697b3775017fa5fe13d6244226", src)
        self.assertIn("5f280b8b435852872fadeb449f4382275e80be56e80035da02274db8006e1cc5", src)


class TestKatGateLogic(unittest.TestCase):
    def test_passing_receipt_is_characterised(self):
        r = run_gate(PASSING)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("CHARACTERISED", r.stdout)

    def test_regimeB_failure_degrades_canon_gate(self):
        # regime B is the canon-gate regime; its failure must gate DEGRADED.
        r = run_gate(DEGRADED_REGIMEB)
        self.assertEqual(r.returncode, 2, r.stderr + r.stdout)
        self.assertIn("DEGRADED", r.stdout)
        self.assertIn("regime B", r.stdout)

    def test_score_failure_is_advisory_not_blocking(self):
        # score does not discriminate -> recorded in reasons, but the canon gate
        # never uses score, so the verdict stays CHARACTERISED. Mutating this to
        # blocking would be a verdict mutation by the back door.
        r = run_gate(DEGRADED_SCORE_ONLY)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("CHARACTERISED", r.stdout)
        self.assertIn("score", r.stdout)

    def test_schema_invalid_rejected(self):
        r = run_gate({"schema": "something-else@v9"})
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)
        self.assertIn("SCHEMA_INVALID", r.stdout)

    def test_missing_noul_rejected(self):
        r = run_gate({"schema": "fleet/jev-kat@v1", "choice": {}})
        self.assertEqual(r.returncode, 3, r.stderr + r.stdout)

    def test_bridged_record_unwraps_receipt(self):
        # `run` writes {bridge, instrument, gated, receipt}; gate must accept it.
        record = {"bridge": "x", "receipt": PASSING}
        r = run_gate(record)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)


if __name__ == "__main__":
    unittest.main()
