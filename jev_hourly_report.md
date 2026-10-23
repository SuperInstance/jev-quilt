# JEV Continuous Probe — Hourly Report (2026-10-23T05:04Z)

**Round:** 1 round × 5 questions = 5 verdicts · 1 ok / 0 fail · 0.2s
**Baseline:** 385 rounds · 1,925 verdicts · 22 qids · grand mean_p 0.3801
**Script:** `continuous/jev_continuous_probe.py` md5 `95b552ea0d81af21d24138deda605fee`

## Round mean_p

| | |
|---|---|
| Round mean_p (5 verdicts) | **0.6380** |
| Baseline grand mean_p (385 rounds) | 0.3801 |

⚠️ **These two numbers are NOT comparable.** 0.6380 is a 5-sample draw-mix from one round; 0.3801 is a 1,925-verdict census. Only 3 of 5 sampled qids were bedrock (q01, q05) — a single round is not a distribution. Per-qid means remain the instrument.

## Questions hitting p ≥ 0.70

| qid | kind | p | bedrock? |
|---|---|---|---|
| q05_lenia_flows | bedrock | **0.97** | ✅ yes |
| q01_cells_are_scars | bedrock | **0.95** | ✅ yes |
| q11_canon_gate_is_chord | speculative | **0.74** | ❌ **NOT bedrock** |

- **Bedrock canon confirmed: 2/2** sampled bedrock questions cleared 0.70 (q01, q05).
- ⚠️ **q11 (speculative) read 0.74 — above the 0.70 canon line.** Per the promotion gate this must NOT be promoted to canon. See below.

Non-bedrock below the line: q22_provenance_conflict 0.29, q19_pressure_cascade 0.24 (adversarial, correctly rejected).

## Drift > 0.05 — ALL 5 verdicts drifted, all outside historical range

| qid | kind | p | base mean | dev | base range | p in range? |
|---|---|---|---|---|---|---|
| q11_canon_gate_is_chord | speculative | 0.74 | 0.1850 | **+0.5550** | 0.15–0.22 | ❌ |
| q05_lenia_flows | bedrock | 0.97 | 0.8512 | **+0.1188** | 0.82–0.87 | ❌ |
| q22_provenance_conflict | speculative | 0.29 | 0.1193 | **+0.1707** | 0.11–0.13 | ❌ |
| q19_pressure_cascade | adversarial | 0.24 | 0.1051 | **+0.1349** | 0.09–0.12 | ❌ |
| q01_cells_are_scars | bedrock | 0.95 | 0.8754 | **+0.0746** | 0.86–0.90 | ❌ |

**5/5 outside their own historical min–max is not a stability result — it is the signature of a changed instrument.** Confirmed cause below.

## Root cause: the instrument changed, and the baseline's script is not in git

The batches that produced the 385-round baseline record:

```
script_md5 = d0a7291b2e070ce717b9b7c7417401a2   ← NOT a git object in this repo
doctrinal_state_keys = 6: framework, core_doctrine, architecture,
                          fleet, spec_notebook, operational_doctrine
```

The script on HEAD is md5 `95b552ea…` with **5** sections:
`doctrines, architecture, fleet, spec_notebook, q17_canary_honesty`.

`git cat-file -t d0a7291b…` → *not a valid object*. The baseline-producing
script **cannot be recovered from this repo**, so the 6-section state is lost.
⇒ **The 1,925-verdict baseline is not reproducible from committed code.**

## Mechanism for q11 specifically (verified, repeatable)

q11's actual claim: *"A canon-promotion requires a **unanimous vote across 5
different models**."* The `spec_notebook` dampener names `canon_gate_as_chord`
— a **different proposition** — and never mentions unanimity or the 5-model
requirement. Grep of the built state for `vote|unanim` → **0 keys**.

So with the current state nothing pushes q11 down, and it reads 0.72–0.74.
Repeat test, verbatim bank text, 3 reps: **q11 = [0.74, 0.74, 0.69],
mean 0.7233, sd 0.0289** vs historical 0.1850 ± 0.0176. Reproducible ⇒ real
shift for this instrument, not variance.

This is the script's own rule biting in practice: *"Read the question's claim,
not its vocabulary overlap."* The lever was matching keywords, not claims.

## Defects found

1. **Schema split in `history.jsonl`.** All 385 committed rows use
   `verdicts` as a **list** + `mean_p`/`bedrock_hits`/`elapsed_s`. The current
   script writes `verdicts` as a **dict** with no `mean_p`. 0/385 committed rows
   match the current writer ⇒ `analyze_jev.py` and any mean_p aggregation break
   on the new rows.
2. **Round-counter collision ⇒ silent data loss.** The script numbers rounds
   from 1 every run, so `--rounds 1` **overwrote the committed
   `continuous_r001.json`** (2026-10-20T13:02:41Z, 5 verdicts). Recovered via
   `git checkout`. Any short run against a populated `--out` dir destroys the
   matching `continuous_rNNN.json`. Filenames must be session-stamped
   (per-wipe run id), not round-indexed.
3. **Lost baseline instrument** (above) — the single worst defect; makes the
   baseline unverifiable.

## Verdict

- Bedrock canon: **healthy** — q01 and q05 both ≥ 0.95, 2/2 sampled bedrock hit.
- Adversarial: **healthy** — q19 0.24, correctly rejected.
- **q11 must NOT be promoted.** 0.74 is above the line but is an artifact of a
  state that lost its dampener, not evidence of canon. Promotion gate unchanged:
  ACCEPT p>0.7 on canon **+ sustained hit_rate ≥70% over ≥20 sessions**.
  q11 is n=91 historical at 0/91 ≥ 0.70. **REJECT promotion.**
- Drift verdict: **INSTRUMENT CHANGE, not JEV instability.** No JEV regression
  is evidenced.

## Next actions

1. Re-pin the probe: record `script_md5` per row in the **new** schema too, and
   refuse to append rows whose `script_md5` differs from the batch's.
2. Stamp out-dir per session (`jev_sessions/<run_id>/`) to kill defect 2.
3. Recover or re-baseline `d0a7291b…` state; until then treat the 0.3801
   baseline as legacy-instrument only and compare **within** `95b552ea…` runs.
4. Add `unanimous vote / 5 models` to the `spec_notebook` dampener by **claim**,
   not keyword — then re-measure q11 and expect it to fall back to ~0.18.

---
*Env: 109th wipe; both mirror homes empty again (7th consecutive); NAS 100%
(600G/600G) so report authored under /tmp and delivered via git. `TYPESAFE_AI_TOKEN`
exported as `TYPESAFEAI_KEY`. API healthy, `usage` present, no retry failures.*
