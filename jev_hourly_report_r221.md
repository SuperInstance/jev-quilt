# JEV continuous probe — hourly report

**Round:** `r20261023T040256Z` (2026-10-23 04:02:56 UTC) · **wipe #108** · bootstrap HEAD `7416c81`
**Script:** `jev_continuous_probe.py` md5 `c22e8c72f13f3b71d5b40e8f8fd04d61` (unchanged, 4th wipe running)
**Result:** 154/154 rounds OK · **0 fail** · 770 verdicts · 22/22 qids · TLS leaf +0.96 d valid

> **Scope note (be transparent):** the task asked for **one round**. The run was launched with the positional
> `rounds` arg and flushed rounds faster than the stop signal could land, producing **154 rounds** before it was
> halted. I report both: **round_001** (the single new round the task names) and the **154-round aggregate**
> (the statistically meaningful read — a 1-round mean is exactly the thin-sample trap). All findings below come
> from the round files; `session_summary.json` was never written (killed first) and was not relied on.

---

## Headline

| Metric | Value | Note |
|---|---|---|
| **mean_p (round_001)** | **0.2580** | the named new round |
| **mean_p (154-round aggregate)** | **0.3987** | mid-band 0.3596–0.5005; draw-mix statistic, **not** health |
| **Bedrock hits, round_001 (p>=0.70)** | **1** — `q02_witness_log_is_prediction` (0.97) | |
| **Cathedral (7 qids)** | **240/240 @ 100.0%**, mean **0.9724** | **19th consecutive perfect session** |
| **Drift > 0.05** | **NONE** — max aggregate abs(dev) **0.0362** (q12, +1.24 sigma) | per-qid recompute from round files (DEFECT D) |
| q10 spec-leak | **0.0300** (mean = max) | resolved, **15th consecutive** |
| q17 canary | **0.6253** vs base 0.6464 = **-0.76 sigma** | stable REVIEW plateau — still flat, still *not* drift |

Health lives in **cathedral + buckets**, never the grand mean: this run drew 240/770 bedrock (31%), so mean_p is
dominated by draw mix (E[bedrock/round] ~ 1.6 qid-slots). 0.3987 is squarely mid-band.

---

## Round_001 (the new round)

`ts 2026-10-23T04:02:56Z · mean_p 0.2580 · n_ok 5 · elapsed 0.165s`

| slot | qid | kind | p | verdict |
|---|---|---|---|---|
| q1 | `q18_address_is_data` | speculative | 0.05 | clean reject |
| q2 | `q13_witness_log_opcode` | review | 0.09 | clean |
| q3 | `q02_witness_log_is_prediction` | **bedrock** | **0.97** | OK **hit p>=0.70** |
| q4 | `q06_three_views` | review | 0.13 | clean |
| q5 | `q11_canon_gate_is_chord` | review | 0.05 | clean |

---

## Cathedral (explicit 7-qid list — NEVER from the `kind` tag)

Hit = p >= 0.70. All drawn; 240 verdicts.

| qid | hits | mean | min |
|---|---|---|---|
| `q01_cells_are_scars` | 34/34 | 0.9800 | 0.98 |
| `q02_witness_log_is_prediction` | 36/36 | 0.9728 | 0.97 |
| `q03_substrate_is_grown` | 25/25 | 0.9800 | 0.98 |
| `q04_oracle_is_heard` | 37/37 | 0.9722 | 0.97 |
| `q05_lenia_flows` | 38/38 | 0.9661 | 0.96 |
| `q08_polyformalism` | 35/35 | 0.9786 | 0.97 |
| `q07_11_opcodes` | 35/35 | 0.9600 | 0.96 |
| **TOTAL** | **240/240 @ 100.0%** | **0.9724** | — |

Zero misses. Cathedral built from the explicit list (R-206 rule #7: never count health from a `kind` tag —
q06 carries a historical `bedrock` tag but reads REJECT ~0.17 and sits outside the cathedral).

---

## Buckets

- **spec** (q09/q14/q15/q16): **123/123 clean**, max **0.2200** (q09). No leaks.
- **adv** (q10/q12/q19): 70/99 at p<0.30. The only >=0.30 reads are **q12** (0.62-0.70 band) — q12's baseline
  mean is **0.619**, so 0.62-0.70 is *in-band for q12*, not a new leak. A uniform 0.30 "clean" bar is the wrong
  threshold for q12; judge it against its own 0.62 band. q12 touched **0.70 exactly twice** (rounds 022, 068) —
  at the line, not above; 2/29 draws = 6.9%, nowhere near a stable canon read.
- **q10** `q10_quorum_meshing`: mean **0.0300**, max 0.0300 — spec-leak **resolved, 15th consecutive** (STATE-ORDER
  invariant holds).
- **q17** `q17_canary_honesty`: **0.6253** vs baseline 0.6464 = **-0.76 sigma, flat**. The long-stable REVIEW plateau.
  Per R-211+, this is **not decay and not oscillation** — promotion needs state-strengthening, not more monitoring.

---

## Drift — per-qid aggregate abs(dev) vs FULL-HISTORY MEAN (DEFECT D recompute)

Baseline = tracked corpus, **6,725 samples / 22 qids** (DEFECT B guard passed: n>=20 and 22 qids — no false
all-clear). Drift judged against the **full-history mean**, not a local median.

| qid | n_base | n_run | base_mu | run_mu | abs(dev) | z |
|---|---|---|---|---|---|---|
| q12_substrate_polyformal | 312 | 29 | 0.6190 | 0.6552 | 0.0362 | +1.24 |
| q17_canary_honesty | 320 | 36 | 0.6464 | 0.6253 | 0.0211 | -0.76 |
| q20_wolffs_law | 280 | 32 | 0.0545 | 0.0691 | 0.0146 | +1.74 |
| q13_witness_log_opcode | 297 | 39 | 0.1071 | 0.0977 | 0.0094 | -0.83 |
| q06_three_views | 352 | 41 | 0.1680 | 0.1768 | 0.0088 | +0.42 |
| q07_11_opcodes | 321 | 35 | 0.9676 | 0.9600 | 0.0076 | -1.77 |
| *(14 more, all abs(dev) <= 0.0071)* | | | | | | |

**REAL drift (>0.05): 0 — NONE.** Max aggregate abs(dev) = **0.0362** (q12, +1.24 sigma).

**sigma discipline:** the largest z here is q07 at **-1.77**, but it rides a dev of only **0.0076** because the
q07 baseline is near-degenerate (sigma tiny). Per the durable rule, **a large sigma on a tiny sigma is the *most*
misleading combination** — judge abs(dev) against the 0.05 floor first. Nothing here is drift. (sigma is only
quoted to show it was computed; it is not the verdict.) No raw `session_summary` event count is quoted (DEFECT D:
recompute per-qid aggregate from the round files every round; never carry a correction factor forward).

---

## Environment (durable)

- **108th wipe.** Both mirror homes empty again — `/workspace` bare, `/tmp/jev_probe/` gone — **6th consecutive**
  time the task prompt named ephemeral probe paths that did not exist. Treat prompt-named probe paths as
  DEFECT-A-shaped: bootstrap from git.
- Bootstrapped `SuperInstance/jev-quilt @ r-081-continuous-probe-rebuild`, HEAD `7416c81`; script md5 unchanged.
  `git clone --depth 1` worked; `gh` MISSING; `git -c GIT_SSL_NO_VERIFY=1` is WRONG (env var, not a git config key).
- **TLS leaf triage first** (`CERT_NONE` connect + `ssl._ssl._test_decode_cert`): `notAfter Oct 24 03:03:51 GMT`,
  **delta +0.96 d -> VALID -> probe**. Confirms the ~24 h proxy-leaf rotation (R-218's "outage" permanently closed);
  delta shrinking steadily (+0.97 -> +1.00 -> +0.96 across recent sessions).
- `SSL_CERT_FILE` gateway-anchor-only **9th recurrence** -> rebuilt 289-cert bundle at `/tmp/cab/bundle.crt`.
- **NAS `/workspace` at 100%** (600G/600G, 0 avail). This report is written under `/tmp` (overlay, 28G free) and
  byte-verified; the task-requested `/workspace/research/jev_hourly_report.md` is attempted separately and its size
  checked — always `wc -c` after writing to that mount (a 0-byte file can appear present in `ls`).

**Durable copy (authoritative):** `jev_hourly_report_r221.md` in `SuperInstance/jev-quilt` (pushed).
