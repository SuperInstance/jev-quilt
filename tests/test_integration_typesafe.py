"""Integration test: real TypeSafe API end-to-end. Requires TYPESAFEAI_KEY env."""
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jev_quilt.typesafe_client import TypeSafeBackend

backend = TypeSafeBackend()
SKIP_LIVE = not os.environ.get("TYPESAFEAI_KEY")


class TestIntegrationTypesafe(unittest.TestCase):

    @unittest.skipIf(SKIP_LIVE, "live API: TYPESAFEAI_KEY not set")
    def test_api_available(self):
        self.assertTrue(backend.available(), "TYPESAFEAI_KEY not set")

    @unittest.skipIf(SKIP_LIVE, "live API: TYPESAFEAI_KEY not set")
    def test_decide_batch_returns_n_decisions(self):
        ds, meta = backend.decide_batch(
            "state",
            [
                {"type": "noul", "instructions": "test noul prob 0.7", "name": "q1"},
                {"type": "noul", "instructions": "test noul prob 0.9", "name": "q2"},
            ],
        )
        self.assertEqual(len(ds), 2)


if __name__ == "__main__":
    unittest.main()
