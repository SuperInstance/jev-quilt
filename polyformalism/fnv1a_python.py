#!/usr/bin/env python3
"""Python reference FNV-1a 64-bit."""
def fnv1a_64(s: str) -> int:
    h = 0xcbf29ce484222325
    for b in s.encode('utf-8'):
        h ^= b
        h = (h * 0x100000001b3) & 0xffffffffffffffff
    return h

# Test vectors (must match Rust + C ports)
vectors = [
    ("", 0xcbf29ce484222325),
    ("a", 0xaf63dc4c8601ec8c),
    ("foobar", 0x85944171f73967e8),
    ("café Δ 日本語", 0x024a555471370b18d),
    ("FNV-1a canary 0xcbf29ce484222325", 0x0895c0b87d89f1d8),
]

print('=== Python FNV-1a 64-bit Test Vectors ===\n')
all_pass = True
for s, expected in vectors:
    actual = fnv1a_64(s)
    match = actual == expected
    if not match:
        all_pass = False
    marker = '✓' if match else '✗'
    print(f'  {marker} {s!r:40s}  expected=0x{expected:016x}  actual=0x{actual:016x}')

print(f'\nResult: {"ALL PASS" if all_pass else "FAIL"}')
