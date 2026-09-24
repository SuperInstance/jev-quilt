"""Integration test: real TypeSafe API end-to-end. Requires TYPESAFEAI_KEY env."""
import os
import sys
import unittest
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt.typesafe_client import TypeSafeBackend

backend = TypeSafeBackend()
SKIP_LIVE = not os.environ.get("TYPESAFEAI_KEY")


@unittest.skipIf(SKIP_LIVE, "live API: TYPESAFEAI_KEY not set")
def _live_only(fn):
    return fn


class TestIntegrationTypesafe(unittest.TestCase):

    @unittest.skipIf(SKIP_LIVE, "live API: TYPESAFEAI_KEY not set")
    def test_api_available(self):
        self.assertTrue(backend.available(), "TYPESAFEAI_KEY not set")

    @unittest.skipIf(SKIP_LIVE, "live API: TYPESAFEAI_KEY not set")
    def test_choice_returns_valid(self):
        if not backend.available():
            self.skipTest("no key")
        ds = backend.decide(
            "state",
            {"type": "choice", "criteria": {"a": 1.0, "b": 2.0}},
        )
        self.assertIn(ds.kind, ("choice", "refusal"))

    @unittest.skipIf(SKIP_LIVE, "live API: TYPESAFEAI_KEY not set")
    def test_noul_returns_probability(self):
        if not backend.available():
            self.skipTest("no key")
        ds = backend.decide("state", {"type": "noul"})
        if ds.kind == "noul":
            self.assertGreaterEqual(ds.noul, 0.0)
            self.assertLessEqual(ds.noul, 1.0)

    @unittest.skipIf(SKIP_LIVE, "live API: TYPESAFEAI_KEY not set")
    def test_batch_returns_n_decisions(self):
        if not backend.available():
            self.skipTest("no key")
        ds, meta = backend.decide_batch(
            "state",
            [
                {"type": "noul", "instructions": "test1"},
                {"type": "noul", "instructions": "test2"},
            ],
        )
        self.assertEqual(len(ds), 2)


if __name__ == "__main__":
    unittest.main()
