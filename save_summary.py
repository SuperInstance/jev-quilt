import json, glob
from collections import defaultdict
from datetime import datetime, timezone

DIR = "jev_sessions"
files = sorted(glob.glob(f"{DIR}/continuous_r*.json"))
per_q = defaultdict(list)
for f in files:
    rec = json.load(open(f))
    if rec.get("status") == "ok":
        for qid, p in rec.get("verdicts", {}).items():
            per_q[qid].append(p)

REF_84W = {
    "q01_cells_are_scars": 0.9685, "q02_witness_log_is_prediction": 0.9368,
    "q03_substrate_is_grown": 0.9700, "q04_oracle_is_heard": 0.9603,
    "q05_lenia_flows": 0.9552, "q07_eleven_opcodes": 0.9487,
    "q08_polyformalism_12_ports": 0.8783, "q17_canary_honesty": 0.7587,
    "q10_quorum_meshing": 0.8597,
}

per_q_stats = {}
for qid, vs in per_q.items():
    per_q_stats[qid] = {
        "n": len(vs), "mean": round(sum(vs)/len(vs),4),
        "min": min(vs), "max": max(vs),
        "pct_ge_0.70": round(sum(1 for v in vs if v>=0.70)/len(vs)*100,1),
        "first": vs[0], "last": vs[-1],
    }

all_p = [v for vs in per_q.values() for v in vs]
bedrock = ["q01_cells_are_scars","q02_witness_log_is_prediction","q03_substrate_is_grown",
           "q04_oracle_is_heard","q05_lenia_flows","q07_eleven_opcodes","q08_polyformalism_12_ports"]
b_all = [v for q in bedrock for v in per_q.get(q, [])]

half = len(files)//2
h1, h2 = [], []
for i,f in enumerate(files):
    rec = json.load(open(f))
    if rec.get("status") == "ok":
        vs = list(rec["verdicts"].values())
        (h1 if i < half else h2).extend(vs)

drift = {}
for qid, ref in REF_84W.items():
    if qid in per_q:
        cur = sum(per_q[qid])/len(per_q[qid])
        drift[qid] = {"ref_84w": ref, "current": round(cur,4), "delta": round(cur-ref,4)}

summary = {
    "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "session_label": "R-085 (5th in 24h after 82w/83w/84w)",
    "rounds_ok": sum(1 for f in files if json.load(open(f)).get("status")=="ok"),
    "rounds_total": len(files),
    "n_verdicts": len(all_p),
    "grand_mean_p": round(sum(all_p)/len(all_p),4),
    "bedrock_aggregate": {
        "n": len(b_all),
        "mean": round(sum(b_all)/len(b_all),4),
        "pct_ge_0.70": round(sum(1 for v in b_all if v>=0.70)/len(b_all)*100,1),
    },
    "questions_at_or_above_0.70_mean": sorted([qid for qid,s in per_q_stats.items() if s["mean"]>=0.70]),
    "questions_below_0.70_mean": sorted([qid for qid,s in per_q_stats.items() if s["mean"]<0.70]),
    "per_q": per_q_stats,
    "drift_vs_84w": drift,
    "n_questions_drifted_gt_0.05": sum(1 for v in drift.values() if abs(v["delta"])>0.05),
    "within_session_halves": {
        "h1_mean": round(sum(h1)/len(h1),4),
        "h1_n": len(h1),
        "h2_mean": round(sum(h2)/len(h2),4),
        "h2_n": len(h2),
        "delta": round((sum(h2)/len(h2)) - (sum(h1)/len(h1)),4),
    },
}
open("summary.json","w").write(json.dumps(summary, indent=2, sort_keys=True))
print("Wrote summary.json")
print(f"Grand mean_p: {summary['grand_mean_p']}")
print(f"Bedrock mean: {summary['bedrock_aggregate']['mean']}, %>=0.70: {summary['bedrock_aggregate']['pct_ge_0.70']}%")
print(f"Drift >0.05: {summary['n_questions_drifted_gt_0.05']}")
