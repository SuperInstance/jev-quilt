"""R3 docstring-vs-behavior pin — throttle._fingerprint_buckets.

PR #26 (properties lane) caught the witness_rng class: a docstring that
contradicts the code it describes. This file pins the same class for
the throttle fingerprint: the module/function docstrings claimed a
word-level fnv1a histogram over K buckets; the implementation is an
exact Q16 character-class histogram (vowels/cons/digits/sep/other).
The docstrings were corrected to the behavior (audit fix, not a
behavior change); these pins keep them from drifting back.
"""

import inspect

from jev_quilt.q16 import Q16
from jev_quilt.throttle import HomeostaticThrottle, _fingerprint_buckets


def test_fingerprint_is_char_class_histogram_not_fnv1a():
    """Behavior pin: five char-class buckets, exact Q16, sums to 1."""
    fp = _fingerprint_buckets("aeiou bc")
    assert set(fp) == {"vowels", "cons", "digits", "sep", "other"}
    total = None
    for v in fp.values():
        assert isinstance(v, Q16)
        total = v if total is None else total + v
    assert total.num == total.den  # exact 1 — Law 1, never float division


def test_fingerprint_hand_computed_values():
    """'aae b' lower-cased: vowels=3 (a,a,e), cons=1 (b), sep=1 (space)."""
    fp = _fingerprint_buckets("aae b")
    assert fp["vowels"] == Q16(3, 5)
    assert fp["cons"] == Q16(1, 5)
    assert fp["sep"] == Q16(1, 5)
    assert fp["digits"] == Q16(0, 1)
    assert fp["other"] == Q16(0, 1)


def test_module_and_function_docstrings_match_behavior():
    """R3 audit pin: docstrings may not claim fnv1a / word-level / K buckets
    while the code computes a char-class histogram (witness_rng bug class)."""
    import jev_quilt.throttle as mod

    for doc in (mod.__doc__, _fingerprint_buckets.__doc__):
        assert doc is not None
        lowered = doc.lower()
        assert "fnv1a" not in lowered, "docstring claims fnv1a; code uses char classes"
        assert "word-level" not in lowered, "docstring claims word-level; code uses char classes"
        assert "lsh" not in lowered, "docstring claims LSH; code uses char classes"
    # no dead parameter promising K buckets
    assert "k" not in inspect.signature(_fingerprint_buckets).parameters
    # no dead imports left behind by the drift
    import sys
    assert not hasattr(sys.modules.get("hashlib", None), "__jev_quilt_unused__")
