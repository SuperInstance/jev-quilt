# JEV Continuous Probe — Hourly Report (r405)

**Session ts:** 2026-10-23T21:03Z · **Round:** r405 (1 round, 0 fails) · **Model:** jev-1.14.0
**Script md5:** `3a255fa4642ec4a83173ab04d773d485` (unchanged, 6th consecutive wipe)
**Source:** `SuperInstance/jev-quilt` @ `14aebbb` (r404 commit) · **Wipe:** 121st

---

## 1. Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.3900** |
| **Bedrock canon (p ≥ 0.70)** | **2/5 — q03 (0.88), q17 (0.70)** |
| **Real drift (\|dev\| > 0.05)** | **NONE** — 0 of 5 drawn qids exceed the bar; max \|dev\| = 0.0200 |
| Script `drift_events` | 1 — **FALSE POSITIVE** (q12, not drawn this round) |
| Cathedral | **332/332 @ 100%** — 312 consecutive green rounds |
| Corpus | 391 distinct rounds / 1,955 verdicts / 22 qids · grand mean_p **0.3830** |

---

## 2. Round r405 verdicts

| qid | kind | p | bedrock? | dev vs prior-5 median | z |
|---|---|---|---|---|---|
| q03 | bedrock | 0.8800 | **YES** | −0.0100 | −1.12 |
| q19 | adversarial | 0.1000 | no | +0.0000 | +0.00 |
| q16 | review | 0.1900 | no | −0.0100 | −2.50 |
| q20 | speculative | 0.0800 | no | −0.0200 | −1.09 |
| q17 | review | 0.7000 | **YES** | +0.0000 | +0.00 |

**Bedrock canon hits (p ≥ 0.70):** `q03` 0.88, `q17` 0.70.
**No drawn qid breaches the 0.05 drift bar.** Max |dev| among drawn = **0.0200** (q20). Every dev is ≤ 0.02, i.e. all five verdicts land inside their own historical range.

**q17 note:** 0.70 is *exactly* the threshold and the script's `bedrock_hit` is `p >= 0.70`, so it counts as a hit. q17 is the one borderline qid in the corpus — mean 0.7029, 58/78 draws ≥ 0.70 (74.4%), and its 12 sub-0.70 draws all sit in a narrow 0.66–0.69 band. It is a genuine 74% hit-rate qid, not a threshold artifact, but it should not be read as a strong canon signal the way q01–q05 are (100% hit-rate, 0.84–0.91 band).

---

## 3. The script's drift flag is a false positive — q12 was NOT drawn

The script reported `drift_events=1`:
```
{"qid": "q12", "recent_p": 0.46, "prior_median": 0.35, "delta": 0.11}
```

But r405 drew **`q03, q19, q16, q20, q17`** — **q12 was not drawn.** The 0.46 is q12's **r403** value echoing forward; the unpatched defect at `jev_continuous_probe.py:317-335` (`drift_check` has no current-round filter) strikes again.

**Drawn-set intersection is EMPTY ⇒ real drift 0.**

Flag-history for this defect: r400 (q02+q12, both un-drawn), r402 (q12, un-drawn), r404 (q12, un-drawn), **r405 (q12, un-drawn)**. It has been correct only by luck whenever the flagged qid happened to be drawn (r401, r403). Patch still owed: filter `drift_check` to the round's sampled qids and exclude the current draw from its own baseline.

**Rule unchanged and now 5-for-5: intersect flagged qids with the round's sampled qids before believing one.**

---

## 4. q12 confirmation test — STILL PENDING

The r233 rule: *one new extreme = candidate; two consecutive rungs at the tail = the plateau is genuinely shifting; the next draw is the confirmation test* (retreat to ≤0.40 ⇒ two-draw spike; hold ≥0.45 ⇒ real plateau advance).

| q12 draw | value |
|---|---|
| r398 | 0.50 |
| r401 | 0.51 |
| r403 | 0.46 |
| r405 | **not drawn** |

All-time tail draws ≥0.45 = 3 (r398, r401, r403). ≥0.50 = 2. ≥0.70 = 0. Era means **0.3667 → 0.3641 → 0.3724 → 0.3850**; era4 sd **0.0529** vs era3 0.0274. The tail is moving; the plateau is not yet.

**The confirmation draw is still pending** — r405 did not draw q12. Note also that q12 is drawn in only **86/391 rounds (22.0%)**, median gap ~3 rounds, so "consecutive draws" ≠ "consecutive rounds" (the r234 correction). Always state the draw-gap before calling a run consecutive.

q12 bedrock hit-rate is **0/86** — spec-band, so no reading of q12 can touch canon regardless of outcome.

---

## 5. q02 erosion watch — TIGHTENS, no escalation

q02 was **not drawn** in r405 (no new data point).

- recent29 mean **0.8190** vs ~0.81 threshold — margin **+0.0090** (r232: 0.8197 — margin shrinking).
- 4-era means **0.8300 → 0.8247 → 0.8258 → 0.8126**; era4 sd inflating 0.0135 → 0.0227.
- All-time draws ≤0.80 = **8** (r140/r171/r184/r210/r315 at 0.80; r329 0.79; r399 0.75; r401 0.77); ≤0.75 = **1** (r399 0.75).
- **q02 bedrock hit-rate 75/75 = 100%** — every q02 draw ever has been ≥ 0.70, so there is still **NO canon erosion**.

**Escalate only on a recent29 breach (< 0.81) or a second sub-0.75 draw.**

---

## 6. mean_p discipline — the −0.0753 aggregate is draw mix

r405 0.3900 vs prev-12 0.4653 = **−0.0753**. This looks like a drop; it is not one. The aggregate is a function of *which questions got sampled*, and r405 drew **no bedrock-kind question except q03** (q19 adversarial, q16/q17 review, q20 speculative), while the 12-round window contains r401 0.6560 and r402 0.6520, both of which drew multiple bedrock-kind questions.

Per-qid dev on the five drawn qids: q03 −0.0100, q19 +0.0000, q16 −0.0100, q20 −0.0200, q17 +0.0000 — **all noise, max |dev| 0.0200**.

**The aggregate moved; the instrument did not.** Always decompose mean_p into per-qid |dev| before reading anything into it.

---

## 7. σ≈0 trap — not triggered this round

The largest z among drawn qids is q16 at **−2.50 on |dev| 0.0100** (base sd 0.0040). |dev| 0.0100 ≤ 0.05, and 0.19 sits squarely inside q16's historical range 0.18–0.22. **Not a new extreme, no movement.** The rule held: check |dev| vs 0.05 FIRST — the largest z is often the smallest real movement.

---

## 8. Cathedral

**332/332 rounds containing a bedrock-kind question had every bedrock verdict hit — 100%.** That is the **312th consecutive green round**. r405's single bedrock-kind question (q03 0.88) hit.

---

## 9. Corpus

- 391 distinct rounds / 1,955 verdicts / 22 qids; grand mean_p **0.3830**.
- All-time bedrock: 647/1,955 = 33.1% (driven by draw mix — most rounds sample low-band questions).
- `history.jsonl` = 409 lines vs 391 distinct rounds ⇒ duplicate-tail persists; `setdefault` (first-occurrence-wins) is the correct read.
- `history[-1].round == max(round) == 405` ⇒ **DEFECT B did not reproduce.**
- 0 fail files added this round (1 historical fail in corpus).

---

## 10. Environment (121st wipe)

- **20th consecutive ephemeral-path wipe** — `/workspace/research/` absent at start; rebuilt `/tmp/jev_probe` from `SuperInstance/jev-quilt @ 14aebbb`.
- **NAS 600G/600G on an empty workspace (22nd recurrence)** ⇒ the report is written into the repo working tree and committed; the durable copy is git, not the NAS.
- **TLS clean on first try** — `curl api.typesafe.ai` → 404 (server reached, bare-GET path wrong) and Python → 404 in the same second ⇒ no cert-anchor wall, no 289-cert rebuild. **5th clean wipe**, confirming the curl-first triage is cheap insurance.
- `gh` absent (**12th wipe**).
- Script md5 `3a255fa4642ec4a83173ab04d773d485` unchanged **6th wipe**; all r229 fixes present (relative `SESSION_DIR`, positional rounds arg, `max(files,history)+1`, existence abort).
- **Positional `1` ran exactly one round — no R-221 overshoot.** The task's literal command (`timeout 60 python3 jev_continuous_probe.py`, no arg) would have run the **default 200 rounds**; always pass the explicit positional count.
- `TYPESAFE_AI_TOKEN` present, accepted via the `TYPESAFEAI_KEY`→`TYPESAFE_AI_TOKEN` fallback chain.
