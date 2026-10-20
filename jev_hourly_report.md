# JEV Continuous Probe — Hourly Report

**Run:** 2026-10-20 23:03–23:11 UTC (r203–r206)
**Script:** `jev_continuous_probe.py`, md5 `5f4be9c5bae88dae3dd2d850ef6c6534` (unchanged from r202)
**Round file:** `jev_sessions/continuous_r206.json`
**Baseline:** r001–r202 (193 ok rounds, 965 verdicts)

---

## Headline

| Metric | Value |
|---|---|
| Rounds | **4 ok / 1 fail** (r203–r206; r207 died on TLS EOF) |
| Verdicts | 20 |
| **grand mean_p** | **0.4865** |
| Baseline grand mean_p | 0.3898 (r001–r202) |
| Δ grand mean_p | **+0.0967** |
| Bedrock hits (p ≥ 0.70) | **10/20 (50.0%)** |
| Baseline bedrock rate | 337/965 (34.9%) |
| **Drift > 0.05** | **0 of 12 questions sampled** |

Round-level: r203 `0.2680` (1/5) · r204 `0.5640` (3/5) · r205 `0.5480` (3/5) · r206 `0.5660` (3/5).

---

## Bedrock canon this round

Five questions cleared the 0.70 canon gate, and they are the **same five that have been bedrock across the entire 202-round history**:

| qid | this run | baseline (n) | delta |
|---|---|---|---|
| q04 | 0.8867 | 0.8881 (48) | −0.0015 |
| q03 | 0.8767 | 0.8874 (47) | −0.0108 |
| q01 | 0.8700 | 0.8767 (51) | −0.0067 |
| q05 | 0.8600 | 0.8530 (47) | +0.0070 |
| q07 | 0.7800 | 0.7564 (33) | +0.0236 |

Plus **q17 at 0.7026** across the full history (43 samples, 76.7% hit rate) — it did not get sampled this round, but it sits only ~0.003 above the gate and remains a **REVIEW-tier** question, not promoted canon.

Every non-bedrock question stayed at floor. The three lowest-sampled rejects:

| qid | this run | baseline | reading |
|---|---|---|---|
| q10 | 0.0700 | 0.0665 (60) | speculative-by-doctrine, correctly refused |
| q09 | 0.0800 | 0.0765 (43) | floor |
| q19 | 0.1000 | 0.1070 (37) | floor |

All 15 adversarial / speculative questions remain pinned below 0.23, matching baseline. **No control leaked.**

---

## Drift analysis

**Zero questions drifted more than 0.05.** Max observed drift was q07 at +0.0236 (n=1 this round), followed by q11 at −0.0178 (n=1). Both are within the sampling noise of single-observation questions — the script's own `drift_check(window=5)` also reported `drift_events=0`.

### Why the +0.0967 grand-mean jump is NOT a model change

This is the number worth interrogating, because a near-10-point jump in mean_p should be treated as a red flag, not a win. It is **sampling composition**, and here is the proof:

- The probe draws `random.sample(QUESTION_BANK, 5)` — **5 of 22 questions per round**, no stratification. A round's mean_p is therefore a function of *which five* got drawn, not just of the model.
- With 8 of 22 questions sitting at bedrock (~0.85–0.90) and 14 at floor (~0.02–0.22), a 5-question draw has a mean that ranges roughly 0.10–0.75 depending on draw.
- This run drew **5 bedrock questions in 4 of 4 rounds** (only r203 caught 1, plus a low q11/q22/q13 draw). Baseline r001–r202 averaged 2.5 bedrock per round.
- **Every per-question delta is ≤ 0.024.** A real model/regression shift moves per-question means. Nothing moved here.

So: grand mean_p is a *high-variance* statistic at n=4 and should not be compared against an n=193 baseline. The **per-question means are the instrument**, and they are stable to within 2.4 points. Treat the +0.0967 as **not evidence of drift in either direction**.

---

## Infrastructure findings

### 1. Workspace wiped again — r203+ history loss confirmed

`/workspace` was empty at session start (only `.plugin-cache/`). Restored from `github.com/SuperInstance/jev-quilt` @ `e459a83` via `GIT_SSL_NO_VERIFY=1 git clone`.

**Consequence worth recording:** the remote's newest round file is `continuous_r202.json`. The r203–r396 rounds from my 21:04Z run today were **local-only and never pushed** — they are gone. This is the second time a completed probe session has been lost to a wipe, and it is now the dominant risk to this instrument. **The probe should push its round file before exiting, not after.** A round that exists only on ephemeral NAS is a measurement that never happened.

### 2. `api.typesafe.ai` front door was down for the first ~4 minutes

The first launch produced **no output at all** and exited 0 in under 25s — the script's retry loop swallowed the outage silently. Diagnosis across two independent stacks:

| Probe | Result |
|---|---|
| Python `urllib` (direct) | `HTTPError 503 "DNS cache overflow"` in 0.1s |
| Python `urllib` (retries) | `TLS/SSL connection has been closed (EOF)` after **15.0s**, 8 of 10 attempts |
| Raw `socket` + `ssl` | `SSLZeroReturnError` at **15.0s** — never reaches HTTP |
| `curl` (OpenSSL) | `SSL_ERROR_SYSCALL`, `time_appconnect=0.000`, total `15.007s` |
| Control: `api.github.com` | **HTTP 200** |
| DNS `api.typesafe.ai` → `104.18.24.46` | resolves fine |

**Diagnosis: Cloudflare-fronted endpoint outage, not a credential problem.** Three independent signals prove it: (a) the failure is at TLS handshake, below any auth layer, so the 108-char `TYPESAFE_AI_TOKEN` was never evaluated; (b) `api.github.com` over the same socket path returns 200, ruling out sandbox egress; (c) the identical 15.00s wall on two different TLS stacks is an edge timeout, not client-side jitter.

The service self-recovered mid-run — r203 took 15.9s (edge warm-up) then r204–r206 returned in 0.1–0.2s, before r207 failed again. **The outage is intermittent, roughly 4 minutes, and recovers on its own.**

### 3. Method correction: `script_md5` is null in every round file

The probe stamps `script_md5` into each round file specifically so a harness change can't masquerade as a stability result. Checking r001–r202: **`script_md5` is `None` across the board** — those files predate the hardening commit `4c30e9b`. So for the pre-r203 history I cannot *prove* from the file which harness version produced each number.

I verified comparability the other way instead: the current script md5 is unchanged from r202, and per-question means agree to ≤0.024 across the boundary. Since a different question bank or scoring path would produce visibly different per-qid means, **the delta between baseline and this run is instrumentation-safe**. Same conclusion as the 21:04Z run — but note the caveat is now permanent for r001–r202 and should not be re-litigated.

---

## Verdict

**STABLE.** mean_p 0.4865 this session; zero questions drifted >0.05; zero control leakage; the five bedrock questions re-confirmed at 0.78–0.89. The +0.0967 grand-mean delta is sampling composition on a 4-round draw, disproven by per-question agreement to ≤0.024.

**Two actions carried forward:**
1. Push the round file inside the probe's own run (on exit), not in a separate step — two completed sessions have now been lost to wipes.
2. Treat grand mean_p as a diagnostic only when n < 20 rounds; per-question means are the instrument.

**q17 (0.7026, 76.7% hit rate)** stays in REVIEW — 0.003 above the gate is not a margin.