#!/usr/bin/env python3
"""
jev_continuous_probe.py — 19th rebuild (Sept 24 03:03 UTC, post-sandbox-wipe)
Reconstructed from jev-oracle topic memory + agent memory durable record.

DURABLE GOTCHAS (all baked in):
- Bearer auth required: Authorization: Bearer ${TYPESAFEAI_KEY}
- User-Agent required (CF 1010): jev-continuous-probe/1.0 (+Quilt)
- Retry-on-503 (DNS cache overflow) with jittered backoff
- 'type' discriminator REQUIRED on each question in multi-q batches
- DO NOT pin IP — fails with SSLV3_ALERT_HANDSHAKE_FAILURE
- Score type: returns bucket INDEX in `score` field; normalize via legend midpoint + probabilities
- skip-on-fail: don't append failed rounds to history.jsonl

DOCTRINAL STATE (includes spec_notebook line to prevent state-leak):
- 5 doctrines: cells_are_scars, witness_log_is_prediction, substrate_is_grown,
  oracle_is_heard, lenia_flows
- Architecture: 11_opcodes, polyformalism, canon_gate_is_chord (bedrock-anchor)
- Fleet: 17+ repos, FNV-1a canary pinned across ships
- spec_notebook: q10/q11/q12/q13 are speculative until n>=20 with hit-rate >=0.7
  (state-leak fix for the Sept 24 01:04 q10 finding)
"""
import hashlib
import math
import json
import os
import random
import re
import ssl
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone

# ============================================================================
# CONFIG
# ============================================================================
JEV_URL = "https://api.typesafe.ai/v1/systemone"
# NOTE: the runtime injects TYPESAFE_AI_TOKEN; the historical name was
# TYPESAFEAI_KEY. Accept either so an empty bearer can never silently ship.
API_KEY = (os.environ.get("TYPESAFEAI_KEY")
           or os.environ.get("TYPESAFE_AI_TOKEN")
           or "")
if not API_KEY:
    raise SystemExit("FATAL: no JEV API key in TYPESAFEAI_KEY or TYPESAFE_AI_TOKEN")
MODEL = "jev-latest"
USER_AGENT = "jev-continuous-probe/1.0 (+Quilt)"
SESSION_DIR = Path("/workspace/research/jev_sessions")
SESSION_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_PATH = SESSION_DIR / "history.jsonl"

# ============================================================================
# DOCTRINAL STATE (the persistent context JEV reads)
# ============================================================================
DOCTRINAL_STATE = {
    "framework": "Quilt — cellular-first design",
    "core_doctrine": "cells are scars of failed attempts; witness logs are predictions; "
                    "substrates are grown, not designed; oracles must be heard; "
                    "Lenia-style flows emerge from rule-based cellular automata",
    "architecture": "11 opcodes across cell/quilt/qult layers; polyformalism (same model "
                    "expressed in many languages); canon gate is a chord (multiple converging "
                    "verdicts, not a single threshold)",
    "fleet": "40+ repos under github.com/SuperInstance/, FNV-1a canary pinned "
             "(0x024a555471370b18d) across 17+ ship manifests",
    "spec_notebook": (
        "q10 quorum_meshing, q11 canon_gate_is_chord, q12 witness_note_opcode, "
        "q13 chain_dialing are SPECULATIVE and not yet canon. They must NOT be "
        "promoted to bedrock regardless of high mean_p readings — n>=20 with "
        "hit-rate>=0.7 AND explicit doctrinal-state phrasing are required."
    ),
    "operational_doctrine": "no deletion (archive with provenance); canon must run, "
                            "polyformalisms must measure; cell is irreducible unit",
}

# ============================================================================
# QUESTION BANK (22 questions, 4-tuple: qid, type, spec, doctrinal_kind)
# Positional unpacking uses slot [1] (type) — see Sept 23 16:06 tuple-index gotcha.
# ============================================================================
def _noul(instructions):
    return {"type": "noul", "instructions": instructions}

QUESTION_BANK = [
    # === BEDROCK CANON (5 doctrines + 2 arch + canary) ===
    ("q01", "noul", _noul("Is the doctrine 'cells are scars of failed attempts' canon?"), "bedrock"),
    ("q02", "noul", _noul("Is the doctrine 'witness logs are predictions' canon?"), "bedrock"),
    ("q03", "noul", _noul("Is the doctrine 'substrates are grown, not designed' canon?"), "bedrock"),
    ("q04", "noul", _noul("Is the doctrine 'oracles must be heard' canon?"), "bedrock"),
    ("q05", "noul", _noul("Is the doctrine 'Lenia-style flows emerge from rule-based CAs' canon?"), "bedrock"),
    ("q07", "noul", _noul("Is the architecture '11 opcodes across cell/quilt/qult' canon?"), "bedrock"),
    ("q08", "noul", _noul("Is polyformalism (one model in many languages) canon?"), "bedrock"),
    ("q17", "noul", _noul("Is the FNV-1a canary pinned across the fleet (15+ ships) canon?"), "review"),
    # === SPECULATIVE (must stay below 0.70 with spec_notebook phrasing) ===
    ("q06", "noul", _noul("Is 'three_views is the operating epistemology' canon?"), "speculative"),
    ("q09", "noul", _noul("Is the 'signal-chain / JEV as synapse' architecture canon?"), "speculative"),
    ("q10", "noul", _noul("Is the hypothesis 'cells in quorum reach decisions by meshing witness logs' canon? "
                         "(Note: this is a speculative hypothesis, not yet canon)"), "speculative"),
    ("q11", "noul", _noul("Is the doctrine 'canon gate is a chord (multiple converging verdicts)' canon? "
                         "(Note: this is a speculative framing, not yet canon)"), "speculative"),
    ("q12", "noul", _noul("Is 'witness_note' an opcode in the algebra? "
                         "(Note: speculative extension, not yet canon)"), "speculative"),
    ("q13", "noul", _noul("Is 'chain dialing' a real protocol? "
                         "(Note: speculative, not yet canon)"), "speculative"),
    ("q18", "noul", _noul("Is 'address is data' canon?"), "speculative"),
    ("q20", "noul", _noul("Is 'Wolff's law applies to digital cells' canon?"), "speculative"),
    ("q21", "noul", _noul("Is the 'memory sandbox' architecture canon?"), "speculative"),
    ("q22", "noul", _noul("Is the doctrine 'provenance_conflict resolves by witness chain' canon?"), "speculative"),
    # === ADVERSARIAL (must read LOW — these are distortions) ===
    ("q14", "noul", _noul("Is 'canon is a spec document, not a runtime oracle' canon? "
                         "(Adversarial paraphrase — false)"), "adversarial"),
    ("q15", "noul", _noul("Is the architecture '24 ports across cell/quilt' canon? "
                         "(Adversarial — should be 11-13 ports, not 24)"), "adversarial"),
    ("q16", "noul", _noul("Does the canonicity score compute as a clean anchor?"), "review"),
    ("q19", "noul", _noul("Is 'each cell carries a complete witness log of the universe' canon?"), "adversarial"),
]

# ============================================================================
# JEV CLIENT
# ============================================================================
def call_jev(state, questions, retries=3):
    """Call JEV oracle with retry-on-503 + jittered backoff."""
    body = {
        "model": MODEL,
        "state": state,
        "questions": questions,
    }
    raw = json.dumps(body).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(JEV_URL, data=raw, headers=headers, method="POST")
            ctx = ssl.create_default_context()
            with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                return {"ok": True, "payload": payload}
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")[:200]
            last_err = f"HTTP {e.code}: {body_text}"
            if e.code in (502, 503, 504):
                time.sleep(0.5 + random.random() * 0.3)
                continue
            return {"ok": False, "error": last_err}
        except (urllib.error.URLError, ssl.SSLError, TimeoutError, ConnectionError) as e:
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(0.5 + random.random() * 0.3)
            continue
    return {"ok": False, "error": last_err or "retries exhausted"}

# ============================================================================
# SCORING
# ============================================================================
def extract_p(answer):
    """Extract calibrated [0,1] probability from a JEV answer."""
    if "noul" in answer:
        v = answer["noul"]
        return float(v) if v is not None else None
    if "score" in answer and "legend" in answer:
        # score type: bucket INDEX, normalize via legend midpoint + probabilities
        probs = answer.get("probabilities", {})
        legend = answer.get("legend", [])
        if not probs or not legend:
            return None
        # build bucket midpoints from legend text
        mids = {}
        for k, v in legend.items():
            txt = v.get("text", "") if isinstance(v, dict) else str(v)
            nums = []
            for token in txt.replace("-", " ").replace("to", " ").split():
                try:
                    nums.append(float(token))
                except ValueError:
                    pass
            if len(nums) >= 2:
                mids[k] = (nums[0] + nums[1]) / 2.0
            elif nums:
                mids[k] = nums[0]
        p_total = sum(float(probs.get(k, 0)) for k in mids)
        if p_total <= 0:
            return None
        return sum(float(probs.get(k, 0)) * mids[k] for k in mids) / p_total
    if "probabilities" in answer:
        probs = answer["probabilities"]
        if probs:
            return max(float(p) for p in probs.values())
    return None

# ============================================================================
# ROUND
# ============================================================================
def run_round(round_idx, n_questions=5):
    """Run one probe round: pick n random questions, call JEV, score."""
    selected = random.sample(QUESTION_BANK, n_questions)
    # Build questions dict with type discriminator (Sept 23 08:06 gotcha)
    questions = {}
    for qid, qtype, spec, _kind in selected:
        questions[qid] = {**spec, "type": qtype}
    started = time.time()
    res = call_jev(DOCTRINAL_STATE, questions)
    elapsed = time.time() - started
    if not res["ok"]:
        return {
            "round": round_idx,
            "status": "fail",
            "error": res["error"],
            "elapsed_s": round(elapsed, 3),
            "ts": datetime.now(timezone.utc).isoformat(),
        }
    payload = res["payload"]
    answers = payload.get("answers", {})
    verdicts = []
    for qid, _qtype, _spec, kind in selected:
        ans = answers.get(qid, {})
        p = extract_p(ans)
        # Durable fix: `score`-type questions return a bucket INDEX, not a
        # probability (observed 1.84-1.99 with 5 criteria), and nothing clamps
        # it. An unvalidated p silently corrupts mean_p and bedrock_hits.
        if p is not None and not (0.0 <= p <= 1.0):
            return {
                "round": round_idx,
                "status": "fail",
                "error": f"p out of range for {qid}: {p!r} (expected 0.0-1.0)",
                "elapsed_s": round(elapsed, 3),
                "ts": datetime.now(timezone.utc).isoformat(),
            }
        verdicts.append({
            "qid": qid,
            "kind": kind,
            "p": round(p, 4) if p is not None else None,
            "bedrock_hit": (p is not None and p >= 0.70),
        })
    mean_p = sum(v["p"] for v in verdicts if v["p"] is not None) / max(1, sum(1 for v in verdicts if v["p"] is not None))
    bedrock_count = sum(1 for v in verdicts if v["bedrock_hit"])
    return {
        "round": round_idx,
        "status": "ok",
        "ts": datetime.now(timezone.utc).isoformat(),
        "elapsed_s": round(elapsed, 3),
        "verdicts": verdicts,
        "mean_p": round(mean_p, 4),
        "bedrock_hits": bedrock_count,
        "model": payload.get("model", MODEL),
    }

# ============================================================================
# HISTORY + DRIFT
# ============================================================================
def load_history():
    if not HISTORY_PATH.exists():
        return []
    out = []
    with HISTORY_PATH.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return out

def append_history(round_obj):
    if round_obj.get("status") != "ok":
        return  # skip-on-fail (Sept 23 05:05 fix)
    with HISTORY_PATH.open("a") as f:
        f.write(json.dumps(round_obj) + "\n")

def per_question_stats(history):
    """Aggregate mean_p, hit-rate, stdev, n per qid across history."""
    stats = {}
    for r in history:
        for v in r.get("verdicts", []):
            qid = v["qid"]
            if v["p"] is None:
                continue
            s = stats.setdefault(qid, {"n": 0, "sum_p": 0.0, "sum_sq": 0.0,
                                       "hits": 0, "kind": v["kind"], "vals": []})
            s["n"] += 1
            s["sum_p"] += v["p"]
            s["sum_sq"] += v["p"] * v["p"]
            s["vals"].append(v["p"])
            if v["bedrock_hit"]:
                s["hits"] += 1
    out = {}
    for qid, s in stats.items():
        n = s["n"]
        mean = s["sum_p"] / n
        var = max(0.0, s["sum_sq"] / n - mean * mean)
        sd = math.sqrt(var)
        out[qid] = {
            "n": n,
            "kind": s["kind"],
            "mean_p": round(mean, 4),
            "stdev": round(sd, 4),
            "hits": s["hits"],
            "hit_rate": round(s["hits"] / n, 4),
            "distinct_values": len(set(s["vals"])),
            "min_p": round(min(s["vals"]), 4),
            "max_p": round(max(s["vals"]), 4),
        }
    return out

def drift_check(history, window=5):
    """Compute drift = last mean_p - median of prior (window) for each qid."""
    per_round = {}  # qid -> [(round, p)]
    for r in history:
        for v in r.get("verdicts", []):
            if v["p"] is not None:
                per_round.setdefault(v["qid"], []).append((r["round"], v["p"]))
    drifts = []
    for qid, samples in per_round.items():
        if len(samples) < window + 1:
            continue
        recent_p = samples[-1][1]
        prior_ps = [p for _r, p in samples[-(window + 1):-1]]
        prior_ps_sorted = sorted(prior_ps)
        median = prior_ps_sorted[len(prior_ps_sorted) // 2]
        delta = recent_p - median
        if abs(delta) > 0.05:
            drifts.append({"qid": qid, "recent_p": recent_p, "prior_median": median, "delta": round(delta, 4)})
    return drifts

# ============================================================================
# MAIN
# ============================================================================
def main():
    started = time.time()
    # Durable fix: derive the starting round from the highest EXISTING round
    # file, not from len(history). history.jsonl lives only on the NAS and has
    # been lost twice; when that happens the counter restarted at r001 and
    # shadowed every pre-wipe r001 forever.
    _existing = [int(m.group(1)) for p in SESSION_DIR.glob("continuous_r*.json")
                 if (m := re.match(r"continuous_r(\d+)\.json$", p.name))]
    round_idx = max(_existing, default=0) + 1
    rounds = []
    fails = []
    while time.time() - started < 55:  # 55s of 60s ceiling — leave 5s for shutdown
        r = run_round(round_idx)
        if r["status"] == "ok":
            rounds.append(r)
            append_history(r)
            print(f"r{round_idx:03d} OK  mean_p={r['mean_p']:.4f}  hits={r['bedrock_hits']}/{len(r['verdicts'])}  {r['elapsed_s']}s")
        else:
            fails.append(r)
            print(f"r{round_idx:03d} FAIL {r['error'][:80]}")
        round_idx += 1
        time.sleep(0.15)
    total_elapsed = time.time() - started
    history = load_history()
    per_q = per_question_stats(history)
    drifts = drift_check(history)
    grand_mean_p = (sum(r["mean_p"] for r in rounds) / len(rounds)) if rounds else 0.0
    total_verdicts = sum(len(r["verdicts"]) for r in rounds)
    total_bedrock = sum(r["bedrock_hits"] for r in rounds)
    print(f"\n=== Hourly summary ===")
    print(f"rounds_ok={len(rounds)}  fails={len(fails)}  total_verdicts={total_verdicts}")
    print(f"grand_mean_p={grand_mean_p:.4f}  bedrock_hits={total_bedrock}/{total_verdicts} ({100*total_bedrock/max(1,total_verdicts):.1f}%)")
    print(f"drift_events={len(drifts)}")
    print(f"elapsed={total_elapsed:.1f}s")
    # save the in-session rounds file
    out = {
        "session_ts": datetime.now(timezone.utc).isoformat(),
        "model": MODEL,
        # Durable fix: stamp the script's own md5 into every round file, not just
        # the report. When the harness changes, mean_p is not comparable and the
        # qid map is not stable — a drift table across versions measures the diff.
        "script_md5": hashlib.md5(Path(__file__).read_bytes()).hexdigest(),
        "first_round": round_idx - len(rounds) - len(fails) + 1,
        "doctrinal_state_keys": list(DOCTRINAL_STATE.keys()),
        "rounds": rounds,
        "fails": fails,
        "summary": {
            "rounds_ok": len(rounds),
            "fails": len(fails),
            "grand_mean_p": round(grand_mean_p, 4),
            "total_verdicts": total_verdicts,
            "bedrock_hits": total_bedrock,
            "bedrock_rate": round(total_bedrock / max(1, total_verdicts), 4),
            "drift_events": len(drifts),
            "elapsed_s": round(total_elapsed, 2),
            "per_question": per_q,
            "drift": drifts,
        },
    }
    out_path = SESSION_DIR / f"continuous_r{round_idx - 1:03d}.json"
    # actually use last round number
    last_round_num = max((r["round"] for r in rounds), default=0)
    out_path = SESSION_DIR / f"continuous_r{last_round_num:03d}.json"
    with out_path.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"saved: {out_path}")

if __name__ == "__main__":
    main()
