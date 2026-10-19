#!/usr/bin/env python3
"""Compute per-question mean_p delta vs R-085 reference."""
import json
from pathlib import Path
from collections import defaultdict

REF = {  # R-085 means from jev-quilt/jev_hourly_report.md
    "q01_cells_are_scars": 0.9684,
    "q02_witness_log_is_prediction": 0.9372,
    "q03_substrate_is_grown": 0.9700,
    "q04_oracle_is_heard": 0.9602,
    "q05_lenia_flows": 0.9551,
    "q07_eleven_opcodes": 0.9479,
    "q08_polyformalism_12_ports": 0.8800,
    "q10_quorum_meshing": 0.8595,
    "q17_canary_honesty": 0.7582,
    "q06_three_views": 0.2202,
    "q09_signal_chain": 0.6042,
    "q11_canon_gate_is_chord": 0.5916,
    "q12_witness_note_opcode": 0.5555,
    "q13_chain_dialing": 0.5984,
    "q14_canon_equals_speculation": 0.0650,
    "q15_twentyfour_ports": 0.1926,
    "q16_canonicity_score": 0.2230,
    "q18_address_is_data": 0.5885,
    "q19_pressure_cascade": 0.2604,
    "q20_wolffs_law": 0.5547,
    "q21_memory_sandbox": 0.2869,
    "q22_provenance_conflict": 0.3353,
}

sess_dir = Path("/tmp/jev_probe/run_r087")
by_qid = defaultdict(list)
for p in sorted(sess_dir.glob("continuous_r*.json")):
    d = json.loads(p.read_text())
    for qid, v in d.get("verdicts", {}).items():
        if isinstance(v, (int, float)):
            by_qid[qid].append(float(v))
        elif isinstance(v, dict) and "p" in v:
            by_qid[qid].append(float(v["p"]))

print("| qid | R-085 ref | R-087 now | n | Δ | %>=0.70 | flag |")
print("|---|---:|---:|---:|---:|---:|---|")
all_deltas = []
for qid in sorted(REF.keys()):
    ref_mean = REF[qid]
    vals = by_qid.get(qid, [])
    if not vals:
        print(f"| {qid} | {ref_mean:.4f} | (no samples) | 0 | — | — |  |")
        continue
    cur = sum(vals) / len(vals)
    n = len(vals)
    hit = sum(1 for v in vals if v >= 0.70) / n * 100
    delta = cur - ref_mean
    all_deltas.append((qid, ref_mean, cur, n, delta, hit))
    flag = "**DRIFT**" if abs(delta) > 0.05 else ""
    print(f"| {qid} | {ref_mean:.4f} | {cur:.4f} | {n} | {delta:+.4f} | {hit:.1f}% | {flag} |")

all_p = [v for vs in by_qid.values() for v in vs]
n_bedrock_hits = sum(1 for v in all_p if v >= 0.70)
print(f"\n**Grand mean_p**: {sum(all_p)/len(all_p):.4f}  (n={len(all_p)})")
print(f"**Bedrock hits (p≥0.70)**: {n_bedrock_hits}/{len(all_p)} = {n_bedrock_hits/len(all_p)*100:.1f}%")

print("\n**Drift events >0.05 (vs R-085 reference):**")
any_drift = False
for qid, ref_mean, cur, n, delta, hit in all_deltas:
    if abs(delta) > 0.05:
        any_drift = True
        print(f"  - {qid}: {ref_mean:.4f} → {cur:.4f} (Δ {delta:+.4f})")
if not any_drift:
    print("  (none — substrate stable to ±0.05)")

print(f"\n**Max abs drift**: {max(abs(d[4]) for d in all_deltas):.4f}")
