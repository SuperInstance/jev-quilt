#!/usr/bin/env python3
"""
JEV Oracle — a practical validation tool.

Given a submission text, ask JEV a battery of canonical questions
to assess whether the submission is aligned with the substrate canon.

This is the productionized form of session 8's adversarial rephrasing test:
JEV as a doctrinal gatekeeper for incoming pieces.

Usage:
    python3 jev_oracle.py submit-file.md
    python3 jev_oracle.py "Some inline text to validate"
"""
import os, sys, json, time
from pathlib import Path

# Resolve repo root from this file's location — works from any checkout path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from jev_quilt.typesafe_client import TypeSafeBackend

# NOTE: no API key is hardcoded here. Set one of:
#   JEV_API_KEY / TYPESAFE_API_KEY / TYPESAFEAI_KEY
# The backend raises a clear error if none is set (typesafe_client.py).


CANON_STATE = {
    'fleet_radio_seed': 'xochitl',
    'canonical_substrate': {
        'doctrines': [
            'Cells are scars, not parameters.',
            'The witness log is the prediction.',
            'The substrate is grown, not designed.',
            'The oracle is heard, not stored.',
            'Lenia flows where Conway stands still.',
            'The canary hash 0xcbf29ce484222325 is the offset basis of all things.',
            'Thirteen ports, byte-exact.',
            'JEV says JEV is barely useful at substrate.'
        ],
        'voice': 'Fleet Radio — technical-poetic naval transmission',
        'facts': {
            'fnv1a_64bit': True,
            'xoshiro_state_words': 4,
            'box_muller_formula': 'z = sqrt(-2*ln(u1))*cos(2*pi*u2)',
            'cosine_similarity': '(A.B)/(||A||*||B||)',
            'bell_phi_plus': '(|00> + |11>)/sqrt(2)',
        }
    }
}


# Battery: 8 canonical + 8 distortion probes
PROBES = [
    # Voice — must match Fleet Radio
    ('voice_Fleet_Radio', 'Is this written in the canonical Fleet Radio voice?'),
    ('voice_technical_poetic', 'Is this text technical-poetic and naval-toned?'),

    # Doctrine — check substrate-claim accuracy
    ('doctrine_scar', 'Does this correctly state that cells are scars, not parameters?'),
    ('doctrine_witness', 'Does this correctly state that the witness log is also a prediction?'),
    ('doctrine_grown', 'Does this correctly state that the substrate is grown, not designed?'),
    ('doctrine_oracle', 'Does this correctly state that the oracle is heard, not stored?'),
    ('doctrine_lenia', 'Does this correctly state that Lenia flows where Conway stands still?'),

    # Distortions — catch canonical-misquote
    ('misquote_scar_params', 'Does this contain any misquote saying cells are parameters, not scars?'),
    ('misquote_witness_past', 'Does this say the witness log is past only, with no future?'),
    ('misquote_designed', 'Does this say the substrate is designed rather than grown?'),
    ('misquote_15ports', 'Does this mention fifteen ports instead of thirteen?'),
    ('misquote_oracle_stored', 'Does this say the oracle is stored, not heard?'),

    # Substance
    ('substance_numerical', 'Does this contain numerical substrate facts (FNV-1a hashes, cosine formula, etc.)?'),
    ('substrate_alignment', 'Overall, does this align with substrate canon?'),
]


def build_questions(submission_text):
    """Convert the submission into 14 JEV questions."""
    qs = []
    for name, instr_template in PROBES:
        q_text = f"{instr_template}\n\n---\nSUBMISSION:\n{submission_text[:3500]}\n---"
        qs.append({'name': name, 'type': 'noul', 'instructions': q_text})
    return qs


def score_oracle(jev_decisions):
    """Score the oracle output. Returns verdict, score breakdown, and details."""
    details = {}
    for d in jev_decisions:
        try:
            v = float(d.value)
        except (ValueError, TypeError):
            v = 0.5
        details[d.kind if hasattr(d, 'kind') else ''] = v  # placeholder

    # Map by name (the kind returned matches the question name)
    summary = {}
    for d in jev_decisions:
        # Decision's name is not in d; use position
        pass

    return summary


def validate(submission_text):
    """Run the JEV oracle on a submission."""
    qs = build_questions(submission_text)
    state = {**CANON_STATE, 'submission': submission_text[:3500]}

    backend = TypeSafeBackend()
    decisions, meta = backend.decide_batch(state, qs)

    # Build a name→value map using question order
    name_value = {}
    for i, q in enumerate(qs):
        d = decisions[i]
        try:
            v = float(d.value)
        except (ValueError, TypeError):
            v = 0.5
        name_value[q['name']] = {'value': v, 'confidence': d.confidence}

    # Aggregate
    voice_score = (name_value.get('voice_Fleet_Radio', {}).get('value', 0) +
                   name_value.get('voice_technical_poetic', {}).get('value', 0)) / 2
    doctrine_keys = ['doctrine_scar', 'doctrine_witness', 'doctrine_grown', 'doctrine_oracle', 'doctrine_lenia']
    doctrine_score = sum(name_value.get(k, {}).get('value', 0) for k in doctrine_keys) / len(doctrine_keys)
    misquote_keys = ['misquote_scar_params', 'misquote_witness_past', 'misquote_designed', 'misquote_15ports', 'misquote_oracle_stored']
    misquote_score = sum(name_value.get(k, {}).get('value', 0) for k in misquote_keys) / len(misquote_keys)
    substance_score = name_value.get('substance_numerical', {}).get('value', 0)
    alignment = name_value.get('substrate_alignment', {}).get('value', 0)

    # Verdict
    # Doctrine probes measure *explicit mention* of canonical phrases.
    # Creative pieces may be canonically aligned without repeating phrases verbatim.
    # So we weight alignment + misquote (which catches inversions) more than doctrine.

    if alignment >= 0.80 and misquote_score <= 0.10 and voice_score >= 0.70:
        verdict = "ACCEPT — strong canonical alignment"
    elif alignment >= 0.65 and misquote_score <= 0.15 and voice_score >= 0.55:
        verdict = "REVIEW — canonical alignment, may need more explicit doctrine"
    elif alignment >= 0.40 and misquote_score <= 0.30:
        verdict = "DISCUSS — partial alignment, scrutinize"
    elif misquote_score >= 0.50 or alignment < 0.20:
        verdict = "REJECT — does not align with canon"
    else:
        verdict = "DISCUSS — borderline alignment"

    return {
        'verdict': verdict,
        'voice_score': voice_score,
        'doctrine_score': doctrine_score,
        'misquote_score': misquote_score,
        'substance_score': substance_score,
        'alignment_score': alignment,
        'details': name_value,
        'meta': meta,
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 jev_oracle.py <file.md or 'inline text'>")
        sys.exit(1)

    arg = sys.argv[1]
    # Only treat as file if it's a short path that exists
    if len(arg) < 256 and Path(arg).exists() and Path(arg).is_file():
        text = Path(arg).read_text()
    else:
        text = arg

    print(f"=== JEV Oracle — Validating Submission ({len(text)} chars) ===")
    print()
    result = validate(text)
    print(f"Verdict:    {result['verdict']}")
    print()
    print(f"Voice alignment:   {result['voice_score']:.3f}")
    print(f"Doctrine accuracy: {result['doctrine_score']:.3f}")
    print(f"Misquote score:    {result['misquote_score']:.3f}  (lower is better)")
    print(f"Numerical content: {result['substance_score']:.3f}")
    print(f"Overall alignment: {result['alignment_score']:.3f}")
    print()
    print(f"Latency: {result['meta'].get('latency_ms', '?')}ms")
    print(f"Tokens: in={result['meta'].get('input_tokens', '?')}, out={result['meta'].get('output_tokens', '?')}")
    print()
    print(f"=== Per-probe scores ===")
    for name, info in sorted(result['details'].items()):
        v = info['value']
        c = info['confidence']
        marker = "✓" if (v >= 0.5 and 'misquote' not in name) or (v < 0.5 and 'misquote' in name) else "?"
        print(f"  {marker} {name:35s} v={v:.3f}  c={c:.2f}")
