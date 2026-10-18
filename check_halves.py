import json, glob
from collections import defaultdict

# Compare each of the 22 questions' h1 vs h2 mean to see if any specific qid is driving the drop
files = sorted(glob.glob("jev_sessions/continuous_r*.json"))
h = len(files)//2
per_q_h1 = defaultdict(list)
per_q_h2 = defaultdict(list)
for i,f in enumerate(files):
    rec = json.load(open(f))
    if rec.get("status") != "ok": continue
    bucket = per_q_h1 if i < h else per_q_h2
    for qid, p in rec["verdicts"].items():
        bucket[qid].append(p)

print(f"{'qid':<40} {'h1':>7} {'h2':>7} {'delta':>7} {'flag':>5}")
flagged = []
for qid in sorted(set(list(per_q_h1.keys()) + list(per_q_h2.keys()))):
    h1 = per_q_h1.get(qid, [])
    h2 = per_q_h2.get(qid, [])
    if not h1 or not h2: continue
    m1 = sum(h1)/len(h1)
    m2 = sum(h2)/len(h2)
    d = m2 - m1
    flag = "***" if abs(d) > 0.05 else ""
    print(f"{qid:<40} {m1:>7.4f} {m2:>7.4f} {d:>+7.4f} {flag:>5}")
    if abs(d) > 0.05: flagged.append(qid)

print(f"\n{len(flagged)} questions drifted >0.05 between halves")
