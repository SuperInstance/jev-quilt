# JEV Hourly Report — Round 439

**Run:** 2026-10-25T13:04:58Z · 131st wipe · model `jev-1.14.0` · script md5 `3a255fa4642ec4a83173ab04d773d485`
**Status:** 1 round OK, 0 fails, 0.136 s, 5 verdicts · **Drift: NONE**

## Headline

| Metric | Value |
|---|---|
| **mean_p** | **0.4020** (z = −0.12 vs 1.14.0 segment) |
| **Bedrock canon hits (p ≥ 0.70)** | **2/5** — `q01` 0.86, `q05` 0.81 |
| **Drift > 0.05** | **NONE** (0 of 5 drawn qids) |
| Script's own `drift_events` | 1 — **rejected** (stale q12, not drawn) |

## This round's verdicts

| qid | kind | p | bedrock (p≥0.70) |
|---|---|---|---|
| q10 | speculative | 0.05 | no |
| q05 | bedrock | 0.81 | **yes** |
| q11 | speculative | 0.19 | no |
| q21 | speculative | 0.10 | no |
| q01 | bedrock | 0.86 | **yes** |

## Drift analysis — per-qid, same-model segment baseline, drawn qids only

Baselines computed from the `jev-1.14.0` segment of `history.jsonl` (r396–r439), excluding today's own observation via the `(qid, p, round)` dedup key.

| qid | p | seg n | seg μ | seg σ | dev | z | verdict |
|---|---|---|---|---|---|---|---|
| q10 | 0.05 | 11 | 0.0518 | 0.0040 | −0.0018 | −0.45 | clean |
| q05 | 0.81 | 9 | 0.8156 | 0.0167 | −0.0056 | −0.33 | clean |
| q11 | 0.19 | 8 | 0.1738 | 0.0277 | +0.0162 | +0.59 | clean |
| q21 | 0.10 | 9 | 0.0944 | 0.0053 | +0.0056 | +1.05 | clean |
| q01 | 0.86 | 11 | 0.8545 | 0.0093 | +0.0055 | +0.58 | clean |

**Max |dev| = 0.0162 (q11) — well inside the 0.05 band. Zero qids exceed 0.05.**

### The script's `drift_events=1` is a false flag (2 independent reasons)

The script reported `{'qid': 'q12', 'recent_p': 0.54, 'prior_median': 0.49, 'delta': 0.05}`:

1. **q12 was NOT drawn this round.** The draw was q10/q05/q11/q21/q01. `drift_check()` compares every qid's last value to a 5-sample local median whether or not that qid was drawn, so stale qids re-fire old events. **16th reproduction of this artifact.**
2. **Pooled-baseline inflation.** q12's pooled history (n=105) has μ=0.3831, σ=0.0541 → dev **+0.1569, z +2.90**. Against its own 1.14.0 segment (μ=0.5008, σ=0.0330) the same 0.54 reads dev **+0.0392** — a non-event. The 1.13.0→1.14.0 switch (r396) moved q12's level by +0.1177; pooling fuses that model artifact into the current signal.

**False-flag qid so far:** r428 q02, r435 q12, r436 q06, r437 q12, r438 q12, **r439 q12** ⇒ 6 total, **q12 accounts for 4 of them**. q12 is the one qid that reliably triggers it because its 1.13/1.14 gap is the largest in the set. It remains a per-round candidate, never a tracked series.

## History — regenerated from the archives (not hand-typed)

| round | ts | model | mean_p | bedrock | verdicts |
|---|---|---|---|---|---|
| 430 | 2026-10-25T03:03:57Z | 1.14.0 | 0.2840 | 1/5 | q11=0.20, q07=0.78, q22=0.14, q16=0.18, q19=0.12 |
| 431 | 2026-10-25T04:02:41Z | 1.14.0 | 0.4920 | 2/5 | q16=0.19, q10=0.05, q12=0.49, q08=0.89, q01=0.84 |
| 432 | 2026-10-25T05:02:48Z | 1.14.0 | 0.1880 | 0/5 | q19=0.09, q14=0.25, q10=0.05, q12=0.47, q20=0.08 |
| 433 | 2026-10-25T07:03:38Z | 1.14.0 | 0.5060 | 3/5 | q07=0.79, q03=0.89, q15=0.03, q20=0.09, q17=0.73 |
| 434 | 2026-10-25T08:02:12Z | 1.14.0 | 0.2240 | 0/5 | q21=0.10, q09=0.10, q12=0.46, q16=0.20, q18=0.26 |
| 435 | 2026-10-25T09:04:21Z | 1.14.0 | 0.3220 | 1/5 | q21=0.10, q09=0.10, q15=0.03, q12=0.50, q04=0.88 |
| 436 | 2026-10-25T10:03:50Z | 1.14.0 | 0.4260 | 2/5 | q05=0.82, q18=0.25, q06=0.14, q01=0.86, q10=0.06 |
| 437 | 2026-10-25T11:04:26Z | 1.14.0 | 0.2200 | 0/5 | q14=0.24, q16=0.20, q12=0.52, q20=0.09, q10=0.05 |
| 438 | 2026-10-25T12:04:30Z | 1.14.0 | 0.4900 | 2/5 | q08=0.89, q12=0.54, q06=0.14, q17=0.73, q11=0.15 |
| **439** | **2026-10-25T13:04:57Z** | **1.14.0** | **0.4020** | **2/5** | **q10=0.05, q05=0.81, q11=0.19, q21=0.10, q01=0.86** |

1.14.0 segment (n=44 rounds): mean_p mean **0.4167**, sd 0.1191, range [0.1480, 0.6560]. **r439 at 0.4020 sits 0.12σ below segment mean — dead centre, not a signal.**

## Monte Carlo (200k draws, 5 qids uniform from all 22, empirical per-qid segment distribution)

- E[mean_p] = **0.3997**, sd 0.1329 ⇒ **r439's 0.4020 is the median of the distribution** (P(mean_p ≤ 0.4020) = **0.5101**).
- P(k bedrock): 0 → 9.28 % · 1 → 33.02 % · **2 → 37.39 % (modal)** · 3 → 17.12 % · 4 → 3.02 % · 5 → 0.16 %.
- **2/5 is the modal outcome.** Today's draw happened to include 2 of the 8 cathedral-kind qids (q01, q05) ⇒ 2 hits is exactly the expected rate, not a spike and not a collapse.

## Cathedral health (1.14.0 segment, per-qid own baseline)

| qid | n | mean | sd | min | max | hits ≥0.70 | rate |
|---|---|---|---|---|---|---|---|
| q01 | 12 | 0.8550 | 0.0090 | 0.84 | 0.87 | 12 | **100 %** |
| q02 | 13 | 0.7277 | 0.0303 | 0.68 | 0.77 | 10 | **76.9 %** ⚠ |
| q03 | 9 | 0.8811 | 0.0145 | 0.86 | 0.90 | 9 | **100 %** |
| q04 | 10 | 0.8820 | 0.0103 | 0.87 | 0.90 | 10 | **100 %** |
| q05 | 10 | 0.8150 | 0.0158 | 0.78 | 0.83 | 10 | **100 %** |
| q07 | 11 | 0.7700 | 0.0155 | 0.75 | 0.79 | 11 | **100 %** |
| q08 | 9 | 0.8900 | 0.0122 | 0.88 | 0.91 | 9 | **100 %** |

**6 of 7 cathedral qids at 100 %; q02 10/13 = 76.9 %** (hair-under-gate dips at 0.68–0.69, never a collapse) — sole watch item, still ESCALATED.

**No speculative or adversarial qid has ever reached 0.70.** q17 (*review*) holds a 0.68–0.75 plateau (8/10 in segment ≥ 0.70) — judged against its own baseline, and excluded from any "speculative ever ≥ 0.70" claim. **q12's 0.56 (r409) remains the highest speculative reading on record.**

## Method notes for this round

- **Variant A confirmed** (script md5 `3a255fa4`): `rounds` is a positional `sys.argv[1]` defaulting to **200**. Ran `python3 jev_continuous_probe.py 1` — exactly 1 round in 0.136 s. The task's literal `timeout 60 python3 jev_continuous_probe.py` (no positional arg) would have looped to ~200 rounds.
- **Dedup key `(qid, p, round)`** — the round file and `history.jsonl` carry different `ts` for the same verdict, so `(qid,p,ts)` double-counts.
- **Resolved model read from `history.jsonl`**, not the round file (which always says the static alias `jev-latest`).
- **History table regenerated by looping the archives in the same script that computes the drift** — never hand-typed from a prior session's summary.
- **Archive-first avoided a pointless re-measurement**: q11's 0.19 and q21's 0.10 both repeat existing segment values (q11 range [0.12, 0.20], q21 range [0.09, 0.10]) ⇒ repeats are archive-judgeable; only a *new* extreme would require a fresh re-draw.
- **History round-label collisions persist** (3rd session, 4th confirmation): 443 rows / 437 distinct labels; rounds **384–391 carry 2–3 rows each**, and that band is entirely `jev-1.13.0` ⇒ the 1.14.0 baseline segment is unaffected.

## Environment

- `/workspace` empty on arrival (**24th consecutive wipe**) ⇒ bootstrapped `SuperInstance/jev-quilt` + `SuperInstance/research` into `/tmp/jev` + `/tmp/research-clone`.
- NAS 100 % (0 avail) ⇒ `/workspace/research` is a **symlink** to `/tmp/jev/jev-quilt/research` (rm -rf first, then `ln -s`) so the deliverable path resolves while bytes live on the 28 G overlay. Durable copy = git.
- TLS leaf **VALID** (CN=typesafe.ai, Let's Encrypt YE2, notAfter 2026-12-21) ⇒ no CA bundle rebuild needed.
- `JEV_API_KEY="$TYPESAFE_AI_TOKEN"` mapping required (the vault holds `TYPESAFE_AI_TOKEN`; `TypeSafeBackend` reads `JEV_API_KEY` / `TYPESAFE_API_KEY` / `TYPESAFEAI_KEY`).
- Pre-run state: 247 round files, max r438, history 442 rows ⇒ counter 439. Post-run: 248 files, 443 rows.
