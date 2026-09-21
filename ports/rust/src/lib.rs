//! jev-quilt Rust port — JEV-SPEC.md §6.2.
//! Pins: fnv1a_1a_utf8("café Δ 日本語") == 0x024a555471370b18d
//! (bytes, not characters — identical to Python and TypeScript).

pub const BASIS: u64 = 0xcbf29ce484222325;
pub const PRIME: u64 = 0x100000001b3;
/// JEV-SPEC §3 pinned vector.
pub const PIN_CAFE: u64 = 0x024a555471370b18d;

pub fn fnv1a(s: &str) -> u64 {
    let mut h = BASIS;
    for b in s.as_bytes() {
        h ^= *b as u64;
        h = h.wrapping_mul(PRIME);
    }
    h
}

/// Hash-chained receipts; verify() re-derives every link.
#[derive(Default)]
pub struct ReceiptChain {
    pub entries: Vec<(String, String, String)>, // (hash, parent, body)
}

impl ReceiptChain {
    pub fn book(&mut self, kind: &str, payload: &str) -> String {
        let body = format!("{{\"kind\":\"{kind}\",\"payload\":{payload}}}");
        let parent = self.entries.last().map(|e| e.0.clone())
            .unwrap_or_else(|| "0".repeat(64));
        let mut h = fnv1a(&format!("{parent}{body}"));
        h = fnv1a(&format!("{h:016x}"));
        let hash = format!("{h:016x}");
        self.entries.push((hash.clone(), parent, body));
        hash
    }
    pub fn verify(&self) -> bool {
        self.entries.iter().enumerate().all(|(i, (hash, parent, body))| {
            let want_parent = if i == 0 { "0".repeat(64) }
                else { self.entries[i - 1].0.clone() };
            if *parent != want_parent { return false; }
            let h = fnv1a(&format!("{parent}{body}"));
            *hash == format!("{:016x}", fnv1a(&format!("{h:016x}")))
        })
    }
}

/// Mean-window predictor + floor; books every observation.
pub struct JevCell {
    pub name: String, pub window: usize, pub floor: f64,
    pub chain: ReceiptChain, pub hist: Vec<f64>, pub alarms: Vec<u64>,
}

impl JevCell {
    pub fn new(name: &str, window: usize, floor: f64) -> Self {
        Self { name: name.into(), window, floor,
               chain: ReceiptChain::default(), hist: vec![], alarms: vec![] }
    }
    pub fn observe(&mut self, t: u64, value: f64) -> bool {
        let mut alarmed = false;
        if self.hist.len() >= self.window {
            let w = &self.hist[self.hist.len() - self.window..];
            let pred: f64 = w.iter().sum::<f64>() / w.len() as f64;
            if (value - pred).abs() > self.floor {
                alarmed = true;
                self.alarms.push(t);
            }
        }
        self.hist.push(value);
        self.chain.book(if alarmed { "jev.alarm" } else { "jev.reading" },
            &format!("{{\"cell\":\"{}\",\"t\":{t},\"value\":{value},\"alarmed\":{alarmed}}}",
                     self.name));
        alarmed
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn pin_cafe() { assert_eq!(fnv1a("café Δ 日本語"), PIN_CAFE); }
    #[test]
    fn pin_basis() { assert_eq!(fnv1a(""), BASIS); }
    #[test]
    fn chain_and_tamper() {
        let mut c = ReceiptChain::default();
        c.book("jev.reading", "{\"t\":0}");
        c.book("jev.alarm", "{\"t\":1}");
        assert!(c.verify());
        c.entries[0].2 = c.entries[0].2.replace('0', "9");
        assert!(!c.verify());
    }
    #[test]
    fn regime_latency_zero() {
        let mut cell = JevCell::new("k", 8, 0.08);
        let mut first = None;
        for t in 0..40u64 {
            let v = if t >= 20 { 0.6 + 0.01 * (t - 20) as f64 }
                    else { 0.05 + 0.005 * (t as f64).sin() };
            if cell.observe(t, v) && first.is_none() { first = Some(t); }
        }
        assert_eq!(first, Some(20));
        assert!(cell.chain.verify());
    }
}
