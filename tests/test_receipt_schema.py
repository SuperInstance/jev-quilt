"""R8 receipt-schema pin: every receipt in docs/receipts/ must document
something VERIFIABLE.

Why this test exists (Goodhart red-team R8):
  "receipts shipped" is a fleet KPI, and a receipt that no one can
  verify inflates the KPI exactly as well as a real one. The
  demonstration fixture in tests/fixtures/receipts/
  (FAKE_R8_minted_prose_receipt.json) is prose wrapped in JSON — no
  hash, no signature, no repro command — and it passes casual review.
  This test asserts the validator REJECTS that fake, and that every
  real receipt under docs/receipts/ carries at least one verifiable
  artifact.

Schema v1 (stdlib-only enforcement):
  required fields : decision (or ledger), verdict
  integrity (>=1) : signature + signer        (cryptographic)
                  | repro                     (command that regenerates)
                  | chain_tip                 (64-hex chain binding)
  banned          : filenames starting FAKE_ / DEMO (explicit untrust)
"""
import json
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
DOCS_RECEIPTS = REPO / "docs" / "receipts"
FIXTURES = REPO / "tests" / "fixtures" / "receipts"
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def validate_receipt(obj: dict, name: str = "<memory>"):
    """Return list of schema-violation strings; empty list = valid."""
    problems = []
    if not isinstance(obj, dict):
        return [f"{name}: not a JSON object"]
    if "decision" not in obj and "ledger" not in obj:
        problems.append(f"{name}: missing 'decision' (or 'ledger')")
    if "verdict" not in obj:
        problems.append(f"{name}: missing 'verdict'")
    integrity = []
    if isinstance(obj.get("signature"), str) and obj.get("signer"):
        integrity.append("signature+signer")
    if isinstance(obj.get("repro"), str) and obj["repro"].strip():
        integrity.append("repro")
    if isinstance(obj.get("chain_tip"), str) and HEX64.match(obj["chain_tip"]):
        integrity.append("chain_tip")
    if not integrity:
        problems.append(
            f"{name}: no verifiable artifact "
            "(need one of: signature+signer, repro, chain_tip)"
        )
    return problems


class TestReceiptSchemaV1(unittest.TestCase):
    def test_fake_demo_receipt_is_rejected(self):
        """Negative control: the R8 minted-fake must FAIL schema v1.
        If this test ever fails, the validator has been Goodharted."""
        fake = json.loads(
            (FIXTURES / "FAKE_R8_minted_prose_receipt.json").read_text()
        )
        problems = validate_receipt(fake, "FAKE_R8_minted_prose_receipt.json")
        self.assertTrue(problems, "fake receipt passed schema v1!")
        self.assertTrue(any("verifiable artifact" in p for p in problems))

    def test_docs_receipts_all_valid(self):
        """Every committed receipt carries >=1 verifiable artifact."""
        if not DOCS_RECEIPTS.exists():
            self.skipTest("docs/receipts/ does not exist on this branch yet")
        bad = []
        for p in sorted(DOCS_RECEIPTS.glob("*.json")):
            if p.name.upper().startswith(("FAKE_", "DEMO")):
                bad.append(f"{p.name}: untrusted filename prefix committed")
                continue
            obj = json.loads(p.read_text())
            bad.extend(validate_receipt(obj, p.name))
        self.assertEqual(bad, [])

    def test_receipt_count_kpi_counts_only_valid(self):
        """The 'receipts shipped' number is the SCHEMA-VALID count.
        A prose receipt may sit in the folder, but it must not count."""
        valid = 0
        if DOCS_RECEIPTS.exists():
            for p in DOCS_RECEIPTS.glob("*.json"):
                if p.name.upper().startswith(("FAKE_", "DEMO")):
                    continue
                if not validate_receipt(json.loads(p.read_text()), p.name):
                    valid += 1
        self.assertGreaterEqual(valid, 1)  # 008-goodhart-audit is real


if __name__ == "__main__":
    unittest.main()
