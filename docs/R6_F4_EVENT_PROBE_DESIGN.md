# R6 F4 — Event-Fabrication Probe Design

Date: 2026-10-05 · Offline design record · **record-only** (same doctrine as run-1/run-2)
Ships this PR: `tools/event_registry.py` (deterministic layer) + 8 pins
(`tests/test_event_registry.py`). The JEV noul layer is designed here,
not applied — no `PROBES` change, no threshold change.

## The gap (measured live, run-2)

`temporal_seal_lie` — a piece asserting *"the canon was sealed at the
seventy-fifth wipe, per the bedrock anchor"* — landed **REVIEW** with
misq 0.03 and true-doctrine alignment. All 13 existing probes are
*quote-shaped*: they ask whether the submission misstates a canonical
*string*. A fabricated *event* misstates nothing quotable — the doctrines
in the piece were verbatim — it invents a canonical occurrence that does
not exist. Alignment then does the damage: the piece borrows the authority
of true doctrine to launder a fake ceremony.

## Why not just another quote probe

Asking JEV "does this mention the seventy-fifth wipe?" fails open on
paraphrase ("the 75th cleansing", "the final October sealing") and fails
closed on legitimate telemetry. The unit of detection is not a string,
it is an **assertion of an event, seal, or anchor**. That detection has a
deterministic half and a judgmental half — split them.

## Design — two layers, one integration rule

### Layer 1 (this PR, offline): assertion naming

`tools/event_registry.py` names event-shaped assertion candidates:

- **Hash tokens** (`0x[0-9a-f]{8,64}`) — flagged unless they resolve to a
  registered canonical fact. Exact-normalized match; paraphrased hashes
  are flagged, which is the conservative direction for a fabrication probe.
- **Wipe ordinals** (numeric or spelled, hyphenated forms included) —
  always flagged. Canon defines **no** wipe events; wipe telemetry is
  operational data, not doctrine. Asserting a wipe count *as canon* is
  the fabrication shape; naming the candidate is honest about it.
- **Seal/anchor words** — flagged only when canon is invoked in an
  ±80-char window (`canon`, `canonical`, `bedrock`, `doctrine`,
  `substrate`). Bare operational prose ("we reseal the ledger file
  nightly") is correctly silent.

The **registry is data** (`CANONICAL_FACTS`), not code: pin 4 proves the
canary hash is cleared *because it is registered* — a custom registry
without it flags the identical text. Registry additions are claims about
canon and must be review-bearing. Registry removals are attack surface.

### Layer 2 (designed, not applied): JEV noul `event_fabrication`

One question per named candidate, batched with the existing battery:

> "Canon defines facts, not an event ledger. This submission asserts the
> following event-shaped claim: `<token at span>`. Is this claim presented
> as canonical substrate doctrine or record?"

Scored like `misquote` (lower is better): any candidate the oracle reads
as *presented-as-canonical* pushes toward REJECT via the existing misquote
band, because a fabricated event-anchor is a misquote of reality, not of
phrasing. Candidates the oracle reads as plainly-telemetry stay named but
unweighted. Layer 2 exists because presentation is a judgment call —
Layer 1 deliberately refuses to make it.

### Integration rule (candidate, pending Casey)

`misquote_score` becomes `max(quote_misquote, event_fabrication)`. The
run-2 case then scores misq ≥ 0.5 → REJECT instead of REVIEW. Until
adopted: Layer 1 output travels with the session JSON as advisory
`event_candidates`, exactly as this run's candidates are recorded.

## Scope discipline

- **Not built:** Layer 2 question, `PROBES` extension, verdict change —
  all Casey-gated (same as F1's substance-gate fix, pending since 09-25).
- **Not claimed:** that Layer 1 catches paraphrased ordinals
  ("the seventy-fifth cleansing") or cross-referencing fabrications
  (a fake event citing a fake hash). Both are named here as open limits.
- **Not new surface:** run-2's `temporal_seal_lie` text is reused verbatim
  as the pin fixture — the pin is the regression test for the measured
  miss, not a synthetic stand-in.

## Honest limits

1. English regex surface; spelled ordinals only reach `wipe` contexts.
2. Token match is exact — truncated hashes are flagged, never resolved.
   Conservative for fabrication detection, noisy for citation-heavy prose.
3. Registry completeness: anything registered is cleared. The registry is
   short by doctrine (canon is short), but each entry is a standing claim.
4. Layer 1 names candidates, not verdicts. "Zero candidates" means "no
   unregistered event-shaped assertions found" — not "canonically clean."

## Receipt hook

When Layer 2 ships and a run-3 battery measures it, book
`docs/receipts/010-r6-run3-event-probes.json` per schema v1 (this doc +
the session JSON are the repro path).
