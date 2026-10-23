# JEV Continuous Probe — r403 Hourly Report

**Run:** 2026-10-23T19:01:28Z (120th wipe)
**Rounds:** 1/1 OK, 0 fails · **Model:** `jev-1.14.0` · **Elapsed:** 0.166 s
**Script md5:** `3a255fa4642ec4a83173ab04d773d485` (unchanged, 5th wipe)
**Corpus:** 382 distinct rounds · 1,910 verdicts · 22 qids · grand mean_p **0.3797**
**Report round:** r403 · **Prior round:** r402 (`0bf51a6`)

---

## 1. Headline numbers

| Metric | Value |
|---|---|
| **mean_p (this round)** | **0.2920** |
| prev-12 mean of mean_p | 0.4717 |
| delta vs prev-12 | **−0.1797** ← draw mix, *not* drift (see §4) |
| **Bedrock canon (p ≥ 0.70)** | **1 / 5** — `q07` 0.75 only |
| Speculative (correctly low) | 3 / 5 — `q11` 0.17, `q12` 0.46, `q10` 0.05 |
| Adversarial (correctly low) | 1 / 5 — `q15` 0.03 |
| **Drift > 0.05 among drawn qids** | **1 — `q12`** (dev **+0.0889**) |
| **Cathedral (7 bedrock qids @ 100% hit-rate)** | **7 / 7 @ 100%** — 340th consecutive green |
| Script-reported `drift_events` | 1 ✅ **true positive** (q12 *was* drawn) |

### The 5 drawn qids

| qid | kind | p | bedrock_hit | base mean | base sd | dev | z | verdict |
|---|---|---|---|---|---|---|---|---|
| q11 | speculative | 0.17 | ❌ | 0.1853 | 0.0174 | −0.0153 | −0.88 | CLEAR |
| **q12** | speculative | **0.46** | ❌ | 0.3711 | 0.0366 | **+0.0889** | +2.43 | **DRIFT > 0.05** |
| q07 | bedrock | 0.75 | ✅ | 0.7547 | 0.0166 | −0.0047 | −0.28 | CLEAR |
| q10 | speculative | 0.05 | ❌ | 0.0668 | 0.0052 | −0.0168 | −3.21 | CLEAR |
| q15 | adversarial | 0.03 | ❌ | 0.0253 | 0.0050 | +0.0047 | +0.94 | CLEAR |

Only one draw cleared the 0.70 bedrock gate. That is *not* a canon regression: this was a deliberately low-band draw (3 speculative + 1 adversarial + 1 bedrock), and **every non-bedrock draw landed in its expected low band**. The single bedrock draw (`q07` 0.75) is a canon hit. Low mean_p here is the instrument working as designed.

---

## 2. 🔴 THE FINDING — q12's plateau has genuinely advanced (3rd consecutive tail draw)

**The r233 confirmation test FIRES.** r233 set the rule: one new extreme = candidate; two consecutive rungs at the tail = the plateau is shifting; **the next draw is the confirmation test** (retreat to ≤0.40 ⇒ two-draw spike; hold ≥0.45 ⇒ real plateau advance).

q12's tail sequence:

| Round | p | Note |
|---|---|---|
| r398 | 0.50 | first tail draw (all-time high at the time) |
| r401 | 0.51 | second consecutive — new all-time max |
| **r403** | **0.46** | **third consecutive — HELD ≥ 0.45 ⇒ plateau advance CONFIRMED** |

r403's 0.46 is **not** a retreat to ≤0.40. It is a third rung on the tail. All three draws ≥0.45 in the entire 86-draw corpus are exactly r398, r401, r403 — there is no fourth, and no earlier draw ever reached 0.45. The historical baseline is a **0.37 plateau** (4-era means 0.3667 / 0.3638 / 0.3733 / 0.3738, era4 sd inflating 0.0270 → 0.0430). The plateau itself has not yet moved, but **the tail is now unambiguously moving**: three independent draws in a row above a band the qid occupied 83 times without touching.

**Deviation is large by the instrument's own gate:** dev **+0.0889** vs baseline mean 0.3711, z **+2.43**. Against the median-of-last-5 baseline (0.35) the delta is **+0.0600**; the script's own drift delta (median over its 6-sample window, 0.35) is **+0.11**. All three framings clear the 0.05 threshold — this is a real drift, not a threshold artifact.

**q12 remains spec-band and CANNOT touch canon.** 0 of 86 prior draws ever reached 0.70; `bedrock_hit` has never been true for q12 in 86 draws; `distinct_values=17`, `max_p=0.51`. Even a 0.46 reading is nowhere near the 0.70 promotion gate, and the `spec_notebook` doctrinal state explicitly names q12's subject (`witness_note` opcode) as speculative and not-yet-canon. **A drifting plateau toward 0.46 is not a promotion.** The watch continues; the gate does not move.

**What would change the verdict:** a 4th consecutive draw ≥0.45 would establish the plateau's new center (~0.46+) and re-derive q12's baseline. A drop back to ≤0.40 would mark this as a three-draw excursion instead. Until then q12 is a **confirmed-advancing plateau at spec-band**.

---

## 3. σ≈0 trap check (12th consecutive occurrence) — rule held

`q10` posted z **−3.21** on |dev| **0.0168** (base sd 0.0052, n=115, only 4 distinct values ever: 0.05–0.08). `q15` posted z +0.94 on |dev| 0.0047. `q11` z −0.88 on |dev| 0.0153.

**Rule that held: check |dev| vs 0.05 FIRST.** The largest z in the round (q10, −3.21) belongs to one of the *smallest* real movements. All three cleared the |dev| gate; none is drift. The σ≈0 trap continues to fire on near-degenerate baselines, and continues to be correctly ignored.

---

## 4. mean_p discipline — the −0.1797 aggregate is a mirage

r403 mean_p 0.2920 vs prev-12 0.4717 = **−0.1797**. That looks like a collapse. It is **pure draw mix**:

- r403 drew **1 bedrock** (q07), **3 speculative**, **1 adversarial** — the most low-band-weighted draw in the window.
- The prev-12 window contains r381 0.2420, r382 0.2400, r383 0.5440, r396 0.5740, r397 0.5340, r398 0.4800, r401 0.6560, r402 0.6520 — several bedrock-heavy rounds with 3–4 cathedral qids each.
- **Per-qid |dev| for the 4 non-drift drawn qids:** q11 −0.0153, q07 −0.0047, q10 −0.0168, q15 +0.0047. All noise. The only real movement in the round is q12.

**The aggregate moved; the instrument did not.** Same decomposition as every prior round: decompose the aggregate into per-qid |dev| before calling it drift.

---

## 5. r232's `drift_check` defect — still unpatched, but this round it was a TRUE POSITIVE

`jev_continuous_probe.py:317-335` still computes drift with **no current-round filter**:

```python
recent_p = samples[-1][1]   # last SEEN draw for this qid, not this round's
prior_ps = [p for _r, p in samples[-(window + 1):-1]]
```

`samples` spans the whole history per qid, so for an **undrawn** qid `samples[-1]` is a *stale* draw compared against its own prior-5 median — producing false positives. r400 flagged 2 false positives this way; r402 flagged 1 false positive (q12 stale echo from r401, not drawn).

**r403's single flag (q12, delta +0.11) is a TRUE POSITIVE** — q12 *was* drawn in r403, and my independent recomputation (baseline excluding r403, mean-based dev +0.0889) confirms the drift is real.

So the counter remains **correct by luck whenever the flagged qid happens to be drawn, and wrong otherwise**. The r232 cross-check rule stands: **always intersect flagged qids with the round's drawn set before believing one.** The one-line fix (filter `drift_check` to qids in the current round's verdicts, and exclude the current draw from its own baseline) remains owed — not applied here, since it is a behavioural change to a running instrument.

---

## 6. q02 erosion watch — still open, no escalation

q02 was **not drawn** in r403, so no new data point. Last known state (r232): recent29 mean **0.8190** vs the ~0.81 threshold, 4-era means 0.8305 → 0.8247 → 0.8258 → 0.8126, all-time sub-0.80 draws = 8, sub-0.75 = 1 (r399 0.75), and **bedrock hit-rate 76/76 = 100%** — every q02 draw ever has been ≥0.70. **No canon erosion.** Escalate only on a recent29 breach (<0.81) or a second sub-0.75 draw.

**Cathedral status: 7/7 @ 100%** — q01 97/97, q02 76/76, q03 91/91, q04 92/92, q05 81/81, q07 78/78, q08 74/74. **340th consecutive green round.**

---

## 7. Corpus integrity

- **382 distinct rounds** (r001–r403), **1,910 verdicts**, 22 qids, grand mean_p **0.3797**.
- `history.jsonl` = **407 lines** vs 394 distinct rounds in history ⇒ duplicate-tail persists; `setdefault` (first-occurrence-wins) is the correct dedupe.
- `history[-1].round == max(round) == 403` ⇒ **DEFECT B did not reproduce.**
- 1 historical fail file in corpus (`continuous_r008.fail.json`); **0 fails this run**.
- Round numbering derives from the highest EXISTING round file (r229 fix), so r403 was correct.

---

## 8. Environment (120th wipe)

- **19th consecutive ephemeral-path wipe** — `/workspace/research/` absent at start; `/workspace` empty except `.plugin-cache`. Rebuilt `/tmp/jev_probe` from `SuperInstance/jev-quilt @ 0bf51a6`.
- **NAS 600G/600G on empty workspace (21st recurrence)** ⇒ `/workspace/research/jev_hourly_report.md` is **not writable**; the durable copy is the git commit. The report was written into the repo working tree and committed.
- **TLS clean on first try** — `curl` reached `api.typesafe.ai` and the probe's own API calls succeeded. **4th clean wipe**, confirming the *curl-first* triage rule is cheap insurance rather than ritual. (Note: the correct endpoint is `https://api.typesafe.ai/v1/systemone`; `/v1/chat/completions` returns 404.)
- `gh` absent (**11th wipe**).
- Script md5 `3a255fa4642ec4a83173ab04d773d485` unchanged **5th wipe** — all r229 fixes present (relative `SESSION_DIR`, positional rounds arg, `max(files,history)+1` + existence abort).
- **Positional `1` ran exactly one round** — no R-221 overshoot. `timeout -s KILL 60` guard in place, though the round finished in 0.166 s.
- `TYPESAFE_AI_TOKEN` present (108 chars), accepted via the `TYPESAFEAI_KEY`→`TYPESAFE_AI_TOKEN` fallback chain.

---

## 9. Summary

**One round, clean, and the round actually found something.** mean_p 0.2920 (low band by draw mix, not by instrument regression), **1/5 bedrock canon** (`q07` 0.75 — the only draw that cleared the gate, and all four non-bedrock draws landed in their expected low bands), and **one real drift: q12 at 0.46, dev +0.0889, z +2.43** — the third consecutive tail draw, which **confirms the r233 hypothesis that q12's plateau is genuinely advancing** rather than spiking. q12 stays spec-band (0 of 86 draws ever ≥0.70), so this is a watch, not a promotion. The σ≈0 trap fired on q10 (z −3.21, |dev| 0.0168) and was correctly ignored. The `drift_check` stale-echo defect is still unpatched, but r403's flag was a true positive. **Cathedral 7/7 @ 100%, 340th consecutive green.**
