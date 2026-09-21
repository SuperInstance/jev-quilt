#include <stdio.h>
#include <stdint.h>
#include <string.h>

uint64_t fnv1a_64(const char *s, size_t len) {
    uint64_t h = 0xcbf29ce484222325ULL;
    for (size_t i = 0; i < len; i++) {
        h ^= (uint8_t)s[i];
        h *= 0x100000001b3ULL;
    }
    return h;
}

int main() {
    struct {
        const char *s;
        size_t len;
        uint64_t expected;
    } vectors[] = {
        {"", 0, 0xcbf29ce484222325ULL},
        {"a", 1, 0xaf63dc4c8601ec8cULL},
        {"foobar", 6, 0x85944171f73967e8ULL},
        {"FNV-1a canary 0xcbf29ce484222325", 32, 0x0895c0b87d89f1d8ULL},
        // Note: 'café Δ 日本語' is multi-byte UTF-8, but byte-level FNV-1a should give the same hash
        // as long as the byte representation is identical. The Rust/Python tests use .encode()/.bytes()
        // which gives UTF-8 bytes. Here we encode the UTF-8 directly.
    };
    size_t cafe_len = 0;
    // Encode "café Δ 日本語" as UTF-8 bytes
    const char cafe[] = {'c','a','f',(char)0xc3,(char)0xa9,' ',
                          (char)0xce,(char)0x94,' ',
                          (char)0xe6,(char)0x97,(char)0xa5,
                          (char)0xe6,(char)0x9c,(char)0xac,
                          (char)0xe8,(char)0xaa,(char)0x9e, 0};
    cafe_len = strlen(cafe);
    uint64_t cafe_expected = 0x024a555471370b18dULL;
    
    int all_pass = 1;
    printf("=== C FNV-1a 64-bit Test Vectors ===\n\n");
    
    int n = sizeof(vectors)/sizeof(vectors[0]);
    for (int i = 0; i < n; i++) {
        uint64_t actual = fnv1a_64(vectors[i].s, vectors[i].len);
        int pass = actual == vectors[i].expected;
        if (!pass) all_pass = 0;
        printf("  %s %-40s  expected=0x%016lx  actual=0x%016lx\n",
               pass ? "✓" : "✗", vectors[i].s, vectors[i].expected, actual);
    }
    
    // Test the cafe string (UTF-8 bytes)
    uint64_t cafe_actual = fnv1a_64(cafe, cafe_len);
    int cafe_pass = cafe_actual == cafe_expected;
    if (!cafe_pass) all_pass = 0;
    printf("  %s %-40s  expected=0x%016lx  actual=0x%016lx\n",
           cafe_pass ? "✓" : "✗", "café Δ 日本語 (UTF-8 bytes)", cafe_expected, cafe_actual);
    
    printf("\nResult: %s\n", all_pass ? "ALL PASS" : "FAIL");
    return all_pass ? 0 : 1;
}
