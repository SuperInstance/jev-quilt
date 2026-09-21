// FNV-1a 64-bit polyformalism test — must match Python reference.
//
// Run with: cargo run --example fnv1a_polyformalism

fn fnv1a_64(s: &str) -> u64 {
    let mut h: u64 = 0xcbf29ce484222325;
    for b in s.bytes() {
        h ^= b as u64;
        h = h.wrapping_mul(0x100000001b3);
    }
    h
}

fn main() {
    let vectors = [
        ("", 0xcbf29ce484222325),
        ("a", 0xaf63dc4c8601ec8c),
        ("foobar", 0x85944171f73967e8),
        ("café Δ 日本語", 0x024a555471370b18d),
        ("FNV-1a canary 0xcbf29ce484222325", 0x0895c0b87d89f1d8),
    ];

    println!("=== Rust FNV-1a 64-bit Test Vectors ===\n");
    let mut all_pass = true;
    for (s, expected) in &vectors {
        let actual = fnv1a_64(s);
        let pass = actual == *expected;
        if !pass { all_pass = false; }
        let marker = if pass { "✓" } else { "✗" };
        println!("  {} {:40?}  expected=0x{:016x}  actual=0x{:016x}",
            marker, s, expected, actual);
    }
    println!("\nResult: {}", if all_pass { "ALL PASS" } else { "FAIL" });
}
