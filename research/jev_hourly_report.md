# JEV Continuous Probe — Hourly Report (r406)

**Run:** 2026-10-23T22:03Z · 1 round, 0 fails · script md5 `3a255fa4642ec4a83173ab04d773d485` (unchanged, 7th wipe)
**Corpus:** 397 distinct rounds / 1,985 verdicts / 22 qids · grand mean_p **0.3833** · bedrock 671/1,985 (33.8%)
**Cathedral:** 651/1,925 = **33.8%**

## Headline

**mean_p 0.2940** — below the prior-12 window (0.4762), delta **−0.1822**. Pure draw mix: only **q02** was bedrock-kind this round, and the other four were speculative/adversarial draws that have always scored low. The aggregate moved; the instrument did not.

**Bedrock hits (p ≥ 0.70): 1/5 — `q02` @ 0.73.**

| qid | kind | p | hit |
|---|---|---|---|
| q22 | speculative | 0.16 | ✗ |
| q21 | speculative | 0.10 | ✗ |
| q14 | adversarial | 0.22 | ✗ |
| **q02** | **bedrock** | **0.73** | **✓** |
| q18 | speculative | 0.26 | ✗ |

## Drift

**Real drift on the drawn set: ONE event — `q02` (0.73 vs prior-5 median 0.79, delta −0.06).**

The script reported `drift_events=2`. Decomposed:

- **`q02` — REAL.** Flagged qid *was* drawn in r406, and its value comes from r406 itself. This is the **first round since the defect was catalogued where the flag points at a qid actually drawn** — the script's drift signal has been a stale echo for 4 of the last 6 rounds, and this time it landed on something real. Do not discount it because of the defect's history; discount it per-round by intersecting with the drawn set, which is exactly what surfaced this.
- **`q12` — FALSE POSITIVE (known defect).** `drift_check` (`jev_continuous_probe.py:317-335`) has no current-round filter. The 0.46 is r403's value; q12 was **not drawn** in r404, r405, or r406. Stale echo.

**Range breaches on the drawn set (the |dev| discipline):**

| qid | p | prior range | verdict |
|---|---|---|---|
| q22 | 0.16 | [0.11, 0.14] | **new high** (sd 0.0068 — near-degenerate σ; z is meaningless here) |
| q18 | 0.26 | [0.20, 0.24] | **new high** (sd 0.0085) |
| q14 | 0.22 | [0.16, 0.22] | inside range (at ceiling) |
| q21 | 0.10 | [0.08, 0.10] | inside range (at ceiling) |
| q02 | 0.73 | [0.75, 0.86] | **new low** |

Three of five drew at or through their historical ceiling. **Direction: everything moved UP except q02, which moved DOWN.** Two speculative qids (q22, q18) at new highs is *narrowing confidence* on speculative material — the instrument becoming more certain that speculation is speculation. q02 is the opposite: canon confidence eroding.

## q02 — the real signal

`q02` is the fleet's bedrock anchor. **79 draws, 79 bedrock hits, 100% hit-rate, never once below 0.70.** Until now.

r406's **0.73 is the lowest q02 has ever drawn**, and the tail is monotone across the last four draws:

```
r392 0.79   r399 0.75   r401 0.77   r406 0.73
```

5-era means: 0.8300 → 0.8300 → 0.8180 → 0.8287 → 0.8180 (baseline excl. r406, n=78)
dev = **−0.0928**, z = **−5.19** against baseline sd 0.0179. |dev| > 0.05 ⇒ real.

**Escalation status: NOT YET — but the margin is gone.**

- recent29 = 0.8134 (threshold < 0.81) — **not crossed**, margin +0.0034
- sub-0.75 draws = **1** (0.73, this round) — a 2nd sub-0.75 draw would escalate
- draws < 0.70 = **0** — **canon has NOT eroded**; 0.73 still clears the 0.70 bedrock gate

**Caveat on the trend's weight:** q02 is drawn in only **79/397 rounds (19.9%)**, median gap ~3 rounds, and the last four draws are spread over r392→r406 (gaps 7, 2, 5). Four draws is not a dense sample. But each of the last three draws is a fresh all-time low, and 0.73 is 2 sd below baseline on a 100%-hit qid. **Watch q02 on its next draw.** A second sub-0.75 draw ⇒ escalate to canon-erosion watch. A draw ≥0.80 ⇒ the tail was noise.

## q12 — confirmation test STILL PENDING

q12 was **not drawn** in r404, r405, or r406. The r233 confirmation test remains open: the next q12 draw decides. ≤0.40 ⇒ two-draw spike; ≥0.45 ⇒ real plateau advance.

Tail draws ≥0.45 = 3 (r398 0.50, r401 0.51, r403 0.46); ≥0.50 = 2; ≥0.70 = 0.
4-era means 0.3691 / 0.3618 / 0.3700 / 0.3736. q12 bedrock hit-rate 0/90 — spec-band, can never touch canon.

Per the draw-gap rule: q12 is drawn in ~23% of rounds, so r398→r401→r403 are three consecutive *draws*, not consecutive *rounds*.

## Method notes carried forward

1. **The drift flag is right ~20% of the time and you cannot tell which 20% without intersecting with the drawn set.** r406 is the counter-example that proves the defect and the rule are both real: same flag, one entry real, one entry stale.
2. **σ≈0 trap, 14th consecutive, rule held.** q22 z +5.92 on a 0.0404 dev with sd 0.0068. The z looks alarming; |dev| 0.0404 < 0.05, and 0.16 is only 0.02 above q22's historical max. **The eye catches the z; |dev| says nothing is wrong.**
3. **q02's z = −5.19 is the inverse case** and is real — because |dev| = 0.0928 > 0.05 *and* it is a new all-time low on a 100%-hit qid. Same rule, opposite sign.
4. **mean_p decomposition is mandatory.** −0.1822 aggregate delta, per-qid |dev|: q22 +0.0404, q21 +0.0096, q14 +0.0275, q02 −0.0928, q18 +0.0365. Three of five are ≤0.05 (noise); one is 0.0404 (near); one is 0.0928 (real).
5. **Draw-mix discipline:** r406 drew exactly one bedrock-kind qid, so the round's mean_p is structurally low. Compare means only after decomposing to the drawn set.

## Environment (122nd wipe)

- **21st consecutive** ephemeral-path wipe — `/workspace/research/` absent on arrival; rebuilt `/tmp/jev_probe` from `SuperInstance/jev-quilt @ 8be3676`.
- **NAS 600G/600G (24th recurrence), now SILENT** — writes to `/workspace` **exit 0 and land 0 bytes**. Verified: `printf 'x' > /workspace/.wtest` → exit 0, 0 bytes. **A successful-looking write is not proof of a written file — always stat the size after writing.** `write` tool cannot reach `/tmp`; use bash heredoc.
- **TLS clean on first try** — `curl https://api.typesafe.ai/` → 404 (server reached, bare-GET path wrong) ⇒ no cert-anchor wall, no 289-cert bundle rebuild. **6th clean wipe**; curl-first triage is cheap insurance.
- `gh` absent (**13th wipe**).
- Script md5 `3a255fa4642ec4a83173ab04d773d485` unchanged **7th wipe**; r229 fixes all present.
- **Positional `1` ran exactly one round, no R-221 overshoot.** Note: the task's literal command (`timeout 60 python3 jev_continuous_probe.py`, no arg) runs the **default 200 rounds** — always pass the explicit positional count.
- Round counter files→405 history→405 ⇒ start=406, no duplicate.
- `TYPESAFE_AI_TOKEN` present (108 chars), accepted via the `TYPESAFEAI_KEY`→`TYPESAFE_AI_TOKEN` fallback chain.
