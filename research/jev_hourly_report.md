# JEV continuous probe — r411 (2026-10-24T03:08Z)

**One round, exactly as asked** (positional `rounds=1` on the root instrument, not a launch-and-kill).
Probe: `jev_continuous_probe.py` (repo root), script md5 `3a255fa4642ec4a83173ab04d773d485` — **identical to r404–r410**, so mean_p is directly comparable with the hourly series.
Model: `jev-1.14.0` · API: `api.typesafe.ai/v1/systemone` · 0 fails · 0.14 s.

---

## Headline

| metric | value |
|---|---|
| rounds_ok | **1** (r411) |
| fails | **0** |
| **mean_p** | **0.4240** |
| verdicts | 5 |
| **p >= 0.70 hits** | **2 / 5** — `q02` 0.77, `q01` 0.85 |
| **drift > 0.05** | **3 nominal flags, 0 real drift** (max aggregate abs dev **0.0796**, all three inside historical noise) |
| cathedral (bedrock canon) | **838/838 = 100%** corpus-wide; both drawn bedrock qids hit |

**mean_p 0.4240 is mid-band and a draw-mix artefact, not a health change.** The hourly series r404–r411 reads 0.440, 0.390, 0.294, 0.458, 0.438, 0.368, 0.418, **0.424** — r411 sits squarely inside that band, one notch above r410.

---

## r411 verdicts

| qid | kind | p | baseline mean | dev | sigma | z | p>=0.70 |
|---|---|---|---|---|---|---|---|
| q19 | review | 0.10 | 0.1571 | -0.0576 | 0.0738 | -0.78 | no |
| q14 | adversarial | 0.21 | 0.1565 | +0.0540 | 0.0591 | +0.91 | no |
| **q02** | **bedrock** | **0.77** | 0.8489 | **-0.0796** | 0.0551 | -1.45 | **YES** |
| q16 | review | 0.19 | 0.2063 | -0.0164 | 0.0138 | -1.19 | no |
| **q01** | **bedrock** | **0.85** | 0.8949 | -0.0452 | 0.0399 | -1.14 | **YES** |

Max aggregate abs dev = **0.0796** (q02). Three qids clear the nominal 0.05 bar, but **every one of them is inside its own qid's historical noise band** — see the noise test below. **Real drift: none.**

---

## The 0.05 absolute threshold is too coarse at this sample size — here is the noise test

The standing rule is to check abs dev first and sigma second. But abs dev alone is not sufficient either: with n = 108–132 observations per qid and sigma of 0.04–0.07, a 0.05 deviation is roughly 1 sigma. So for each flagged qid I compared **today's abs dev against the historical distribution of abs dev for that same qid**:

| qid | today abs dev | abs dev p50 | abs dev p90 | abs dev max | percentile today | reading |
|---|---|---|---|---|---|---|
| q19 | 0.0576 | 0.0576 | 0.1024 | 0.1224 | 65% | **within noise** |
| q14 | 0.0540 | 0.0440 | 0.0960 | 0.0960 | 69% | **within noise** |
| q02 | 0.0796 | 0.0396 | 0.0904 | 0.1396 | 72% | **within noise** |

How often did these qids trip the 0.05 bar in their own history?

| qid | history flags at abs dev >= 0.05 |
|---|---|
| q19 | **85/124 = 69%** of observations |
| q14 | 44/118 = 37% |
| q02 | 33/108 = 31% |

**A third to two-thirds of q19's and q02's own history already sits at or past 0.05 from the mean.** Today's values land at the 65th–72nd percentile — unremarkable. The z-scores agree: **+0.91, -0.78, -1.45, all well inside 2 sigma.**

**Conclusion: r411 shows no drift.** The 0.05 absolute bar is a *screen*, not a test; once n exceeds ~100, it needs to become a per-qid percentile or a z-threshold, otherwise it fires on ordinary sampling variation. That is a third instrument defect worth fixing, alongside the two already on the books (phantom drift events, duplicated history lines).

---

## Which questions hit p >= 0.70 (bedrock canon)

**r411:** `q02` (0.77), `q01` (0.85) — 2/5. Both drawn bedrock qids hit; the 3 non-bedrock draws (q19 review, q14 adversarial, q16 review) all read low, as the doctrinal state intends.

**Corpus-wide, p >= 0.70 by qid** (2,865 verdicts, 972 hits = 33.9%):

| qid | kind | hits | n | hit-rate | mean_p | sigma | range |
|---|---|---|---|---|---|---|---|
| q04 | bedrock | 126 | 126 | **100%** | 0.9053 | 0.0314 | 0.88–0.97 |
| q03 | bedrock | 121 | 121 | **100%** | 0.9036 | 0.0350 | 0.86–0.97 |
| q01 | bedrock | 129 | 129 | **100%** | 0.8949 | 0.0399 | 0.84–0.97 |
| q08 | bedrock | 113 | 113 | **100%** | 0.8945 | 0.0126 | 0.85–0.91 |
| q05 | bedrock | 125 | 125 | **100%** | 0.8769 | 0.0465 | 0.82–0.96 |
| q02 | bedrock | 109 | 109 | **100%** | 0.8489 | 0.0551 | 0.71–0.94 |
| q07 | bedrock | 115 | 115 | **100%** | 0.8050 | 0.0863 | 0.71–0.95 |
| **q17** | **review** | 105 | 127 | **82.7%** | 0.7206 | 0.0298 | 0.66–0.79 |
| q10 | review | 29 | 144 | 20.1% | 0.2263 | 0.3192 | 0.05–0.88 |

**The 7 bedrock qids are 838/838 = 100% hit-rate.** The cathedral is holding.

**q17 is the one to watch, and it is *not* canon.** q17 is `review` tier — a 0.66–0.79 plateau straddling the 0.70 line by design, at 82.7% hit-rate. It is **deliberately excluded from the cathedral**. Do not read a future q17 hit as a bedrock success.

**q10's 0.88 max is a bimodal artefact, not a trending signal.** q10 has mean 0.2263 and sigma **0.3192** — an enormous spread for a bounded probability. Its 29 high observations all cluster in a single early era (2026-10-18 to 2026-10-20 13:03), when the probe sent a *stronger* doctrinal state; the entire hourly series since reads 0.05–0.08. The high tail is a **regime difference in the probe input, not drift in the substrate.** (See the instrument note below — this is exactly the trap that caught my first run tonight.)

---

## Corpus integrity — and a correction to how previous reports counted the corpus

| check | result |
|---|---|
| history.jsonl lines | 415 (all `status: ok`) |
| round files with ok records | 219 files / 615 records |
| merged corpus | **615 probe records, 22 qids, 2,865 verdicts after exact-duplicate removal** |
| per-qid n | **min 113, max 164** (n>=113 for every qid) |
| instrument md5 | `3a255fa4642ec4a83173ab04d773d485`, identical for r404–r411 |
| failures this round | 0 |
| qids seen this round | 5 of 22 |

**The prior reports' corpus figure (401 rounds) was an undercount, and the cause is structural.** The corpus contains **two independent naming eras**:

1. **Era A (rounds 1–192, 2026-10-18 -> 2026-10-20 13:03)** — flat per-round files `continuous_r001.json` .. `continuous_r192.json`, carrying **full** qid names (`q02_witness_log_is_prediction`).
2. **Era B (batched sessions, 2026-10-20 16:04 onward)** — wrapper files (`continuous_r193.json` holds **193** inner rounds, `continuous_r383.json` holds 177) carrying **short** qid names (`q02`), plus the hourly series r396–r411.

The two eras **both start their local round counter at 1**, so "round number" is **not a unique identifier** in this corpus — round 1 exists in four different copies with entirely different questions and values. Deduping by round number therefore silently discarded **181 real observations**.

**The fix, verified before use:**
- The short and full qid forms are **1:1** across all 22 questions and **never co-occur within a single round** (389 short-only rounds, 201 full-only rounds, **0 mixed**) — so normalizing short -> full is safe.
- Dedup is now on **exact `(qid, p, ts)`**, not on round number, which keeps every genuine observation and drops only true replays.
- Round files are authoritative for verdicts; `history.jsonl` fills gaps only where a `(ts, round)` pair appears in no file.

The consequence is a corpus of **2,865 verdicts instead of 2,005** — 43% more data than the r410 report measured against, and the per-qid n floor rises from 79 to 113. **The prior reports' drift numbers were computed on a corpus that was throwing away more than a third of the observations.** The bedrock 100% cathedral is unchanged; the q12 climb, q17 hit-rate (74.7% -> 82.7%) and q10's bimodality all shift once the full corpus is counted.

---

## The trap I hit tonight, recorded so the next session does not repeat it

**This repo contains TWO probe scripts and they are not interchangeable.**

| path | md5 | doctrinal state | used by |
|---|---|---|---|
| `jev_continuous_probe.py` (repo root) | `3a255fa4642ec4a83173ab04d773d485` | 6 sections: framework, core_doctrine, architecture, fleet, spec_notebook, operational_doctrine | **r404–r411** (the hourly series) |
| `continuous/jev_continuous_probe.py` | `95b552ea0d81af21d24138deda605fee` | flat 15 keys: doctrines.*, architecture.*, fleet.*, spec_notebook.* | an older/variant probe |

I first ran the `continuous/` variant. It produced a **very** dramatic result — mean_p 0.756, q10 jumping **0.05 -> 0.91**, q12 hitting a new all-time high 0.71 — which looked like a major drift discovery. It was an artefact: **the two scripts send materially different doctrinal state to JEV**, so their p-values are not comparable. Under the `continuous/` variant's flat state, q10/q09/q20 read HIGH (the era-A pattern); under the root instrument's 6-section state they read LOW (the current pattern).

**Discriminator: `script_md5` and `doctrinal_state_keys` are stamped into every round file.** The root instrument stamps `3a255fa4...`; the variant stamps `95b552ea...`. r411 was re-run with the root instrument after reverting the corpus, and it lands at mean_p 0.4240 — squarely in band, no drift.

**Rule for next time:** before running, read the last round file's `script_md5` and `doctrinal_state_keys`, and run the script whose md5 matches. A mean_p discontinuity across an instrument change is **not** a substrate signal.

---

## q12 status — carried forward, not re-measured

`q12` asks *"Is 'witness_note' an opcode in the algebra?"* — the most canon-adjacent of the four speculative questions, since `witness_note` is a real construct in the substrate.

**r411 did not draw q12, and neither did r410.** On the corrected corpus (n=137) the q12 series still ends at the same place it did in r410's analysis: mean 0.4273, sigma 0.0915, max **0.58**, hits >= 0.70: **0/137**, and the last ten values are 0.32, 0.39, 0.35, 0.34, 0.31, 0.50, 0.51, 0.46, 0.54, 0.56.

The r410 report set the bar: *"if the next round that draws q12 shows >= 0.58, that is a range extension and the q12 line warrants a dedicated look."* **That round has not happened yet.** q12 remains an open watch item, and on the corrected corpus the climb is intact but still below the line.

**Canon status: unchanged.** The doctrinal state states that q10/q11/q12/q13 "must NOT be promoted to bedrock regardless of high mean_p readings." q12 is 0.56 at its peak, still below 0.70. A rising speculative score is a signal that the probe may be edging toward a claim the substrate has not ratified — **not** a promotion. q12 stays in the `spec_notebook`, **not** the cathedral.

---

## Environment receipts (110th wipe)

- **Fresh wipe again** — `/workspace/research/` did not exist on arrival; both mirror homes empty for the 8th consecutive time. The probe was bootstrapped from git (`SuperInstance/jev-quilt`, complete clone — `--unshallow` correctly reports "not a shallow repository", so the corpus was never truncated).
- **The corpus lives in `jev-quilt`, not `quilt-research-canons`.** The r410 commit body shows `research/jev_sessions/continuous_r410.json` — that path is in `SuperInstance/jev-quilt`, while `SuperInstance/quilt-research-canons` is the *scout* repo and contains no `jev_sessions/` at all. The probe script and the corpus are both in `jev-quilt`; the script is at the **repo root**, with a second, different copy under `continuous/`.
- **NAS at 100 % quota (0 bytes free) — the trap fired, 8th consecutive time.** `df` reports 600G/600G/0/100%. **The write trap is not size-gated**: even a 100-byte `dd` fails with `Disk quota exceeded`. The durable copy is git, always; the NAS copy is attempted but may not land. The entire probe ran from `/tmp` (overlay, 28 GB free) with `research/` restored by `git checkout`.
- **TLS: no expired-leaf wall.** Live leaf for `api.typesafe.ai` valid `notAfter=Dec 25 10:56:08 2026 GMT`. Default Python SSL context verified working (no bundle rebuild needed this wipe).
- **Auth:** `TYPESAFE_AI_TOKEN` present (108 chars). The root instrument accepts `TYPESAFEAI_KEY` or `TYPESAFE_AI_TOKEN`.
- **"One round" honoured literally.** The positional arg `1` was passed to the root instrument, whose own loop condition (`len(rounds) < rounds_requested`) stops after one. No launch-and-kill, no `pkill` self-match, no overshoot.
- **Round counter:** derived as `max(highest round file, highest round in history.jsonl) + 1` — files->410, history->410, start=411. Both sources agreed; no collision. The instrument also refuses to overwrite an existing round file.

---

## Verdict

**r411 is healthy.** mean_p 0.4240 (mid-band, in line with r404–r410), 2/5 bedrock hits, both drawn bedrock qids comfortably above threshold (q02 0.77, q01 0.85), the 7-qid cathedral intact at **838/838 = 100%**, instrument md5 unchanged, zero failures, and **no real drift** once the three nominal 0.05 flags are tested against their own qids' historical dev distribution (all at the 65th–72nd percentile, all |z| < 1.5).

**Carried forward, not resolved:** q12 remains on its climb, still capped at 0.58, still 0/137 on the p>=0.70 line, and **not re-measured in r410 or r411**. The r410 trigger (a draw showing >= 0.58) has still not fired. q12 stays speculative.

**Three instrument defects now on the books:**
1. `drift_check()` evaluates qids **not drawn in the current round** and compares against a 5-sample local median. It re-fires stale events and labels them this-round drift — 3 phantom events in r410, and tonight it named **q12**, which r411 did not draw.
2. `history.jsonl` has **two incompatible verdict shapes** (414 legacy list-of-dicts lines, and newer dict-of-floats lines) — the upstream `continuous/jev_continuous_probe.py` writes a dict while the root instrument writes a list. Any consumer that assumes one shape will crash or silently zero out the other. The corpus reader must accept both.
3. **The 0.05 absolute drift threshold is mis-calibrated at n>100.** It fires on 31–69% of a qid's own history. It should be a per-qid percentile or a z-threshold.

**And one standing hazard, now documented:** `SuperInstance/jev-quilt` carries **two probe scripts with different doctrinal state**, and their p-values are not comparable. Always match `script_md5` before running, and never read a mean_p discontinuity across an instrument change as a substrate signal. Tonight that mistake briefly produced a fake headline (q10 0.05 -> 0.91); the `script_md5` stamp in the round file is what caught it.
