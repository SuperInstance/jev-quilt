//! Below the quilt.
//!
//! Python `jev_quilt` *simulates* exactness; this crate *is* it.
//! Law 1 at the type level: a coordinate is (i64, i64) — the compiler
//! makes it impossible to hold identity as f64 anywhere in the fabric.
//! Law 4 at the metal: the receipt chain is a value, not a log file.

/// Exact rational n/d. Invariant: den > 0, gcd(num, den) == 1.
/// Fixed-point is the special case d | 10^6; general rationals stay exact.
#[derive(Clone, Copy, PartialEq, Eq, Debug, Hash)]
pub struct Q16 {
    pub num: i64,
    pub den: i64,
}

impl Q16 {
    pub const SCALE: i64 = 1_000_000;

    pub fn new(num: i64, den: i64) -> Option<Self> {
        if den <= 0 {
            return None; // honest refusal; the sign lives in num
        }
        let g = gcd(num.unsigned_abs() as u64, den as u64) as i64;
        Some(Q16 { num: num / g, den: den / g })
    }

    pub fn from_int(n: i64) -> Self {
        Q16 { num: n, den: 1 }
    }

    /// Fixed-point convenience: 1_000_000ths, the q16 wire format.
    /// Normalized like every other value — 0.5 IS 1/2, not "close to".
    pub fn fixed(micro: i64) -> Self {
        Q16::new(micro, Self::SCALE).expect("SCALE > 0")
    }

    pub fn checked_add(self, o: Q16) -> Option<Q16> {
        let n = (self.num as i128).checked_mul(o.den as i128)?
            + (o.num as i128).checked_mul(self.den as i128)?;
        let d = (self.den as i128).checked_mul(o.den as i128)?;
        if n > i64::MAX as i128 || d > i64::MAX as i128 {
            return None; // overflow is a refusal, never a wrap
        }
        Q16::new(n as i64, d as i64)
    }

    pub fn checked_mul(self, o: Q16) -> Option<Q16> {
        let n = (self.num as i128).checked_mul(o.num as i128)?;
        let d = (self.den as i128).checked_mul(o.den as i128)?;
        if n > i64::MAX as i128 || d > i64::MAX as i128 {
            return None;
        }
        Q16::new(n as i64, d as i64)
    }

    /// The one permitted betrayal, spelled so it can never be silent:
    /// identity never passes through this; projections may.
    pub fn to_f64_betrayal(self) -> f64 {
        self.num as f64 / self.den as f64
    }
}

fn gcd(mut a: u64, mut b: u64) -> u64 {
    while b != 0 {
        let t = b;
        b = a % b;
        a = t;
    }
    if a == 0 { 1 } else { a }
}

/// A cell. Identity is an integer lattice point, full stop — there is no
/// constructor that takes a float, so law 1 is enforced by the type system
/// rather than by discipline.
#[derive(Clone, PartialEq, Eq, Debug, Hash)]
pub struct Cell {
    pub name: String,
    pub coord: (i64, i64),
}

impl Cell {
    pub fn new(name: &str, k: i64, s: i64) -> Self {
        Cell { name: name.to_string(), coord: (k, s) }
    }
}

/// fnv1a-64, the same algorithm the fleet's rate limiter and the hermit
/// WAL use — integrity, not security.
pub fn fnv1a(data: &str) -> u64 {
    let mut h: u64 = 0xcbf2_9ce4_8422_2325;
    for b in data.as_bytes() {
        h ^= *b as u64;
        h = h.wrapping_mul(0x0000_0100_0000_01b3);
    }
    h
}

/// One booked state change. The chain is a VALUE: verify() recomputes it.
#[derive(Clone, PartialEq, Eq, Debug)]
pub struct Receipt {
    pub tick: u64,
    pub prev_hash: u64,
    pub kind_hash: u64,
    pub payload_hash: u64,
    pub chain: u64,
}

pub struct Bookkeeper {
    pub cell: String,
    pub tick: u64,
    pub prev: u64,
    pub log: Vec<Receipt>,
}

impl Bookkeeper {
    pub fn new(cell: &str) -> Self {
        Bookkeeper { cell: cell.to_string(), tick: 0, prev: 0, log: Vec::new() }
    }

    pub fn book(&mut self, decision_kind: &str, state_fingerprint: u64) -> Receipt {
        self.tick += 1;
        let kind_hash = fnv1a(decision_kind);
        let payload_hash = fnv1a(&format!(
            "{}:{}:{:016x}:{:016x}", self.cell, self.tick, kind_hash, state_fingerprint
        ));
        let chain = fnv1a(&format!("{:016x}:{:016x}", self.prev, payload_hash));
        let r = Receipt { tick: self.tick, prev_hash: self.prev, kind_hash, payload_hash, chain };
        self.log.push(r.clone());
        self.prev = chain;
        r
    }

    /// Replay from nothing. The log either re-derives or it doesn't.
    pub fn verify(&self) -> bool {
        let mut prev: u64 = 0;
        for (i, r) in self.log.iter().enumerate() {
            // payload_hash was committed at book time over
            // cell:tick:kind:fingerprint; the receipt deliberately does not
            // retain the fingerprint — the chain binds it, and the original
            // fingerprint lives in the projection. So verify re-derives the
            // CHAIN (and tick discipline); payload integrity is transitive.
            let expect_chain = fnv1a(&format!("{:016x}:{:016x}", prev, r.payload_hash));
            if r.tick != (i + 1) as u64 || r.prev_hash != prev || r.chain != expect_chain {
                return false;
            }
            prev = r.chain;
        }
        true
    }

    pub fn wake_state(&self) -> (u64, Option<u64>) {
        (self.tick, self.log.last().map(|r| r.chain))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rationals_are_exact_not_close() {
        let a = Q16::new(1, 3).unwrap();
        let b = Q16::new(1, 6).unwrap();
        assert_eq!(a.checked_add(b).unwrap(), Q16::new(1, 2).unwrap());
    }

    #[test]
    fn fixed_point_is_a_special_case_not_a_limit() {
        let q = Q16::fixed(500_000); // 0.5
        assert_eq!(q, Q16::new(1, 2).unwrap());
        assert_eq!(q.checked_mul(Q16::new(1, 3).unwrap()).unwrap(),
                   Q16::new(1, 6).unwrap());
    }

    #[test]
    fn overflow_is_a_refusal_not_a_wrap() {
        let big = Q16::new(i64::MAX - 1, 1).unwrap();
        assert!(big.checked_add(Q16::new(5, 1).unwrap()).is_none());
    }

    #[test]
    fn zero_denominator_refused() {
        assert!(Q16::new(1, 0).is_none());
        assert!(Q16::new(1, -4).is_none());
    }

    #[test]
    fn identity_has_no_float_constructor() {
        let c = Cell::new("spine.accusation", 1, 2);
        assert_eq!(c.coord, (1, 2));
        // there is no Cell::from_f64 — this test is the absence of a method
    }

    #[test]
    fn receipt_chain_replays_and_detects_tamper() {
        let mut bk = Bookkeeper::new("test.cell");
        bk.book("decided", 42);
        bk.book("rejected", 43);
        assert!(bk.verify());
        assert_eq!(bk.wake_state().0, 2);
        let mut forged = bk;
        forged.log[0].payload_hash ^= 0xdead_beef; // tamper
        assert!(!forged.verify());
    }

    #[test]
    fn fnv1a_matches_reference_vector() {
        // reference: Python jev_quilt.q16.fnv1a("") == 0xcbf29ce484222325
        assert_eq!(fnv1a(""), 0xcbf2_9ce4_8422_2325);
        assert_eq!(fnv1a("a"), 0xaf63_dc4c_8601_ec8c);
    }
}
