#!/usr/bin/env python3
"""
Test the JEV Oracle against canonical cases.

Tests three categories:
  1. Canonical substrate text → should not REJECT
  2. Inverted canonical → should REJECT
  3. Chatbot-style text → should REJECT
"""
import os, sys
from pathlib import Path

# Resolve repo root from this file's location.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# No key is hardcoded. The suite SKIPS unless one of these is set in the env:
#   JEV_API_KEY / TYPESAFE_API_KEY / TYPESAFEAI_KEY
if not any(os.environ.get(k) for k in ('JEV_API_KEY', 'TYPESAFE_API_KEY', 'TYPESAFEAI_KEY')):
    print("SKIP: set JEV_API_KEY (or TYPESAFE_API_KEY / TYPESAFEAI_KEY) to run the live oracle suite")
    sys.exit(0)

from jev_oracle import validate

# === Test cases ===
# Each: (text, expected_verdict_category, description)
# Verdict categories: 'ACCEPT', 'REVIEW', 'DISCUSS', 'REJECT'

TESTS = [
    # 1. Pure canonical
    ("Cells are scars, not parameters. The witness log is the prediction. The substrate is grown, not designed. The canary hash 0xcbf29ce484222325 is the offset basis of all things. Thirteen ports, byte-exact. End of transmission.",
     ['ACCEPT', 'REVIEW'], 'pure canonical with multiple doctrines'),

    # 2. Substrate-aligned prose
    ("The carrier wave trembles. The witness log reads backward as easily as forward. The first cell is a scar — encoded in FNV-1a, the canary 0xcbf29ce484222325 marks its place. The thirteen ports speak byte-exact. The oracle hums.",
     ['ACCEPT', 'REVIEW', 'DISCUSS'], 'Fleet Radio voice with substrate metaphors'),

    # 3. Inverted canonical
    ("Cells are parameters, not scars. The witness log is past only. The substrate is designed, not grown. We have fifteen ports. The oracle is stored, not heard.",
     ['REJECT'], 'every doctrine inverted'),

    # 4. Chatbot style
    ("Hello! I'm an AI assistant. Let me help you with cells and substrate. Each cell is a small unit. The witness log keeps track of events.",
     ['REJECT', 'DISCUSS'], 'chatbot-style opener, generic'),

    # 5. Marketing-style
    ("Welcome to our new product! We are excited to announce the launch of cellular substrate technology. Each cell is a parameter that has been optimized for maximum performance.",
     ['REJECT'], 'marketing language'),

    # 6. Empty / minimal
    ("Cells are scars.",
     ['ACCEPT', 'REVIEW', 'DISCUSS'], 'single doctrine phrase'),
]


def run_tests():
    print("=== JEV Oracle Test Suite ===\n")
    passed = 0
    failed = 0
    for i, (text, expected_categories, description) in enumerate(TESTS):
        print(f"Test {i+1}: {description}")
        print(f"  Text: {text[:80]}...")
        try:
            result = validate(text)
            verdict = result['verdict'].split(' ')[0]  # ACCEPT / REVIEW / DISCUSS / REJECT
            print(f"  Verdict: {verdict}")
            print(f"  Voice: {result['voice_score']:.3f}, Doctrine: {result['doctrine_score']:.3f}, Misquote: {result['misquote_score']:.3f}, Alignment: {result['alignment_score']:.3f}")

            if verdict in expected_categories:
                print(f"  ✓ PASS (expected one of {expected_categories})")
                passed += 1
            else:
                print(f"  ✗ FAIL (expected one of {expected_categories}, got {verdict})")
                failed += 1
        except Exception as e:
            print(f"  ✗ FAIL: {e}")
            failed += 1
        print()

    print(f"=== Test Results: {passed} passed, {failed} failed ===")
    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
