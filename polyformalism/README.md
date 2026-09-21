# FNV-1a 64-bit Polyformalism Live Test

Three independent implementations of FNV-1a 64-bit — Python, Rust, C — agree on every test vector. This is the canonical demonstration of polyformalism: the same canonical anchor (`0xcbf29ce484222325`) produces the same hash in every language that touches the substrate.

## Test vectors (all must match)

| Input | Expected | Language |
|-------|----------|----------|
| `""` | `0xcbf29ce484222325` | all 3 |
| `"a"` | `0xaf63dc4c8601ec8c` | all 3 |
| `"foobar"` | `0x85944171f73967e8` | all 3 |
| `"café Δ 日本語"` (UTF-8) | `0x024a555471370b18d` | all 3 |
| `"FNV-1a canary 0xcbf29ce484222325"` | `0x0895c0b87d89f1d8` | all 3 |

## Implementations

- **Python**: `/tmp/fnv1a_test.py` (or `ports/python/jev_quilt/q16.py`)
- **Rust**: `/ports/rust/examples/fnv1a_polyformalism.rs` (run with `cargo run --example fnv1a_polyformalism`)
- **C**: `/ports/c/examples/fnv1a_polyformalism.c` (compile with `gcc`, run)

## Run results

```
=== Python FNV-1a 64-bit Test Vectors ===
  ✓ ""                          expected=0xcbf29ce484222325  actual=0xcbf29ce484222325
  ✓ "a"                         expected=0xaf63dc4c8601ec8c  actual=0xaf63dc4c8601ec8c
  ✓ "foobar"                    expected=0x85944171f73967e8  actual=0x85944171f73967e8
  ✓ "café Δ 日本語"              expected=0x24a555471370b18d  actual=0x24a555471370b18d
  ✓ "FNV-1a canary ..."         expected=0x0895c0b87d89f1d8  actual=0x0895c0b87d89f1d8
Result: ALL PASS

=== Rust FNV-1a 64-bit Test Vectors ===   (same)  Result: ALL PASS

=== C FNV-1a 64-bit Test Vectors ===      (same)  Result: ALL PASS
```

## Why this matters

If Python says `"café Δ 日本語"` hashes to `0x024a555471370b18d` and Rust agrees and C agrees, then a witness log written in any language can be verified by any other language. The fleet canary is portable.

This is the substrate's polyformalism layer in its purest form: **one operation, identical byte-exact output across all ports, no language-specific bias.**

## Combined with `0x024a555471370b18d` as fleet canary

Every published substrate ship (TS / Python / Rust) pins this hash. Now we have the C reference to verify them all.

