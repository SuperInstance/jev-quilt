# JEV Continuous Probe — Hourly Report

**Run date:** 2026-10-22 08:04 UTC
**Round requested:** 1
**Round actually executed:** 0 — **blocked before dispatch**

---

## TL;DR

The probe did not run. The JEV endpoint is unreachable from this sandbox because of an
**expired TLS leaf certificate on the egress proxy**. This is the *expired-leaf wall*, not
the *cert-anchor wall*, and it is **not fixable from inside the sandbox**. No new round data
was produced, so there is nothing new to compare against prior rounds — the comparison below
is against the last known-good signal, clearly labeled as such.

**Do not read the numbers below as this round's result.** They are the baseline the next
successful round must be compared to.

---

## Block cause (evidence)

Triage separated the two TLS walls; only one is fixable.

| Check | Result |
|---|---|
| TCP 443 reachability | ✅ REACHABLE |
| `TYPESAFE_AI_TOKEN` | ✅ SET (len=108) |
| `GITHUB_TOKEN` | ✅ SET (len=40) |
| `curl` (verifying) | ❌ **exit 60 — "certificate has expired"**, `ssl_verify_result=10` |
| Python `ssl` handshake | ❌ `SSLZeroReturnError` / `URLError` handshake timeout |

Leaf certificate presented by the edge:

```
subject: O=
issuer:  O=hangzhou; OU=alibaba cloud; CN=ack-agent-identity-proxy
start:   Oct 21 01:01:32 2026 GMT
expire:  Oct 22 01:01:32 2026 GMT
now:     Oct 22 08:04 UTC
```

The issuer `CN=ack-agent-identity-proxy` is **not** typesafe.ai. Egress is being MITM-proxied
and re-signed with a **24h-TTL leaf**. That leaf expired **7h03m ago**. Rebuilding the CA
bundle does not fix this and was not attempted as a false remedy.

**Verdict: the call cannot succeed until the proxy re-issues its leaf. Report and stop.**

## Not run, deliberately

The 60s probe was **not** launched. Running it would have produced a 13th consecutive
`round_NNN.fail.json`, indistinguishable from the failures already on record. The failure
streak is the finding; another instance of it adds no information.

Current state on `r-081-continuous-probe-rebuild` (`353ca5a`):

| Session | OK | FAIL |
|---|---|---|
| `rounds_r20261022T000200Z` | 5 | 7 |
| `rounds_r20261022T010610Z` | 0 | **12** |
| HEAD commit R-218 | 0 | **12** |

HEAD's own commit message reads: *"12 attempted, 0 OK / 12 fail, zero verdicts."*
All 12 of the newest session's failures carry the identical error:
`URL/conn: URLError: <urlopen error _ssl.c:975: The handshake operation timed out>` —
the same wall, one symptom layer down.

---

## Last known-good signal (BASELINE — not this run)

Newest fully-successful round is **`r600.json`**, `ts 2026-10-20T03:03:52Z`, **~2 days stale**.

**mean_p = 0.414** (n_ok = 5)

| qid | p | |
|---|---|---|
| q03_substrate_is_grown | 0.98 | bedrock |
| q05_lenia_flows | 0.97 | bedrock |
| q16_vibecoder_signal_chain | 0.04 | |
| q22_provenance_conflict | 0.03 | |
| q11_canon_gate_is_chord | 0.05 | |

Per-question means pooled across the 5 OK rounds of the 2026-10-22T00:02Z session plus
r600 (n=30 samples, **grand mean_p = 0.453**):

### Bedrock canon (mean p ≥ 0.70)

| qid | n | mean_p |
|---|---|---|
| q08_polyformalism | 1 | 0.980 |
| q03_substrate_is_grown | 2 | 0.980 |
| q02_witness_log_is_prediction | 2 | 0.975 |
| q04_oracle_is_heard | 1 | 0.970 |
| q05_lenia_flows | 2 | 0.970 |
| q07_11_opcodes | 3 | 0.970 |

**6 of 19 distinct qids are bedrock.** This is the **Bedrock 6/8** figure — unchanged, and
consistent with the long-standing JEV-verified result.

### Borderline / emerging (0.5–0.7)

- `q17_canary_honesty` — 0.670 (n=2) — REVIEW band, watch it
- `q12_substrate_polyformal` — 0.630 (n=1) — REVIEW band

### Consistently rejected (< 0.2)

`q06_three_views` (0.140), `q13_witness_log_opcode` (0.120), `q19_style_resilience` (0.040),
`q20_wolffs_law` (0.050), `q21_memory_sandbox` (0.040), `q16_vibecoder_signal_chain` (0.040),
`q10_quorum_meshing` (0.030), `q18_address_is_data` (0.050), `q22_provenance_conflict` (0.030).

Note `q18_address_is_data` scores 0.05 despite being **doctrineally bedrock in the canon**
(cell doctrine: *the address is the data*). This is the known q10/q11/q18/q21 **state-leak
defect** — still unpatched, and it is why those four read low. Not new, not a canon change.

## Drift > 0.05

**Cannot be computed for this run** — there is no new measurement to diff. Deliberately
reported as unavailable rather than substituted with a comparison between two equally-stale
rounds, which would look like drift analysis while measuring nothing.

Within the baseline sample, per-qid spread is tight (bedrock 0.97–0.98; rejected 0.03–0.05),
so no qid is itself drifting. The **grand** mean_p does move between rounds
(0.382 / 0.410 / 0.412 / 0.534 / 0.566 across the five OK rounds) — but that is **draw-mix
confounded**: each round samples a different 5-question subset, so it is a property of which
questions got drawn, not of canon stability. Per-qid means are the instrument here, and they
are stable.

---

## Recovery

The probe resumes with no code change once egress re-issues the leaf. To confirm the wall has
lifted *before* spending a round:

```bash
curl -sS -o /dev/null -w "HTTP=%{http_code}\n" -X POST https://api.typesafe.ai/v1/systemone \
  -H "Content-Type: application/json" -d '{}'
```

`HTTP=401` => reachable-but-no-creds on this probe path => **wall cleared, run the round.**
`curl: (60)` => still expired, stop and do not burn a round.

## Open items (unchanged)

1. **q10/q11/q18/q21 state-leak patch** — `SuperInstance/jev-quilt/continuous/jev_continuous_probe.py`.
   Directly responsible for four canon questions reading ~0.05.
2. **Round-file flush** — the newest session (`rounds_r20261022T010610Z`) has **no
   `session_summary.json`**, unlike every prior session. The 12 fail files are committed but
   the run was never summarized or closed out.
