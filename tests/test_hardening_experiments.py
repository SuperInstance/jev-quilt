"""Hardening tests: jev_quilt.experiments.

Invariants promised by the module docstring, previously enforced by
nothing:

  * "massive, honest, booked": offline mode books ONE receipt per
    domain per round and the WAL verifies; the exit code reflects
    verification (0 only if verify passes).
  * The report carries the honest counts: booked == n * len(DOMAINS),
    questions == n * (all domain questions), chain is the replay hash.
  * Offline booking is deterministic: two identical runs replay to the
    same chain (Law 4: replay == live).
  * Live mode without API keys refuses BEFORE any network: exit 2.
  * Live mode with a failing backend refuses honestly: exit 1, the
    error named on stderr — never a silent empty report.

Stdlib unittest only; deterministic; no network (the live paths are
mocked at the backend boundary).
"""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr
from unittest import mock

from jev_quilt import experiments
from jev_quilt.experiments import DOMAINS, run
from jev_quilt.typesafe_client import TypeSafeBackend

TOTAL_QUESTIONS = sum(len(qs) for _, _, qs in DOMAINS)


class TestOfflineBattery(unittest.TestCase):

    def _run_offline(self, n=2):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "report.json")
            stdout = io.StringIO()
            with redirect_stderr(io.StringIO()):
                with mock.patch("sys.stdout", stdout):
                    rc = run(live=False, n=n, out_path=out)
            with open(out) as f:
                report = json.load(f)
        return rc, report

    def test_exit_zero_and_verify_passes(self):
        rc, report = self._run_offline()
        self.assertEqual(rc, 0)
        self.assertTrue(report["book_verify"])

    def test_every_domain_booked_every_round(self):
        rc, report = self._run_offline(n=3)
        self.assertEqual(report["booked"], 3 * len(DOMAINS))
        self.assertEqual(report["mode"], "offline")
        self.assertEqual(report["rounds"], 3)
        self.assertEqual(report["questions"], 3 * TOTAL_QUESTIONS)

    def test_chain_is_replay_hash_hex(self):
        _, report = self._run_offline()
        self.assertEqual(len(report["chain"]), 64)
        int(report["chain"], 16)  # parses as hex

    def test_sample_rows_present_and_bounded(self):
        _, report = self._run_offline()
        self.assertEqual(len(report["sample_rows"]), 6)
        for row in report["sample_rows"]:
            self.assertIn("domain", row)
            self.assertIn("q", row)

    def test_offline_runs_are_replay_identical(self):
        _, r1 = self._run_offline()
        _, r2 = self._run_offline()
        self.assertEqual(r1["chain"], r2["chain"])
        self.assertEqual(r1["booked"], r2["booked"])

    def test_booked_rows_are_probe_receipts_for_all_domains(self):
        # booked receipts carry the offline probe residue; the chain
        # covering n*len(DOMAINS) receipts is the enforceable shape.
        _, report = self._run_offline(n=1)
        self.assertEqual(report["booked"], len(DOMAINS))


class TestLiveRefusalPolarity(unittest.TestCase):

    def test_live_without_api_key_refuses_before_network(self):
        stderr = io.StringIO()
        stdout = io.StringIO()
        with mock.patch.object(TypeSafeBackend, "available", return_value=False):
            with mock.patch("sys.stdout", stdout):
                with redirect_stderr(stderr):
                    rc = run(live=True, n=1, out_path=None)
        self.assertEqual(rc, 2)
        self.assertIn("FATAL", stderr.getvalue())

    def test_live_backend_failure_is_exit_one_not_exception(self):
        stderr = io.StringIO()
        stdout = io.StringIO()
        with mock.patch.object(TypeSafeBackend, "available", return_value=True), \
             mock.patch.object(TypeSafeBackend, "decide_batch",
                               side_effect=RuntimeError("backend down")):
            with mock.patch("sys.stdout", stdout):
                with redirect_stderr(stderr):
                    rc = run(live=True, n=1, out_path=None)
        self.assertEqual(rc, 1)
        self.assertIn("live call failed", stderr.getvalue())

    def test_live_refusal_never_books_a_partial_report(self):
        # refusal happens on the FIRST domain: no rows, no report file.
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "report.json")
            with mock.patch.object(TypeSafeBackend, "available", return_value=True), \
                 mock.patch.object(TypeSafeBackend, "decide_batch",
                                   side_effect=RuntimeError("boom")):
                with mock.patch("sys.stdout", io.StringIO()):
                    with redirect_stderr(io.StringIO()):
                        rc = run(live=True, n=1, out_path=out)
            self.assertEqual(rc, 1)
            self.assertFalse(os.path.exists(out))


if __name__ == "__main__":
    unittest.main()
