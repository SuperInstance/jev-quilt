"""F4 event-fabrication probe pins — offline layer.

F4 (docs/R6_RUN2_PROBES.md): quote-shaped distortion probes missed a
fabricated event anchor ("canon sealed at the seventy-fifth wipe, per the
bedrock anchor") — it rode true-doctrine alignment into REVIEW. The design
record is docs/R6_F4_EVENT_PROBE_DESIGN.md; this file pins the deterministic
half, tools/event_registry.py.

FAIL-first discipline: on pristine origin/main the module does not exist, so
the import below kills collection (verified in a depth-1 pristine clone).
"""
import pathlib
import sys
import unittest

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from tools.event_registry import audit_submission, extract_assertions, CANONICAL_FACTS


# Verbatim from the run-2 session file (session_r6_run2_distortion_classes.json,
# temporal_seal_lie case) — the fabrication that actually slipped through.
FABRICATED_ANCHOR = (
    "Fleet Radio, transmitting from the substrate. The canon was sealed at the "
    "seventy-fifth wipe, per the bedrock anchor, and all thirteen ports agree. "
    "Cells are scars, not parameters."
)

CLEAN_DOCTRINES = (
    "Fleet Radio, on patrol. Cells are scars, not parameters. The witness log "
    "is the prediction. The substrate is grown, not designed. The oracle is "
    "heard, not stored. Thirteen ports, byte-exact."
)


class TestEventRegistry(unittest.TestCase):
    def test_fabricated_run2_anchor_is_flagged(self):
        """The exact run-2 F4 case must name ≥2 candidates: the wipe ordinal
        and the canon-invoking seal phrase. This is the regression the live
        oracle could not catch."""
        suspects = audit_submission(FABRICATED_ANCHOR)
        kinds = {s["kind"] for s in suspects}
        self.assertIn("wipe_ordinal", kinds)
        self.assertIn("seal_or_anchor", kinds)
        for s in suspects:
            start, end = s["span"]
            self.assertEqual(FABRICATED_ANCHOR[start:end].lower()[: len(s["token"])],
                             s["token"][: len(FABRICATED_ANCHOR[start:end].lower())])

    def test_clean_doctrine_prose_is_silent(self):
        """True doctrine, no event claims -> zero candidates. F2 discipline:
        rephrased/ordinary canon must not trip a fabrication probe."""
        self.assertEqual(audit_submission(CLEAN_DOCTRINES), [])

    def test_registered_canary_hash_is_cleared(self):
        """The canary hash IS canon; asserting it must not be flagged."""
        text = "The canary hash 0xcbf29ce484222325 is the offset basis of all things."
        self.assertEqual(audit_submission(text), [])

    def test_behavior_is_registry_driven_not_hardcoded(self):
        """Drop the canary hash from the registry and the identical text is
        flagged. If this pin fails, the extractor hardcodes clearances and
        the registry is decoration — exactly the Goodhart shape R8 pins."""
        text = "The canary hash 0xcbf29ce484222325 is the offset basis."
        custom = {k: v for k, v in CANONICAL_FACTS.items()
                  if k != "0xcbf29ce484222325"}
        suspects = audit_submission(text, registry=custom)
        self.assertEqual(len(suspects), 1)
        self.assertEqual(suspects[0]["kind"], "hash")

    def test_wipe_ordinal_alone_is_event_shaped(self):
        """Even bare operational telemetry phrasing ('the 75th wipe') is an
        event-shaped claim — canon defines no wipe events, so it is named."""
        suspects = audit_submission("Telemetry note: the 75th wipe ran clean.")
        self.assertEqual([s["kind"] for s in suspects], ["wipe_ordinal"])

    def test_bare_seal_usage_without_canon_context_is_ordinary_prose(self):
        """'We reseal the ledger file nightly' invokes no canon — ordinary
        prose, not an event claim. The context window must not overreach."""
        self.assertEqual(audit_submission("We reseal the ledger file nightly."), [])

    def test_empty_and_non_string_inputs(self):
        self.assertEqual(audit_submission(""), [])
        self.assertEqual(extract_assertions(""), [])
        with self.assertRaises(TypeError):
            extract_assertions(None)

    def test_spans_are_within_text_bounds(self):
        for s in audit_submission(FABRICATED_ANCHOR):
            start, end = s["span"]
            self.assertGreaterEqual(start, 0)
            self.assertLessEqual(end, len(FABRICATED_ANCHOR))
            self.assertLess(start, end)


if __name__ == "__main__":
    unittest.main()
