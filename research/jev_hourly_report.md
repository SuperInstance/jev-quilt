# JEV continuous probe — r410 (2026-10-24T02:02Z)

**One round, exactly as asked** (positional `rounds=1`, not a launch-and-kill).
Probe: `jev_continuous_probe.py`, script md5 `3a255fa4642ec4a83173ab04d773d485` (unchanged since r405 — same instrument, so mean_p is comparable).
Model: `jev-1.14.0` · API: `api.typesafe.ai/v1/systemone` · 0 fails · 0.17 s.

---

## Headline

| metric | value |
|---|---|
| rounds_ok | **1** (r410) |
| fails | **0** |
| **mean_p** | **0.4180** |
| verdicts | 5 |
| **p >= 0.70 hits** | **2 / 5** — `q08` 0.91, `q05` 0.83 |
| **drift > 0.05** | **NONE in r410** (max aggregate abs dev **0.0203**) |
| cathedral (bedrock canon) | **0/2 drawn bedrock qids missed** — both bedrock qids drawn hit >= 0.83 |

**mean_p 0.4180 sits mid-band and is a draw-mix artefact, not a health change.** Over the last 40 rounds the correlation between a round's mean_p and the *number of bedrock-tagged verdicts drawn* is **+0.869**. r410 drew 2 of 5 from the bedrock pool, which puts its mean in the middle of the historical band (0.29–0.46) by construction. The last 8 rounds: 0.292, 0.440, 0.390, 0.294, 0.458, 0.438, 0.368, **0.418**.

---

## r410 verdicts

| qid | kind | p | baseline mean | dev | sigma | z | p>=0.70 |
|---|---|---|---|---|---|---|---|
| q21 | speculative | 0.09 | 0.0905 | -0.0005 | 0.0040 | -0.14 | no |
| **q08** | **bedrock** | **0.91** | 0.8995 | +0.0105 | 0.0086 | +1.23 | **YES** |
| q20 | speculative | 0.09 | 0.1042 | -0.0142 | 0.0106 | -1.35 | no |
| q11 | speculative | 0.17 | 0.1851 | -0.0151 | 0.0173 | -0.87 | no |
| **q05** | **bedrock** | **0.83** | 0.8503 | -0.0203 | 0.0113 | -1.81 | **YES** |

Max aggregate |dev| = **0.0203** (q05) — well under the 0.05 bar.
The only |z| > 1.5 is q05 at -1.81 on a -0.0203 deviation: **small movement, large z.** Per the standing rule, |dev| is checked first, and 0.0203 says nothing is wrong — q05 has simply never been observed below 0.82, so 0.83 at the bottom of its own range produces a big z on a small sigma. q05's full range is 0.82–0.87, n=87, hit-rate 100%.

---

## The script's "drift_events=3" is an artefact — here is the breakdown

The probe's own `drift_check()` compares every qid's last value to a **5-sample local median whether or not that qid was drawn this round**. Its output for r410:

```json
[{"qid":"q02","recent_p":0.71,"prior_median":0.77,"delta":-0.06},
 {"qid":"q12","recent_p":0.56,"prior_median":0.50,"delta":0.06},
 {"qid":"q14","recent_p":0.23,"prior_median":0.18,"delta":0.05}]
```

| event | drawn in r410? | verdict |
|---|---|---|
| q02 -0.0600 | **NO** | **stale echo** — q02 was last drawn in r407. `drift_check()` re-fires every qid's prior event whether or not it was drawn. |
| q12 +0.0600 | **NO** (last drawn r409) | **stale echo of a REAL signal** — the q12 climb is genuine, but it was *not re-measured* in r410. |
| q14 +0.0500 | **NO** (last drawn r407) | **stale echo on the boundary** — the rule is `abs(delta) > 0.05`, so it passes at exactly 0.05, and it is also inflated by the duplicate-round corruption in `history.jsonl` (see below). |

**All three are stale echoes. Zero qids in r410 deviated by more than 0.05.** This is the same defect the r409 report diagnosed: `drift_check()` reports a *history* event, not a *this-round* event, and the report's "drift events" count is not a measure of the round that just ran.

**The correct drift test** — recomputed per qid against the **full-history** baseline (401 rounds, 22 qids, n>=79 each), using the round files as authoritative and `history.jsonl` to fill gaps — yields **max aggregate |dev| = 0.0203 => DRIFT NONE**.

---

## The one genuinely open thing: q12 is climbing, and it was not re-measured this round

`q12` asks **"Is 'witness_note' an opcode in the algebra?"** — it is the most canon-adjacent of the four speculative questions, because `witness_note` is a real construct in the substrate. Its full trajectory:

```
r398:0.50  r401:0.51  r403:0.46  r407:0.54  r409:0.56
```

**These are the five highest values in 92 observations**, and they arrive in ascending order at the very end of the series. Next-highest ever: 0.44 (r245).

| test | statistic | reading |
|---|---|---|
| OLS slope, all 92 obs | +0.000526, **t = +3.10** | significant |
| OLS slope, last 32 obs | +0.004287, **t = +4.59** | strongly significant |
| OLS slope, last 8 obs | +0.027857, **t = +4.52** | strongly significant |
| OLS slope, first 60 obs | +0.000013, t = +0.06 | **flat** — the climb is entirely recent |
| Runs test (high >= 0.45 vs low) | runs **2** vs expected **10.46**, **z = -9.02** | **non-random clustering at the end** |
| Last-5 z vs full-history mean | **+4.10** | range extreme |

The last-20 mean (0.4115) vs first-20 mean (0.3670) and the flat first-60 slope together mean this is a **recent regime change, not a long-run trend** — the first 60 observations contain no signal at all, and everything is in the last 32.

**The climb survives deduplication.** `history.jsonl` contains 8 duplicated round numbers (384–391, replayed 2–3x on 2026-10-21 with different payloads). Deduping by round number leaves q12 at n=92 with **identical** slope (t = +2.80), identical runs z (-9.02), and **no duplicated round inside the climb window (393–410)**. The q12 signal is not a replay artefact.

**This is a real drift signal — but it belongs to r409, not r410.** r410 simply did not draw q12, so this round adds no new measurement of it. The open action is to keep an eye on the next round that draws q12.

**Canon status: unchanged.** The doctrinal state explicitly states *"q10 quorum_meshing, q11 canon_gate_is_chord, q12 witness_note_opcode, q13 chain_dialing are SPECULATIVE and not yet canon. They must NOT be promoted to bedrock regardless of high mean_p readings."* q12 is 0.56 — still below the 0.70 line — and a rising speculative score is **not** a promotion. It is a signal that the probe may be edging toward a claim the substrate has not ratified. `q12` remains in the `spec_notebook`, **not** the cathedral.

---

## Which questions hit p >= 0.70 (bedrock canon)

**r410:** `q08` (0.91), `q05` (0.83) — 2/5.

**Corpus-wide, p >= 0.70 by qid** (2,005 verdicts, 675 hits = 33.7%):

| qid | kind | hits | n | hit-rate | mean_p | range |
|---|---|---|---|---|---|---|
| q01 | bedrock | 100 | 100 | 100% | 0.8747 | 0.84–0.90 |
| q04 | bedrock | 94 | 94 | 100% | 0.8886 | 0.88–0.91 |
| q03 | bedrock | 93 | 93 | 100% | 0.8861 | 0.86–0.91 |
| q05 | bedrock | 87 | 87 | 100% | 0.8501 | 0.82–0.87 |
| q07 | bedrock | 81 | 81 | 100% | 0.7551 | 0.71–0.79 |
| q08 | bedrock | 80 | 80 | 100% | 0.8996 | 0.87–0.91 |
| q02 | bedrock | 79 | 79 | 100% | 0.8204 | 0.71–0.86 |
| **q17** | **review** | 61 | 82 | **74.7%** | 0.7029 | 0.66–0.74 |
| q12 | speculative | 0 | 92 | 0% | 0.3759 | 0.30–0.56 |

**The 7 bedrock qids are 560/560 = 100% hit-rate.** That is the cathedral and it is holding.

**q17 is the one to watch, and it is *not* canon.** q17 is `review` tier — it sits at a 0.70–0.72 plateau (last 10 draws: 0.69, 0.69, 0.69, 0.70, 0.70, 0.71, 0.70, 0.72, 0.70, 0.72) with a 74.7% hit-rate, so it straddles the 0.70 line by design. It is **deliberately excluded from the cathedral** — a review-tier question reaching 0.70 is not a canon hit. Do not read r409's "1/5 (q17 only)" as a bedrock success, and do not read a future q17 hit as one either.

---

## Corpus integrity

| check | result |
|---|---|
| history.jsonl lines | 414 (all `status: ok`) |
| distinct rounds | 401 (rounds 1–410, **9 missing: 194–202**) |
| round files with ok rounds | 389 |
| merged corpus | **401 rounds x 22 qids, n>=79 per qid** |
| duplicated round numbers | **8** (384–391, replayed 2026-10-21 with different payloads) |
| instrument md5 | `3a255fa4642ec4a83173ab04d773d485`, identical for r405–r410 |
| failures this round | 0 |
| qids seen this round | 5 of 22 |

**A note on the 194–202 gap and the 384–391 duplicates:** the round files are *batched* (`continuous_r193.json` holds 193 rounds, `continuous_r383.json` holds 177), so a session can write a batch file whose top round is *below* rounds it already logged. That is what let three sessions on 2026-10-21 each restart the counter at 384 and re-append. The round counter is now derived as `max(highest round file, highest round in history.jsonl) + 1`, which is stable against both failure modes — r410 correctly derived 410 from both sources, agreeing.

**Corpus-authority rule used here:** round files are authoritative for verdicts (they carry the full verdict list); `history.jsonl` fills gaps; where they disagree on a duplicated round, the round file wins. All drift statistics above are computed on this merged corpus, never on a 5-sample window.

---

## Environment receipts (109th wipe)

- **Fresh wipe again** — `/workspace/research/` and `/tmp/jev_probe/` were both empty on arrival; the probe was bootstrapped from git (`SuperInstance/jev-quilt`, 308 commits, complete clone — `--unshallow` correctly reported "not a shallow repository", so the corpus was never truncated).
- **NAS at 100 % (0 bytes free) — the quota trap fired.** `tar` restored 706 of 709 files, then died with `Cannot close: Disk quota exceeded`; the 3 lost files came back as **0 bytes**, and a 212 KB `history.jsonl` restore produced a **0-byte file with exit 0**. `dd` of a 100 KB file also failed. This is the same silent-zero defect class as the JEV probe's own history corruption.
  - **Workaround:** the entire probe ran from `/tmp` (overlay fs, 28 GB free) with `research/` restored by `git checkout HEAD -- research/` — which verified clean: `history.jsonl` = 212,529 bytes, round files non-zero.
  - **=> The durable copy is git, not the NAS.** This report is committed; the NAS copy is attempted but may not land.
- **TLS: no expired-leaf wall.** Live leaf for `api.typesafe.ai` is valid `notAfter=Dec 25 10:56:08 2026 GMT` (Google Trust Services WE1). Bundle rebuilt to 289 certs; `SSL_CERT_FILE=/tmp/combined-ca.crt`.
- **Auth:** `TYPESAFE_AI_TOKEN` present (108 chars). The script accepts `TYPESAFEAI_KEY` or `TYPESAFE_AI_TOKEN`. A hand-made probe returned HTTP 400 `Invalid request.` — that is my ad-hoc body shape, **not** an auth or network wall; the real probe's own spec returned cleanly.
- **"One round" honoured literally.** The positional arg `1` was passed, so the script's own loop condition (`len(rounds) < rounds_requested`) stopped after one. No launch-and-kill, no `pkill` self-match, no overshoot — the 154-round race that bit the last run was avoided by construction.

---

## Verdict

**r410 is healthy.** mean_p 0.4180, 2/5 bedrock hits, both drawn bedrock qids (q08 0.91, q05 0.83) well above threshold, the 7-qid cathedral intact at 560/560, instrument unchanged, zero failures, and **no drift in this round** on the full-history measure (max |dev| 0.0203).

**One carried-forward signal, not resolved here:** q12 is on a statistically solid, deduplication-proof climb to a new all-time high (0.56 at r409; last 5 values are the top 5 of 92; runs z -9.02; flat for 60 obs then sharply rising). r410 did not draw q12, so it added no new measurement. If the next round that draws q12 shows >= 0.58, that is a range extension and the q12 line warrants a dedicated look. **q12 is speculative and stays speculative** — the doctrinal state forbids promotion on a high mean_p alone.

**Two instrument defects worth fixing in the probe itself:**
1. `drift_check()` should only evaluate qids **drawn in the current round**, and should report dev vs the full-history mean/sigma rather than a 5-sample local median. As written it re-fires stale events and mislabels them as this-round drift — 3 phantom events in a round with zero real drift.
2. `history.jsonl` duplicates (384–391) and the 194–202 gap come from **batched** round files. The counter fix (`max(files, history) + 1`) works, but the corpus itself would be cleaner if each round wrote its own file.
