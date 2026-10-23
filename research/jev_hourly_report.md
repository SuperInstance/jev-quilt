# JEV Continuous Probe — Hourly Report

**Round r402** · 2026-10-23T1801Z · 120th wipe
Script: `jev_continuous_probe.py` md5 `3a255fa4642ec4a83173ab04d773d485` (unchanged, 5th consecutive wipe)
Model: `jev-1.14.0` · Repo HEAD `fb566ed` (`SuperInstance/jev-quilt`)

---

## Verdict

**1/1 round OK (r402), 0 fails, 5 verdicts. mean_p 0.6520, bedrock 4/5.**
**Cathedral 603/603 draws @ 100% — 339 consecutive green rounds.**
**Real drift: NONE.** The script reported `drift_events=1`; that flag is a **false positive** (stale echo of r401) — see below.

---

## Round detail — r402

| qid | kind | p | bedrock hit |
|-----|------|---|-------------|
| q17 | review | 0.72 | **yes** |
| q10 | speculative | 0.05 | no |
| q07 | bedrock | 0.75 | **yes** |
| q01 | bedrock | 0.86 | **yes** |
| q04 | bedrock | 0.88 | **yes** |

**Questions hitting p ≥ 0.70 (bedrock canon): q17, q07, q01, q04** — 4 of 5 drawn.
Cathedral qids drawn this round: q07, q01, q04 — all three ≥ 0.70.

**mean_p 0.6520** vs prev-12 mean 0.4520 = **+0.2000**. This is *draw mix*, not drift:
r402 drew 4/5 bedrock-band (the highest bedrock yield in the window) with a single low-band
control (q10 = 0.05), while the prev-12 window contains r391 (0.2220) and r395 (0.2820) at
1/5 and 1/5 cathedral each. **Per-qid |dev| among the 5 drawn qids maxes at 0.0175** — a
quarter of the 0.05 gate. **Decompose the aggregate before calling it drift** — the mean
moved, the instrument did not.

---

## Drift analysis (threshold |dev| > 0.05)

**No drawn qid cleared the 0.05 gate.** Max per-qid |dev| = **0.0175** (q17).

| qid | p_now | base_mean | dev | base_sd | z | base_max | new extreme? | gate |
|-----|-------|-----------|-----|---------|---|----------|--------------|------|
| q17 | 0.72 | 0.7025 | +0.0175 | 0.0140 | +1.25 | 0.74 | no | clear |
| q01 | 0.86 | 0.8749 | −0.0149 | 0.0092 | −1.62 | 0.90 | no | clear |
| q04 | 0.88 | 0.8888 | −0.0088 | 0.0087 | −1.01 | 0.91 | no | clear |
| q10 | 0.05 | 0.0669 | −0.0169 | 0.0050 | **−3.37** | 0.08 | no | clear |
| q07 | 0.75 | 0.7550 | −0.0050 | 0.0165 | −0.30 | 0.79 | no | clear |

**σ≈0 trap, 11th consecutive — rule held.** q10's z = **−3.37** is the round's largest z
and a textbook trap: base sd **0.0050** (near-degenerate), era4 sd 0.0043, value 0.05 sits
*inside* the historical range [0.05, 0.08], and |dev| 0.0169 is a third of the gate. The eye
catches the z; |dev| says nothing moved. **Check |dev| vs 0.05 FIRST — the largest z is
often the smallest real movement.** This rule has now survived 11 consecutive rounds.

All five drawn qids have **flat baselines** (era4 sd ≤ 0.0133) and **no new extremes** —
so even the "flat baseline + new extreme" candidate case never opened.

### The script's `drift_events=1` is a FALSE POSITIVE — the r232 finding, reproduced

`drift_check` (`jev_continuous_probe.py:317-335`) still has **no current-round filter**:

```python
recent_p = samples[-1][1]   # last SEEN draw for this qid, not this round's
prior_ps = [p for _r, p in samples[-(window + 1):-1]]
```

`per_round` is keyed by qid across the *entire* corpus, so for a qid not drawn this round,
`samples[-1]` is a **stale draw from an earlier round**, compared against its own prior-5
median. The single flag was:

| flagged qid | recent_p | from round | prior_median | delta | drawn in r402? |
|-------------|----------|-----------|--------------|-------|----------------|
| q12 | 0.51 | **r401** | 0.37 | +0.1400 | **NO** |

**The drawn-set intersection of the flags is EMPTY.** q12 was not drawn in r402 — the flag
is a double-counted echo of r401's 0.51, which was **already adjudicated and reported last
hour** (r233). This is the second consecutive false positive after r400, whose two flags
(q02 from r399, q12 from r398) were likewise stale echoes of adjudicated rounds.

**Rule (carried, now with two reproductions): `drift_events` from the script is a CANDIDATE
LIST requiring a drawn-set cross-check, not a verdict. Always intersect the flagged qids
with the round's sampled qids before believing one.** The counter is biased upward by the
number of un-drawn qids and can never report drift for a qid that *was* drawn — wrong in
both directions. Fix (behavioural change to a running instrument; still **not applied**):
filter `drift_check` to qids present in the current round's verdicts and exclude the
current draw from the baseline.

---

## Watches

### q12 plateau (spec-band) — no new data, confirmation test still pending

q12 was **not drawn** in r402, so the r233 discriminator stands unchanged:

- n = 89 draws, mean 0.3710, max 0.51, min 0.30.
- Draws ≥ 0.45 in the entire corpus: exactly **two** — r398 (0.50) and r401 (0.51).
- Last 10 draws: 0.36, 0.40, 0.38, 0.37, 0.35, 0.37, 0.40, 0.36, **0.50, 0.51**.
- **0 of 89 draws ≥ 0.70; bedrock hit-rate 0/89.** A 0.51 reading on a question that has
  *never* touched canon cannot erode canon.
- **r233's rule stands: the NEXT q12 draw is the confirmation test** — retreat to ≤ 0.40 ⇒
  two-draw spike; hold ≥ 0.45 ⇒ real plateau advance. Still pending.

### q02 erosion (bedrock/canon) — no new data, watch still tightening

q02 was **not drawn** in r402.

- recent29 mean **0.8176** vs the ~0.81 escalation threshold — margin 0.0076, still shrinking.
- 4-era means: 0.8305 → 0.8247 → 0.8258 → **0.8115**, era4 sd inflating to 0.0226.
- Draws ≤ 0.80 all-time = 9; ≤ 0.75 = **1** (r399 = 0.75).
- **Every q02 draw ever is ≥ 0.70** ⇒ bedrock hit-rate 77/77 = 100% ⇒ **no canon erosion.**
- Escalate only on a recent29 breach (< 0.81) or a second sub-0.75 draw. Neither has occurred.

---

## Cathedral

**603 cathedral draws, 603 hits — 100.00%, zero misses in the entire corpus.**
**339 consecutive green rounds** (r233 recorded 329; +10 across the intervening rounds).

*Reconciliation note:* no round ever draws all 7 cathedral qids — the probe draws 5 qids per
round against a 7-qid cathedral set, so "7/7" was always the *per-qid* hit-rate, not a
per-round count. The 339 figure is the count of rounds in which at least one cathedral qid
was drawn and every cathedral qid drawn that round hit. Both r233 ("329th") and this report
use that same cumulative-any-cathedral-draw basis, so the two are directly comparable.

---

## Corpus

- **393 distinct rounds / 1,965 verdicts / 22 qids**, grand mean_p **0.3827**.
- `history.jsonl` = **406 lines** vs 393 distinct ⇒ **duplicate-tail persists** (rounds
  384-391 appear 2-3×). `setdefault` (first-occurrence-wins) is the correct dedup and is
  what every number above uses.
- `history[-1].round == max(round) == 402` ⇒ **DEFECT B did not reproduce** (the r396
  round-counter gap bug remains fixed).
- Round files: 210 under `research/jev_sessions/` (r001-r402), plus a stale legacy
  `jev_sessions/` tree frozen at r395 — see Environment.

---

## Environment (120th wipe)

- **19th consecutive** ephemeral-path wipe — `/workspace/research/` absent at start; rebuilt
  the probe in `/tmp/jev_probe` from `SuperInstance/jev-quilt`.
- **NAS 600G/600G on an empty workspace (21st recurrence)** ⇒ **the requested output path
  `/workspace/research/jev_hourly_report.md` could NOT be written.** Reproduced the exact
  trap: the file **appeared in `ls` at 0 bytes** while the write returned **exit 1,
  "Disk quota exceeded"**; the `write` tool failed with **-122**. This report is therefore
  written to the repo's own `research/jev_hourly_report.md` and **committed** — the durable
  copy is git, as in prior rounds.
- **Stale-path trap (NEW, worth recording):** the repo carries **two** session trees —
  `research/jev_sessions/` (live, r396-r401 present) and a root-level `jev_sessions/`
  (legacy, **frozen at r395**). A depth-1 clone initially exposed only the legacy tree,
  making the corpus look like it stopped at r395 and contradicting the r401 commit
  message. Fix: **`git fetch --unshallow`** (300 commits) — `SESSION_DIR` in the script
  points at `research/jev_sessions/`, and the *root* `jev_sessions/` is dead weight. A
  depth-1 clone of this repo misreports the corpus tail; always unshallow before analysis.
- **TLS clean on first try** — curl 200 and Python 200 against `api.typesafe.ai` in the same
  second ⇒ no cert-anchor wall, no 289-cert bundle rebuild. **4th clean wipe**, confirming
  the curl-first triage rule is cheap insurance rather than ritual.
- `gh` absent (**11th wipe**); push via the explicit token URL, verified through the
  commits API.
- Script md5 `3a255fa4642ec4a83173ab04d773d485` unchanged **5th wipe**. All r229 fixes
  present (relative `SESSION_DIR`, positional `main(rounds_requested=)`, round counter from
  existing files, existence abort). Positional `1` ran **exactly one round** — no R-221
  overshoot.
- `TYPESAFE_AI_TOKEN` present and accepted via the `TYPESAFEAI_KEY` → `TYPESAFE_AI_TOKEN`
  fallback chain.
