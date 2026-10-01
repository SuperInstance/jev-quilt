# JEV Hourly Report — 2026-10-01 23:02Z (50th-wipe)

**Run tag**: `runs/20261001_2302`
**Sandbox state**: 50th full wipe. `/workspace/` is NAS quota-blocked (`-122 close`),
so the probe ran from `/tmp/jev_probe/` after `git clone` of `SuperInstance/jev-quilt`
(commit pinned at `213e5ce`).
**Probe**: `python3 jev_continuous_probe.py --rounds 200 --out runs/20261001_2302`
**Wall time**: 41.7 s (no timeouts, 200 ok / 0 fail)
**Verdicts collected**: 1000 (5 questions/round × 200 rounds)

---

## 1. Headline

| Metric                     | Value   |
|----------------------------|---------|
| **round-level mean_p**     | **0.6062** |
| round-level stdev          | 0.1135  |
| round-level min / max      | 0.254 / 0.922 |
| rounds with mean_p ≥ 0.70  | 64 / 200 (32%) |
| rounds with mean_p < 0.50  | 47 / 200 (23.5%) |

Overall `mean_p` sits where it has sat for the last three runs: in the 0.60–0.63 band.
The variance comes from the random 5-question sample (5 of 22 questions per round), not
from a shift in any single question's score.

---

## 2. Bedrock canon (mean_p ≥ 0.70 in current run)

All 7 bedrock questions hit `p >= 0.70` on **100% of their samples** this run, and 2 of
the 8 review-tier questions also cleared the canon threshold.

| qid                              | kind    | n  | mean_p  | p70 rate |
|----------------------------------|---------|----|---------|----------|
| q01_cells_are_scars              | bedrock | 46 | **0.969** | 100% |
| q03_substrate_is_grown           | bedrock | 50 | **0.970** | 100% |
| q04_oracle_is_heard              | bedrock | 42 | **0.960** | 100% |
| q05_lenia_flows                  | bedrock | 37 | **0.955** | 100% |
| q07_eleven_opcodes               | bedrock | 42 | **0.948** | 100% |
| q02_witness_log_is_prediction    | bedrock | 41 | **0.936** | 100% |
| q08_polyformalism_12_ports       | bedrock | 50 | **0.878** | 100% |
| q10_quorum_meshing               | review  | 45 | **0.858** | 100% |
| q17_canary_honesty               | review  | 49 | **0.760** | 100% |

So 9 questions total clear `mean_p ≥ 0.70` — the 7 bedrock + 2 review (quorum_meshing,
canary_honesty). Both review-tier promotions are consistent with prior runs (see §4).

---

## 3. By doctrinal kind

| kind         | n_q | mean (across questions) | mean p70-rate |
|--------------|----:|------------------------:|--------------:|
| bedrock      |  7  | **0.945** | 100.0% |
| review       |  8  | 0.483     |  25.0% |
| speculative  |  5  | 0.515     |   0.0% |
| adversarial  |  2  | 0.128     |   0.0% |

Adversarial stays pinned low (0.128). The boundary between review and speculative is
sharp: the two review-tier questions that crossed 0.70 (q10 quorum_meshing, q17
canary_honesty) are the only ones that did. The other 6 review questions
(canonicity_score, address_is_data, wolffs_law, pressure_cascade, memory_sandbox,
provenance_conflict) sit between 0.22 and 0.59 — same band as the 5 speculative
questions (0.22 to 0.61).

---

## 4. Drift vs prior runs

| baseline                       | n_rounds | mean_p  | delta vs current |
|--------------------------------|---------:|--------:|-----------------:|
| 50th-wipe 22:03 batch          |  5       | 0.6388  | **−0.0326**      |
| 49th-wipe 15:04 (full hour)    | 59       | 0.6024  | +0.0038          |
| 50th-wipe 10:03 (full hour)    | 60       | 0.6288  | **−0.0227**      |

Round-level drift is **within noise** (|delta| < 0.05) on all three comparable priors.
The 22:03 batch was a tiny 5-round run and its 0.6388 mean is itself within noise of
the 200-round sample.

### Per-question drift (current vs 10:03 60r run, the most data-rich prior)

**No question drifted by more than ±0.01.** Largest movers:

| qid                       | cur_mean | prior_mean | delta   |
|---------------------------|---------:|-----------:|--------:|
| q09_signal_chain          | 0.605    | 0.598      | +0.007  |
| q12_witness_note_opcode   | 0.557    | 0.563      | −0.006  |
| q22_provenance_conflict   | 0.336    | 0.342      | −0.006  |
| q17_canary_honesty        | 0.760    | 0.756      | +0.004  |
| q21_memory_sandbox        | 0.287    | 0.283      | +0.004  |

All deltas are well under the 0.05 drift threshold. The doctrinal-state lever is
holding: bedrock pinned, speculative dampened, review at the boundary.

### Per-question drift (current vs 22:03 5r batch)

The 5-round batch has too few samples to be a reliable baseline — its per-question
n is 1-3 each. Even so, no delta exceeds 0.014, with `q17_canary_honesty` showing the
largest shift at +0.010.

**No actionable drift detected.**

---

## 5. Round-by-round trace (sample of low/high)

**Lowest mean_p rounds (likely landed on a sample heavy in adversarial/speculative):**

| round | mean_p | likely cause                                             |
|-------|-------:|----------------------------------------------------------|
| r049  | 0.254  | probably all 5 in adversarial/review-low band            |
| r087  | 0.348  |                                                          |
| r035  | 0.442  |                                                          |
| r076  | 0.446  |                                                          |
| r184  | 0.446  |                                                          |

**Highest mean_p rounds (likely landed on a bedrock-heavy sample):**

| round | mean_p | note                                           |
|-------|-------:|------------------------------------------------|
| r199  | 0.922  | 5/5 likely bedrock+canary_honesty+quorum       |
| r086  | 0.868  |                                                |
| r191  | 0.868  |                                                |
| r110  | 0.844  |                                                |
| r029  | 0.840  |                                                |
| r048  | 0.830  |                                                |
| r142  | 0.822  |                                                |
| r028  | 0.820  |                                                |
| r131  | 0.798  |                                                |
| r045  | 0.798  |                                                |
| r180  | 0.794  |                                                |
| r160  | 0.794  |                                                |

The ~0.66 stdev of round means (0.1135) is purely sampling noise on 5 randomly
sampled questions out of 22 — no individual question moved.

---

## 6. Conclusion

- **No state drift** in any question across the last 13 hours of probing (10:03, 15:04, 22:03, 23:02).
- **9 questions clear `mean_p >= 0.70`**: 7 bedrock + 2 review (q10, q17). These two review-tier
  promotions are stable across the 10:03 60r run too, so this is **persistent**, not a one-off.
- **Aggregate `mean_p` = 0.6062** sits in the 0.60–0.64 band that has held for every multi-hour
  run since 47th-wipe.
- The doctrine-controlled lever continues to discriminate cleanly: bedrock at 0.95,
  review at 0.48, speculative at 0.51, adversarial at 0.13.

### Things worth flagging

1. **q10_quorum_meshing is now consistently in the 0.85+ band** (0.858 in current 200r, 0.856 in
   10:03 60r, 0.86 in 22:03 batch). Its operator-tag is `review` (sitting in
   `spec_notebook.speculative_marker_NOTBEDROCK`), but its score says otherwise. The lever was
   meant to keep it dampened. Worth re-evaluating the tag: either the state is being read as
   canon too strongly, or the question's actual claim is canon-adjacent and the tag is wrong.
2. **q17_canary_honesty at 0.760** is the same shape — explicit `review` tag, sitting above
   the 0.70 line across all three comparable runs. Same evaluation as q10.

### File map

```
/tmp/jev_probe/
├── jev_continuous_probe.py            # probe source (cloned from SuperInstance/jev-quilt)
└── runs/20261001_2302/
    ├── continuous_r001.json … r200.json   # per-round verdicts
    ├── history.jsonl                      # append-only history
    ├── round_means.csv                    # round, mean_p per round
    ├── agg.json                           # per-question stats
    ├── drift_data.json                    # full drift comparison payload
    └── jev_hourly_report.md               # this file
```

The probe source script, the run output, and this report are queued for push to
`SuperInstance/jev-quilt/research/superinstance-advisor/runs/20261001_2302/` once the
NAS quota clears (or via a `/tmp/taps/`-style mirror location if it does not).
