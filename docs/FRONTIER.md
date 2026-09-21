# FRONTIER — the ladder past v0.3

*Two builds, one kernel. Every rung here ships a **toy** (small enough to teach a
kid the idea in an afternoon) and an **industrial** version (built to work in
rough seas — offline, deterministic, provable after a reboot). The toy is not a
lesser thing; it is the same law with the sea taken out, so the law can be seen.*

This is the fleet's own research ladder for jev-quilt, cross-referenced with the
AI-Writings reverse-actualization **Forward Arc** (`reverse-actualization/forward/
GAPS.md`), where each rung was first dramatized as a 2036 capability and then
compiled into a runnable acceptance test. Several rungs are already proven in a
sibling sandbox; this file maps them home to jev-quilt's primitives.

---

## The rough-seas contract

"Works in rough seas" is not a vibe; it is a checklist the five laws already imply:

1. **Offline-first exactness.** The boat loses the cloud. `auto → q16` must decide
   without a network, bit-identical every time (law 1). The cloud is a garnish,
   never a dependency.
2. **Graceful degradation, declared.** `typesafe-api → openjev-local → q16` is a
   *descent*, not a failure cascade. Each fallback is exact or honestly labeled;
   none silently rounds identity.
3. **Provable after a reboot.** A cell woken cold replays its book and is
   bit-for-bit where it was (law 4). A crash mid-haul costs nothing but time.
4. **Deadbands survive noise.** Rough water is noise. Hooks eat deltas *above a
   floor* (law 2); the ordinary chop never wakes the cell, so the real change
   isn't buried in false alarms.
5. **Calibrated, not merely legal.** A bounded decision that cannot be *illegal*
   can still be *over-confident* — and over-confidence is what sinks boats (see
   the bored-middle, below). Viability floors must adapt to conditions (law 5).

The teaching version of each is the same checklist with a calm pool instead of a
gale — which is exactly why a child can see the law before the sea hides it.

---

## The ladder

### R1 · Calibrated alarm floor — the bored-middle *(SHIPPED — `jev_quilt/calibrate.py`)*
- **The failure it prevents.** A *fixed* alarm floor tuned for normal seas sleeps
  through a small anomaly hiding in a long calm — the rogue ripple in a flat sea.
  Legal the whole time; over-confident the whole time.
- **Toy.** `examples/rough_seas.py`: a flat calm, one small ripple; the fixed
  floor misses it, the calibrated floor catches it. Ten lines a kid can read.
- **Industrial.** `CalibratedFloor` over the predictor's `surprise`, exact-ℚ,
  tightening in the calm and relaxing after a spike (no alarm storm, no permanent
  deafness). Pairs with `MeanPredictor`.
- **Extends.** `predictor.alarm` (law 5). **Test:** `tests/test_calibrate.py` —
  the calibrated floor catches a 0.03 ripple a 0.05 fixed floor sleeps through.
- **Forward Arc:** G2.

### R2 · The commons & earned standing — the fourth verdict
- **The failure it prevents.** Every cell re-asking the fleet what it already
  knows cold — a radio channel jammed with questions whose answers are aboard. And
  the opposite: a cell trusting a proven route whose sea has since changed.
- **Toy.** Two cells, one page, a handful of repeated intents; watch queries fall
  as standing is earned, and watch standing evaporate the moment the answer goes
  stale.
- **Industrial.** A content-addressed deposit commons (the bookkeeper generalized
  across pages); `ACT / CONFIRM / ESCALATE` plus a conferred, revocable **`ANSWER`**
  — the right to stop asking, granted by the commons, torn up on the first miss.
- **Extends.** `bookkeeper`, `inquire.next_questions`. **Test:** redundant-query
  share falls sharply with no rise in error; revocation within a few ticks of a
  regime change. **Forward Arc:** G3, G4.

### R3 · Learned memory horizon — recency vs distance *(readings already seed this)*
- **The failure it prevents.** Trusting old logs when the fishery has moved
  (should have forgotten), or being whipsawed by one noisy sounding (should have
  averaged). The wrong memory length is wrong in opposite ways in different seas.
- **Toy.** Two worlds — a drifting one and a stable-but-noisy one — and a gate
  that learns which memory length wins each. Short memory wins the drift; long
  memory wins the noise; the learned one wins both.
- **Industrial.** A `DriftReading`/`TendencyReading` ensemble whose decay is
  *learned per page* by hindsight, in the exact family.
- **Extends.** `readings.*`. **Test:** learned horizon matches the best fixed
  horizon in *both* worlds. **Forward Arc:** G7.

### R4 · The self-directing compiler & the self-authored gap
- **The failure it prevents.** A backlog that only grows when a human has time to
  write it. On a boat, the human is hauling gear; the system should be able to
  say, precisely and provably, *here is a thing I cannot yet do, and here is the
  test for it* — and wait for a yes.
- **Toy.** A tiny compiler cell that reads a ledger of gaps, re-verifies the
  built ones, and prints the open ones as next work — self-direction you can watch.
- **Industrial.** The compiler probes a built capability to its breaking point,
  **authors a new gap spec with a machine-checkable predicate**, confirms the
  current policy fails it, and evolves one that passes — the whole loop gated only
  by a human *yes* (the fleet's oldest safety instinct: bounded autonomy).
- **Extends.** `engine`, `bookkeeper`, `inquire`. **Test:** an authored spec is
  harder than the current frontier, currently fails, and is then closed.
  **Forward Arc:** G6, G10.

### R5 · Metabolism — IO flow as an energy budget
- **The idea.** Every booked delta is already a double-entry transaction. Make the
  units *mean* something: a conserved budget (attention, fuel, trust). A cell that
  spends more than it earns starves and goes quiet; a useful cell is fed. The
  quilt grows an economics, and triage becomes physics instead of policy — the
  boat's real constraint (you cannot run every winch at once) modeled honestly.
- **Toy.** A handful of cells and a fixed budget; watch attention flow to the
  cells that pay their way.
- **Industrial.** Budget as a first-class booked quantity; back-pressure and
  priority fall out of conservation. **Extends.** `bookkeeper`, `engine`.
  **Forward Arc:** G9.

### R6 · The learning kernel that stays bit-checkable *(the deep one)*
- **The tension.** Law 1 says identity never floats and the book replays exactly.
  But a cell that *learns* changes its behavior — and a changed behavior seems to
  break the golden. On a boat you need both: gear that improves with the season,
  and gear you can trust to be exactly itself after a power cycle.
- **The resolution to prove.** Make the *update itself* an exact-ℚ, deterministic,
  bounded operation, so a learned cell still has a golden — one that advances
  step-legibly instead of freezing. A learned substrate that is still replay-
  verifiable is the whole ballgame.
- **Extends.** everything. **Test:** a learning cell's book replays bit-for-bit
  and its golden advances by declared, legal steps. **Forward Arc:** G8.

---

## The teaching ladder (for the next generation)

A newcomer — a deckhand, a kid, a new engineer — walks these in order, each a
runnable toy, each one law:

1. **A cell holds a typed number.** `0.73` *as what?* (law 1 — `q16`, `Cell`)
2. **A hook eats a change, not a value.** Nobody polls. (law 2 — `Hook`, deadband)
3. **A decision is one pass; the render is someone else's job.** (law 3 — `inquire`)
4. **Every change is booked; replay equals live.** Pull the plug, come back, prove
   it. (law 4 — `Bookkeeper`)
5. **A feeling before the fact.** The predictor guesses; `surprise` grades it.
6. **Confidence must be earned, not assumed.** The calibrated floor — the ripple
   in the calm. (R1)
7. **Stand on what the fleet already knows.** The commons; the right to stop
   asking. (R2)
8. **The boat that teaches itself a game** — and lets you jump in and steer.
   (game-agents; R3–R6 underneath)

Every rung is a half-hour a parent and a child could do at a table, and the same
rung, hardened, is what keeps the real boat off the rocks. That is the doctrine:
*build the toy so the law can be seen, build the industrial so the law can be
trusted, and never let them drift into two different laws.*

---

*Filed against AI-Writings `reverse-actualization/forward/GAPS.md` (G2–G10) and
the substrate essay `systems-engineering/the-quilt-substrate.md`. R1 is aboard;
R2–R6 are the next hauls.*
