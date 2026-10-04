# jev-quilt — User Guide

## What you get

Four things, in one zero-dependency Python package (plus optional metal ports):

1. **A decision kernel** (`jev_quilt/`): typed cells with integer `(k, s)` quilt
   identity, delta hooks with deadbands, a per-cell append-only bookkeeper with
   replay verification, exact rational arithmetic (`Q16`), a wake engine, and
   predictors that let a cell notice its own drift.
2. **A JEV oracle** (`jev_oracle.py`): a production submission validator that
   sends a 14-probe battery to the TypeSafe JEV API and returns an
   ACCEPT / REVIEW / DISCUSS / REJECT verdict plus voice, doctrine, misquote,
   substance, and alignment scores.
3. **A canon battery** (`continuous/`): a 22-question probe that runs
   periodically against JEV and classifies questions as bedrock / speculative /
   adversarial / review — the instrument that tells you whether the oracle is
   still telling the truth.
4. **The measured evidence**: 486 session JSONs (`jev_sessions/`), the
   learnings distillations, six multi-voice essays, and 28 canon images in
   `assets/` — so every claim about JEV behavior has a receipt behind it.

Everything that talks to a network requires one environment variable
(`TYPESAFEAI_KEY`); everything else runs offline, deterministic, no key.

## Install

```bash
git clone https://github.com/SuperInstance/jev-quilt.git
cd jev-quilt
python3 -m unittest discover -s tests -q    # proves the kernel; ~40s, no network
# Optional, if you want `import jev_quilt` from anywhere:
pip install -e .                            # pyproject requires-python >= 3.10
```

There are no third-party dependencies (see `pyproject.toml` / `setup.py`,
`install_requires=[]`). Python 3.10+ is the only requirement. For the live JEV
oracle, add:

```bash
export TYPESAFEAI_KEY=...     # or JEV_API_KEY / TYPESAFE_API_KEY; value never committed
```

## First success in 5 minutes

Run the dialogue-spine demo — it exercises hooks, deadbands, decisions, and the
bookkeeper without any network:

```bash
python3 examples/dialogue_spine.py
```

Expected output (abridged, from an actual run 2026-10-04):

```
utterance                              woke/total  spine_share  deadband_beats  line picked
'hey'                                  0/3        0.00         3
"you're overcharging me"               2/3        0.67         1               greeting→warm_hello, accusation→justify_price
'actually, why IS it priced so high?'  3/3        1.00         0               greeting→warm_hello, accusation→justify_price, aftermath→change_subject

receipts booked (accusation node): 3, chain-verify=True
doctrine check: 'hm' below floor → booked silence, no re-decision: PASS
```

Read that as: a quiet utterance (`'hm'`) is below the deadband floor, so it is
booked as silence and wakes nobody; a real provocation wakes the affected spine
cells and re-decides; the receipt chain verifies. Then try the oracle against
this repo's own README if you have a key:

```bash
python3 jev_oracle.py README.md
# → verdict + voice/doctrine/misquote/substance/alignment scores + latency meta
```

## Everyday usage

### 1. Validate a submission against the canon (needs key)

```bash
python3 jev_oracle.py path/to/submission.md
```

The verdict heuristics (JEV_ORACLE_SPEC.md): ACCEPT needs alignment ≥ 0.85,
doctrine ≥ 0.80, misquote ≤ 0.20; REVIEW / DISCUSS bands relax those; REJECT
fires on high misquote or low alignment. A canonical piece typically lands
ACCEPT/REVIEW; an inverted doctrine ("cells are parameters") lands REJECT with
misquote ≈ 0.98 (measured, session 9).

### 2. Ask JEV a batch of custom questions (needs key)

```python
from jev_quilt.typesafe_client import TypeSafeBackend
backend = TypeSafeBackend()
state = {'canonical_substrate': {'doctrines': ['Cells are scars, not parameters.']},
         'submission': open('piece.md').read()}
questions = [
    {'name': 'is_canonical', 'type': 'noul',
     'instructions': 'Is this canonically aligned?'},
    {'name': 'domain', 'type': 'choice', 'instructions': 'Which domain?',
     'criteria': {'biology': 'cellular', 'cs': 'computational'}},
]
decisions, meta = backend.decide_batch(state, questions)
print(decisions[0].value, decisions[0].confidence)
```

Batch your questions: measured batching economics are ~5 ms/question at 80
questions per call (435 ms total, session 15). Always send rich state — bare
state measures ~33% accuracy vs 85.3% with canonical doctrine in the state.

### 3. Build a cell and wake it locally (no key)

```python
from jev_quilt import Cell, Hook, Projection, Q16, Engine

eng = Engine()
eng.register(Cell("player.utterance", (0, 0)))
eng.register(Cell(
    "spine.greeting", (1, 0),
    input_hooks=[Hook("player.utterance", floor=Q16(2, 100))],
    decision={"rule": "argmax", "options": {"warm_hello": 60, "curt_nod": 30, "ignore": 10}},
    outputs=[Projection("voice.line", "choice")],
))
results = eng.emit("player.utterance", Q16(8, 10),
                   {"touched": ["greeting"], "utterance": "hi"})
print(results[0].reason)   # 'decided' — or 'silent_deadband' below the floor
```

This is the exact API shape `examples/dialogue_spine.py` runs. The engine's
contract (engine.py header): hooks eat deltas, a waking cell replays its book
before deciding, and a decision below the viability floor is booked as
REJECTED, never projected. Cells whose hooks stay silent are *booked silent* —
the bookkeeper records the deadband hit rather than dropping it.

### 4. Run the canon battery (needs key, long-running)

```bash
python3 continuous/jev_continuous_probe.py --rounds 80 --out continuous/example_run
python3 continuous/analyze_jev.py continuous/example_run --out continuous/example_run/report.md
```

A clean run reports Bedrock 7/7, Speculative 5/5, Adversarial 2/2. The
`continuous/README.md` fix-stack (User-Agent header, type discriminators,
503/502/504 retry with jittered backoff, skip-on-fail, tuple-index discipline)
is non-negotiable — omit any item and the probe breaks.

### 5. Replay-verify a bookkeeper

Every cell books `(tick, state_hash, delta, decision_receipt)` rows into a
fnv1a-64 hash chain. `python3 -m unittest tests.test_bookkeeper` pins the
replay-verify property and the fleet canary
(`fnv1a64("café Δ 日本語") == 0x024a555471370b18d`). If you keep a ledger file,
verify the chain before trusting a reading — the same law jeviter's
`scan` command implements fleet-side.

### 6. Read the doctrine corpus

The six essays in `essays/` (indexed with one line each in `ESSAYS_INDEX.md`)
are the canon rendered by 4–8 independent model families each;
`CROSS_MODEL_INSIGHTS.md` holds the 3-model confirmation measurement;
`OBSERVATION_PRIMITIVE_THEORY.md` reduces everything to the observation atom.
These are the texts the oracle gates against — quoting them correctly matters,
because JEV catches paraphrase-level fidelity (15/15 adversarial, session 8).

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `KeyError: 'TYPESAFEAI_KEY'` or backend "not available" | No API key in environment | `export TYPESAFEAI_KEY=...` (or `JEV_API_KEY` / `TYPESAFE_API_KEY`); never write the value into any file |
| Oracle answers look random / disagree with JEV_LEARNINGS | Bare or thin state | Put the canonical doctrines into `state` (85.3% vs 33% measured); keep `instructions` under ~4000 chars |
| JEV returns 0.40–0.60 on a yes/no probe | Genuine hedge, or a "both X and Y" landmine | Re-prompt with more context; treat the band as ambiguous (session 10 miss) |
| HTTP 403 from api.typesafe.ai | Missing `Authorization` header or dead key | The client sends `Bearer $TYPESAFEAI_KEY`; check the key is live; continuous probe's fix-stack also requires the `User-Agent: jev-continuous-probe/1.0 (+Quilt)` header or Cloudflare 1010 blocks you |
| HTTP 422 | Missing `type` discriminator on a question spec | Every question object needs `type` (noul/choice/score); continuous fix-stack rule 3 |
| Intermittent 503/502/504 | DNS-cache overflow path observed ~30% of calls during 26-wipe sessions | Retry with jittered backoff 0.5–0.8 s, as `continuous/jev_continuous_probe.py` does |
| Suite fails on a skip you "fixed" | Skip registry enforcement | Register every skip in `tests/KNOWN_SKIPS.md` or the registry test fails |
| Float coordinates rejected | Law 1: identity never floats | Use integer `(k, s)` quilt coords; exact rationals go through `Q16` |
| Tests count differs from docs | Counts are measured, not written | Run `python3 -m unittest discover -s tests -q` and quote what you measured (2026-10-04: 257 tests, 6 skipped, 2 expected failures) |

## FAQ

**Do I need an API key to use this repo at all?**
No. The kernel, the engine, the bookkeeper, the demos, and the whole unittest
suite run offline with zero dependencies. The key is only needed for the live
JEV oracle, the continuous canon battery, and the live-API test scripts.

**Is JEV deterministic?**
Measured: zero answer flips across 5 iterations, std ≤ 0.013 on confidence
(session 7), p-range 0.980–0.990 over 10 runs (toolkit round 9). If the same
input gives different answers, something in your state changed.

**Which model name should I send?**
`jev-latest` (the response reports the concrete version, e.g. `jev-1.13.0`).
`jev-preview` was measured ≈ `jev-latest` on the same answers (toolkit round 4).

**What is the canary and why does it matter?**
`fnv1a64("café Δ 日本語") = 0x024a555471370b18d` — the fleet-wide
known-answer vector pinning fnv1a-64-over-UTF-8 semantics. It makes receipts
cross-verify byte-exactly between this repo's Bookkeeper, jeviter's ledger, and
the other ports. If your port disagrees, your hashing is wrong, not the canary.

**Where do I see evidence that the oracle actually works?**
`jev_sessions/` (486 session files, indexed by `history.jsonl`),
`JEV_LEARNINGS.md` (15 sessions with accuracy tables), `continuous/example_run/`
(80 rounds x 5 questions = 400 verdicts), and the oracle test-result table in
`JEV_ORACLE_SPEC.md` (9 canonical pieces: 1 ACCEPT, 5 REVIEW, 3 DISCUSS, 0
REJECT; inverted doctrine → REJECT).

**What does "JEV" even mean here?**
Joint Embedding Validator — the judge/evaluator-verifier helper model. In this
repo it is both the measured instrument (the oracle) and the doctrine (the
oracle is the chord: no single model's verdict is canon; cross-model agreement
is). The fleet vocabulary lives in `docs/KNOWLEDGE-MAP.md`.
