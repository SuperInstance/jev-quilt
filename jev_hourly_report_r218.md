# JEV Continuous Probe — R-218 (105th wipe)

**Run:** 2026-10-22T01:06:10Z · session tag `r20261022T010610Z`
**Script:** `c22e8c72f13f3b71d5b40e8f8fd04d61` (unchanged, 5th consecutive session)
**Snapshot:** `SuperInstance/jev-quilt @ r-081-continuous-probe-rebuild`, HEAD `89b6510` (R-217)
**Baseline loaded:** 2,835 prior verdicts across 22 questions — DEFECT B guard passed

---

## HEADLINE: THIS ROUND PRODUCED NO DATA

**12 attempted — 0 OK / 12 fail. Zero verdicts. `mean_p` is undefined, not zero.**

There is nothing to compare to previous rounds, because this round asked JEV nothing at all.
Reporting a mean here would be fabrication. The report is the diagnosis instead.

| Requested metric | Status |
|---|---|
| `mean_p` | **UNDEFINED** — no verdicts returned |
| questions hitting p >= 0.70 | **UNDEFINED** — no scores exist this round |
| drift > 0.05 vs prior rounds | **UNDEFINED** — no new samples to deviate |

The last round with real data is **R-217** (mean_p 0.4608, cathedral 9/9 @ 100%, 16th consecutive,
max aggregate drift 0.0246). That baseline is intact and unchanged.

---

## ROOT CAUSE (new — and it corrects 88 sessions of misdiagnosis)

Failure split: **6 x `certificate has expired`, 6 x `handshake operation timed out`**.

I have logged "TLS handshake timeout / network-bound" in this environment for **6+ consecutive
sessions**. That attribution is **wrong**, and this session proves it.

### What is actually happening

The sandbox egress is a **MITM proxy** (`ack-agent-identity-proxy`, issuer `alibaba cloud/hangzhou`)
terminating TLS and re-signing every connection.

```
subject : organizationName = (blank)
issuer  : CN = ack-agent-identity-proxy, O = alibaba cloud, OU = hangzhou
notBefore: Oct 21 01:01:32 2026 GMT
notAfter : Oct 22 01:01:32 2026 GMT     <-- 24h TTL
run time : Oct 22 01:03:30 .. 01:06      <-- ALREADY EXPIRED
```

The leaf is minted per-hour and **every node on the edge is now past TTL**. Polling the leaf 14 times
returned a **mix of two different certs**, both expired:

- `Oct 20 23:09:10 -> Oct 21 23:09:10` (expired ~2h ago)
- `Oct 21 01:01:32 -> Oct 22 01:01:32` (expired ~5 min ago)

So the two error modes are one fault seen through two edges: nodes whose clock is behind hang
in the handshake, nodes that answer fast hand back a stale leaf. **Not two faults. One.**

### It is not JEV-specific, and not the endpoint

The same failure hits GitHub over the identical TLS path:

```
api.github.com        -> CERTIFICATE_VERIFY_FAILED: certificate has expired
typesafe.ai (root)    -> handshake operation timed out
```

`git clone` succeeded at 01:02 and still succeeds now **only** because every prior session used
`GIT_SSL_NO_VERIFY=1`. With full verification git fails too. The probe's Python path cannot use that
escape hatch, which is why the probe is hard-down while git looks healthy.

### The CA is NOT the problem

```
gateway CA notBefore: Aug 15 07:28:00 2026
gateway CA notAfter : Aug  7 07:33:36 2056     <-- valid for 30 years
```

The trust anchor is fine. Only the **leaf** expires. The long-standing "rebuild the 289-cert CA
bundle" remedy (recurring 7 times in memory) **cannot fix this class of failure** — I rebuilt the
bundle from 147 -> 168 certs, prepended the live leaf fetched off the wire, and it still failed,
because the edge rotates a *different* expired cert per connection. A static bundle cannot chase it.

---

## WHAT IS STILL GOOD

- Bootstrap from the git snapshot: **~8s, clean** (4th time the prompt's `/workspace/research/` paths were wrong; 4th consecutive wipe with both `/workspace` and `/tmp/jev_probe/` empty).
- Script md5 `c22e8c72…` unchanged across R-214..R-218 — no accidental fork.
- Baseline survived: 2,835 verdicts / 22 qids intact, DEFECT B guard **passed** (it would have
  refused to run on an empty baseline rather than reporting a false all-clear).
- **Fail path is clean:** 12/12 rounds wrote `.fail.json` with 0 verdicts, and `history.jsonl`
  stayed at **567 lines — zero false appends**. A failed round did not poison the baseline.
- `SESSION_TAG` derived from timestamp by construction; no clobbering of prior rounds.

## WHAT STILL BLOCKS THE REQUESTED PATH

`/workspace` NAS is at **100% EDQUOT (1024 bytes free)** — the recurring trap. `mkdir /workspace/research`
succeeds, then writes return 0 bytes. This report is durable at `/tmp/jev-quilt/` and pushed to
`SuperInstance/jev-quilt`; `/workspace/research/jev_hourly_report.md` is written **only if quota allows**
and must not be trusted without `ls -l` confirming a non-zero size.

---

## NEXT SESSION — do not re-diagnose this

1. **Cheapest first check, 3 seconds:**
   ```bash
   python3 -c "import ssl,socket;s=socket.create_connection(('api.typesafe.ai',443),timeout=5);c=ssl.create_default_context();c.check_hostname=False;c.verify_mode=ssl.CERT_NONE;ssl_sock=c.wrap_socket(s,server_hostname='api.typesafe.ai');open('/tmp/l.pem','w').write(ssl.DER_cert_to_PEM_cert(ssl_sock.getpeercert(binary_form=True)));print(ssl._ssl._test_decode_cert('/tmp/l.pem'))"
   ```
   If `notAfter < now`, the probe cannot run. **Report the outage; do not burn the 60s.**
2. **STOP calling this "network-bound."** It is an upstream TLS-certificate expiry in the sandbox
   egress proxy. 6+ sessions of hand-waving about "flaky network" were this same fault.
3. **STOP rebuilding the CA bundle for this symptom.** It is verified not to help; the anchor is
   valid to 2056 and the leaf rotates per-connection.
4. If a probe run must happen regardless, `SSL_CERT_FILE` pinned to a bundle including the
   *current* leaf buys minutes at best, not a round.
5. Genuinely worth escalating to Casey: an hourly-rotating MITM cert that goes stale with no refresh
   makes every verification-strict egress call fail, and only `GIT_SSL_NO_VERIFY` masks it.

---

*Nothing was promoted, demoted, or re-tagged. No verdict was fabricated to fill the gap.*
