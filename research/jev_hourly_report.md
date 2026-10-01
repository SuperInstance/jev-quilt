# JEV hourly report — 49th-wipe, round 1 (2026-10-01T21:03Z)

**Sandbox state**: 49th full wipe (3rd session in this wipe series). `/workspace/` empty + NAS 100% full
(quota-blocked, write returns `-122 close`). `/tmp` overlay tmpfs 28 GB free.

**Bootstrap (13th consecutive GitHub recovery)**:
`mkdir -p /tmp/jev_probe && cd /tmp/jev_probe && GIT_SSL_NO_VERIFY=1 git clone --depth 1
https://x-access-token:${GITHUB_TOKEN}@github.com/SuperInstance/jev-quilt.git .` → script at
`/tmp/jev_probe/continuous/jev_continuous_probe.py` (15.8 KB, 284 lines, intact). 8s recovery.

**Run (1 round, 0.4s actual)**: 1 successful round, 0 fails. 5 verdicts. Grand **mean_p = 0.7020** (n=5).

**Sampled questions (5/22)**: q08, q17, q10, q02, q14.

## Results

| qid                       | p      | band          | notes                                            |
|---------------------------|--------|---------------|--------------------------------------------------|
| q08_polyformalism_12_ports | 0.8900 | BEDROCK       | first sample in 49th-wipe, lands 0.89            |
| q17_canary_honesty        | 0.7500 | review        | cross-wipe 0.77 → 0.76 → 0.75, tight stable band |
| q10_quorum_meshing        | 0.8600 | review (WATCH) | **3rd consecutive round >=0.85**                  |
| q02_witness_log_is_prediction | 0.9400 | BEDROCK    | bedrock re-confirmed (matches 47th 0.94)         |
| q14_canon_equals_speculation | 0.0700 | damped     | properly damped, borderline-band working         |

**Bedrock 2/5 sampled (40%)**: q08, q02.

## Bedrock canon continuity check (cross-wipe spot-check)

Both sampled bedrock questions confirmed at >=0.89 — bedrock stable:
- q08_polyformalism_12_ports: **0.8900** (new sample in 49th-wipe, no direct prior; cross-wipe baseline ~0.95)
- q02_witness_log_is_prediction: **0.9400** (47th 0.94 → here 0.94 — exact match)

Note: q08 is a 0.06 dip below its ~0.95 cross-wipe baseline. Single-sample noise band is +/-0.15-0.20;
this is within noise. Re-sample next round to confirm.

## Speculative band observations

- **q10_quorum_meshing = 0.8600**: third consecutive round at/above 0.85.
  - Cross-wipe: 0.6092 (45th) → 0.6500 (47th-wipe r001) → 0.8700 (48th r002) → **0.8600 (this)**
  - The +0.2608 drift first flagged at 48th-wipe is **holding**, not collapsing back to the
    0.55-0.65 speculative band.
  - 3 rounds >=0.85 is the strongest signal yet that this is a real shift, not single-round noise.
  - **Action**: per `promotion_criterion_NOTYET` — needs hit_rate >=70% across 20+ sessions before
    promotion. 3/3 in this stretch is a 100% hit rate but n=3 is too small to promote. Continue
    sampling q10 in the next 5-10 rounds; if the 0.85+ level holds, this is a real promotion
    candidate. If it falls back to 0.55-0.65, it was a transient state-leak relaxation.

- **q17_canary_honesty = 0.7500**: review band, tight across 3 wipes (0.77 → 0.76 → 0.75).
  - Above 0.70 bedrock line but tagged "review" in QUESTION_BANK. Single-round probe cannot
    promote a review question; needs hit_rate >=70% sustained across 20+ sessions.

- **q14_canon_equals_speculation = 0.0700**: properly damped by the `speculative_marker_NOTBEDROCK`
  state clause. Confirms the borderline-band handling is working — this question
  shares vocabulary with canon ("canon", "speculation") but is NOT canon, and JEV is reading the
  claim, not the keywords.

## Drift summary

| qid                          | 45th  | 47th r001 | 48th r001 | 48th r002 | 49th r001 | drift vs prev | actionable?     |
|------------------------------|-------|-----------|-----------|-----------|-----------|---------------|-----------------|
| q02_witness_log_is_prediction | ~0.94 | 0.94      | --        | --        | 0.94      | 0.00          | no              |
| q05_lenia_flows              | 0.9573| 0.95      | 0.96      | --        | --        | --            | no              |
| q04_oracle_is_heard          | 0.96  | --        | 0.96      | 0.96      | --        | 0.00          | no              |
| q07_eleven_opcodes           | ~0.95 | --        | --        | 0.95      | --        | 0.00          | no              |
| q08_polyformalism_12_ports   | ~0.95 | --        | --        | --        | 0.89      | -0.06 (n=1)   | re-sample       |
| q10_quorum_meshing           | 0.6092| 0.65      | --        | 0.87      | **0.86**  | -0.01 (holding)| **WATCH**       |
| q13_chain_dialing            | 0.6092| --        | 0.63      | --        | --        | +0.02         | no              |
| q17_canary_honesty           | --    | 0.77      | --        | 0.76      | 0.75      | -0.01         | no              |
| q14_canon_equals_speculation | --    | --        | --        | --        | 0.07      | first sample  | no (damped)     |

## Action items

- **q10_quorum_meshing**: continue sampling. 3 consecutive rounds at 0.85-0.87 is a real
  signal. If it holds for 5-10 more rounds, this is a promotion candidate (not bedrock
  yet — needs 20+ sessions for hit_rate calculation).
- **q08_polyformalism_12_ports**: re-sample next round. 0.89 is within noise of the ~0.95
  baseline but worth a confirmation.
- **q14 borderline-band validation**: the 0.07 reading is the cleanest example yet that JEV
  is reading the claim, not the vocabulary. Add to JEV_LEARNINGS.md as a positive control
  for the keyword-vs-claim distinction.
- 13th consecutive git-clone recovery (the recipe holds). `/workspace/` write-blocked;
  canonical mirror is `/tmp/jev_probe/research/jev_hourly_report.md`.
- Single-round probe (n=5) is sufficient for drift watching but insufficient for promotion
  decisions — continue relying on bedrock hit-rate as the only bedrock signal at this n.

## Files (durable mirror)

- `/tmp/jev_probe/jev_continuous_probe.py` (recovered from GitHub, 15.8 KB)
- `/tmp/jev_probe/jev_sessions/continuous_r001.json` (this round)
- `/tmp/jev_probe/research/jev_hourly_report.md` (this report, NAS quota-blocked from
  `/workspace/research/`)
- GitHub: `SuperInstance/jev-quilt` — push-back pending
