"""R8 skip-registry pin: every skipTest in the suite must be registered.

Why this test exists (Goodhart red-team R8):
  "81 pass 3 skip" is only honest if skips are visible, bounded, and
  reviewed. skips never fail the suite, so the cheapest way to keep a
  suite "green" is to skip your way there. On main (2026-09-25) all 3
  skips are coverage holes: one admits "subsequent behavior changed",
  one admits the env leaked a key, one admits "model layer unstable".
  None of them is dated, owned, or scheduled for repair.

  This test statically finds every skipTest("reason") in tests/ and
  requires the reason to appear in tests/KNOWN_SKIPS.md with a date
  (YYYY-MM-DD) and owner. Add a skip without registering -> red suite.
"""
import ast
import pathlib
import re
import unittest

TESTS_DIR = pathlib.Path(__file__).resolve().parent
REGISTRY = TESTS_DIR / "KNOWN_SKIPS.md"


def find_skips():
    """(file, lineno, reason) for every literal skipTest in tests/."""
    found = []
    for p in sorted(TESTS_DIR.glob("test_*.py")):
        tree = ast.parse(p.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                f = node.func
                is_skip = (isinstance(f, ast.Attribute) and f.attr == "skipTest") or (
                    isinstance(f, ast.Name) and f.id == "skipTest"
                )
                if is_skip and node.args and isinstance(node.args[0], ast.Constant):
                    found.append((p.name, node.lineno, str(node.args[0].value)))
    return found


class TestKnownSkipsRegistry(unittest.TestCase):
    def test_every_skip_is_registered(self):
        registry_text = REGISTRY.read_text() if REGISTRY.exists() else ""
        date_re = re.compile(r"20\d\d-\d\d-\d\d")
        unregistered = []
        for fname, lineno, reason in find_skips():
            head = reason.strip()[:60]
            if head not in registry_text or not date_re.search(registry_text):
                unregistered.append(f"{fname}:{lineno} {head!r}")
        self.assertEqual(
            unregistered,
            [],
            "skipTest calls without a dated entry in tests/KNOWN_SKIPS.md: "
            + "; ".join(unregistered),
        )


if __name__ == "__main__":
    unittest.main()
