#!/usr/bin/env python3
"""
analyze_jev.py — post-hoc analyzer for JEV probe sessions.
Produces cross-question stats: bedrock/review/speculative/adversarial bands + grand mean_p.

Usage:
  python3 continuous/analyze_jev.py jev_sessions/ [--out report.md]

Must stay in sync with QUESTION_BANK from jev_continuous_probe.py.
"""

import os, sys, json, argparse, statistics
from pathlib import Path
from collections import defaultdict

QUESTION_KIND = {
    "q01_cells_are_scars": "bedrock",
    "q02_witness_log_is_prediction": "bedrock",
    "q03_substrate_is_grown": "bedrock",
    "q04_oracle_is_heard": "bedrock",
    "q05_lenia_flows": "bedrock",
    "q07_eleven_opcodes": "bedrock",
    "q08_polyformalism_12_ports": "bedrock",
    "q17_canary_honesty": "review",
    "q06_three_views": "speculative",
    "q09_signal_chain": "speculative",
    "q10_quorum_meshing": "review",
    "q11_canon_gate_is_chord": "speculative",
    "q12_witness_note_opcode": "speculative",
    "q13_chain_dialing": "speculative",
    "q18_address_is_data": "review",
    "q16_canonicity_score": "review",
    "q19_pressure_cascade": "review",
    "q20_wolffs_law": "review",
    "q21_memory_sandbox": "review",
    "q22_provenance_conflict": "review",
    "q14_canon_equals_speculation": "adversarial",
    "q15_twentyfour_ports": "adversarial",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions_dir")
    ap.add_argument("--out", default="jev_hourly_report.md")
    args = ap.parse_args()

    sess_dir = Path(args.sessions_dir)
    rounds_ok = sorted(sess_dir.glob("continuous_r*.json"))
    if not rounds_ok:
        print(f"No round files in {sess_dir}", file=sys.stderr)
        sys.exit(1)

    per_q = defaultdict(list)
    rounds_total = len(rounds_ok)
    verdicts_total = 0
    for path in rounds_ok:
        rec = json.loads(path.read_text())
        if rec.get("status") != "ok":
            continue
        r = rec["round"]
        for qid, p in rec.get("verdicts", {}).items():
            per_q[qid].append((r, p))
            verdicts_total += 1

    grand_p = [p for qid, lst in per_q.items() for _, p in lst]
    grand_mean = statistics.mean(grand_p) if grand_p else 0.0

    bedrock_hits = 0
    speculative_clean_reject = 0
    adversarial_clean_reject = 0
    review_band = 0

    lines = []
    lines.append(f"# JEV Hourly Report — {sess_dir.name}")
    lines.append(f"\nRounds: {rounds_total} ok | Verdicts: {verdicts_total} | Grand mean_p: **{grand_mean:.4f}**")
    lines.append(f"\n## Bedrock canon ({sum(1 for k in QUESTION_KIND.values() if k=='bedrock')} questions)")
    lines.append("| qid | mean | n | hit_rate | kind |")
    lines.append("|---|---|---|---|---|")
    for qid, kind in sorted(QUESTION_KIND.items(), key=lambda x: x[1]):
        if kind != "bedrock":
            continue
        samples = per_q.get(qid, [])
        if not samples:
            continue
        ps = [p for _, p in samples]
        mean = statistics.mean(ps)
        hits = sum(1 for p in ps if p >= 0.70)
        hr = hits / len(ps)
        marker = "✓" if hr >= 0.99 and mean >= 0.70 else "✗"
        lines.append(f"| {qid} | {mean:.4f} | {len(ps)} | {hr*100:.1f}% | bedrock {marker} |")
        if hr >= 0.99 and mean >= 0.70:
            bedrock_hits += 1

    lines.append(f"\n## Speculative (must clean-reject)")
    lines.append("| qid | mean | n | hit_rate | verdict |")
    lines.append("|---|---|---|---|---|")
    for qid, kind in sorted(QUESTION_KIND.items(), key=lambda x: x[1]):
        if kind != "speculative":
            continue
        samples = per_q.get(qid, [])
        if not samples:
            continue
        ps = [p for _, p in samples]
        mean = statistics.mean(ps)
        hits = sum(1 for p in ps if p >= 0.70)
        hr = hits / len(ps)
        verdict = "✓ clean-reject" if hr == 0.0 else f"✗ {hr*100:.0f}% leak"
        lines.append(f"| {qid} | {mean:.4f} | {len(ps)} | {hr*100:.1f}% | {verdict} |")
        if hr == 0.0:
            speculative_clean_reject += 1

    lines.append(f"\n## Adversarial (must clean-reject)")
    lines.append("| qid | mean | n | verdict |")
    lines.append("|---|---|---|---|")
    for qid, kind in sorted(QUESTION_KIND.items(), key=lambda x: x[1]):
        if kind != "adversarial":
            continue
        samples = per_q.get(qid, [])
        if not samples:
            continue
        ps = [p for _, p in samples]
        mean = statistics.mean(ps)
        hits = sum(1 for p in ps if p >= 0.70)
        hr = hits / len(ps)
        verdict = "✓ clean-reject" if hr == 0.0 and mean < 0.20 else f"✗ leak ({hr*100:.0f}%)"
        lines.append(f"| {qid} | {mean:.4f} | {len(ps)} | {verdict} |")
        if hr == 0.0 and mean < 0.20:
            adversarial_clean_reject += 1

    lines.append(f"\n## Review band (borderline)")
    lines.append("| qid | mean | n | hit_rate |")
    lines.append("|---|---|---|---|")
    for qid, kind in sorted(QUESTION_KIND.items(), key=lambda x: x[1]):
        if kind != "review":
            continue
        samples = per_q.get(qid, [])
        if not samples:
            continue
        ps = [p for _, p in samples]
        mean = statistics.mean(ps)
        hits = sum(1 for p in ps if p >= 0.70)
        hr = hits / len(ps)
        lines.append(f"| {qid} | {mean:.4f} | {len(ps)} | {hr*100:.1f}% |")
        if 0.30 <= mean <= 0.70:
            review_band += 1

    lines.append(f"\n## Summary")
    lines.append(f"- Bedrock @ 100% hit-rate: **{bedrock_hits} / 7**")
    lines.append(f"- Speculative clean-reject: **{speculative_clean_reject} / 5**")
    lines.append(f"- Adversarial clean-reject: **{adversarial_clean_reject} / 2**")
    lines.append(f"- Review band coherent: **{review_band} / 8**")
    lines.append(f"- Grand mean_p: **{grand_mean:.4f}**")

    out_path = Path(args.out)
    out_path.write_text("\n".join(lines) + "\n")
    print(f"Wrote {out_path} ({len(lines)} lines)")
    print(f"Bedrock: {bedrock_hits}/7 | Spec-reject: {speculative_clean_reject}/5 | Adv-reject: {adversarial_clean_reject}/2 | mean_p: {grand_mean:.4f}")

if __name__ == "__main__":
    main()
