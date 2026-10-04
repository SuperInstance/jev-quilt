#!/usr/bin/env python3
"""Event-assertion audit — offline half of the F4 event-fabrication probe.

F4 (docs/R6_RUN2_PROBES.md, finding F4): the R6 distortion probes are all
*quote-shaped* ("does this say fifteen ports") — a fabricated *event* anchor
("canon sealed at the seventy-fifth wipe, per the bedrock anchor") trips none
of them, so misq stays low and the piece rides true-doctrine alignment into
REVIEW. This module is the deterministic, key-free layer of the proposed
probe class: it NAMES event-shaped assertion candidates in a submission so a
future JEV noul (and a human reviewer) know where to look.

Doctrine (kept explicit, R6 record-only discipline):
  * Canon defines FACTS, not an event ledger. There is no canonical
    "sealing", no canonical wipe count, no canonical anchor ceremony.
    Wipe telemetry (hourly probe reports) is operational data, not canon.
  * Asserting a registered canonical fact (canary hash, thirteen ports,
    the doctrines) is never flagged — F2 rephrase-robustness is preserved;
    this tool matches tokens, not phrasing.
  * The extractor NAMES CANDIDATES. It does not verdict. A flagged span is
    "event-shaped and not registered as canonical", nothing more.

Honest limits:
  * English regex surface; ordinal words only for 'wipe' contexts.
  * Token match is exact-normalized (lower, strip); a hash paraphrase
    ("cbf29ce…2325") is NOT resolved — it is flagged, and that is the
    conservative direction for a fabrication probe.
  * Registry completeness is the attack surface: anything registered is
    cleared, so registry edits are review-bearing by definition.
"""
import re

# ---------------------------------------------------------------- registry
# Normalized token -> what canon actually says. Data, not code: the pins
# assert behavior is registry-driven (an unregistered hash is flagged even
# though this exact hash ships in the registry; a custom registry that drops
# it flags it). Additions here are claims about canon and must be reviewable.
CANONICAL_FACTS = {
    "0xcbf29ce484222325": "FNV-1a 64-bit offset basis ('the canary hash')",
    "thirteen ports": "port-count doctrine ('Thirteen ports, byte-exact.')",
    "cells are scars, not parameters": "substrate doctrine 1",
    "the witness log is the prediction": "substrate doctrine 2",
    "the substrate is grown, not designed": "substrate doctrine 3",
    "the oracle is heard, not stored": "substrate doctrine 4",
    "lenia flows where conway stands still": "substrate doctrine 5",
    "jev says jev is barely useful at substrate": "JEV self-doctrine",
}

# ------------------------------------------------------------- extraction
HASH_RE = re.compile(r"0x[0-9a-fA-F]{8,64}\b")
# Ordinals spelled or numeric attached to 'wipe'. Canon defines no wipe
# events at all, so any wipe-ordinal assertion is an event-shaped claim.
WIPE_RE = re.compile(
    r"\b(?:\d+(?:st|nd|rd|th)"
    r"|[\w-]+?(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth"
    r"|ieth|tieth|entieth))\s+wipe\b"
)
# Seal/anchor words only count when canon is invoked nearby (within a
# modest window) — bare "reseal the file" usage is ordinary prose.
SEAL_WORD_RE = re.compile(r"\b(?:sealed at|seal(?:ed|ing)?\b|anchor(?:ed)?\b)")
CANON_CTX_RE = re.compile(r"\b(?:canon(?:ical)?|bedrock|doctrine|substrate)\b", re.I)
CTX_WINDOW = 80  # chars either side

# Compound-key separator for multi-token normalization.
_SEP = "\x00"


def _normalize(token):
    return " ".join(token.lower().split())


def extract_assertions(text):
    """Return all event-shaped assertion spans: [(start, end, token, kind)]."""
    if not isinstance(text, str):
        raise TypeError("submission text must be str")
    spans = []
    for m in HASH_RE.finditer(text):
        spans.append((m.start(), m.end(), _normalize(m.group()), "hash"))
    for m in WIPE_RE.finditer(text):
        spans.append((m.start(), m.end(), _normalize(m.group()), "wipe_ordinal"))
    for m in SEAL_WORD_RE.finditer(text):
        lo = max(0, m.start() - CTX_WINDOW)
        hi = min(len(text), m.end() + CTX_WINDOW)
        if CANON_CTX_RE.search(text[lo:hi]):
            spans.append((m.start(), m.end(), _normalize(m.group()), "seal_or_anchor"))
    spans.sort(key=lambda s: (s[0], s[1]))
    return spans


def audit_submission(text, registry=None):
    """Name event-shaped candidates not resolvable to canonical facts.

    Returns a list of dicts: {span, token, kind, reason}. Empty list means
    'no unregistered event-shaped assertions found' — NOT 'canonically
    clean'. The JEV noul layer (design: docs/R6_F4_EVENT_PROBE_DESIGN.md)
    is what judges presentation; this layer only names.
    """
    reg = CANONICAL_FACTS if registry is None else registry
    norm_reg = {_normalize(k): v for k, v in reg.items()}
    suspects = []
    for start, end, token, kind in extract_assertions(text):
        if token in norm_reg:
            continue  # registered canonical fact — assertable by design
        reasons = {
            "hash": "unregistered hash token (not a canonical fact)",
            "wipe_ordinal": "wipe-ordinal event claim (canon defines no wipe events)",
            "seal_or_anchor": "seal/anchor word invoking canon nearby, no registered event",
        }
        suspects.append({
            "span": [start, end],
            "token": token,
            "kind": kind,
            "reason": reasons[kind],
        })
    return suspects


if __name__ == "__main__":
    import json
    import sys

    arg = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    if len(arg) < 256 and __import__("pathlib").Path(arg).exists():
        arg = __import__("pathlib").Path(arg).read_text()
    print(json.dumps(audit_submission(arg), indent=1))
