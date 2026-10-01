"""Fleet canary test — FNV-1a 64-bit must match across all substrates."""
import unittest

FLEET_CANARY_STRING = "café Δ 日本語"
FLEET_CANARY_VALUE = 0x024a555471370b18d
FNV1A_OFFSET_BASIS = 0xcbf29ce484222325
FNV1A_PRIME = 0x100000001b3


def fnv1a_64(s: str) -> int:
    """FNV-1a 64-bit hash, byte-level."""
    h = FNV1A_OFFSET_BASIS
    for b in s.encode('utf-8'):
        h ^= b
        h = (h * FNV1A_PRIME) & 0xffffffffffffffff
    return h


class TestFleetCanary(unittest.TestCase):
    def test_fleet_canary_matches(self):
        """The fleet canary string must hash to the pinned value."""
        self.assertEqual(fnv1a_64(FLEET_CANARY_STRING), FLEET_CANARY_VALUE)
    
    def test_fleet_canary_unicode(self):
        """Explicit UTF-8 byte encoding must produce stable hash."""
        # 'café Δ 日本語' in UTF-8:
        # c(1) a(1) f(1) é(2)   (1) Δ(2)   (1) 日(3) 本(3) 語(3) = 17 bytes
        expected_cafe_bytes = (
            b'c\x61\x66\xc3\xa9\x20\xce\x94\x20'
            b'\xe6\x97\xa5\xe6\x9c\xac\xe8\xaa\x9e'
        )
        s = expected_cafe_bytes.decode('utf-8')
        self.assertEqual(s, FLEET_CANARY_STRING)
        self.assertEqual(len(s.encode('utf-8')), 18)
        self.assertEqual(fnv1a_64(s), FLEET_CANARY_VALUE)
    
    def test_basis_vector(self):
        """Empty string hashes to offset basis."""
        self.assertEqual(fnv1a_64(""), FNV1A_OFFSET_BASIS)
    
    def test_reference_vectors(self):
        """Standard FNV-1a reference vectors."""
        # From http://www.isthe.com/chongo/tech/comp/fnv/
        self.assertEqual(fnv1a_64("a"), 0xaf63dc4c8601ec8c)
        self.assertEqual(fnv1a_64("foobar"), 0x85944171f73967e8)


if __name__ == '__main__':
    unittest.main()
