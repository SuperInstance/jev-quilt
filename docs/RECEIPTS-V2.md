# Receipts v2 — from tamper-evident to non-repudiable

Status: design note (doc-only). Nothing here is shipped.
Date: 2026-09-21

## Why v2 exists

The current receipt layer is FNV-1a hash-chained: each Receipt's sha() walks the
chain and re-derives payload_hash from the retained payload (see PR #3's repair —
the text, not just the hash field, is chained). This gives us **tamper evidence**
inside one process and one ledger: any edit anywhere upstream breaks re-derivation.

Two honest limits remain:

1. **No non-repudiation.** FNV-1a is not a signature. Anyone holding the ledger can
   recompute the whole chain. A receipt proves *the ledger is intact*, not *who
   wrote it*. Cross-node, "the bookkeeper says so" is not a proof.
2. **Legacy-weak primitive.** FNV-1a-64 is a fast non-cryptographic hash, chosen for
   exact-rational reproducibility across Python/Rust/TS (café Δ 日本語 →
   0x024a555471370b18d pinned in three suites). Corroboration from the frontier:
   inchwormz/agent-receipts ships BLAKE3 + Ed25519 hash-chained receipts — the
   fleet's receipt doctrine is right, our primitive reads legacy next to it.

## v2 shape: verify-only signature layer

Keep the FNV-1a chain exactly as-is (it is the reproducible, cross-language spine —
the pinned vectors stay valid). Add a **signature envelope** around it:

```
SignedReceipt = {
  receipt:      <existing Receipt, unchanged>,
  chain_head:   fnv1a-64 of the chain tip this receipt seals,
  signer:       <node/agent identity key id>,
  signature:    Ed25519.sign(signer_sk, BLAKE3(receipt.canonical_bytes || chain_head))
}
```

Rules:

- **Sign, don't replace.** The FNV-1a chain remains the in-ledger truth; signatures
  are an envelope a verifier can strip. Old verifiers still work.
- **Verify-only receipts for cross-node claims.** A node that only ever verifies
  never needs a signing key — verification is permissionless, minting is not.
- **One key per node identity, not per receipt.** Key rotation books a receipt of
  its own (new key signs the old key's retirement) or the chain forks socially.
- **Non-repudiation is a cross-node property only.** Within one WAL the chain
  already settles disputes; signatures earn their cost exactly where the chain
  cannot: two nodes, two bookkeepers, one argument.

## What v2 does NOT do (honest gaps)

- No timestamp authority — wall-clock smuggling stays a documented gap (see the
  floor-as-clock essay: time claims must derive from the ledger, not ride along).
- No key distribution — signer identity resolution is out of scope; v2 signs
  key IDs, it does not prove key IDs belong to anyone.
- No revocation beyond retirement receipts — a stolen key writes until rotation.
- Receipt bloat: every signed receipt is ~96 bytes heavier; WAL compactification
  (aef8b40) must decide whether signatures survive folding or stay on the tip.

## Acceptance sketch (when built)

1. Same receipt, three suites, signature byte-identical across Python/Rust/TS
   (canonical bytes discipline, same as the café pin).
2. Tamper test: flip one payload bit → chain re-derivation fails AND signature
   verification fails, independently.
3. Strip test: verifier that ignores envelopes reproduces today's behavior
   bit-for-bit (backward compat is a test, not a hope).
4. Cross-node test: node A signs, node B verifies, node B cannot mint an A
   receipt with its own key (negative test).

## Why now, why not now

Corroboration arrived (agent-receipts) and the cross-language floor is proven
(three suites, one vector) — the design can be written honestly. The build waits
for a real two-node dispute; until then the FNV-1a chain is the right cost.
