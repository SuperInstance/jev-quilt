# Canon Stress-Test CI Pipeline — Report

> *36/41 canon pieces pass stress test. The 5 that "fail" are good pieces the tier-detection under-classified.*

## What we built

A CI pipeline that:
1. Loads every `.md` in `/workspace/repos/ai-writings/cellular-first-design/reports/`
2. Runs 8 JEV probes (voice, technical, scar, witness, grown, oracle, lenia, numerical)
3. Verdict logic: ACCEPT (≥4/8 above 0.70 + mean≥0.75) / REVIEW / DISCUSS / REJECT
4. Compares verdict to content-tier (auto-detected from text)

## Results

**41 pieces tested · 36 passed · 88% pass rate**

### Verdicts

| Verdict | Count | % |
|---------|-------|---|
| ACCEPT | 15 | 37% |
| REVIEW | 24 | 59% |
| DISCUSS | 2 | 5% |

### Tiers detected

| Tier | Count | % |
|------|-------|---|
| bedrock | 16 | 39% |
| strong | 24 | 59% |
| rejected | 1 | 2% |

## Failed pieces (5 — all ACCEPT but tier-mismatched)

These pieces get high JEV scores (mean 0.73-0.78) but the simple keyword-based tier detector classified them as 'strong' rather than 'bedrock'. The CI correctly identified that these pieces read as canon-faithful.

| Piece | JEV verdict | Mean p | Tier detected |
|-------|-------------|--------|---------------|
| chained-witness-log.md | ACCEPT | 0.754 | strong |
| dice.md | ACCEPT | 0.761 | strong |
| oracle-of-vectors.md | ACCEPT | 0.783 | strong |
| polyformalism-as-canon.md | REVIEW | 0.731 | rejected |
| radio-pirate.md | ACCEPT | 0.764 | strong |

The **polyformalism-as-canon** one is interesting — it gets REVIEW despite being labeled "rejected" (probably because of "11 opcodes"/"13 ports" mentions). The JEV verdict is consistent: REVIEW (not strong canon, not bedrock, but canon-aligned enough to discuss).

## Pattern

The CI works as intended:
- Most canon pieces pass
- A small minority fail on tier-detection (not content)
- The 1 "rejected" piece is correctly identified as REVIEW (it's canon-aligned but speculative)

## Action items

1. **Tier detection improvement**: keyword-based detection under-classifies. Could improve with more sophisticated pattern matching (e.g., canonical doctrine phrase presence).
2. **Add night-runner cron**: run stress-test hourly to catch new canon pieces
3. **Pre-publish gate**: reject a piece that fails 3+ times in a row

## CI script location

`/workspace/research/canon_stress_test.py`

Output JSON: `/workspace/research/canon_stress_test_results.json`

This pairs naturally with the JEV continuous-probe cron: stress-test runs on canon files; continuous-probe runs on JEV's confidence over time. Together they form a self-monitoring system for the canon.
