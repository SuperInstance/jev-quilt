# jev-quilt

**JEV for quilt as understood output.** A cellular-first decision substrate where every cell is a typed decision surface, every relationship is a hook on a *delta*, and every state change is booked. Cells decide with Jev-class System One models (TypeSafe API or openjev-compatible local servers) or with exact q16 rational rules — never with a float where identity matters.

> Sibling of the quilt polyformalism (quilt-studio, twist-engine, tidepool). Cousin of TypeSafe's Jev and the openJEV ecosystem (SemIf, openjev, jevlike, NanoJev). This repo is the **fleet's own angle**: the cell as the unit, the quilt kernel as the spine, the bookkeeper as the memory.

## The one-sentence idea

A spreadsheet cell can hold `0.73` — but *as what*? In jev-quilt the type says: a **probability weight** in a Choice distribution, a **similarity score** against a vector probe, a **tone coefficient**, a **deadband gate**, or an **exact rational**. The value is the same shape; the semantics are declared at the cell. Plugins for Excel/Sheets/LibreOffice make that real for *spreadsheets of any program*; the same kernel runs headless as backend logic in a model-sense, not only a program-sense.

## Five laws

1. **Identity never floats.** Cell identity = integer `(k, s)` quilt coordinates + declared type. Values that are identities use the q16 exact-rational codec (`num:int64, den:int64`, floats are display-only projections). Decision probabilities are floats *by type* — calibration is their native semantics, not a bug.
2. **Hooks eat deltas, not values.** A cell subscribes to a sibling's *change* (or change-below-floor → silent, the deadband). Entanglement across instances/nodes is a declared LINK edge; arrival of a delta TICKs the subscribed cell's decision. Nobody polls.
3. **Decide in one pass, project elsewhere.** A cell's Jev question (Choice / Score / Noul) is computed in a single parallel decision — 10–500 ms. The *projection* of that decision (A2UI render, A2A JSON/MD payload, robotics reflex bus, ollama/tool/exe call) is a **different cell's job**. The decider never renders; the renderer never decides. This is the browser-use/jev-ultrafast split generalized to everything.
4. **Every state change is booked.** Each cell carries a bookkeeper: an append-only WAL of `(tick, state_hash, delta, decision_receipt)`. Replay ≡ live. A cell woken by a delta first replays its book to catch up — then decides. (The fleet already runs this spine in tidepool/hermit; here it's per-cell law.)
5. **Viability is binary, difference is not.** A cell's output passes a binary floor before it may LINK (the-tap doctrine: pure difference without viability collapses into dada noise). Above the floor, deltas are graded, hedged, and nudged — never silenced.

## The cell (v0 schema)

```python
Cell(
    name="npc.tone",                      # registry name
    coord=(k, s),                          # quilt identity — integers, never floats
    input_hooks=[Hook("player.utterance", on="delta", floor=DEADBAND)],
    decision=Choice(                       # one of Choice | Score | Noul | Q16Rule
        state_ref="dialogue.spine",
        options=["warm", "neutral", "guarded"],
    ),
    backend="auto",                        # typesafe-api | openjev-local | q16 | auto
    outputs=[Projection(to="voice.tone", as_type="coefficient"),
             Projection(to="a2a.payload", as_type="json")],
    bookkeeper=True,                       # WAL on, replay-verified
)
```

Backends resolve `auto → q16` (deterministic, always available) → `openjev-local` (SemIf-compatible server if reachable) → `typesafe-api` (if `TYPESAFE_API_KEY` set). Exactness first, cloud last — the same doctrine as the lattice kernel.

## What this enables (the genres — see `docs/ideation/` and AI-Writings `ideation/`)

- **Fractaled dialogue.** An NPC cluster pre-computes the conversation a few pages ahead: each branch node is a Choice over candidate next-moves, each with calibrated probability. Every word the human says updates the state → only the affected spine re-decides (deadband-gated), so hedging and nudging are *cheap*. Voice-speed, because reflexes never touch an LLM.
- **The boat.** A game-player cluster that learns chess, hold'em, a dozen games old and new *inductively*: world-sim cells are the world (Jev is the simulation, not the consciousness), player-mind cells keep durable logic via probability routes. The developer GANs by handing in rules text + look-and-feel specs. A human can jump in mid-evolution and guide it.
- **Robotics last-mile.** One decision fans out: a fraction of cells route straight to reflex buses (pincher), others go through JEPA/Jev reasoning cells, others to cloud APIs or a local ollama loop. Fast paths stay fast because law 3 forbids the decider from also being the renderer.
- **Spreadsheet plugins.** `=JEV.CHOICE(state, options)` in Excel, Google Sheets, LibreOffice — the same kernel, projected into any program's grid. Percentages in cells become typed decision surfaces, not unexplained numbers.
- **Agent culture.** Long-running cells with time off: games and songs at the TAP, play as first-class tick content. The elephant/JEPA precedent, now on the JEV substrate. (Mostly real work still — culture is bounded, not the job.)

## Landscape (researched 2026-09-21)

- **Jev (TypeSafe AI)** — closed System One API; state + typed questions → Choice/Score/Noul with calibrated probabilities, single parallel pass, per-request pricing. SDK: `typesafe-sdk`.
- **SemIf** (TheoLeeCJ, MIT, ~1.9k★) — open reproduction reading Qwen3.5-4B logits directly; 3090/WebGPU; the reference local backend.
- **openjev** (razorback16) — Jev-wire-compatible decision server on DiffusionGemma 26B, Docker.
- **jevlike** (vinnylarouge) — *trainable*, ships Doom/chess/Wikispeedia demos — the existence proof for the boat.
- **NanoJev** — Qwen3-0.6B decision heads, edge daemons.
- **browser-use/jev-ultrafast** — Jev picks DOM op+element; small LLM writes text only when needed — law 3's existence proof.
- **Known honest caveat** (HN, JevBench): open clones rarely emit type errors but can *pick the wrong valid option confidently*. Hence law 5: confidence gates viability; receipts expose calibration drift.

## Status

v0 design + reference kernel skeleton (`jev_quilt/`: cells, hooks, bookkeeper, backends) with tests. Not yet: plugin binaries, the boat, fractal dialogue engine, network entanglement transport. The queue names the lanes.

## License

MIT for our code; vendored inspirations keep their own.
