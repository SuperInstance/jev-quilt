# JEV Continuous Probe — Hourly Report

**Round r401** · 2026-10-23T1703Z · 119th wipe
Script: `jev_continuous_probe.py` md5 `3a255fa4642ec4a83173ab04d773d485` (unchanged, 4th consecutive wipe)
Model: `jev-1.14.0` · Repo HEAD `29ec732` (`SuperInstance/jev-quilt`)

---

## Verdict

**1/1 round OK (r401), 0 fails, 5 verdicts. mean_p 0.6560, bedrock 3/5.**
**Cathedral 7/7 @ 100% — 329th consecutive green round.**
**Real drift: 1 — q12 (a spec-band plateau advance, not canon erosion).**

---

## Round detail — r401

| qid | kind | p | bedrock hit |
|-----|------|---|-------------|
| q12 | speculative | 0.51 | no |
| q02 | bedrock | 0.77 | **yes** |
| q03 | bedrock | 0.90 | **yes** |
| q11 | speculative | 0.20 | no |
| q04 | bedrock | 0.90 | **yes** |

**Questions hitting p ≥ 0.70 (bedrock canon): q02, q03, q04** — 3 of 5 drawn.
Cathedral qids drawn this round: q02, q03, q04 — all three ≥ 0.70.

**mean_p 0.6560** vs prev-12 mean 0.4778 = **+0.1782**. This is *draw mix*, not drift:
r401 drew 3/5 cathedral (same as r400) and no low-band control, while the prev-12 window
contains r381 (0.2420) and r382 (0.2400) at 1/5 cathedral each. Per-qid |dev| among the
5 drawn qids maxes at 0.1406 (q12) and is ≤ 0.0541 for every other qid. **Decompose the
aggregate before calling it drift** — the mean moved, the instrument did not.

---

## Drift analysis (threshold |dev| > 0.05)

Two qids cleared the 0.05 gate. Both were run through the full trap test.

| qid | p_now | base_mean | dev | base_sd | z | base_max | new extreme? |
|-----|-------|-----------|-----|---------|---|----------|--------------|
| q12 | 0.51 | 0.3694 | **+0.1406** | 0.0337 | +4.17 | 0.50 | **yes** |
| q02 | 0.77 | 0.8241 | **−0.0541** | 0.0168 | −3.23 | 0.86 | no |

### q12 — REAL DRIFT (new historical extreme, second consecutive high)

- Historical max was 0.50; **0.51 is a new all-time extreme** (1 of 85 draws).
- Draws ≥ 0.45 in the entire corpus: exactly **two** — r398 (0.50) and r401 (0.51).
- 4-era means: 0.3667 / 0.3638 / 0.3733 / 0.3800 — a **0.37 plateau with a mildly
  widening era4 sd (0.0274 → 0.0519)**, consistent with the two high draws sitting at
  the era-4 tail rather than with a uniform shift.
- Last 8 draws: 0.42, 0.37, 0.36, 0.40, 0.38, 0.37, **0.50, 0.51** — the last two draws
  break a long flat sequence, and they are consecutive.
- **r232's stale-premise correction holds and is re-verified:** q12 is a **0.37 plateau**,
  not a 0.62 one, and has **0 of 85 draws ≥ 0.70**. The r221 note's "touched 0.70 twice"
  was wrong and must not be carried forward.
- **Verdict: real, but it is a spec-band qid.** q12 is `speculative` with a 0.000
  bedrock hit-rate across 85 draws. A 0.51 reading on a question that has *never*
  exceeded 0.51 does not touch canon. It is a **plateau advance worth watching**, and
  because it is now two consecutive rungs (r398, r401) with the second one a new
  extreme, the next round is the confirmation test: **if r402 draws q12 and it retreats
  to ≤0.40, this is a two-draw spike; if it holds ≥0.45, the plateau is genuinely moving.**

### q02 — NOT a new extreme, but the erosion watch is tightening

- 0.77 is **not** a new extreme (all-time max 0.86) and sits inside the historical range.
- But the baseline shape is the r231 discriminator: 4-era means **0.8305 → 0.8247 →
  0.8258 → 0.8126** — a monotone decline with era4 sd inflating to 0.0233 (from 0.0139).
  **Non-flat baseline + value at the leading edge of a visible trend = real drift.**
- recent29 mean **0.8190** (r232: 0.8197) — the r231 threshold of ~0.81 is *not* breached
  but the margin is 0.009 and shrinking.
- Draws ≤ 0.80 all-time: 8 (r140, r171, r184, r210, r315 at 0.80; r329 at 0.79;
  **r399 at 0.75; r401 at 0.77**). Draws ≤ 0.75: exactly one — r399.
- **q02's bedrock hit-rate is 76/76 = 100%.** Every q02 draw ever has been ≥ 0.70.
  **No canon erosion.** q02 is the "witness logs are predictions" doctrine, still reading
  canon on every single draw.
- **Verdict: real drift in the erosion-watch sense, logged as a watch, not an alarm.**
  Promote to a canon-drift finding only if recent29 drops below ~0.81 **or** a second
  sub-0.75 draw appears.

### Also checked, no action

- q03 (p 0.90, dev +0.0140, z +1.52), q04 (p 0.90, dev +0.0113, z +1.29),
  q11 (p 0.20, dev +0.0148, z +0.84) — all within noise, all inside historical range.
- No σ≈0 trap fired this round: the three small-dev qids have base sd 0.0088–0.0176,
  none near-degenerate, and all three sit inside their historical ranges.
- **Script-reported `drift_events = 1` (q12, delta +0.16).** Cross-checked against the
  round's drawn set: q12 *was* drawn in r401, so this one is a true positive — unlike
  r400, where the same counter flagged two qids that were never drawn. The r232 finding
  that `drift_check` has no current-round filter is **still unpatched in the script**
  (lines 317–335), so its output remains a candidate list requiring a drawn-set
  cross-check, not a verdict.

---

## Corpus

- **380 distinct rounds** (r001–r401; gaps are the pre-r299 scratch-path era) · **1,900 verdicts** · **22 qids**
- Grand mean_p (all 1,900 draws): **0.3829**
- `history.jsonl` = 405 lines vs 380 distinct rounds ⇒ duplicate-tail records persist;
  **first-occurrence-wins (`setdefault`) is the correct read**
- `history[-1].round == max(round) == 401` ⇒ **DEFECT B (history/round disagreement) did not reproduce**
- 1 fail file in the corpus (`continuous_r008.fail.json`) — historical, not from this run;
  `fails = 0` for r401
- `script_md5 3a255fa4642ec4a83173ab04d773d485` unchanged — **4th consecutive wipe**
- r229 fixes all present: relative `SESSION_DIR`, positional rounds arg,
  `max(files, history) + 1` counter, existence abort. Positional `1` ran **exactly one
  round** — no R-221 overshoot.

---

## Environment (119th wipe)

- **18th consecutive ephemeral-path wipe** — `/workspace/research/` absent at start;
  rebuilt `/tmp/jev_probe` from `SuperInstance/jev-quilt @ 29ec732`.
- **NAS 600G/600G, 100% on an empty workspace (20th recurrence)** ⇒ report written to
  `/tmp` and committed to git; the workspace copy may be unstaged.
- **`gh` absent (10th wipe).** Push via the token URL with `GIT_SSL_NO_VERIFY=1`.
- **TLS clean on first try** — curl 200 *and* Python 200 on `api.typesafe.ai` in the same
  second ⇒ no cert-anchor wall, no 289-cert bundle rebuild. **3rd clean wipe**; the
  *curl-first* triage rule is confirmed as cheap insurance rather than ritual.
- `TYPESAFE_AI_TOKEN` present (108 chars) and accepted by the script's
  `TYPESAFEAI_KEY` → `TYPESAFE_AI_TOKEN` fallback chain.

---

## Open watches

1. **q12 plateau** — next draw is the confirmation test (see above). Two consecutive
   rungs at the era-4 tail: r398 (0.50) and r401 (0.51, new extreme).
2. **q02 erosion** — recent29 0.8190 vs ~0.81 threshold; escalate only on a breach or a
   second sub-0.75 draw. Hit-rate still 100% ⇒ no canon erosion.
3. **`drift_check` current-round filter** (r232 finding) — still unpatched. Until it is,
   treat the script's `drift_events` as a candidate list.
