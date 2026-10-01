# Positioning — adjacent frontier work, what we claim, what we don't

*Researched 2026-09-22. Three external results landed this week that sit
next to the receipts/WAL work. Each is recorded here with the exact claim
it narrows, the exact claim it does NOT touch, and what (if anything) it
changes about our next build. Adjacent, not colliding — until proven
otherwise, and then this file says so in plain words.*

---

## 1. FLUCTLIGHT (arXiv 2608.12365) — brain-native agent database

**What it is.** An agent memory/database substrate with WAL
checkpointing, replay-on-boot, and Jepsen-style chaos testing: agents
sharing a memory region get crash recovery and cross-agent provenance
for free from the WAL design.

**The measured fact we care about.** Shared-brain provenance
contamination: agents writing into a *shared* memory show ~18%
cross-contamination of provenance (whose experience became whose
memory), vs 100% correct attribution in isolated replay. **No mitigation
is shipped** — the number is reported, the fix is future work.

**What this narrows for us.** Prior art on WAL-resume lanes (our
tidepool/jeviter resume work is now externally validated as a real
category — we must *cite* FLUCTLIGHT, we cannot claim it). Their
position is WAL *replay*; ours is hash-chained *receipts* — the chain is
the audit surface, replay is only one consumer. Different law, same sea.

**What it does NOT touch.** The FUEL/epoch receipts claim (see §3), and
the cellular deadband/throttle claims. WAL replay proves a boot equals
a past state; it says nothing about whether each *decision* was
surprising, budgeted, or honest.

**The ammunition.** If anyone asks "why do agents need receipts when a
WAL gives you provenance?": FLUCTLIGHT's own number — 18% contamination
in the shared case — is the answer. A WAL records *what was written*; it
does not record *what the writer was entitled to believe at the time*,
and it does not make contamination structurally detectable. A
namespace-scoped, hash-chained receipt (cell identity bound to every
booked delta) turns that 18% from an undetected drift into a
chain-verification failure. Namespaced receipts are the mitigation
FLUCTLIGHT reports not having. That is a positioning claim, not a
shipped feature: our receipts today are per-cell chains within one
bookkeeper; cross-bookkeeper namespaces are exactly the RECEIPTS-V2
cross-node scope.

## 2. LEVI (arXiv 2605.09764) — search architecture beats model scale

**What it is.** An evolutionary/prompt-optimization framework that
selects a *representative proxy benchmark* under an evaluation-cost
budget: CSS+mean proxy selection hits rank-correlation ρ≈0.61–0.70 vs
0.31 for k-medoids and 0.04 for random-subset regression, at a fixed
~2,500-LLM-call budget. Best-of-seven task scores at 3.3–6.7× lower
dollar cost than frontier-model baselines.

**What this narrows for us.** Cost of evaluation is now a *first-class
fitness axis* in the QD/MAP-Elites literature. The the-tap Red Queen
critic rotation currently rotates *models*; LEVI's result says the
*evaluation subset* is a lever with measured payoff — a champion
exhausting the evaluation budget on easy cells is fitness-gaming the
same as one flattering the metric. File under: Red Queen niche-gate
tuning, cost axis, post-GAME-read.

**What it does NOT touch.** Nothing about receipts, fuel, or WAL. This
is method debt we should *owe*: any future lane that claims "diverse
evaluation" needs a LEVI-style rank-faithfulness argument for its proxy
subset, or an honest note that it doesn't have one.

## 3. Ephemora Cell (MichaelS1011, GitHub/PyPI) — sign-ready WASM execution records

**What it is.** A capability-based WASM runtime for untrusted
agent-generated code: fuel metering (CPU instruction budget, exact
loop-stop), memory/time/I/O caps, and — closest to our work —
**execution records canonicalized per RFC 8785 JCS and sign-ready
(ES256 sign()/verify())**: status, fuel_consumed, elapsed_ms, and the
attested policy baseline, one record per run. 8/8 attack classes blocked
(measured, scripts in repo). MCP stdio server; sub-ms warm path.

**What this narrows for us.** It is the nearest shipped neighbor to the
FUEL-receipts direction (FLUX WASM lane, ability-transfer fuel
governance): a *sign-ready, canonical* execution record with fuel is a
real, published, third-party thing now. Our FUEL receipts claim must
therefore be stated precisely or not at all:

- Ephemora records **one run** of **one untrusted program** against an
  **enforced resource budget** — the receipt's job is *"this code was
  contained and cost this much."*
- JEV receipts book **a decision cell's surprise** against its **own
  prediction**, chained across the cell's whole life — the receipt's
  job is *"this belief was graded at the time it was held."*
- The honest overlap: both are hash/signature-bound, both meter fuel,
  both refuse to round identity. The honest difference: execution
  containment is *external enforcement* (the sandbox is the law), while
  a JEV receipt is *internal bookkeeping* (the cell grades itself and
  the chain makes lying expensive). One attests the wall; the other
  attests the conversation inside the wall.

**What it does NOT touch.** It corroborates rather than competes:
"WASM receipts spec: FUEL metering (deterministic replay) not epochs"
(edge-watch, 2026-09-15) now has a second independent witness —
Ephemora's fuel counts CPU instructions with a documented per-platform
caveat (fuel is per-platform, not cross-platform), which is exactly why
FUEL-not-epochs matters: epochs are wall-clock and wall-clock lies
across platforms; fuel at least has an honest per-platform disclaimer.
Also note its epoch-based wall-clock timeout is the *safety net on top
of* fuel, not the metering itself — the same layering our WASM
receipts doc proposes.

**Cite on:** FLUX WASM receipts lane, RECEIPTS-V2 cross-node scope,
ability-transfer fuel governance doc. Do not re-derive; differ.

---

## 4. Write-path provenance triptych (2026-09-22 edge-watch) — the memory-write receipts lane is heating up

Three results landed this week on the exact axis RECEIPTS-V2 and the
memory-poisoning positioning essay (arXiv 2605.08442) occupy:
persistent-memory attacks that ride a *write* into the store and execute
*later*, at retrieval. Recorded together because their joint message is
a scheduling signal, not three separate diffs.

**The triptych.**

1. **MemGhost (arXiv 2607.05189)** — poisoned long-term memory leaks
   chain-of-thought: 87.5% of protected reasoning recovered from a
   compromised LTM write. Proves the write path is the attack surface;
   retrieval-time defenses see the payload too late.
2. **Forensic trajectory signatures (arXiv 2606.30566)** — agent
   trajectories are attributable at AUC 0.9904 from behavior alone.
   Proves *detection after the fact* is nearly solved — attribution is
   commoditizing.
3. **Memory-poisoning-axis harness (csoai; CVE-2026-24301 "CoSnitch")**
   — signed receipts + deterministic predicates as the evaluation
   fixture for memory-poisoning defenses. This is the receipts lane
   being *framed by someone else* — with signatures and predicates, but
   (per the scan) without namespacing or hash-chained write lineage.

**What this narrows for us.** Our unclaimed defense candidate —
namespaced, hash-chained *memory-write receipts* (every write books a
namespaced receipt; replay re-derives; a poisoned write is a chain
break at the write, not a detection problem at the read) — now has a
citation obligation AND a preemption clock. The harness in item 3 is
shaping the evaluation vocabulary; if we ship after it hardens, we are
a variation instead of a position.

**What it does NOT touch.** The FNV-1a chain design, the cross-language
café pin, and the RECEIPTS-V2 signature envelope (verify-only,
cross-node scope). The triptych attacks *what gets written*; the chain
attacks *whether the ledger of writes is honest*. Complementary, and
that complementarity is exactly the one-argument close: a WAL row that
is simultaneously replay source, signed record, and meter receipt.

**Cite on:** RECEIPTS-V2 "why now" section, candor WAL REVOKE caller
lane (authority-without-erasure; candor main currently has no REVOKE —
verified 2026-09-22 by grep), memory-poisoning positioning essay.
Do not re-derive; differ, and differ soon.

---

## Standing rule (from this scan)

When an external result lands adjacent to a fleet claim, the first
deliverable is a one-paragraph *claim diff*: what they proved, what we
still claim, what we now must cite. This file is that diff, dated.
Positioning without citation is costume.
