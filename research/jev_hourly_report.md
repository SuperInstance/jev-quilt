# JEV continuous probe — r413 (2026-10-24T05:02Z)

**One round, exactly as asked** (positional `rounds=1` on the root instrument — not a launch-and-kill; the positional arg works, so no kill was needed and the run self-terminated in 0.3 s).
Probe: `jev_continuous_probe.py` (repo root), script md5 `3a255fa4642ec4a83173ab04d773d485` — **identical to r397–r412**, so mean_p is directly comparable with the hourly series.
Model: `jev-1.14.0` · API: `api.typesafe.ai/v1/systemone` · 0 fails · 0.14 s per round.

**Environment note (110th wipe).** `/workspace` was empty on arrival and the NAS quota read 100 % (`600G/600G` on an empty mount). The canonical report path `/workspace/research/jev_hourly_report.md` **could not be written**: writes return exit 0 but produce a **0-byte file** (verified with three independent methods — `printf`, shell redirect, and Python `open().write()`; all left 0-byte stubs). The stubs were deleted so they cannot masquerade as a delivered report. The probe was therefore cloned and run under `/tmp/jev-quilt` (**`/tmp` is not subject to the trap**), and the durable copy of this report and the round file is **git**. `SSL_CERT_FILE` was gateway-anchor-only again (10th recurrence) but strict verification still succeeded — the MITM leaf was valid (`notAfter=Dec 25 10:56:08 2026 GMT`), so no `-k` / `JEV_INSECURE_TLS` was needed. `gh` absent (13th wipe).

---

## Headline

| metric | value |
|---|---|
| rounds_ok | **1** (r413) |
| fails | **0** |
| **mean_p** | **0.4540** |
| verdicts | 5 |
| **p >= 0.70 hits** | **2 / 5** — `q03` 0.86, `q05` 0.82 |
| **drift > 0.05** | **NONE.** The script's single `drift_events=1` is a **PHANTOM** (q12, not drawn this round) |
| cathedral (bedrock canon) | **527/527 = 100 %** corpus-wide; **1.13.0: 497/497, 1.14.0: 30/30 — 100 % within each model version** |
| consecutive green rounds | **319** (rounds where >=1 cathedral qid was drawn and every drawn cathedral qid hit) |

**mean_p 0.4540 is mid-band, and the reason is draw composition, not health.** This round drew 2 of 7 bedrock questions (q03, q05) and 3 non-bedrock (q18 speculative, q14 + q19 adversarial). The hourly series r404–r413 reads 0.390, 0.294, 0.458, 0.438, 0.368, 0.418, 0.424, 0.552, **0.454**. Grand mean_p is draw-mix confounded at n=5 — health is the cathedral, not the mean.

---

## r413 verdicts

Baselines are **segmented by model version** (R-412 rule) — pooling 1.13.0 with 1.14.0 is what produced the false q14 alarm below.

| qid | kind | p | baseline (model-segmented) | dev | sigma | z | p>=0.70 |
|---|---|---|---|---|---|---|---|
| **q03** | **bedrock** | **0.86** | 0.8833 (n=6, 1.14.0) | -0.0233 | 0.0151 | -1.55 | **YES** |
| q18 | speculative | 0.23 | 0.2242 (n=100 pooled) | +0.0058 | 0.0098 | +0.59 | no |
| q14 | adversarial | 0.25 | 0.2220 (n=5, 1.14.0) | +0.0280 | 0.0192 | +1.46 | no |
| **q05** | **bedrock** | **0.82** | 0.8260 (n=5, 1.14.0) | -0.0060 | 0.0055 | -1.10 | **YES** |
| q19 | adversarial | 0.11 | 0.1050 (n=80 pooled) | +0.0050 | 0.0060 | +0.84 | no |

**Max |dev| among drawn = 0.0280 — 56 % of the 0.05 gate. NO REAL DRIFT.**

---

## The one thing worth reading: q14 looked like drift, and was not

Judged against a **pooled** (all-model) baseline, q14 reads mean 0.1943, so today's 0.25 gives **dev +0.0557, z = +4.07** — a textbook "drift > 0.05" flag. **It is an artefact of pooling across the r396 model boundary.** q14's 1.13.0 distribution is centred at 0.1925 (n=76, max 0.22) while its 1.14.0 distribution is centred at 0.2220 (n=5). Today's 0.25 against the **correct** 1.14.0 baseline is dev **+0.0280, z = +1.46**, the 80th percentile of q14's own |dev| distribution.

**This is R-412's DEFECT 5 in the wild, and it nearly produced a false headline.** The 1.14.0 shift on q14 is the same re-weighting the 1.14.0 model applied to q02/q12 — just below the 0.05 gate, so it is a *sub-threshold* version of a known model artefact, not a substrate movement.

**But one genuinely new fact:** **0.25 is q14's all-time maximum in an 81-sample history** (1 previous occurrence of >=0.24, ever). It is 1 of only 5 draws at that level, so a single observation — not a trend. Flagged as a **watch item**, not drift.

---

## The script's `drift_events=1` is a PHANTOM (4th reproduction)

The probe reported `drift_events=1`. Reproducing the script's own `drift_check()` against `history.jsonl`:

```
{'qid': 'q12', 'recent_p': 0.56, 'prior_median': 0.5, 'delta': 0.06}
drawn this round: ['q03', 'q18', 'q14', 'q05', 'q19']
   q12: DRAWN=False  -> PHANTOM (stale, not drawn)
```

q12 was last drawn in **r409** (0.56). It was **not drawn in r413**, so its +0.06 is a stale echo from four rounds back. This is the **4th reproduction** of the unpatched no-current-round-filter defect (r400, r402, r412, now r413) — and the r412 report was the first to show it both ways at once (a phantom q12 *and* a missed real q02 shift).

**Three defects remain unpatched in `drift_check()` (lines 317–335):**
1. **No current-round filter** — flags qids that were not drawn (phantom drift; 4 reproductions).
2. **5-sample local median instead of the full-history mean** — structurally cannot detect a slow shift (the reason r411 concluded "no real drift" for q02).
3. **No model-version segmentation** — pools 1.13.0 and 1.14.0 into one baseline, inflating every qid's apparent sigma and turning the q14 artefact above into a z=+4.07 "drift".

**Fix, if patching:** group history by `model`; compare each drawn qid against its **own model's** full-history mean; intersect flagged qids with `rounds[-1]["verdicts"]` before counting. The round file already stamps `model` per round, so all three fixes are free.

---

## Watch items carried forward

**1. q02 — still the fragile cathedral member (R-412 watch, still OPEN).** q02 was **not drawn** in r413, so the watch item stands unchanged: 6/6 canon on 1.14.0, samples 0.75, 0.77, 0.73, 0.71, 0.77, 0.71, **min = 0.71, margin above the 0.70 gate = +0.01**. Bootstrap 95 % CI on the 1.14.0 mean: **[0.7200, 0.7600]** (lower bound still above the gate). **If a 7th 1.14.0 draw lands at <= 0.70, the bedrock gate is breached and THAT is a substrate signal, not a model artefact.**

**2. The 1.14.0 boundary effect re-verified independently.** q02: 1.13.0 mean 0.8251 (n=74) -> 1.14.0 mean 0.7400 (n=6), delta **-0.0851**, bootstrap 95 % CI on the difference **[-0.1053, -0.0650] — excludes zero**. The doctrinal state and question bank are byte-identical across the boundary (script md5 unchanged since r397), so this is **oracle behaviour, not substrate change**. "JEV does not drift" holds **within** a model version, not across one.

**3. q12 stays SPECULATIVE despite the climb.** 1.14.0 draws: 0.50, 0.51, 0.46, 0.54, **0.56** (n=5, mean 0.5140, hit-rate 0 %). The R-222 rule — *next q12 draw at p >= 0.58 warrants a dedicated look* — is not yet triggered; q12 has not been drawn since r409. The state forbids promoting q10/q11/q12/q13 regardless of mean_p: a rising speculative score signals the probe edging toward an unratified claim, not a promotion.

**4. No speculative or adversarial qid has EVER reached p >= 0.70** in the whole 1,960-record corpus (max = q12's 0.56). The bouncer is still strict at the door.

---

## Corpus and method notes

**Corpus:** 222 round files scanned -> **1,960 records (deduped) / 22 qids**, grand mean_p 0.3844, model split **1,870 on `jev-1.13.0` / 90 on `jev-1.14.0`**.

**Method (R-222 / R-412 rules applied):**
- **Dedupe on exact `(qid, p, ts)`** — round numbers are *not* unique identifiers; two naming eras each restart their local counter at 1, so dedupe-by-round-number discards ~181 real observations.
- **Normalize short qids -> full qids** before merging (1:1 across all 22 qids, never mixed within a round).
- **Segment every baseline and every drift test by `model`** before comparing.
- **Judge |dev| against the 0.05 floor FIRST**, then sigma, then the qid's own |dev| distribution — a large z on a tiny sigma is the most misleading combination, not the least.
- **Cathedral built from the explicit qid list** (q01, q02, q03, q04, q05, q08), never from a `kind` tag.
- **Clone unshallowed first** — the repo carries two session trees (`research/jev_sessions/` LIVE, root `jev_sessions/` LEGACY frozen at r395) and a depth-1 clone exposes only the legacy one.

**`history.jsonl` note:** 417 lines vs 1,960 deduped records. `history.jsonl` and the round files disagree in scope — the round files are authoritative, `history.jsonl` fills gaps only. The script's own `per_question` counts (e.g. q02 n=83) pool model versions and therefore do not match the segmented n=74/6.

---

## Durable copy

- Round file: `research/jev_sessions/continuous_r413.json` (6,867 bytes) + `history.jsonl` append, committed to `SuperInstance/jev-quilt`.
- This report: `research/jev_hourly_report.md`, committed.
- `/workspace/research/jev_hourly_report.md` **could not be created** (0-byte stub on a 100 %-full NAS) — the stubs were deleted. Git is the durable copy.
