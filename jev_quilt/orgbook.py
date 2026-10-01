"""OrgBook (G18): book the dispatch org *on* jev_quilt instead of a flat CSV.

`DISPATCH.md` says the build org is a quilt: every dispatch is a typed cell
booked into a double-entry ledger, routing is by earned standing, and waking
the expensive tier is gated by a deadband. Until now that was prose plus a
hand-maintained `dispatch-ledger.csv` — a WAL in spirit, but one that never
ran on the kernel. `OrgBook` is the replay-verifiable half of G18: the org's
own cells obey the same five laws the software does.

  * **Law 1 (identity never floats).** A dispatch is booked as an exact
    `Receipt` — tier, task class, runner, verdict and outcome are strings and
    booleans, never a float touches identity.
  * **Law 2/R2 (standing, not a vibe).** `route()` does not decide anything
    itself — it is *exactly* `standing.verdict(Standing.from_book(...), ...)`,
    the same fourth-verdict machine `standing.py` already proved. A runner's
    ANSWER-unsupervised is conferred by replaying its own booked-correct runs
    on a task class and revoked the instant one comes back wrong — R2,
    applied to the org rather than to a single cell.
  * **Law 3 (decide-one-pass).** `route()` is a pure read of the booked
    history; it never mutates the book. Only `record_dispatch()` writes.
  * **Law 4 (every dispatch is booked; replay ≡ live).** `record_dispatch`
    is the only way a dispatch becomes real; `replay()` walks the WAL tick by
    tick and reconstructs, from nothing but the entries booked *before* each
    dispatch, the exact routing decision the org made live — bit-for-bit.
  * **Law 5 (viability binary).** `outcome` is folded to a boolean `correct`
    before it ever reaches `standing.py` — a dispatch either passed its
    acceptance test or it did not; grading finer than that lives elsewhere.

Nothing here reimplements standing, commons, or the bookkeeper's chain
discipline — it wires them onto a new kind of cell (the dispatcher) exactly as
`diploma.py` wired them onto a portable envelope and `claim.py` wired them onto
reproduction. Exact and deterministic throughout: two org-books built from the
same dispatch sequence reconstruct the same decisions and agree on the same
digest, on deck or in a datacenter.

G20a (closes C9 — fail-open revocation, `ai-writings/situations/FABLE-ANSWER.md`
§3-4): a dispatch's identity — `dispatch_id`, `runner`, `key` (task_class),
`correct`, `base_verdict`, `answer` — is booked as `Receipt`'s TYPED, uncapped
fields, never packed into `Bookkeeper`'s 200-char capped residue. `book_for`,
`replay`, and (through `standing.Standing.from_book`) `route` all read those
typed fields; none of them parses the residue to decide anything. A REFUSED
admission's `reason` can be arbitrarily long — it stays in the freeform
residue (still capped, still an audited render, never a decision input) — and
no longer costs the dispatch its identity: `route()` and `replay()` see every
booked dispatch, including a refusal, so one booked-wrong (refused) admission
revokes standing exactly as Law 2/R2 promises, instead of silently vanishing
past the cap. Declared cost, exactly as `fold.py`'s v2 note declares for the
peak rule: `chain()`, `decisions_digest()`, and `Schoolhouse.pins()` change
for any script that already hit the residue-truncation bug (a refused
admission is now VISIBLE to replay), because the org's chain now binds the
typed identity fields too, not merely the capped residue text.

Honest limit (flagged, not fixed here): O7 / R5 — cost-per-passed-acceptance-
test as a *conserved* budget that throttles a tier — is a metabolism, not a
wire. It is out of scope for this module (see `NEW-DIRECTIONS.md` §B); this
file books the *routing* half only.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional

from .bookkeeper import Bookkeeper, Receipt
from .standing import Standing, verdict as standing_verdict, DEFAULT_DIPLOMA

# Outcomes that fold to `correct=True` when the caller doesn't pass `correct`
# explicitly (Law 5: viability is binary — pick a side, don't average it).
_CORRECT_OUTCOMES = {"correct", "pass", "passed", "viable", "ok", "done"}


@dataclass(frozen=True)
class Dispatch:
    """One reconstructed routing decision, as `OrgBook.replay()` derives it
    purely from the entries booked strictly before it."""
    dispatch_id: str
    tick: int
    runner: str
    task_class: str
    base_verdict: str
    verdict: str
    answer: Optional[str]


class OrgBook:
    """The dispatch org, booked on a `Bookkeeper` — one WAL, many runners.

    `diploma` is the streak length a runner must clear on a task class before
    it earns ANSWER-unsupervised on it (same default as `standing.py`, so an
    org-book with the fleet's default settings behaves identically to a bare
    `Standing` over the same receipts).
    """

    def __init__(self, cell_name: str = "org", *, diploma: int = DEFAULT_DIPLOMA):
        self.book = Bookkeeper(cell_name)
        self.diploma = max(1, diploma)

    # ── booking (the only write path — law 4) ──────────────────────────
    def record_dispatch(self, dispatch_id: str, tier: str, task_class: str,
                         runner: str, verdict: str, outcome: str, *,
                         base_verdict: Optional[str] = None,
                         correct: Optional[bool] = None,
                         answer: Optional[str] = None,
                         **extra) -> Receipt:
        """Book one dispatch as a `Receipt` — the org's double-entry row.

        `verdict` is the tier decision actually taken (ESCALATE/ACT/ANSWER/
        CONFIRM); `outcome` is whether the dispatch passed its acceptance
        test. `base_verdict`, when given, is the verdict `route()` would have
        handed down before any standing was consulted — recording it is what
        lets `replay()` reconstruct the live decision bit-for-bit without the
        caller re-supplying it out of band.
        """
        if correct is None:
            correct = str(outcome).lower() in _CORRECT_OUTCOMES
        answer_value = answer if answer is not None else tier
        # The residue: still a capped, human-readable RENDER (Law 3) — kept
        # exactly as before, for audit/display, and it may still be cut at
        # the 200-char cap for a long `reason`/etc. That is fine now: no
        # read path below decides from it any more.
        payload = {
            "dispatch_id": dispatch_id,
            "runner": runner,
            "tier": tier,
            "verdict": verdict,
            "outcome": outcome,
            "correct": bool(correct),
            "key": task_class,
            "answer": answer_value,
        }
        if base_verdict is not None:
            payload["base_verdict"] = base_verdict
        payload.update(extra)
        # G20a: the identity this dispatch is BOOKED under — typed, uncapped,
        # never packed into the residue. `book()` refuses (raises) rather
        # than truncate any of these (Law 6 totality).
        return self.book.book({"dispatch_id": dispatch_id},
                              {"outcome": outcome, "correct": bool(correct)},
                              verdict, payload,
                              dispatch_id=dispatch_id, runner=runner,
                              key=task_class, correct=bool(correct),
                              base_verdict=base_verdict, answer=answer_value)

    # ── deriving per-runner / per-class books (pure reads) ─────────────
    def book_for(self, runner: str, task_class: Optional[str] = None) -> Bookkeeper:
        """A real `Bookkeeper` holding exactly this runner's (optionally,
        this runner-on-this-class's) receipts, in original tick order — so
        routing is a pure function of the booked history, never a side
        table. Ticks are NOT renumbered (they stay the org WAL's own ticks):
        `Standing.from_book` only walks `.entries` in order, so this is
        replay-safe without pretending the sub-book is a from-genesis WAL.

        Reads the TYPED `runner`/`key` fields (G20a) — never the capped
        residue — so a dispatch whose freeform `reason` overran the render
        cap is still found here, exactly like any other booked dispatch."""
        entries = [e for e in self.book.entries
                  if e.runner == runner
                  and (task_class is None or e.key == task_class)]
        return Bookkeeper(cell_name=f"{self.book.cell_name}::{runner}", entries=entries)

    def standing_for(self, runner: str) -> Standing:
        return Standing.from_book(self.book_for(runner), diploma=self.diploma)

    # ── routing (law 2/R2 — a pure read, never a write) ────────────────
    def route(self, task_class: str, runner: str, base_verdict: str):
        """Exactly `standing.verdict(Standing.from_book(book_for(runner)),
        task_class, base_verdict)` — a runner's ANSWER-unsupervised is
        conferred by replaying its booked-correct runs on `task_class` and
        revoked on one booked-wrong. No routing logic lives here; this is
        wiring, not a second decision procedure."""
        return standing_verdict(self.standing_for(runner), task_class, base_verdict)

    # ── replay (law 4: replay ≡ live, on the org) ──────────────────────
    def replay(self) -> list[Dispatch]:
        """Reconstruct every routing decision from the WAL, bit-for-bit.

        For each booked dispatch, in tick order, recompute what `route()`
        would have returned using ONLY the entries booked strictly before
        it (the runner's standing at the moment that dispatch was actually
        decided) and record the reconstructed `(verdict, answer)`. A dispatch
        booked without a `base_verdict` (the caller didn't record what the
        pre-standing decision would have been) is skipped for reconstruction
        purposes — there is nothing to bit-for-bit against — but every
        recorded dispatch is otherwise walked in the org's own tick order, so
        two org-books built from the same sequence reconstruct identically.
        """
        # G20a: `base`/`runner`/`task_class`/`dispatch_id` are read off the
        # TYPED fields (never the capped residue) — so a well-formed WAL
        # (every dispatch booked through `record_dispatch`, which always
        # sets them) never hits `base is None: continue` for a reason as
        # shallow as a long `reason` string; that branch is reachable now
        # only for a dispatch a caller deliberately booked without
        # recording its pre-standing verdict.
        decisions: list[Dispatch] = []
        entries = self.book.entries
        for i, e in enumerate(entries):
            base = e.base_verdict
            if base is None:
                continue
            runner = e.runner
            task_class = e.key
            prior = [x for x in entries[:i]
                    if x.runner == runner and x.key == task_class]
            sub = Bookkeeper(cell_name=f"{self.book.cell_name}::{runner}::replay",
                             entries=prior)
            s = Standing.from_book(sub, diploma=self.diploma)
            v, answer = standing_verdict(s, task_class, base)
            decisions.append(Dispatch(
                dispatch_id=e.dispatch_id,
                tick=e.tick,
                runner=runner,
                task_class=task_class,
                base_verdict=base,
                verdict=v,
                answer=answer,
            ))
        return decisions

    # ── the deterministic pin (content-addressed agreement) ────────────
    def chain(self) -> str:
        """The org WAL's own chain hash (`Bookkeeper.replay()`) — two
        org-books booked from the same dispatch sequence agree bit-for-bit."""
        return self.book.replay()

    def decisions_digest(self) -> str:
        """A content-addressed digest over every reconstructed routing
        decision (`replay()`), in WAL order. Two org-books built from an
        identical dispatch sequence — hence an identical WAL chain — always
        agree on this digest too; it is the second, independent pin the
        predicate asks for (decisions, not just receipts)."""
        h = hashlib.sha256()
        for d in self.replay():
            h.update(f"{d.dispatch_id}\x1f{d.runner}\x1f{d.task_class}\x1f"
                     f"{d.base_verdict}\x1f{d.verdict}\x1f{d.answer}".encode("utf-8"))
        return h.hexdigest()
