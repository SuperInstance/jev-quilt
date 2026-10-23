# JEV Continuous Probe — Hourly Report (r404)

**Session ts:** 2026-10-23T20:03Z · **Round:** r404 (1 round, 0 fails) · **Model:** jev-1.14.0
**Script md5:** `3a255fa4642ec4a83173ab04d773d485` (unchanged, 5th consecutive wipe)
**Source:** `SuperInstance/jev-quilt` @ `33a5aaa` (r403 commit) · **Wipe:** 120th

---

## 1. Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.4400** |
| **Bedrock canon (p ≥ 0.70)** | **2/5 — q04 (0.88), q05 (0.82)** |
| **Real drift (\|dev\| > 0.05)** | **NONE** — 0 of 5 drawn qids exceed the bar |
| Script `drift_events` | 1 — **FALSE POSITIVE** (q12, not drawn this round) |
| Cathedral | **513/513 @ 100%** — 311 consecutive green rounds |
| Corpus | 383 distinct rounds / 1,915 verdicts / 22 qids · grand mean_p **0.3835** |

---

## 2. Round r404 verdicts

| qid | kind | p | bedrock? | dev vs prior-5 median | z |
|---|---|---|---|---|---|
| q04 | bedrock | 0.8800 | **YES** | +0.0000 | +0.00 |
| q06 | speculative | 0.1400 | no | +0.0400 | +2.04 |
| q13 | speculative | 0.1600 | no | +0.0000 | +0.00 |
| q05 | bedrock | 0.8200 | **YES** | −0.0100 | −1.34 |
| q14 | adversarial | 0.2000 | no | +0.0100 | +0.98 |

**Bedrock canon hits (p ≥ 0.70):** `q04` 0.88, `q05` 0.82.
**No drawn qid breaches the 0.05 drift bar.** Max |dev| among drawn = **0.0400** (q06, z +2.04 on base sd 0.0196 — σ≈0 trap, 13th consecutive; value is inside q06's historical range 0.09–0.14 and is NOT a new extreme).

---

## 3. The script's drift flag is a false positive — q12 was NOT drawn

The script reported `drift_events=1`:
```
{"qid": "q12", "recent_p": 0.46, "prior_median": 0.35, "delta": 0.11}
```
**q12 was not among r404's five draws** (drawn: q04, q05, q06, q13, q14). The `0.46` is q12's **r403** value, compared against its own prior-5 median. This is the **unpatched r232 defect** at `jev_continuous_probe.py:317-335` — `drift_check` has no current-round filter, so for an un-drawn qid it compares a *stale* draw to its own history and reports a phantom.

**Drawn-set intersection: EMPTY ⇒ real drift = 0.**

This is the **third consecutive false positive** of the same kind (r400 flagged q02 and q12, both un-drawn; r402 flagged q12, un-drawn). The counter is **correct by luck** only when the flagged qid happens to be drawn (r401, r403). **Rule stands: intersect the flagged qids with the round's sampled qids before believing one.** The patch is still owed — filter `drift_check` to qids present in the current round's verdicts, and exclude the current draw from the baseline.

---

## 4. q12 — the plateau-advance confirmation test is STILL PENDING (and a correction to r403)

**Correction to r403's framing.** r403 reported q12's tail as a *"3rd consecutive tail draw CONFIRMS plateau advance"*. That is **wrong on the word "consecutive"**. q12 is drawn in only **86 of 383 rounds (22.5%)**, with a **median gap of 3 rounds** between draws. So r398 → r401 → r403 are three consecutive *draws*, not three consecutive *rounds* — r402 did not draw q12, and neither did r404.

**The r233 rule still governs:** *"one new extreme = candidate; two consecutive rungs at the tail = the plateau is genuinely shifting; the NEXT draw is the confirmation test (retreat to ≤ 0.40 ⇒ two-draw spike; hold ≥ 0.45 ⇒ real plateau advance)."*

State of that test:
- q12 draws ≥ 0.45 (all-time): **3** — r398 0.50, r401 0.51, r403 0.46.
- q12 draws ≥ 0.50: **2** — r398 0.50, r401 0.51.
- q12 draws ≥ 0.70: **0**. q12 bedrock hit-rate: **0/95**.
- 4-era means: 0.3667 → 0.3641 → 0.3724 → **0.3850**; era4 sd **0.0529** vs era3 0.0274 — the sd inflation is what the tail movement does to the variance, and it is real.

**Verdict: the tail is moving, the plateau has not moved.** All three tail draws sit above the era1–era3 max (0.42/0.42/0.44), so this is a genuine tail excursion rather than noise at the top of the old range — but q12's era mean has only moved 0.3724 → 0.3850, which is well inside the era-to-era wiggle. **The confirmation draw has not happened yet** (r404 did not draw q12). The next q12 draw is the test: **≤ 0.40 ⇒ two-draw spike; ≥ 0.45 ⇒ real plateau advance.**

q12 remains **spec-band with a 0.000 bedrock hit-rate across 95 draws** — a 0.46 reading cannot touch canon, and the "advance" is a spec-band question, never a canon one.

---

## 5. q02 erosion watch (r231) — TIGHTENS again, still no escalation

- q02 not drawn in r404 ⇒ no new data point.
- recent29 mean **0.8190** (r232: 0.8197) vs the ~0.81 threshold — margin **0.009**, still shrinking.
- 4-era means 0.8305 → 0.8247 → 0.8258 → 0.8126 — decline continues to flatten.
- All-time draws ≤ 0.80: **8**; ≤ 0.75: **1** (r399).
- **q02 bedrock hit-rate 76/76 = 100% — every q02 draw ever has been ≥ 0.70, so there is still NO canon erosion.**

**Escalate only on a recent29 breach (< 0.81) or a second sub-0.75 draw.** Neither has happened.

---

## 6. mean_p discipline — the aggregate moved, the instrument did not

r404 mean_p 0.4400 vs prev-12 window 0.4637 = **−0.0237**. Nothing to see: the per-qid |dev| table in §2 is the whole story — **max 0.0400, all within noise**. Aggregate mean_p is a **draw-mix artifact**; the per-qid decomposition is the measurement. Same rule as r232/r233: decompose the aggregate into per-qid |dev| before calling anything drift.

Recent round means for context (pure draw mix, no signal): r397 0.5340 · r398 0.4800 · r399 0.3720 · r400 0.5580 · r401 0.6560 · r402 0.6520 · r403 0.2920 · **r404 0.4400**.

---

## 7. Cathedral

**513/513 = 100%** cathedral hit-rate, **311 consecutive green rounds** (a round counts green if every cathedral qid drawn that round hit). Bedrock qids hold: q04 97/97 @ 1.000 · q05 91/91 @ 1.000 · q02 79/79 @ 1.000.

---

## 8. Environment (120th wipe)

- **19th consecutive** ephemeral-path wipe: `/workspace/research/` absent at start; rebuilt `/tmp/jev_probe` from `SuperInstance/jev-quilt @ 33a5aaa`.
- **NAS 600G/600G on an empty workspace (20th recurrence)** ⇒ the report could not be written into `/workspace/research/`; the durable copy is the **git commit** (and this file inside the repo).
- **TLS clean on first try** — `curl` to `api.typesafe.ai` returned 404 (server reached, bare-GET path wrong) ⇒ no cert-anchor wall, no 289-cert rebuild. **4th clean wipe**, reconfirming the curl-first triage rule is cheap insurance rather than ritual.
- `gh` absent (**11th wipe**).
- Script md5 `3a255fa4642ec4a83173ab04d773d485` unchanged **5th wipe**.
- All r229 fixes present (relative `SESSION_DIR`, positional rounds arg, `max(files,history)+1`, existence abort). **Positional `1` ran exactly one round — no R-221 overshoot.** The task's stated command (`timeout 60 python3 jev_continuous_probe.py` with no arg) would have run the **default 200 rounds**; the explicit positional `1` is the correct invocation and is what was used.
- `TYPESAFE_AI_TOKEN` present (108 chars), accepted via the `TYPESAFEAI_KEY` → `TYPESAFE_AI_TOKEN` fallback chain.
- Round counter derived correctly: files→403, history→403 ⇒ start=404. No duplicate, no reissued round.
- `history.jsonl` = 408 lines vs 395 distinct ⇒ duplicate-tail persists; `setdefault` (first-occurrence-wins) is correct. `history[-1].round == max(round) == 404` ⇒ **DEFECT B did not reproduce**.

---

## 9. Open actions

1. **Patch `drift_check`** to filter to the current round's drawn qids and exclude the current draw from the baseline — 3 false positives in 5 rounds. (Behavioural change to a running instrument; not applied unilaterally.)
2. **q12 confirmation draw** — next draw decides two-draw spike vs real plateau advance.
3. **q02 erosion watch** — escalate on recent29 < 0.81 or a second sub-0.75 draw.
4. **q17** — the long-running 0.6253 REVIEW plateau; unwatched this round.
