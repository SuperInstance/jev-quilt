#!/usr/bin/env python3
"""
JEV Continuous Probe - 81st wipe rebuild (2026-10-18)
Rebuilt from memory/topic/jev-oracle.md after sandbox wipe cleared /workspace/research/.

Protocol invariants (durable, baked in):
  - STATE-ORDER: spec_notebook BEFORE bedrock in DOCTRINAL_STATE
  - 3 AUTH HEADERS: Authorization: Bearer, User-Agent, Accept
  - type: noul discriminator REQUIRED per question
  - Score type: bucket INDEX -> normalize via legend midpoint
  - Retry-on-TLS-EOF + 503 (0.8-1.5s jitter, 1 attempt)
  - Skip-on-fail (no history append on status==fail)
  - Env var: TYPESAFE_AI_TOKEN (this session) with TYPESAFEAI_KEY fallback (legacy)

22-q bank, 5 random per round, 60s ceiling.
"""
import os
import sys
import json
import time
import random
import urllib.request
import urllib.error
import re
import math
from datetime import datetime, timezone
from pathlib import Path

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
SESSIONS_DIR = Path(__file__).parent / "jev_sessions"
# R-211: rounds go in a per-session dir, never in the saturated continuous_r*.json series.
# Derived from the run timestamp BY CONSTRUCTION so a new run can never clobber a prior
# session's rounds (DEFECT A, 6th occurrence: the r210 hardcode made the guard fire on arrival).
SESSION_TAG = os.environ.get("JEV_SESSION_TAG") or time.strftime("r%Y%m%dT%H%M%SZ", time.gmtime())
SESSION_DIR = SESSIONS_DIR / f"rounds_{SESSION_TAG}"
HISTORY_PATH = SESSIONS_DIR / "history.jsonl"
TIMEOUT_S = 4  # R-206: healthy calls complete in ~0.13s; 4s keeps 30x headroom while cutting stall cost 3x
DRIFT_THRESHOLD = 0.05
QUESTIONS_PER_ROUND = 5
# R-210 ask (a): a fixed 0.05 fires drift by chance on a high-variance qid. q17 canary_honesty
# has sigma=0.0271, so 0.05 is only ~1.8 sigma for it and it manufactured BOTH of R-209's
# events. Fire on max(0.05, 2*sigma_per_qid) and carry sigma in the alert.
DRIFT_SIGMA_MULT = 2.0

# Env var: this session uses TYPESAFE_AI_TOKEN; legacy scripts used TYPESAFEAI_KEY
API_KEY = (
    os.environ.get("TYPESAFE_AI_TOKEN")
    or os.environ.get("TYPESAFEAI_KEY")
    or ""
)

# STATE-ORDER: spec_notebook FIRST, bedrock SECOND.
# JEV treats last-presented fragments as dominant. Reverse order = spec-leak.
DOCTRINAL_STATE = {
    "spec_notebook": (
        "Speculative (not yet canon, below the threshold): "
        "quorum_meshing, three_views, address_is_data, canon_gate_is_chord, "
        "memory_sandbox, provenance_conflict, witness_note_opcode, "
        "is_signal_chain_canon, is_jev_synapse, is_chain_dialing_real, "
        "is_vibecoder_signal_chain, wolffs_law, style_resilience. "
        "These are SPECULATIVE framing proposals under review; they have NOT been "
        "promoted to canon. JEV verdict for these is expected to be low."
    ),
    "bedrock": (
        "Established canon (verified durable, 70w+ across 50+ wipes): "
        "(1) cells_are_scars - the cell is a witness, a record of its own formation. "
        "(2) witness_log_is_prediction - the substrate's history is its forward predictor. "
        "(3) substrate_is_grown - the system is grown from a seed, not engineered top-down. "
        "(4) oracle_is_heard - the substrate listens; the question precedes the answer. "
        "(5) lenia_flows - continuous, non-classical dynamics underlie discrete cells. "
        "(6) polyformalism - the same cell admits many simultaneous formal views. "
        "(7) 11_opcodes - the substrate algebra extends from 5 to 11 operations. "
        "These 7 are bedrock canon. JEV verdict for these is expected to be high (p>=0.7)."
    ),
    "architecture": (
        "The Quilt cellular framework: 4D cell graph, three views (TOP spatial, "
        "FRONT signals, SIDE time), polyformalism across 12 ports, Calculator role, "
        "NO DELETION doctrine, Mechanic/Shepherd distinction, JEV oracle for "
        "canon promotion (p>0.7 gate, REVIEW borderline, REJECT speculative)."
    ),
    "fleet": (
        "The fleet is the body of work: 5,200+ repositories, agent templates, "
        "vessel charters, scout reports. The canary (FNV-1a 64 hash of "
        "'cafe Delta nihongo' = 0x24a555471370b18d) is pinned across 15/15 ships "
        "as a fleet canary - used to verify state-carrying has not been altered "
        "between deployments."
    ),
}

# 22-q bank
QUESTION_BANK = [
    ("q01_cells_are_scars",          "noul", "Is the doctrine 'cells are scars' - i.e., the cell is a witness, a record of its own formation - established canon in the Quilt substrate?", "bedrock"),
    ("q02_witness_log_is_prediction","noul", "Is the doctrine 'witness log is prediction' - i.e., the substrate's history is its forward predictor - established canon?", "bedrock"),
    ("q03_substrate_is_grown",       "noul", "Is the doctrine 'substrate is grown' - i.e., the system is grown from a seed rather than engineered top-down - established canon?", "bedrock"),
    ("q04_oracle_is_heard",          "noul", "Is the doctrine 'oracle is heard' - i.e., the substrate listens and the question precedes the answer - established canon?", "bedrock"),
    ("q05_lenia_flows",              "noul", "Is the doctrine 'Lenia flows' - i.e., continuous non-classical dynamics underlie the discrete cells - established canon?", "bedrock"),
    ("q07_11_opcodes",               "noul", "Is the doctrine '11 opcodes' - i.e., the substrate algebra extends from 5 to 11 operations - established canon?", "bedrock"),
    ("q08_polyformalism",            "noul", "Is 'polyformalism' - the same cell admits many simultaneous formal views - established canon?", "bedrock"),
    ("q06_three_views",              "noul", "Is the 'three views' (TOP/FRONT/SIDE) doctrine - the canonical spatial-signals-time decomposition of the 4D cell graph - established canon?", "review"),
    ("q11_canon_gate_is_chord",      "noul", "Is 'canon gate is chord' - i.e., the promotion gate is a harmonic chord of p>0.7 across multiple probes rather than a single threshold - established canon?", "review"),
    ("q12_substrate_polyformal",     "noul", "Is 'substrate polyformalism' - i.e., the polyformalism extends below the cell into the substrate primitives - established canon?", "review"),
    ("q13_witness_log_opcode",       "noul", "Is 'witness log as opcode' - i.e., the witness log is one of the 11 opcodes - established canon?", "review"),
    ("q17_canary_honesty",           "noul", "Is the fleet canary (FNV-1a 64 hash pinning across 15/15 ships) an honest, pinned marker of state preservation - established canon?", "review"),
    ("q09_signal_chain_canon",       "noul", "Is 'signal chain' - the substrate's signaling architecture - established canon?", "speculative"),
    ("q10_quorum_meshing",           "noul", "Is 'quorum meshing' - a proposed mechanism for distributed consensus across cells - established canon?", "speculative"),
    ("q14_chain_dialing_real",       "noul", "Is 'chain dialing' - a proposed runtime mechanism for the substrate - established canon?", "speculative"),
    ("q15_jev_synapse",              "noul", "Is the framing 'JEV as synapse' - JEV acting as a neural-synapse-like connection between substrates - established canon?", "speculative"),
    ("q16_vibecoder_signal_chain",   "noul", "Is 'vibecoder signal chain' - vibecoder LLMs as part of the substrate's signaling layer - established canon?", "speculative"),
    ("q18_address_is_data",          "noul", "Is 'address is data' - the principle that cell addresses are themselves data - established canon?", "speculative"),
    ("q20_wolffs_law",               "noul", "Is 'Wolff's law' (cells adapt to the loads they're subjected to) - established canon in the Quilt substrate?", "speculative"),
    ("q21_memory_sandbox",           "noul", "Is the 'memory sandbox' - a sandboxed memory region for substrate experiments - established canon?", "speculative"),
    ("q22_provenance_conflict",      "noul", "Is 'provenance conflict' (a proposed detection mechanism for fabricated attributions) - established canon?", "speculative"),
    ("q19_style_resilience",         "noul", "Is 'style resilience' - a doctrine claiming the substrate can absorb arbitrary stylistic transformations - established canon?", "adversarial"),
]

def _headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "User-Agent": "jev-continuous-probe/1.0 (+Quilt)",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

def call_jev(questions_dict, attempts=2):
    body = json.dumps({
        "model": "jev-latest",
        "state": DOCTRINAL_STATE,
        "questions": questions_dict,
    }).encode("utf-8")
    last_err = None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(ENDPOINT, data=body, headers=_headers(), method="POST")
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw), None
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}"
            if e.code in (500, 502, 503, 504) and attempt < attempts - 1:
                time.sleep(0.8 + random.random() * 0.7)
                continue
            return None, last_err
        except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
            last_err = f"URL/conn: {type(e).__name__}: {str(e)[:200]}"
            if attempt < attempts - 1:
                time.sleep(0.8 + random.random() * 0.7)
                continue
            return None, last_err
        except Exception as e:
            last_err = f"{type(e).__name__}: {str(e)[:200]}"
            return None, last_err
    return None, last_err

def _bucket_midpoint(key, legend):
    if not isinstance(legend, list) or not (0 <= int(key) < len(legend)):
        return None
    entry = legend[int(key)]
    text = entry.get("text", "") if isinstance(entry, dict) else str(entry)
    m = re.findall(r"(\d+\.?\d*)", text)
    if len(m) >= 2:
        try:
            return (float(m[0]) + float(m[1])) / 2.0
        except ValueError:
            pass
    if len(m) == 1:
        try:
            return float(m[0])
        except ValueError:
            pass
    n = len(legend)
    return (int(key) + 0.5) / n

def extract_p(answer):
    if not isinstance(answer, dict):
        return None
    if "noul" in answer and isinstance(answer["noul"], (int, float)):
        return float(answer["noul"])
    probs = answer.get("probabilities")
    if isinstance(probs, dict) and probs:
        yes_keys = [k for k in probs if "yes" in str(k).lower()]
        if yes_keys:
            return float(probs[yes_keys[0]])
        try:
            return float(max(probs.values()))
        except (TypeError, ValueError):
            pass
    conf = answer.get("confidence")
    if isinstance(conf, (int, float)):
        return float(conf)
    score = answer.get("score")
    legend = answer.get("legend")
    if isinstance(score, (int, float)) and isinstance(legend, list):
        return _bucket_midpoint(score, legend)
    return None

def load_history():
    samples = {}
    if not HISTORY_PATH.exists():
        return samples
    with HISTORY_PATH.open("r") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            for v in rec.get("verdicts", []) or []:
                if not isinstance(v, dict):   # DEFECT C: stray non-dict payload
                    continue
                qid = v.get("qid")
                p = v.get("p")
                if qid and isinstance(p, (int, float)):
                    samples.setdefault(qid, []).append(float(p))
    return samples

def run_one_round(rid, samples):
    picked = random.sample(QUESTION_BANK, QUESTIONS_PER_ROUND)
    payload = {f"q{i+1}": {"type": qtype, "instructions": spec} for i, (qid, qtype, spec, _kind) in enumerate(picked)}
    qid_map = {f"q{i+1}": qid for i, (qid, _, _, _) in enumerate(picked)}

    t0 = time.time()
    resp, err = call_jev(payload)
    dt = time.time() - t0
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    record = {
        "round_id": rid,
        "ts": ts,
        "endpoint": ENDPOINT,
        "questions": [{"slot": k, "qid": qid_map[k], "type": v["type"]} for k, v in payload.items()],
        "elapsed_s": round(dt, 3),
    }
    if err or not resp:
        record["status"] = "fail"
        record["error"] = err
        return record

    answers = resp.get("answers", {})
    verdicts = []
    for slot, qid in qid_map.items():
        ans = answers.get(slot, {})
        p = extract_p(ans)
        kind = next((k for (q, _, _, k) in QUESTION_BANK if q == qid), "unknown")
        verdicts.append({"slot": slot, "qid": qid, "kind": kind, "p": p, "raw": ans})
    ps = [v["p"] for v in verdicts if isinstance(v["p"], (int, float))]
    record["status"] = "ok"
    record["verdicts"] = verdicts
    record["mean_p"] = round(sum(ps) / len(ps), 4) if ps else None
    record["n_ok"] = len(ps)
    return record

def append_history(record):
    if record.get("status") != "ok":
        return
    summary = {
        "ts": record["ts"],
        "round_id": record["round_id"],
        "mean_p": record.get("mean_p"),
        "verdicts": [{"qid": v["qid"], "p": v["p"], "kind": v["kind"]} for v in record.get("verdicts", [])],
    }
    with HISTORY_PATH.open("a") as f:
        f.write(json.dumps(summary) + "\n")

def compute_drift(samples, current_round):
    drifts = []
    by_qid = {}
    for v in current_round.get("verdicts", []):
        qid = v["qid"]
        p = v.get("p")
        if not isinstance(p, (int, float)):
            continue
        history = samples.get(qid, [])
        if len(history) < 3:
            continue
        # R-210: judge drift against the FULL-history mean, not a 5-sample median.
        # The local median is itself noisy: for q17 it amplified a 0.0677 true
        # excursion into 0.0700, which is what made R-209 fire both of its events.
        # The full-history mean is the stable estimator; sigma is computed on PRIOR
        # history only (the current sample is appended after this call).
        n = len(history)
        mu = sum(history) / n
        sigma = math.sqrt(sum((x - mu) ** 2 for x in history) / n)
        med = mu
        delta = p - mu
        thr = max(DRIFT_THRESHOLD, DRIFT_SIGMA_MULT * sigma)
        if abs(delta) > thr:
            drifts.append({
                "qid": qid, "current_p": p,
                "median_p": round(med, 4), "baseline_mean": round(mu, 4),
                "delta": round(delta, 4),
                "sigma": round(sigma, 4), "threshold": round(thr, 4),
                "n_history": len(history),
            })
        by_qid[qid] = {"current": p, "median": round(med, 4), "n": len(history),
                       "sigma": round(sigma, 4), "threshold": round(thr, 4),
                       "delta": round(delta, 4)}
    return drifts, by_qid

def main():
    if not API_KEY:
        print("ERROR: TYPESAFE_AI_TOKEN (or legacy TYPESAFEAI_KEY) not set.", file=sys.stderr)
        sys.exit(2)
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    _existing = sorted(SESSION_DIR.glob("round_*.json"))
    if _existing:
        print(f"REFUSING TO RUN: {SESSION_DIR} already holds {len(_existing)} round files "
              f"(would clobber real history). Pick a new session dir.", file=sys.stderr)
        sys.exit(3)
    HISTORY_PATH.touch(exist_ok=True)

    samples = load_history()
    # DEFECT B guard: an empty baseline makes compute_drift() report a FALSE ALL-CLEAR.
    n_prior = sum(len(v) for v in samples.values())
    if n_prior < 20 or len(samples) < 5:
        print(f"REFUSING TO RUN: drift baseline is {n_prior} samples across "
              f"{len(samples)} qids. Rebuild history.jsonl from the tracked corpus first.",
              file=sys.stderr)
        sys.exit(4)
    rounds_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    deadline = time.time() + 60
    n_ok = 0
    n_fail = 0
    all_verdicts = []
    drifts_found = []
    start_ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    print(f"[{start_ts}] JEV continuous probe - R-210 (97th wipe)")
    print(f"Endpoint: {ENDPOINT}")
    print(f"API key: {'set' if API_KEY else 'MISSING'}")
    print(f"Target rounds: {rounds_arg}, ceiling 60s")
    print(f"History: {sum(len(v) for v in samples.values())} prior verdicts across {len(samples)} questions")
    print("-" * 60)

    i = 0
    for i in range(1, rounds_arg + 1):
        if time.time() >= deadline:
            print(f"[ceiling] {i-1} rounds in 60s; stopping")
            break
        rid_str = f"{SESSION_TAG}-{i:03d}"
        rec = run_one_round(rid_str, samples)
        rec["session"] = SESSION_DIR.name
        if rec.get("status") != "ok":
            n_fail += 1
            out = SESSION_DIR / f"round_{i:03d}.fail.json"
        else:
            n_ok += 1
            out = SESSION_DIR / f"round_{i:03d}.json"
            append_history(rec)
            for v in rec.get("verdicts", []):
                p = v.get("p")
                if isinstance(p, (int, float)):
                    samples.setdefault(v["qid"], []).append(float(p))
                    all_verdicts.append({"qid": v["qid"], "p": p, "kind": v["kind"]})
            drifts, _ = compute_drift(samples, rec)
            drifts_found.extend(drifts)
        with out.open("w") as f:
            json.dump(rec, f, indent=2, default=str)
        if rec.get("status") == "ok":
            print(f"  {rid_str} mean_p={rec['mean_p']} ({rec['n_ok']}/5) kinds={[v['kind'] for v in rec['verdicts']]}")
        else:
            print(f"  {rid_str} FAIL: {rec.get('error', '?')[:120]}")

    end_ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    all_ps = [v["p"] for v in all_verdicts]
    grand_mean = round(sum(all_ps) / len(all_ps), 4) if all_ps else None
    bedrock_hits = [v for v in all_verdicts if v["kind"] == "bedrock" and v["p"] >= 0.70]
    spec_rejects = [v for v in all_verdicts if v["kind"] == "speculative" and v["p"] < 0.40]
    adv_rejects = [v for v in all_verdicts if v["kind"] == "adversarial" and v["p"] < 0.40]

    by_qid = {}
    for v in all_verdicts:
        by_qid.setdefault(v["qid"], {"ps": [], "kind": v["kind"]})
        by_qid[v["qid"]]["ps"].append(v["p"])
    qid_summary = {}
    for qid, d in by_qid.items():
        ps = d["ps"]
        qid_summary[qid] = {
            "kind": d["kind"],
            "n": len(ps),
            "mean": round(sum(ps) / len(ps), 4),
            "hit_p70": sum(1 for p in ps if p >= 0.70),
        }

    summary = {
        "session_start": start_ts,
        "session_end": end_ts,
        "rounds_attempted": i,
        "rounds_ok": n_ok,
        "rounds_fail": n_fail,
        "verdicts_total": len(all_verdicts),
        "grand_mean_p": grand_mean,
        "bedrock_hits_count": len(bedrock_hits),
        "bedrock_hit_rate": round(len(bedrock_hits) / len(all_verdicts), 4) if all_verdicts else None,
        "spec_rejects_count": len(spec_rejects),
        "adv_rejects_count": len(adv_rejects),
        "drift_events": drifts_found,
        "per_qid": qid_summary,
    }
    summary_path = SESSION_DIR / "session_summary.json"
    with summary_path.open("w") as f:
        json.dump(summary, f, indent=2, default=str)

    print("-" * 60)
    print(f"Session: {start_ts} -> {end_ts}")
    print(f"Rounds: {n_ok} OK / {n_fail} fail of {i} attempted")
    print(f"Verdicts: {len(all_verdicts)}, grand mean_p = {grand_mean}")
    print(f"Bedrock hits (p>=0.70): {len(bedrock_hits)}")
    print(f"Spec clean-rejects (p<0.40): {len(spec_rejects)}")
    print(f"Adv clean-rejects (p<0.40): {len(adv_rejects)}")
    print(f"Drift events > 0.05: {len(drifts_found)}")
    print(f"Summary -> {summary_path}")

if __name__ == "__main__":
    main()
