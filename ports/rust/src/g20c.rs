//! G20c — the Deposit Reader.
//!
//! G20b's own STRETCH note (`ports/rust/src/g20b.rs`'s module docstring):
//! `Commons.root()`'s MMR/leaf mechanics were reproduced in Rust, but the
//! commons **deposit table itself** (which `(key, answer, weight)` triples
//! exist at all) was taken from the fixture as ground truth. This module
//! closes that gap: it independently DERIVES the deposit table — every
//! `Deposit`'s identity/amount/trust-weight and the resulting
//! `commons_root` — from nothing but the raw witness readings, the
//! recipient's own trust/quorum/floor, and `Schoolhouse.enroll`'s bridge,
//! by re-implementing the real pipeline: `Claim.from_books` (G16) ->
//! `attest` (G17) -> `admit` (G11/G14) -> `Commons.deposit`/`forget` (R2/
//! G12). Never by copying Python's table, always by recomputing from the
//! same raw inputs `vectors/gen_g20c_deposit_reader_vectors.py` exports.
//!
//! ## Reproduced byte-for-byte (see `tests` below — this is the gate)
//!
//!   * `Q16` exact-rational arithmetic (`q16.py`) — add/mul/compare, gcd
//!     reduction, sign normalization.
//!   * `predictor.surprise` — exact graded difference.
//!   * `CalibratedFloor` (`calibrate.py`) — the adaptive floor
//!     (`mean(window) * slack`, clamped by `floor_min`), predict-before-
//!     update discipline preserved (`swarm_drift` folds every witness's
//!     surprise in before judging ANY of them, the same law `Claim.
//!     from_books` and `admit`'s `_recompute_drift` share).
//!   * `Claim.from_books`'s swarm algorithm (`claim.py`) — modal value
//!     (ties broken lexicographically), consensus magnitude, per-witness
//!     drift flags, `Claim.consensus()`'s unanimity-and-quorum gate.
//!   * `attest.canonical_attestation_bytes` / `attest.attestation_root`
//!     (`attest.py`) — the pipe-joined canonical form and the meta-leaf
//!     MMR root the signature seals; re-derived and checked against the
//!     carried `root`, independent of the signature itself (see STRETCH).
//!   * `admit`'s recipient-side judgment (`attest.py`) — trust-based
//!     drop, `_recompute_drift` over the trust-passed subset, the
//!     unanimity+quorum `conferred` gate, and G14 sea-grading (ANSWER vs
//!     CONFIRM against the recipient's OWN re-graded floor).
//!   * `Schoolhouse.enroll`'s ONE bridge (`schoolhouse.py`): a conferred
//!     admission becomes `Commons.deposit(key, admission.value,
//!     len(admission.trusted), source=att.signer)`; a refused admission
//!     deposits nothing.
//!   * `Commons.deposit`/`forget`/`deposits()` (`commons.py`) — weight
//!     pooling across independent issuers for the same `(key, answer)`,
//!     and G12 tombstone bookkeeping — re-implemented here as
//!     `CommonsBuilder`, feeding the SAME leaf/MMR mechanics G20b already
//!     proved (`crate::g20b::commons_root`, reused, not rewritten).
//!
//! ## STRETCH (not reproduced here — honest boundary)
//!
//!   * **Ed25519/BLAKE3 signature verification itself.** `admit` calls
//!     `verify_attestation` first, which checks a real Ed25519 signature
//!     over a BLAKE3-hashed message. Reproducing that from scratch means a
//!     from-scratch 255-bit modular-arithmetic bignum + Curve25519 point
//!     arithmetic + SHA-512 + BLAKE3, in pure `std` (no crypto crate) — a
//!     second-reader project of its own, exactly as G20b's own STRETCH note
//!     flagged. This reader instead independently re-derives the ROOT
//!     integrity check (`attestation_root` recomputed and compared against
//!     the carried `root` — this catches ANY edited reading, consensus,
//!     quorum, or floor, same as `verify_attestation`'s first check) and
//!     everything admit() does AFTER "the signature verified": the
//!     fixture's scenario never tampers with a signature, so Python's own
//!     `verify_attestation` always returns `ok=True` here, and this reader
//!     picks up the derivation from that same true point — same STRETCH
//!     shape as G20b, extended one rung further rather than closed.
//!   * Non-ASCII text and the `float` `reading_fn` path: out of scope, same
//!     ASCII/exact-only boundary G20b already documents.

use crate::g20b::{commons_root, mmr_root};
use crate::sha256::sha256;
use std::collections::{BTreeMap, BTreeSet};

// ── Q16: exact-rational identity, mirroring `jev_quilt/q16.py` ──────────
// i128 rather than i64: Python's ints are arbitrary precision; this
// fixture's numbers are small, but cross-multiplication (`a.num*b.den`)
// wants the headroom.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Q16 {
    pub num: i128,
    pub den: i128,
}

fn gcd(a: i128, b: i128) -> i128 {
    if b == 0 {
        a
    } else {
        gcd(b, a % b)
    }
}

impl Q16 {
    pub fn new(num: i128, den: i128) -> Self {
        assert!(den != 0, "q16: zero denominator");
        let g = gcd(num.abs(), den.abs());
        let g = if g == 0 { 1 } else { g };
        let (mut n, mut d) = (num / g, den / g);
        if d < 0 {
            n = -n;
            d = -d;
        }
        Q16 { num: n, den: d }
    }
    pub fn int(n: i128) -> Self {
        Q16::new(n, 1)
    }
    pub fn add(self, o: Q16) -> Q16 {
        Q16::new(self.num * o.den + o.num * self.den, self.den * o.den)
    }
    pub fn sub(self, o: Q16) -> Q16 {
        Q16::new(self.num * o.den - o.num * self.den, self.den * o.den)
    }
    pub fn mul(self, o: Q16) -> Q16 {
        Q16::new(self.num * o.num, self.den * o.den)
    }
    pub fn gt(self, o: Q16) -> bool {
        self.num * o.den > o.num * self.den
    }
}

/// `predictor.surprise(outcome, predicted)`: exact graded difference.
pub fn surprise(outcome: Q16, predicted: Q16) -> Q16 {
    let d = outcome.sub(predicted);
    Q16::new(d.num.abs(), d.den)
}

/// Parse a diploma/attestation-style `"num/den"` wire floor back into Q16
/// (`diploma.parse_floor`).
pub fn parse_floor(s: &str) -> Q16 {
    let mut parts = s.splitn(2, '/');
    let n: i128 = parts.next().unwrap().parse().expect("parse_floor: bad numerator");
    let d: i128 = parts.next().unwrap().parse().expect("parse_floor: bad denominator");
    Q16::new(n, d)
}

// ── CalibratedFloor: adaptive alarm floor, mirroring `calibrate.py` ─────
pub struct CalibratedFloor {
    k: usize,
    slack: Q16,
    floor_min: Q16,
    window: Vec<Q16>,
}

impl CalibratedFloor {
    /// `k` must be in the same 1/K-exact family `calibrate.py` enforces;
    /// this reader trusts the fixture's `floor_k` (always 4 here) rather
    /// than re-validating the whole `EXACT_K` set.
    pub fn new(k: usize) -> Self {
        CalibratedFloor {
            k,
            slack: Q16::new(5, 2),
            floor_min: Q16::new(1, 1000),
            window: Vec::new(),
        }
    }
    pub fn floor(&self) -> Option<Q16> {
        if self.window.len() < self.k {
            return None;
        }
        let mean = self
            .window
            .iter()
            .fold(Q16::int(0), |a, &b| a.add(b))
            .mul(Q16::new(1, self.k as i128));
        let f = mean.mul(self.slack);
        Some(if f.gt(self.floor_min) { f } else { self.floor_min })
    }
    pub fn update(&mut self, s: Q16) {
        self.window.push(s);
        if self.window.len() > self.k {
            self.window.remove(0);
        }
    }
}

// ── the shared swarm-drift law: `Claim.from_books` AND `admit`'s
//    `_recompute_drift` are the SAME algorithm over two different witness
//    sets (the whole claim vs. the recipient's trust-passed subset) ──────
/// One witness's fold-in reading: (name, value, drifting).
pub type JudgedReading = (String, String, bool);

/// Modal value (most-reported; ties broken lexicographically), consensus
/// magnitude over the agreeing witnesses, every witness's surprise against
/// it, the WHOLE set folded into `cal` before anyone is judged against the
/// resulting floor. Returns witnesses sorted by name (matching `sorted
/// (raw.keys())`/`names` in both `claim.py` and `attest.py`).
pub fn swarm_drift(witnesses: &[(String, String, Q16)], cal: &mut CalibratedFloor) -> Vec<JudgedReading> {
    if witnesses.is_empty() {
        return Vec::new();
    }
    let mut sorted: Vec<&(String, String, Q16)> = witnesses.iter().collect();
    sorted.sort_by(|a, b| a.0.cmp(&b.0));

    let mut counts: BTreeMap<&str, usize> = BTreeMap::new();
    for (_, v, _) in &sorted {
        *counts.entry(v.as_str()).or_insert(0) += 1;
    }
    let top = *counts.values().max().unwrap();
    let modal = counts
        .iter()
        .filter(|(_, &c)| c == top)
        .map(|(v, _)| *v)
        .min()
        .unwrap()
        .to_string();

    let agreeing: Vec<Q16> = sorted.iter().filter(|(_, v, _)| *v == modal).map(|(_, _, m)| *m).collect();
    let consensus_mag = agreeing
        .iter()
        .fold(Q16::int(0), |a, &b| a.add(b))
        .mul(Q16::new(1, agreeing.len() as i128));

    let surprises: Vec<Q16> = sorted.iter().map(|(_, _, m)| surprise(*m, consensus_mag)).collect();
    for s in &surprises {
        cal.update(*s);
    }
    let f = cal.floor();

    sorted
        .iter()
        .zip(surprises.iter())
        .map(|((name, val, _mag), s)| {
            let drifting = f.map_or(false, |fl| s.gt(fl));
            (name.clone(), val.clone(), drifting)
        })
        .collect()
}

/// `Claim.consensus()`: unanimity among the non-drifting subset AND at
/// least `quorum` of them — a majority with a live dissenter is not
/// reproducible.
pub fn claim_consensus(readings: &[JudgedReading], quorum: usize) -> Option<String> {
    let trusted: Vec<&JudgedReading> = readings.iter().filter(|(_, _, d)| !d).collect();
    if trusted.len() < quorum {
        return None;
    }
    let values: BTreeSet<&str> = trusted.iter().map(|(_, v, _)| v.as_str()).collect();
    if values.len() == 1 {
        Some((*values.iter().next().unwrap()).to_string())
    } else {
        None
    }
}

// ── attest.py: canonical bytes + attestation_root (no crypto — see the
//    module docstring's STRETCH) ─────────────────────────────────────────
fn attestation_leaf(witness: &str, value: &str, drifting: bool) -> [u8; 32] {
    let canon = format!("{}\u{1f}{}\u{1f}{}", witness, value, drifting as i32);
    sha256(canon.as_bytes())
}

pub fn canonical_attestation_bytes(
    readings: &[JudgedReading],
    consensus: Option<&str>,
    quorum: i64,
    earned_floor: Option<&str>,
) -> Vec<u8> {
    let mut sorted = readings.to_vec();
    sorted.sort_by(|a, b| a.0.cmp(&b.0));
    let rs_part = sorted
        .iter()
        .map(|(w, v, d)| format!("{}\u{1f}{}\u{1f}{}", w, v, *d as i32))
        .collect::<Vec<_>>()
        .join("|");
    format!(
        "{}|{}|{}|{}",
        rs_part,
        consensus.unwrap_or(""),
        quorum,
        earned_floor.unwrap_or("")
    )
    .into_bytes()
}

pub fn attestation_root(
    readings: &[JudgedReading],
    consensus: Option<&str>,
    quorum: i64,
    earned_floor: Option<&str>,
) -> [u8; 32] {
    let mut sorted = readings.to_vec();
    sorted.sort_by(|a, b| a.0.cmp(&b.0));
    let mut leaves: Vec<[u8; 32]> = sorted.iter().map(|(w, v, d)| attestation_leaf(w, v, *d)).collect();
    let meta = sha256(
        format!(
            "__meta__\u{1f}{}\u{1f}{}\u{1f}{}",
            consensus.unwrap_or(""),
            quorum,
            earned_floor.unwrap_or("")
        )
        .as_bytes(),
    );
    leaves.push(meta);
    mmr_root(&leaves)
}

// ── attest.admit: the recipient's OWN verdict over an Attestation ──────
#[derive(Debug, Clone, PartialEq)]
pub struct Admission {
    pub conferred: bool,
    pub verdict: String,
    pub value: Option<String>,
    pub reason: Option<String>,
    pub trusted: Vec<String>, // sorted
    pub dropped: Vec<String>, // sorted
}

/// Mirrors `attest.admit` exactly, taking "the signature already verified"
/// as given (see the module docstring's STRETCH): trust-based drop, THEN
/// `_recompute_drift` over the trust-passed subset (mutating `cal`, same
/// as Python mutates the recipient's `CalibratedFloor` in place), THEN the
/// unanimity+quorum gate, THEN G14 sea-grading against the recipient's OWN
/// re-graded floor.
#[allow(clippy::too_many_arguments)]
pub fn admit(
    all_readings: &[JudgedReading], // the attestation's carried readings (ALL witnesses)
    trust: &BTreeMap<String, i64>,
    quorum: usize,
    magnitudes: &BTreeMap<String, Q16>,
    cal: &mut CalibratedFloor,
    earned_floor_wire: Option<&str>,
    base_verdict: &str,
) -> Admission {
    let all_ids: BTreeSet<String> = all_readings.iter().map(|(w, _, _)| w.clone()).collect();
    let trust_passed: Vec<&JudgedReading> = all_readings
        .iter()
        .filter(|(w, _, _)| *trust.get(w).unwrap_or(&0) > 0)
        .collect();
    let trust_passed_ids: BTreeSet<String> = trust_passed.iter().map(|(w, _, _)| w.clone()).collect();
    let trust_dropped: BTreeSet<String> = all_ids.difference(&trust_passed_ids).cloned().collect();

    let witnesses_for_drift: Vec<(String, String, Q16)> = trust_passed
        .iter()
        .map(|(w, v, _)| {
            let mag = *magnitudes
                .get(w)
                .unwrap_or_else(|| panic!("admit: reading_magnitude missing for witness {w:?}"));
            (w.clone(), v.clone(), mag)
        })
        .collect();
    let judged = swarm_drift(&witnesses_for_drift, cal);
    let drift_dropped: BTreeSet<String> = judged.iter().filter(|(_, _, d)| *d).map(|(w, _, _)| w.clone()).collect();

    let trusted: Vec<&JudgedReading> = trust_passed
        .iter()
        .filter(|(w, _, _)| !drift_dropped.contains(w))
        .cloned()
        .collect();
    let mut dropped: Vec<String> = trust_dropped.union(&drift_dropped).cloned().collect();
    dropped.sort();
    let mut trusted_ids: Vec<String> = trusted.iter().map(|(w, _, _)| w.clone()).collect();
    trusted_ids.sort();

    let values: BTreeSet<&str> = trusted.iter().map(|(_, v, _)| v.as_str()).collect();
    let conferred = trusted.len() >= quorum && values.len() == 1;
    if !conferred {
        return Admission {
            conferred: false,
            verdict: base_verdict.to_string(),
            value: None,
            reason: Some("not_reproduced_for_recipient".to_string()),
            trusted: trusted_ids,
            dropped,
        };
    }
    let value = (*values.iter().next().unwrap()).to_string();

    let earned_floor_q = earned_floor_wire.map(parse_floor);
    let recipient_sea = cal.floor();
    let verdict = match (earned_floor_q, recipient_sea) {
        (Some(efq), Some(rs)) if rs.gt(efq) => "CONFIRM",
        _ => "ANSWER",
    };
    Admission {
        conferred: true,
        verdict: verdict.to_string(),
        value: Some(value),
        reason: None,
        trusted: trusted_ids,
        dropped,
    }
}

// ── schoolhouse.enroll's ONE bridge + commons.py, re-implemented ────────
/// `Commons.deposit`/`forget`/`deposits()`/`root()`, re-implemented (not
/// re-derived from the fixture): weight pooling across independent
/// issuers for the same `(key, answer)`, G12 tombstones, feeding the SAME
/// leaf/MMR mechanics G20b already proved (`crate::g20b::commons_root`).
#[derive(Default)]
pub struct CommonsBuilder {
    weights: BTreeMap<(String, String), i64>,
    tombstones: BTreeSet<(String, String)>,
}

impl CommonsBuilder {
    pub fn new() -> Self {
        Self::default()
    }
    /// `Commons.deposit`: weight <= 0 is a no-op (mirrors the Python guard).
    pub fn deposit(&mut self, key: &str, answer: &str, weight: i64) {
        if weight <= 0 {
            return;
        }
        *self.weights.entry((key.to_string(), answer.to_string())).or_insert(0) += weight;
    }
    /// The `Schoolhouse.enroll` bridge in one call: deposits iff the
    /// admission conferred, at `weight = len(admission.trusted)`.
    pub fn enroll(&mut self, key: &str, admission: &Admission) {
        if admission.conferred {
            let answer = admission.value.as_ref().expect("conferred admission always carries a value");
            self.deposit(key, answer, admission.trusted.len() as i64);
        }
    }
    /// `Commons.forget`: deletes the live weight, books the tombstone.
    pub fn forget(&mut self, key: &str, answer: &str) {
        self.weights.remove(&(key.to_string(), answer.to_string()));
        self.tombstones.insert((key.to_string(), answer.to_string()));
    }
    /// `Commons.deposits()`: canonical `(key, answer)` order — `BTreeMap`
    /// iteration is already exactly that order.
    pub fn deposits(&self) -> Vec<(String, String, i64)> {
        self.weights.iter().map(|((k, a), w)| (k.clone(), a.clone(), *w)).collect()
    }
    pub fn tombstones(&self) -> Vec<(String, String)> {
        self.tombstones.iter().cloned().collect()
    }
    /// `Commons.root()` — reuses G20b's proven leaf/MMR mechanics.
    pub fn root(&self) -> [u8; 32] {
        commons_root(&self.deposits(), &self.tombstones())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::g20b::hex32;
    use crate::minijson::{parse, Json};

    const VECTORS_JSON: &str = include_str!("../../../vectors/g20c_deposit_reader_vectors.json");

    fn load() -> Json {
        parse(VECTORS_JSON).expect("vectors JSON must parse")
    }

    fn q16_from(j: &Json) -> Q16 {
        Q16::new(j.get("num").unwrap().as_i64().unwrap() as i128, j.get("den").unwrap().as_i64().unwrap() as i128)
    }

    fn str_list(j: &Json) -> Vec<String> {
        j.as_arr().unwrap().iter().map(|s| s.as_str().unwrap().to_string()).collect()
    }

    /// A question's raw (name, value, magnitude) witness triples, sorted.
    fn witnesses_of(q: &Json) -> Vec<(String, String, Q16)> {
        let ws = q.get("witnesses").unwrap().as_obj().unwrap();
        let mut out: Vec<(String, String, Q16)> = ws
            .iter()
            .map(|(name, info)| {
                (
                    name.clone(),
                    info.get("value").unwrap().as_str().unwrap().to_string(),
                    q16_from(info.get("magnitude").unwrap()),
                )
            })
            .collect();
        out.sort_by(|a, b| a.0.cmp(&b.0));
        out
    }

    fn trust_of(q: &Json) -> BTreeMap<String, i64> {
        q.get("recipient_trust")
            .unwrap()
            .as_obj()
            .unwrap()
            .iter()
            .map(|(k, v)| (k.clone(), v.as_i64().unwrap()))
            .collect()
    }

    #[test]
    fn q16_and_surprise_arithmetic_matches_hand_verified_python() {
        // From a hand run of jev_quilt.q16/predictor against the same
        // 7-witness drift example this module's docstring describes:
        // consensus 740/7, a0's surprise 2760/7, floor 9235/56.
        let mags: Vec<(String, String, Q16)> = vec![
            ("a0".into(), "v".into(), Q16::int(500)),
            ("b1".into(), "v".into(), Q16::int(40)),
            ("b2".into(), "v".into(), Q16::int(41)),
            ("b3".into(), "v".into(), Q16::int(39)),
            ("b4".into(), "v".into(), Q16::int(42)),
            ("b5".into(), "v".into(), Q16::int(38)),
            ("b6".into(), "v".into(), Q16::int(40)),
        ];
        let mut cal = CalibratedFloor::new(4);
        let judged = swarm_drift(&mags, &mut cal);
        assert_eq!(cal.floor(), Some(Q16::new(9235, 56)));
        let a0 = judged.iter().find(|(n, _, _)| n == "a0").unwrap();
        assert!(a0.2, "a0 should be judged drifting");
        for name in ["b1", "b2", "b3", "b4", "b5", "b6"] {
            let r = judged.iter().find(|(n, _, _)| n == name).unwrap();
            assert!(!r.2, "{name} should NOT be judged drifting");
        }
    }

    #[test]
    fn swarm_drift_reproduces_claim_readings_and_consensus_for_every_question() {
        let v = load();
        for q in v.get("questions").unwrap().as_arr().unwrap() {
            let witnesses = witnesses_of(q);
            let floor_k = q.get("floor_k").unwrap().as_i64().unwrap() as usize;
            let claim_quorum = q.get("claim_quorum").unwrap().as_i64().unwrap() as usize;

            let mut cal = CalibratedFloor::new(floor_k);
            let judged = swarm_drift(&witnesses, &mut cal);

            let expected_readings = q.get("expected").unwrap().get("claim_readings").unwrap().as_arr().unwrap();
            assert_eq!(judged.len(), expected_readings.len());
            for exp in expected_readings {
                let w = exp.get("witness").unwrap().as_str().unwrap();
                let got = judged.iter().find(|(n, _, _)| n == w).unwrap();
                assert_eq!(got.1, exp.get("value").unwrap().as_str().unwrap(), "value mismatch for {w}");
                assert_eq!(got.2, exp.get("drifting").unwrap().as_bool().unwrap(), "drifting mismatch for {w}");
            }

            let consensus = claim_consensus(&judged, claim_quorum);
            let expected_consensus = q.get("expected").unwrap().get("claim_consensus").unwrap();
            match expected_consensus {
                Json::Null => assert_eq!(consensus, None, "question {:?}", q.get("key")),
                Json::Str(s) => assert_eq!(consensus.as_deref(), Some(s.as_str())),
                _ => panic!("claim_consensus must be str or null"),
            }
        }
    }

    #[test]
    fn attestation_root_recomputed_and_matches_the_carried_root() {
        let v = load();
        for q in v.get("questions").unwrap().as_arr().unwrap() {
            let att = q.get("expected").unwrap().get("attestation").unwrap();
            let readings: Vec<JudgedReading> = att
                .get("readings")
                .unwrap()
                .as_arr()
                .unwrap()
                .iter()
                .map(|r| {
                    (
                        r.get("witness").unwrap().as_str().unwrap().to_string(),
                        r.get("value").unwrap().as_str().unwrap().to_string(),
                        r.get("drifting").unwrap().as_bool().unwrap(),
                    )
                })
                .collect();
            let consensus = att.get("consensus").unwrap().as_str();
            let quorum = att.get("quorum").unwrap().as_i64().unwrap();
            let earned_floor = att.get("earned_floor").unwrap().as_str();

            let root = attestation_root(&readings, consensus, quorum, earned_floor);
            assert_eq!(hex32(&root), att.get("root").unwrap().as_str().unwrap(), "question {:?}", q.get("key"));

            // canonical bytes must be non-empty and deterministic under
            // re-sorting (a cheap smoke check the byte layout is stable).
            let bytes1 = canonical_attestation_bytes(&readings, consensus, quorum, earned_floor);
            let mut shuffled = readings.clone();
            shuffled.reverse();
            let bytes2 = canonical_attestation_bytes(&shuffled, consensus, quorum, earned_floor);
            assert_eq!(bytes1, bytes2, "canonical bytes must not depend on input order");
        }
    }

    #[test]
    fn admit_matches_python_admission_for_every_question() {
        let v = load();
        for q in v.get("questions").unwrap().as_arr().unwrap() {
            let witnesses = witnesses_of(q);
            let magnitudes: BTreeMap<String, Q16> = witnesses.iter().map(|(n, _, m)| (n.clone(), *m)).collect();
            let trust = trust_of(q);
            let floor_k = q.get("floor_k").unwrap().as_i64().unwrap() as usize;
            let admit_quorum = q.get("admit_quorum").unwrap().as_i64().unwrap() as usize;

            let att = q.get("expected").unwrap().get("attestation").unwrap();
            let all_readings: Vec<JudgedReading> = att
                .get("readings")
                .unwrap()
                .as_arr()
                .unwrap()
                .iter()
                .map(|r| {
                    (
                        r.get("witness").unwrap().as_str().unwrap().to_string(),
                        r.get("value").unwrap().as_str().unwrap().to_string(),
                        r.get("drifting").unwrap().as_bool().unwrap(),
                    )
                })
                .collect();
            let earned_floor = att.get("earned_floor").unwrap().as_str();

            let mut cal = CalibratedFloor::new(floor_k);
            let admission = admit(&all_readings, &trust, admit_quorum, &magnitudes, &mut cal, earned_floor, "CONFIRM");

            let exp = q.get("expected").unwrap().get("admission").unwrap();
            assert_eq!(admission.conferred, exp.get("conferred").unwrap().as_bool().unwrap(), "key {:?}", q.get("key"));
            assert_eq!(admission.verdict, exp.get("verdict").unwrap().as_str().unwrap());
            assert_eq!(admission.value.as_deref(), exp.get("value").unwrap().as_str());
            assert_eq!(admission.reason.as_deref(), exp.get("reason").unwrap().as_str());
            assert_eq!(admission.trusted, str_list(exp.get("trusted").unwrap()));
            assert_eq!(admission.dropped, str_list(exp.get("dropped").unwrap()));
        }
    }

    /// THE GATE: derive the whole commons deposit table + root from raw
    /// witness inputs alone (never reading the fixture's own `expected`
    /// intermediate fields) and compare against `commons`/`pins`.
    #[test]
    fn deposit_table_and_commons_root_derived_end_to_end_from_raw_witness_inputs_alone() {
        let v = load();
        let mut commons = CommonsBuilder::new();

        for q in v.get("questions").unwrap().as_arr().unwrap() {
            let key = q.get("key").unwrap().as_str().unwrap();
            let witnesses = witnesses_of(q);
            let magnitudes: BTreeMap<String, Q16> = witnesses.iter().map(|(n, _, m)| (n.clone(), *m)).collect();
            let trust = trust_of(q);
            let floor_k = q.get("floor_k").unwrap().as_i64().unwrap() as usize;
            let claim_quorum = q.get("claim_quorum").unwrap().as_i64().unwrap() as usize;
            let admit_quorum = q.get("admit_quorum").unwrap().as_i64().unwrap() as usize;

            // issuer side: reproduce the claim (needed only to prove
            // earns_standing — `attest` refuses otherwise; the carried
            // readings equal `swarm_drift`'s own output over ALL witnesses).
            let mut issuer_cal = CalibratedFloor::new(floor_k);
            let claim_readings = swarm_drift(&witnesses, &mut issuer_cal);
            assert!(
                claim_consensus(&claim_readings, claim_quorum).is_some(),
                "question {key:?}: claim must earn standing (fixture design invariant)"
            );

            // recipient side: admit, under the recipient's OWN trust/quorum/floor.
            let mut recipient_cal = CalibratedFloor::new(floor_k);
            let admission = admit(&claim_readings, &trust, admit_quorum, &magnitudes, &mut recipient_cal, None, "CONFIRM");

            // the ONE bridge: a conferred admission becomes a commons deposit.
            commons.enroll(key, &admission);
        }

        for pair in v.get("forgets").unwrap().as_arr().unwrap() {
            let a = pair.as_arr().unwrap();
            commons.forget(a[0].as_str().unwrap(), a[1].as_str().unwrap());
        }

        let expected_deposits: Vec<(String, String, i64)> = v
            .get("commons")
            .unwrap()
            .get("deposits")
            .unwrap()
            .as_arr()
            .unwrap()
            .iter()
            .map(|d| {
                (
                    d.get("key").unwrap().as_str().unwrap().to_string(),
                    d.get("answer").unwrap().as_str().unwrap().to_string(),
                    d.get("weight").unwrap().as_i64().unwrap(),
                )
            })
            .collect();
        assert_eq!(commons.deposits(), expected_deposits);

        let expected_tombstones: Vec<(String, String)> = v
            .get("commons")
            .unwrap()
            .get("tombstones")
            .unwrap()
            .as_arr()
            .unwrap()
            .iter()
            .map(|pair| {
                let a = pair.as_arr().unwrap();
                (a[0].as_str().unwrap().to_string(), a[1].as_str().unwrap().to_string())
            })
            .collect();
        assert_eq!(commons.tombstones(), expected_tombstones);

        let expected_root = v.get("commons").unwrap().get("expected_root_hex").unwrap().as_str().unwrap();
        assert_eq!(hex32(&commons.root()), expected_root);
        assert_eq!(hex32(&commons.root()), v.get("pins").unwrap().get("commons_root").unwrap().as_str().unwrap());
    }

    /// Negative control: tampering one witness's magnitude BEFORE deriving
    /// must change the derived deposit table — proving this recomputes
    /// from inputs rather than trivially echoing the fixture's own numbers.
    #[test]
    fn tampering_a_witness_magnitude_changes_the_derived_table() {
        let v = load();
        let north1 = v
            .get("questions")
            .unwrap()
            .as_arr()
            .unwrap()
            .iter()
            .find(|q| q.get("issuer").unwrap().as_str().unwrap() == "issuer-north-1")
            .unwrap();
        let mut witnesses = witnesses_of(north1);
        let trust = trust_of(north1);
        let floor_k = north1.get("floor_k").unwrap().as_i64().unwrap() as usize;
        let admit_quorum = north1.get("admit_quorum").unwrap().as_i64().unwrap() as usize;

        // real weight for this question alone: 5 trusted (n0 dropped by drift).
        let real_weight = {
            let magnitudes: BTreeMap<String, Q16> = witnesses.iter().map(|(n, _, m)| (n.clone(), *m)).collect();
            let mut cal = CalibratedFloor::new(floor_k);
            let claim_readings = swarm_drift(&witnesses, &mut cal);
            let mut rcal = CalibratedFloor::new(floor_k);
            let admission = admit(&claim_readings, &trust, admit_quorum, &magnitudes, &mut rcal, None, "CONFIRM");
            admission.trusted.len()
        };
        assert_eq!(real_weight, 5);

        // tamper: n1's magnitude, made to agree with n0's wild reading —
        // this changes the consensus magnitude, hence every surprise,
        // hence who gets flagged drifting, hence the trusted count.
        for w in witnesses.iter_mut() {
            if w.0 == "n1" {
                w.2 = Q16::int(500);
            }
        }
        let magnitudes: BTreeMap<String, Q16> = witnesses.iter().map(|(n, _, m)| (n.clone(), *m)).collect();
        let mut cal = CalibratedFloor::new(floor_k);
        let claim_readings = swarm_drift(&witnesses, &mut cal);
        let mut rcal = CalibratedFloor::new(floor_k);
        let tampered_admission = admit(&claim_readings, &trust, admit_quorum, &magnitudes, &mut rcal, None, "CONFIRM");

        assert_ne!(
            tampered_admission.trusted.len(),
            real_weight,
            "tampering a magnitude must change the derived trusted-witness weight"
        );
    }
}
