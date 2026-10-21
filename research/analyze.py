import json, os, glob
from collections import defaultdict

DIR = "jev_sessions"
files = sorted(glob.glob(f"{DIR}/continuous_r*.json"))
print(f"Loaded {len(files)} rounds")

per_q = defaultdict(list)
bedrock_hits = defaultdict(int)
q_questions = {}
for f in files:
    rec = json.load(open(f))
    if rec.get("status") != "ok":
        continue
    for qid, p in rec.get("verdicts", {}).items():
        per_q[qid].append(p)
        if p >= 0.70:
            bedrock_hits[qid] += 1

# Bedrock qids
bedrock = ["q01_cells_are_scars","q02_witness_log_is_prediction","q03_substrate_is_grown",
           "q04_oracle_is_heard","q05_lenia_flows","q07_eleven_opcodes","q08_polyformalism_12_ports"]

print("\n=== Per-question stats (sorted) ===")
print(f"{'qid':<40} {'n':>4} {'mean_p':>8} {'min':>6} {'max':>6} {'%>=0.7':>7} {'first':>7} {'last':>7}")
rows = []
for qid in sorted(per_q):
    vs = per_q[qid]
    mean = sum(vs)/len(vs)
    hi = sum(1 for v in vs if v>=0.70)
    rows.append((qid, len(vs), mean, min(vs), max(vs), hi/len(vs)*100, vs[0], vs[-1]))

for qid, n, mean, lo, hi, pct, first, last in rows:
    print(f"{qid:<40} {n:>4} {mean:>8.4f} {lo:>6.3f} {hi:>6.3f} {pct:>6.1f}% {first:>7.3f} {last:>7.3f}")

# Grand mean
all_p = [v for vs in per_q.values() for v in vs]
print(f"\nGrand mean_p: {sum(all_p)/len(all_p):.4f} (n={len(all_p)})")

# 7 bedrock stats
print("\n=== 7 bedrock aggregate ===")
b_all = [v for q in bedrock for v in per_q.get(q, [])]
print(f"  n={len(b_all)}, mean={sum(b_all)/len(b_all):.4f}, %>=0.70={sum(1 for v in b_all if v>=0.70)/len(b_all)*100:.1f}%")

# Drift vs 84w reference (from memory: 84w = the 14:01Z session)
REF_84W = {
    "q01_cells_are_scars": 0.9685,
    "q02_witness_log_is_prediction": 0.9368,
    "q03_substrate_is_grown": 0.9700,
    "q04_oracle_is_heard": 0.9603,
    "q05_lenia_flows": 0.9552,
    "q07_eleven_opcodes": 0.9487,
    "q08_polyformalism_12_ports": 0.8783,
    "q17_canary_honesty": 0.7587,
    "q10_quorum_meshing": 0.8597,
}
print("\n=== Drift vs 84w reference (>|0.05| flagged) ===")
flagged = []
for qid, ref in REF_84W.items():
    if qid not in per_q: continue
    cur = sum(per_q[qid])/len(per_q[qid])
    delta = cur - ref
    flag = "***" if abs(delta)>0.05 else ""
    print(f"  {qid:<40} {ref:.4f} -> {cur:.4f}  Δ={delta:+.4f} {flag}")
    if abs(delta)>0.05: flagged.append((qid, ref, cur, delta))

print(f"\n{len(flagged)} questions drifted >0.05 vs 84w")

# Within-session halves
half = len(files)//2
h1, h2 = [], []
for i,f in enumerate(files):
    rec = json.load(open(f))
    if rec.get("status") != "ok": continue
    vs = list(rec.get("verdicts", {}).values())
    (h1 if i < half else h2).extend(vs)
print(f"\nWithin-session halves: h1 mean={sum(h1)/len(h1):.4f} (n={len(h1)}), h2 mean={sum(h2)/len(h2):.4f} (n={len(h2)})")

# Bedrock hit @ 100%
print("\n=== Bedrock hit @ >=0.70 ===")
for q in bedrock:
    if q in per_q:
        n = len(per_q[q])
        hi = sum(1 for v in per_q[q] if v>=0.70)
        print(f"  {q:<40} {hi}/{n} = {hi/n*100:.1f}%")

# q17 and q10 separate
for q in ["q17_canary_honesty","q10_quorum_meshing"]:
    if q in per_q:
        vs = per_q[q]
        print(f"\n  {q}: n={len(vs)}, mean={sum(vs)/len(vs):.4f}, min={min(vs):.3f}, max={max(vs):.3f}, %>=0.70={sum(1 for v in vs if v>=0.70)/len(vs)*100:.1f}%")

# All questions with mean >=0.70
print("\n=== All questions with mean_p >= 0.70 in this session ===")
for qid, n, mean, lo, hi, pct, first, last in rows:
    if mean >= 0.70:
        print(f"  {qid:<40} mean={mean:.4f}  n={n}")
