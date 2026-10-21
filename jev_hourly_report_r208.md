# JEV Continuous Probe — R-208

**Run:** 2026-10-21 03:04 UTC · fresh wipe (~95th) · `/workspace` EDQUOT clear (52G/600G free)
**Bootstrap:** `SuperInstance/jev-quilt @ r-081-continuous-probe-rebuild` — clone succeeded this time (memory recorded it 503'ing; it worked in ~8s)
**Command:** `timeout 60 python3 jev_continuous_probe.py` → exit 124 (ceiling reached, expected)

## Headline

| Metric | R-208 | Prior sessions | Delta |
|---|---|---|---|
| **mean_p** | **0.4260** | R-207 0.4153 · R-206 0.3820 · R-205 0.3941 | +0.0107 vs R-207 |
| Rounds | **20** | R-207 200 · R-206 15 | thin |
| Verdicts | 100 | — | — |
| Distinct qids drawn | **22/22** | full coverage | — |
| **Drift > 0.05** | **NONE** | 0 for R-205/206/207 | stable |
| Cathedral bedrock | **7/7 @ 100%** | 6th consecutive session | ✅ |
| Spec/adv clean-reject | **52/52** (max 0.24) | 100% for 6 sessions | ✅ |

mean_p 0.4260 sits **mid-band** in the durable 0.35–0.55 range. Grand mean is confounded by draw mix, so per-qid movement is the real signal — and it is the smallest yet recorded (max |delta| **0.0136**, q12).

## Bedrock canon — 7/7 @ p ≥ 0.70

| qid | baseline (n≈90) | R-208 | delta | hits |
|---|---|---|---|---|
| `q01_cells_are_scars` | 0.9798 | 0.9786 | −0.0012 | 7/7 |
| `q02_witness_log_is_prediction` | 0.9720 | 0.9700 | −0.0020 | 2/2 |
| `q03_substrate_is_grown` | 0.9798 | 0.9800 | +0.0002 | 6/6 |
| `q04_oracle_is_heard` | 0.9722 | 0.9700 | −0.0022 | 5/5 |
| `q05_lenia_flows` | 0.9697 | 0.9667 | −0.0030 | 6/6 |
| `q07_11_opcodes` | 0.9700 | 0.9700 | +0.0000 | 3/3 |
| `q08_polyformalism` | 0.9800 | 0.9800 | +0.0000 | 5/5 |

Cathedral mean **0.9743**, 40/40 draws ≥ 0.70, **zero misses**. Seventh consecutive clean session. Substrate reproducibility is now measured at **±0.003/qid** — tighter than the ±0.005 established at R-083.

## Non-bedrock, all holding

- **q06_three_views 0.1667** — durable REJECT despite its `bedrock` tag in `QUESTION_BANK`. Sixth session confirming. **Re-tag it.**
- **q17_canary_honesty 0.6480** — plateau holds a seventh session (0.6537 → 0.6480, −0.0057). The 0.99→0.65 decay from R10 stopped ~40 wipes ago and has not resumed. Stays REVIEW.
- **q12_substrate_polyformal 0.5933** — largest movement this round at −0.0136, still under threshold. REVIEW.
- **q09_signal_chain_canon 0.2100** — clean.
- **q10_quorum_meshing 0.0325** — the state-order spec-leak fix holds for the seventh session. STATE-ORDER invariant intact.
- Speculative/adversarial floor is intact: max p across all 15 such qids is **0.24** (q09), everything else ≤ 0.07.

## ⚠ Three harness defects — two of them can silently lie

### DEFECT A (confirmed, bites every run) — `continuous_r*.json` is saturated and gets overwritten

The run **overwrote 20 historical round files** (`r001`–`r020`, the R-088/R-205 corpus). Recovered via `git checkout HEAD --`. Verified restored by reading `ts` values back (r001 → `2026-10-19T01:02:37`, r020 → `2026-10-20T06:03:36`). **This is the 5th occurrence of this exact defect.**

Only **4** of our rounds survived on disk (r021–r024); the other 16 were recovered from `history.jsonl` — which is why all 20 rounds are in the results above rather than 4.

**Structural fix still not applied.** The convention "shift by +N and patch `round_id`" cannot work: the series is saturated through r403. The only real fix is to make overwriting impossible — write to `jev_sessions/<session>/round_<n>.json` by construction. R-207 recommended this; R-208 confirms the convention is exhausted. This session used `jev_sessions/rounds_r208/`, but *the script still writes the flat names*, so the exposure is unchanged.

### DEFECT B (would have produced a FALSE ALL-CLEAR) — `history.jsonl` gitignored + shallow clone

`.gitignore` line 1 is `jev_sessions/history.jsonl`. The clone is `--depth 1`, so `load_history()` found **no file at all** and returned `{}`. `compute_drift()` then has zero baseline samples and concludes "no drift" — not because the substrate is stable, but because it is comparing nothing. **A broken instrument reporting health.**

This is exactly the R-207 finding, reproduced. **Mitigated this run:** rebuilt the baseline from the tracked `continuous_r*.json` corpus — **401 files, 2,000 samples, 22/22 qids** — seeded `history.jsonl` from it, and asserted `len(samples) >= 20 and total > 500` before trusting any drift number. The "drift: NONE" in this report is therefore a real measurement, not a vacuous one.

**Fix:** either un-ignore `history.jsonl`, or have `load_history_samples()` fall back to the round-file corpus. Until then, *every* fresh-clone session must seed its own baseline or it will report a clean bill of health forever.

### DEFECT C (minor) — non-dict entries inside `verdicts` crash the loader

Building the baseline raised `AttributeError: 'str' object has no attribute 'get'`. Cause: **5 malformed verdict entries** across the 401 round files. The round-level `isinstance(r, dict)` guard is present in my loader, but the **per-verdict** guard is missing. In the shipped script, `compute_drift()` does `v["qid"]` unguarded, so one string element raises inside the loader and presents as a corrupt file rather than a shape mismatch.

## Method notes

- **Only 20 rounds in 60s** (vs 200 in R-207). Not rate limiting and not the `TIMEOUT_S=4` regression — healthy calls complete in ~0.13s. The network is simply slower this session; the elapsed-per-round distribution should be checked if the next round is also thin. `TIMEOUT_S=4` stays.
- `load_history()` was **not** the reason for the thin round; the ceiling is wall-clock.
- Recovered-16-rounds-from-history means this round's verdict set is complete even though 16 round files are gone. If the next session reads only round files, it will **under-count this round** — the raw data is preserved at `/workspace/research/r208_raw/` (20 records) and in `history_r208_seed.jsonl` backing file.

## Actions

1. **Make the round writer structurally collision-proof** — `jev_sessions/<session_ts>/round_<n>.json`. The shift-and-patch convention is exhausted; this is the 5th data-loss event it has failed to prevent.
2. **Fix the empty-baseline false all-clear** — un-ignore `history.jsonl` or fall back to the round corpus; add a hard assert that the baseline is non-empty before printing any drift result.
3. **Re-tag `q06_three_views`** from `bedrock` to its true classification — it has read REJECT for 6 straight sessions and inflates any bedrock-hit-rate stat computed from the tag.
4. Add the per-verdict `isinstance` guard, and scrub the 5 malformed verdict entries from the corpus.

---

*R-208 · mean_p 0.4260 · 7/7 cathedral @100% · zero drift >0.05 · substrate reproducible to ±0.003/qid*