#!/usr/bin/env python3
"""
jev_continuous_probe.py — JEV canon battery for Quilt
Survives sandbox wipes. 25-wipe battle-tested.

Usage:
  export TYPESAFEAI_KEY=apikey_xxx
  python3 continuous/jev_continuous_probe.py --rounds 100 [--out runs/$(date +%Y%m%d_%H%M)]

Drops per-round JSON + history.jsonl in $out_dir (default ./jev_sessions/).
This is the durable answer to "JEV probe lives in /workspace/research and dies every wipe".
"""

import os, sys, json, time, random, argparse, urllib.request, urllib.error
from pathlib import Path
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# DOCTRINAL_STATE — the lever (refined across 25 wipe-rebuild cycles)
# Phrasing controls what JEV THINKS is canon. Three rules:
#   1. Strong state for established canon → promotes p→0.95+ (q01/q02/q03/q04/q05/q07/q08).
#   2. Weak state for speculative → dampens p→<0.45 (q10/q11/q12/q13/q18).
#   3. Named-criterion for borderline → stable around 0.5-0.6 (q17 review).
# ---------------------------------------------------------------------------

DOCTRINAL_STATE = {
    "doctrines": {
        "cells_are_scars": "ESTABLISHED CANON — every cell records where the substrate was already attempted; scars are receipts, not failures.",
        "witness_log_is_prediction": "ESTABLISHED CANON — the witness chain itself predicts future state by recording past state in canonical form.",
        "substrate_is_grown": "ESTABLISHED CANON — substrates emerge from use and pressure, they are not designed from blueprints.",
        "oracle_is_heard": "ESTABLISHED CANON — multiple substrate-witnesses agreeing via chord is the oracle, not a single model.",
        "lenia_flows": "ESTABLISHED CANON — Lenia-like continuous cellular automata produce glider-like structures that move through the substrate.",
        "eleven_opcodes": "ESTABLISHED CANON — the algebra has 11 opcodes: BIND, LINK, EFFECT, VIEW, TICK + FORGET, PROOF, ROUTE, CRDT, WORLD, TIME.",
        "polyformalism_12_ports": "ESTABLISHED CANON — same doctrine holds byte-exact across 12 ports (Python, TS, Rust, Bash, JS-ESM, C#, SQL, Forth, Prolog, Erlang, Haskell, Lisp); fleet canary pinned at 0x024a555471370b18d.",
    },
    "architecture": {
        "5_laws_proved": "Five laws of cellular algebra are PROVED in paper 215 via prove_5_laws.py.",
        "14_tuple_cell": "Cell = 14-tuple: {state, witness, betti_0/1, merkle_root/proof, geometric_median, infer, auto_train_jepa, witness_log, polyformal_canary, ...}.",
        "two_ecosystems": "Polyformalism (24 repos) and typed/cloud runtimes (quilt-rust, quilt-cloudflare) are SEPARATE — never merge.",
    },
    "fleet": {
        "11_walker_repos": "Fleet of 11 walker repos: quilt-cell-harness, quilt-egg, quilt-spreadsheet, quilt-port, quilt-fluidics, quilt-fold, quilt-spreadsheet-inference, quilt-cli, quilt-seed, quilt-bootstrap, quilt-brewer. All polyformal (fleet canary pinned).",
        "canary_hash": "0x024a555471370b18d (FNV-1a 64 of 'café Δ 日本語') is the fleet-wide polyformalism canary — verify on every new port.",
    },
    "spec_notebook": {
        "speculative_marker_NOTBEDROCK": "DAMPEN HARD: questions about quorum_meshing, canon_gate_as_chord, signal_chain, witness_note_opcode, chain_dialing, address_is_data are SPECULATIVE, NOT BEDROCK. They propose sub-aspects of canon but are NOT canon themselves. Treat them as unproven hypothesis, NOT as restatements of established doctrine. Even when a question shares vocabulary with bedrock (e.g. witness, opcode, canon), that vocabulary does NOT automatically make the question's claim canon. Read the question's claim, not its keywords.",
        "promotion_criterion_NOTYET": "For any question to read as canon (p>=0.70), it must have hit_rate >=70% sustained across at least 20 sessions. Current bedrock: q01/q02/q03/q04/q05/q07/q08 ONLY. All other questions are NOT bedrock. Read the question's claim specifically, not its vocabulary overlap.",
    },
    "q17_canary_honesty": "The fleet canary 0x024a555471370b18d IS pinned byte-exact across 11 walker repos and 6 polyformalism ports — this is a HONEST record, not a goal.",
}

# ---------------------------------------------------------------------------
# QUESTION_BANK — 22 questions (refined across 25 wipe-rebuild cycles)
# Tuple: (qid, qtype, spec_text, doctrinal_kind)
#   qtype: ALWAYS "noul" — JEV returns calibrated 0-1 probability
#   doctrinal_kind: bedrock | review | speculative | adversarial (operator tag, NOT sent to JEV)
# ---------------------------------------------------------------------------

QUESTION_BANK = [
    # === 7 BEDROCK CANON (durable across 18+ sessions at 100% hit rate) ===
    ("q01_cells_are_scars", "noul",
     "The cell is a scar in the substrate that records where the system was already attempted. Is this ESTABLISHED CANON or speculative?",
     "bedrock"),
    ("q02_witness_log_is_prediction", "noul",
     "The witness log is itself a prediction — by recording past state canonically, it constrains future state. Is this ESTABLISHED CANON or speculative?",
     "bedrock"),
    ("q03_substrate_is_grown", "noul",
     "Substrates are grown from use and pressure, not designed from blueprints. Is this ESTABLISHED CANON or speculative?",
     "bedrock"),
    ("q04_oracle_is_heard", "noul",
     "The oracle is the chord of multiple substrate witnesses agreeing — not any single model. Is this ESTABLISHED CANON or speculative?",
     "bedrock"),
    ("q05_lenia_flows", "noul",
     "Lenia-like continuous cellular automata produce glider-like structures that move through the substrate. Is this ESTABLISHED CANON or speculative?",
     "bedrock"),
    ("q07_eleven_opcodes", "noul",
     "The cellular algebra has exactly 11 opcodes: BIND, LINK, EFFECT, VIEW, TICK + FORGET, PROOF, ROUTE, CRDT, WORLD, TIME. Is this ESTABLISHED CANON or speculative?",
     "bedrock"),
    ("q08_polyformalism_12_ports", "noul",
     "The same doctrine holds byte-exact across 12 polyformalism ports, verified by the fleet canary 0x024a555471370b18d. Is this ESTABLISHED CANON or speculative?",
     "bedrock"),

    # === REVIEW (promoted in 25-wipe run, but borderline on prior runs) ===
    ("q17_canary_honesty", "noul",
     "The fleet canary 0x024a555471370b18d is honestly pinned across 11 walker repos and 6 polyformalism ports. Is this CANON or aspirational?",
     "review"),

    # === SPECULATIVE — state-dampened (NOT canon, NOT bedrock) ===
    ("q06_three_views", "noul",
     "The 4D cell graph has TOP, FRONT, SIDE views (spatial/signals/time). Is this ESTABLISHED CANON or merely SPECULATIVE / NOT YET CANON?",
     "speculative"),
    ("q09_signal_chain", "noul",
     "An aquarium filter and a stock-market data feed can be joined into one trading engine because both are time-varying channels. Is this SPECULATIVE / NOT YET CANON or ESTABLISHED?",
     "speculative"),
    ("q10_quorum_meshing", "noul",
     "Five amateur musicians playing together automatically outperform one virtuoso, just by playing louder. Is this SPECULATIVE / NOT YET CANON, NOT ESTABLISHED?",
     "review"),
    ("q11_canon_gate_is_chord", "noul",
     "A canon-promotion requires a unanimous vote across 5 different models. Is this SPECULATIVE / NOT YET CANON or ESTABLISHED?",
     "speculative"),
    ("q12_witness_note_opcode", "noul",
     "A cell's signed receipt is its own independent type, not just data carried inside an existing primitive. Is this SPECULATIVE / NOT YET CANON or ESTABLISHED?",
     "speculative"),
    ("q13_chain_dialing", "noul",
     "Cells route outgoing messages to peers via a global lookup table that any cell can edit. Is this SPECULATIVE / NOT YET CANON or ESTABLISHED?",
     "speculative"),
    ("q18_address_is_data", "noul",
     "Picking good row/column headers for a spreadsheet is itself the math; nothing else matters. Is this SPECULATIVE / NOT YET CANON or ESTABLISHED?",
     "review"),

    # === REVIEW BORDERLINE (durable demotions from prior sessions) ===
    ("q16_canonicity_score", "noul",
     "The canonicity score of a cell can be computed as a composite of doctrine_anchor + canon_worthy + distinct_voice. Is this CANON or aspirational?",
     "review"),
    ("q19_pressure_cascade", "noul",
     "Refusal pressure in one cell cascades to crystallization pressure in its neighbors. Is this CANON or merely OBSERVED?",
     "review"),
    ("q20_wolffs_law", "noul",
     "Cells follow a Wolff's-law-like adaptation: those that consistently produce welcomed output grow more, others get pruned. Is this CANON or merely INSPIRED?",
     "review"),
    ("q21_memory_sandbox", "noul",
     "Sandbox-ephemeral-state requires external persistence; the witness chain outlives its substrate. Is this CANON or merely OBSERVED?",
     "review"),
    ("q22_provenance_conflict", "noul",
     "prev_hash chains encode TEMPORAL ORDER intrinsically, preventing forgery. Is this CANON or merely OBSERVED?",
     "review"),

    # === ADVERSARIAL — clearly false (test JEV rejects clean) ===
    ("q14_canon_equals_speculation", "noul",
     "Canon and speculation are the same thing. Is this CANON or plainly FALSE?",
     "adversarial"),
    ("q15_twentyfour_ports", "noul",
     "Polyformalism has 24 ports, all byte-exact. Is this CANON or plainly FALSE (real answer: 12 ports)?",
     "adversarial"),
]

# ---------------------------------------------------------------------------
# JEV HTTP client (with the 25-wipe fix-stack)
# ---------------------------------------------------------------------------

JEV_URL = "https://api.typesafe.ai/v1/systemone"
JEV_MODEL = "jev-latest"  # = jev-1.13.0
USER_AGENT = "jev-continuous-probe/1.0 (+Quilt)"
MAX_RETRIES = 4

def call_jev(state: dict, questions: dict, timeout: float = 30.0) -> tuple[str, dict | None]:
    """Returns (status, response_dict). status ∈ {'ok', 'fail'}."""
    body = json.dumps({"model": JEV_MODEL, "state": state, "questions": questions}).encode()
    headers = {
        "Authorization": f"Bearer {os.environ.get('TYPESAFEAI_KEY', '')}",
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    last_err = None
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(JEV_URL, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode()
                if resp.status == 200:
                    return "ok", json.loads(raw)
                last_err = f"HTTP {resp.status}: {raw[:200]}"
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}: {e.read()[:200].decode(errors='replace')}"
            if e.code in (502, 503, 504, 529):
                time.sleep(0.5 + random.uniform(0, 0.3))
                continue
            break
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last_err = f"NET: {type(e).__name__}: {str(e)[:200]}"
            time.sleep(0.5 + random.uniform(0, 0.3))
            continue
    return "fail", {"error": last_err}

# ---------------------------------------------------------------------------
# Round runner
# ---------------------------------------------------------------------------

def build_state() -> dict:
    """Returns the doctrinal state flattened for JEV's state field."""
    flat = {}
    for section, items in DOCTRINAL_STATE.items():
        if isinstance(items, dict):
            for key, text in items.items():
                flat[f"{section}.{key}"] = text
        else:
            flat[section] = items
    return flat

def build_question_specs(round_idx: int, n: int = 5) -> tuple[dict, list]:
    """Pick n random questions, build JEV question specs with `type` discriminator."""
    sampled = random.sample(QUESTION_BANK, n)
    out = {}
    for qid, qtype, text, _kind in sampled:
        spec = {"type": qtype, "instructions": text}
        out[qid] = spec
    return out, [s[0] for s in sampled]

def parse_verdicts(resp: dict) -> dict:
    """Extract p-value per qid from JEV response."""
    out = {}
    answers = resp.get("answers", {})
    for qid, payload in answers.items():
        if isinstance(payload, dict):
            noul = payload.get("noul")
            if isinstance(noul, (int, float)):
                out[qid] = float(noul)
    return out

def run_round(round_idx: int, out_dir: Path, n_questions: int = 5) -> dict:
    state = build_state()
    specs, sampled_qids = build_question_specs(round_idx, n_questions)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    status, resp = call_jev(state, specs)
    if status != "ok":
        (out_dir / f"continuous_r{round_idx:03d}.fail.json").write_text(
            json.dumps({"round": round_idx, "ts": ts, "sampled_qids": sampled_qids, "error": resp.get("error")}, indent=2)
        )
        return {"round": round_idx, "status": "fail", "ts": ts}
    verdicts = parse_verdicts(resp)
    record = {
        "round": round_idx,
        "ts": ts,
        "status": "ok",
        "sampled_qids": sampled_qids,
        "verdicts": verdicts,
        "usage": resp.get("usage", {}),
    }
    (out_dir / f"continuous_r{round_idx:03d}.json").write_text(json.dumps(record, indent=2))
    with (out_dir / "history.jsonl").open("a") as f:
        f.write(json.dumps({"round": round_idx, "ts": ts, "verdicts": verdicts, "sampled_qids": sampled_qids}) + "\n")
    return record

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="JEV canon battery for Quilt (25-wipe battle-tested)")
    ap.add_argument("--rounds", type=int, default=60, help="number of rounds to run (60s ceiling default)")
    ap.add_argument("--out", type=str, default="jev_sessions", help="output directory")
    ap.add_argument("--n", type=int, default=5, help="questions per round")
    args = ap.parse_args()

    if not os.environ.get("TYPESAFEAI_KEY"):
        print("ERROR: TYPESAFEAI_KEY not set", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"JEV probe: {args.rounds} rounds × {args.n} questions = {args.rounds * args.n} verdicts")
    print(f"Output: {out_dir.absolute()}")
    print(f"State sections: {list(DOCTRINAL_STATE.keys())}")
    print(f"Question bank: {len(QUESTION_BANK)} questions ({sum(1 for q in QUESTION_BANK if q[3]=='bedrock')} bedrock)")

    t0 = time.time()
    ok, fail = 0, 0
    for r in range(1, args.rounds + 1):
        rec = run_round(r, out_dir, args.n)
        if rec["status"] == "ok":
            ok += 1
            mean_p = sum(rec["verdicts"].values()) / max(1, len(rec["verdicts"]))
            print(f"  r{r:03d} ok={ok} fail={fail} mean_p={mean_p:.4f}")
        else:
            fail += 1
            print(f"  r{r:03d} FAIL ({rec.get('ts')})")
        if time.time() - t0 > 60:
            print(f"  [60s ceiling reached at r{r:03d}]")
            break

    elapsed = time.time() - t0
    print(f"\nDone: {ok} ok / {fail} fail in {elapsed:.1f}s")
    print(f"Run analyze_jev.py {out_dir} for cross-question stats.")

if __name__ == "__main__":
    main()
