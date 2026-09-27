"""G20b — the Second Reader: keep the checked-in cross-language fixture
honest.

`vectors/g20b_second_reader_vectors.json` is what the non-Python (Rust)
reader in `ports/rust/src/g20b.rs` reproduces `OrgBook.chain()`,
`OrgBook.decisions_digest()`, and `Commons.root()` from — a second,
independent witness to `Schoolhouse.pins()` (see
`ai-writings/situations/FABLE-ANSWER.md`, G20b). This test does NOT
re-verify the Rust reader (that is `cargo test`'s job, in
`ports/rust/`); it verifies the *fixture itself* stays truthful:

  * `test_committed_vectors_match_a_fresh_regeneration` — regenerating
    the vectors from `vectors/gen_g20b_second_reader_vectors.py` right
    now reproduces the checked-in file byte-for-byte. A committed fixture
    that has drifted from the generator (someone edited one without the
    other) fails here loudly, before it ever reaches the Rust side.
  * `test_pins_match_a_live_schoolhouse_style_orgbook_and_commons` — the
    fixture's `pins` are cross-checked against fresh `OrgBook`/`Commons`
    objects built the same way, independent of the generator module's own
    internal self-checks (belt and suspenders: two different call paths
    into the same Python implementation, not just one script's opinion of
    itself).
"""
import importlib.util
import json
import os
import unittest

from jev_quilt.orgbook import OrgBook
from jev_quilt.commons import Commons

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
GEN_PATH = os.path.join(REPO_ROOT, "vectors", "gen_g20b_second_reader_vectors.py")
VECTORS_PATH = os.path.join(REPO_ROOT, "vectors", "g20b_second_reader_vectors.json")


def _load_generator_module():
    spec = importlib.util.spec_from_file_location("gen_g20b_second_reader_vectors", GEN_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestG20bVectorsFreshness(unittest.TestCase):

    def test_committed_vectors_match_a_fresh_regeneration(self):
        mod = _load_generator_module()
        org, calls = mod.build_orgbook()
        entries = mod.export_orgbook_entries(org, calls)
        commons = mod.build_commons()

        fresh = {
            "diploma": mod.DIPLOMA,
            "orgbook": {
                "cell_name": org.book.cell_name,
                "entries": entries,
                "expected_chain": org.chain(),
            },
            "decisions_digest": {"expected": org.decisions_digest()},
            "mmr_vectors": mod.build_mmr_vectors(),
            "commons": {
                "quorum": commons.quorum,
                "deposits": [{"key": d.key, "answer": d.answer, "weight": d.weight}
                            for d in commons.deposits()],
                "tombstones": sorted([list(p) for p in commons._tombstones]),
                "expected_root_hex": commons.root().hex(),
            },
        }

        with open(VECTORS_PATH, encoding="utf-8") as f:
            committed = json.load(f)

        self.assertEqual(fresh["diploma"], committed["diploma"])
        self.assertEqual(fresh["orgbook"], committed["orgbook"])
        self.assertEqual(fresh["decisions_digest"], committed["decisions_digest"])
        self.assertEqual(fresh["mmr_vectors"], committed["mmr_vectors"])
        self.assertEqual(fresh["commons"], committed["commons"])
        self.assertEqual(
            {"chain": fresh["orgbook"]["expected_chain"],
             "decisions_digest": fresh["decisions_digest"]["expected"],
             "commons_root": fresh["commons"]["expected_root_hex"]},
            committed["pins"],
        )

    def test_pins_match_a_live_schoolhouse_style_orgbook_and_commons(self):
        """A second Python call path (not the generator module) into the
        same OrgBook/Commons scenario shape, cross-checked against the
        committed fixture's pins — catches the generator quietly agreeing
        with only itself."""
        with open(VECTORS_PATH, encoding="utf-8") as f:
            committed = json.load(f)

        org = OrgBook("org.g20b", diploma=committed["diploma"])
        for row in committed["orgbook"]["entries"]:
            t = row["typed"]
            org.record_dispatch(
                t["dispatch_id"], row["payload"]["tier"], t["key"], t["runner"],
                row["payload"]["verdict"], row["payload"]["outcome"],
                base_verdict=t["base_verdict"], correct=t["correct"],
                answer=t["answer"],
                **({"reason": row["payload"]["reason"]} if "reason" in row["payload"] else {}),
            )
        self.assertEqual(org.chain(), committed["pins"]["chain"])
        self.assertEqual(org.decisions_digest(), committed["pins"]["decisions_digest"])

        c = Commons(quorum=committed["commons"]["quorum"])
        for d in committed["commons"]["deposits"]:
            c.deposit(d["key"], d["answer"], d["weight"])
        for key, answer in committed["commons"]["tombstones"]:
            c._tombstones.add((key, answer))
        self.assertEqual(c.root().hex(), committed["pins"]["commons_root"])


if __name__ == "__main__":
    unittest.main()
