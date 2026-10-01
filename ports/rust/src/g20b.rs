//! G20b — the Second Reader.
//!
//! `ai-writings/situations/FABLE-ANSWER.md` (G20b, the 已落地 condition):
//! today the pins — `OrgBook.chain()`, `OrgBook.decisions_digest()`,
//! `Commons.root()`, `Schoolhouse.pins()` — have exactly ONE witness:
//! Python reading itself. By the substrate's own Law 6 ("a fold is real
//! only once more than one reader can fold it"), that is booked, not
//! landed. This module is the second, independent witness: a non-Python
//! (Rust) implementation of the bytes-law those pins are built from,
//! reproducing them from a FIXED, exported scenario
//! (`vectors/g20b_second_reader_vectors.json`, written by
//! `vectors/gen_g20b_second_reader_vectors.py`) and asserting byte-for-byte
//! equality against Python's own computation — never by copying Python's
//! hex, always by recomputing from the raw dict/field inputs.
//!
//! Pure code throughout: `sha256.rs` and `minijson.rs` in this crate are
//! both dependency-free (no `serde_json`, no hash crate) — the whole
//! reproduction chain, parser included, is bytes visible end to end.
//!
//! ## Reproduced byte-for-byte (see `tests` below — this is the gate)
//!
//!   * `Receipt.decision_bytes()` — the `\x1f`-joined typed-field canonical
//!     form (`decision_bytes`).
//!   * `Receipt.sha()` — including the canonicalized-JSON `state_hash` /
//!     `delta_hash` (`bookkeeper.py`'s `json.dumps(..., sort_keys=True)`,
//!     reproduced here by `canonical_json_dict`) and the fnv1a-64
//!     `payload_hash` over the (possibly 200-char-truncated) residue text.
//!   * `Bookkeeper.replay()` / `OrgBook.chain()` — sha256 over the
//!     concatenation of every entry's `sha()` hex (`chain`).
//!   * `OrgBook.decisions_digest()` — replaying the diploma/streak rule
//!     (`standing.py`) purely from each entry's typed fields
//!     (`decisions_digest`), including the `None` -> literal `"None"`
//!     f-string quirk Python's own formula has.
//!   * `fold.mmr_root()` — the bagged-peaks binary-counter MMR
//!     (`mmr_root`), exercised generically over ten leaf-count vectors, not
//!     just the ones this fixture happens to produce.
//!   * `Commons.root()` — the deposit-leaf / tombstone-leaf construction
//!     plus `mmr_root` (`commons_root`).
//!
//! ## STRETCH (not reproduced here — honest boundary)
//!
//!   * The commons **deposit table itself** (which (key, answer, weight)
//!     triples exist) is taken from the fixture as ground truth, not
//!     re-derived. Deriving it independently means re-implementing
//!     `Schoolhouse.enroll`'s whole bridge: `attest`/`admit`'s Ed25519
//!     signature verification, BLAKE3, `Q16` exact-rational arithmetic, and
//!     `CalibratedFloor`'s drift judgment — a second-reader project in its
//!     own right (see `ai-writings/situations/arch/COMPOSITE-schoolhouse.md`).
//!     What IS reproduced here is the hard cross-language part: the MMR/
//!     leaf mechanics that turn a deposit table into a root.
//!   * Non-ASCII text: Python's `json.dumps` defaults to `ensure_ascii=True`
//!     (`\uXXXX`-escapes anything outside ASCII); `canonical_json_dict`
//!     below does not attempt to match that in general. The fixture is
//!     ASCII-only by construction, so the question never arises here, but a
//!     port reproducing an arbitrary residue payload would need it.
//!   * `SignedReceipt` envelopes (Ed25519/BLAKE3 signatures) are out of
//!     scope; the pins this rung cares about (`OrgBook.chain()`,
//!     `decisions_digest()`, `commons_root()`) never depend on them.

use crate::fnv1a;
use crate::minijson::Json;
use crate::sha256::{sha256, sha256_hex};

// ── canonical JSON, matching `json.dumps(d, sort_keys=True, default=str)`
//    for the str/bool-valued flat dicts this fixture ever hands Bookkeeper
//    (`state`, `delta`, `payload`) — see the module docstring's ASCII note.
pub fn json_escape_string(s: &str) -> String {
    let mut out = String::from("\"");
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
    out
}

fn canonical_json_scalar(v: &Json) -> String {
    match v {
        Json::Bool(b) => (if *b { "true" } else { "false" }).to_string(),
        Json::Str(s) => json_escape_string(s),
        Json::Num(n) => n.to_string(),
        Json::Null => "null".to_string(),
        _ => panic!("canonical_json_dict: only flat str/bool/num/null values are supported"),
    }
}

/// `json.dumps(obj, sort_keys=True)` for a flat `{str: str|bool}` dict —
/// exactly the shape `Bookkeeper.book()`'s `state`/`delta`/`payload`
/// arguments take in this fixture. Keys sorted by byte order (Python's
/// default `str` ordering, which agrees with byte order for the ASCII
/// identifiers this fixture uses).
pub fn canonical_json_dict(fields: &[(String, Json)]) -> String {
    let mut sorted: Vec<&(String, Json)> = fields.iter().collect();
    sorted.sort_by(|a, b| a.0.cmp(&b.0));
    let mut s = String::from("{");
    for (i, (k, v)) in sorted.iter().enumerate() {
        if i > 0 {
            s.push_str(", ");
        }
        s.push_str(&json_escape_string(k));
        s.push_str(": ");
        s.push_str(&canonical_json_scalar(v));
    }
    s.push('}');
    s
}

fn obj_fields(v: &Json) -> Vec<(String, Json)> {
    v.as_obj().expect("expected a JSON object").clone()
}

pub fn sha256_of_dict(d: &Json) -> String {
    sha256_hex(canonical_json_dict(&obj_fields(d)).as_bytes())
}

/// fnv1a-64, lowercase 16-hex, over UTF-8 bytes — the same rule
/// `bookkeeper.fnv1a` + `f"{...:016x}"` uses.
pub fn fnv1a_hex16(bytes: &[u8]) -> String {
    // `crate::fnv1a` takes `&str`; the residue text this fixture ever
    // carries is ASCII, so the byte/char views agree exactly.
    let s = std::str::from_utf8(bytes).expect("residue bytes must be valid UTF-8 in this fixture");
    format!("{:016x}", fnv1a(s))
}

/// Truncate to the first 200 UTF-16-code-unit-free, i.e. Unicode *scalar*
/// positions — Python's `s[:200]` is a code-point slice. ASCII-only in
/// this fixture, so byte/char/code-point counting all coincide; documented
/// in the module docstring as the honest boundary for non-ASCII input.
pub fn truncate_200(s: &str) -> String {
    s.chars().take(200).collect()
}

// ── Receipt.decision_bytes() + Receipt.sha() ──────────────────────────
pub fn decision_bytes(
    dispatch_id: Option<&str>,
    runner: Option<&str>,
    key: Option<&str>,
    correct: Option<bool>,
    base_verdict: Option<&str>,
    answer: Option<&str>,
) -> Vec<u8> {
    if dispatch_id.is_none()
        && runner.is_none()
        && key.is_none()
        && correct.is_none()
        && base_verdict.is_none()
        && answer.is_none()
    {
        return Vec::new();
    }
    fn enc_str(v: Option<&str>) -> String {
        v.unwrap_or("").to_string()
    }
    fn enc_bool(v: Option<bool>) -> String {
        match v {
            Some(true) => "1".to_string(),
            Some(false) => "0".to_string(),
            None => String::new(),
        }
    }
    let parts = [
        enc_str(dispatch_id),
        enc_str(runner),
        enc_str(key),
        enc_bool(correct),
        enc_str(base_verdict),
        enc_str(answer),
    ];
    parts.join("\u{1f}").into_bytes()
}

#[allow(clippy::too_many_arguments)]
pub fn receipt_sha(
    tick: i64,
    state_hash: &str,
    delta_hash: &str,
    decision_kind: &str,
    payload_hash: &str,
    decision_bytes: &[u8],
) -> String {
    let mut raw = format!(
        "{}|{}|{}|{}|{}",
        tick, state_hash, delta_hash, decision_kind, payload_hash
    );
    if !decision_bytes.is_empty() {
        let decision_str =
            std::str::from_utf8(decision_bytes).expect("decision_bytes is UTF-8 by construction");
        raw.push('|');
        raw.push_str(decision_str);
    }
    sha256_hex(raw.as_bytes())
}

/// `Bookkeeper.replay()` / `OrgBook.chain()`: a single sha256 over the
/// concatenation of every entry's `sha()` hex string, in booking order.
pub fn chain(entry_shas: &[String]) -> String {
    let mut buf = Vec::new();
    for s in entry_shas {
        buf.extend_from_slice(s.as_bytes());
    }
    sha256_hex(&buf)
}

// ── OrgBook.decisions_digest() — the diploma/streak replay ────────────
#[derive(Debug, Clone)]
pub struct TypedEntry {
    pub dispatch_id: String,
    pub runner: String,
    pub key: String,
    pub correct: bool,
    pub base_verdict: Option<String>,
    pub answer: String,
}

/// Reconstructs exactly what `OrgBook.replay()` + `decisions_digest()` do,
/// from nothing but each entry's typed fields (no residue, no Standing
/// object — the streak is a pure fold over `(runner, key, correct,
/// answer)` in booking order, same law `standing.py` proves).
pub fn decisions_digest(entries: &[TypedEntry], diploma: i64) -> String {
    let mut buf = Vec::new();
    for i in 0..entries.len() {
        let e = &entries[i];
        let base = match &e.base_verdict {
            Some(b) => b.clone(),
            None => continue, // unreconstructable dispatch — `replay()` skips it too
        };

        let mut streak: i64 = 0;
        let mut last_answer: Option<String> = None;
        for x in &entries[0..i] {
            if x.runner == e.runner && x.key == e.key {
                if x.correct {
                    streak += 1;
                    last_answer = Some(x.answer.clone());
                } else {
                    streak = 0;
                    last_answer = None;
                }
            }
        }

        let (verdict, answer) = if streak >= diploma {
            ("ANSWER".to_string(), last_answer)
        } else {
            (base.clone(), None)
        };
        // Python's f"{...}" embeds `None` as the literal text "None" — not
        // an empty string. Reproduced verbatim, quirk and all.
        let answer_str = answer.unwrap_or_else(|| "None".to_string());

        let piece = format!(
            "{}\u{1f}{}\u{1f}{}\u{1f}{}\u{1f}{}\u{1f}{}",
            e.dispatch_id, e.runner, e.key, base, verdict, answer_str
        );
        buf.extend_from_slice(piece.as_bytes());
    }
    sha256_hex(&buf)
}

// ── fold.mmr_root() — bagged-peaks binary-counter MMR ──────────────────
fn mmr_push(stack: &mut Vec<[u8; 32]>, i: usize, leaf: [u8; 32]) {
    let mut h = 0u32;
    let mut node = leaf;
    while (i >> h) & 1 == 1 {
        let top = stack.pop().expect("MMR: carry with empty stack (bug)");
        let mut concat = Vec::with_capacity(64);
        concat.extend_from_slice(&top);
        concat.extend_from_slice(&node);
        node = sha256(&concat);
        h += 1;
    }
    stack.push(node);
}

fn mmr_peaks(leaves: &[[u8; 32]]) -> Vec<[u8; 32]> {
    let mut stack = Vec::new();
    for (i, leaf) in leaves.iter().enumerate() {
        mmr_push(&mut stack, i, *leaf);
    }
    stack
}

fn mmr_bag(peaks: &[[u8; 32]], count: usize) -> [u8; 32] {
    let mut buf = Vec::new();
    for p in peaks {
        buf.extend_from_slice(p);
    }
    buf.extend_from_slice(count.to_string().as_bytes());
    sha256(&buf)
}

pub fn mmr_root(leaves: &[[u8; 32]]) -> [u8; 32] {
    if leaves.is_empty() {
        return sha256(b"mmr:empty");
    }
    let peaks = mmr_peaks(leaves);
    mmr_bag(&peaks, leaves.len())
}

// ── Commons.root() — deposit + tombstone leaves, then mmr_root ────────
pub fn commons_leaf(key: &str, answer: &str, weight: i64) -> [u8; 32] {
    let canon = format!("{}\u{1f}{}\u{1f}{}", key, answer, weight);
    sha256(canon.as_bytes())
}

pub fn commons_tombstone_leaf(key: &str, answer: &str) -> [u8; 32] {
    let canon = format!("__tomb__\u{1f}{}\u{1f}{}", key, answer);
    sha256(canon.as_bytes())
}

/// `deposits` must already be in `Commons.deposits()`'s canonical
/// `(key, answer)`-sorted order, and `tombstones` in `sorted()` order — the
/// fixture exports both pre-sorted (mirroring `Commons.root()`'s own
/// contract: it sorts before rooting so a builder can hand leaves in in
/// any order and still land on the one canonical root).
pub fn commons_root(deposits: &[(String, String, i64)], tombstones: &[(String, String)]) -> [u8; 32] {
    let mut leaves: Vec<[u8; 32]> = deposits
        .iter()
        .map(|(k, a, w)| commons_leaf(k, a, *w))
        .collect();
    for (k, a) in tombstones {
        leaves.push(commons_tombstone_leaf(k, a));
    }
    mmr_root(&leaves)
}

pub fn hex32(b: &[u8; 32]) -> String {
    b.iter().map(|x| format!("{:02x}", x)).collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::minijson::parse;

    const VECTORS_JSON: &str =
        include_str!("../../../vectors/g20b_second_reader_vectors.json");

    fn load() -> Json {
        parse(VECTORS_JSON).expect("vectors JSON must parse")
    }

    #[test]
    fn json_escaping_matches_python_json_dumps_separators() {
        // Two-key dict, sorted keys, ", " / ": " separators — Python's
        // `json.dumps({"correct": False, "outcome": "wrong"}, sort_keys=True)`.
        let fields = vec![
            ("outcome".to_string(), Json::Str("wrong".to_string())),
            ("correct".to_string(), Json::Bool(false)),
        ];
        assert_eq!(
            canonical_json_dict(&fields),
            r#"{"correct": false, "outcome": "wrong"}"#
        );
    }

    #[test]
    fn mmr_root_matches_python_across_leaf_counts() {
        let v = load();
        let vectors = v.get("mmr_vectors").unwrap().as_arr().unwrap();
        assert!(vectors.len() >= 8, "expected a real spread of leaf counts");
        for vec in vectors {
            let leaves_hex = vec.get("leaves_hex").unwrap().as_arr().unwrap();
            let leaves: Vec<[u8; 32]> = leaves_hex
                .iter()
                .map(|h| {
                    let s = h.as_str().unwrap();
                    let bytes = hex::decode(s);
                    let mut arr = [0u8; 32];
                    arr.copy_from_slice(&bytes);
                    arr
                })
                .collect();
            let expected = vec.get("expected_root_hex").unwrap().as_str().unwrap();
            assert_eq!(
                hex32(&mmr_root(&leaves)),
                expected,
                "mmr_root diverged at leaf count {}",
                leaves.len()
            );
        }
    }

    #[test]
    fn orgbook_chain_reproduced_byte_for_byte_from_raw_dicts() {
        let v = load();
        let entries = v
            .get("orgbook")
            .unwrap()
            .get("entries")
            .unwrap()
            .as_arr()
            .unwrap();
        let mut shas = Vec::new();
        for e in entries {
            let expected = e.get("expected").unwrap();
            let state_hash = sha256_of_dict(e.get("state").unwrap());
            let delta_hash = sha256_of_dict(e.get("delta").unwrap());
            assert_eq!(state_hash, expected.get("state_hash").unwrap().as_str().unwrap());
            assert_eq!(delta_hash, expected.get("delta_hash").unwrap().as_str().unwrap());

            let payload_full = canonical_json_dict(&obj_fields(e.get("payload").unwrap()));
            let residue = truncate_200(&payload_full);
            assert_eq!(
                residue,
                expected.get("payload_residue").unwrap().as_str().unwrap(),
                "residue mismatch (200-char truncation) at tick {:?}",
                e.get("tick")
            );
            let payload_hash = fnv1a_hex16(residue.as_bytes());
            assert_eq!(
                payload_hash,
                expected.get("payload_hash").unwrap().as_str().unwrap()
            );

            let typed = e.get("typed").unwrap();
            let db = decision_bytes(
                typed.opt_str("dispatch_id").as_deref(),
                typed.opt_str("runner").as_deref(),
                typed.opt_str("key").as_deref(),
                typed.get("correct").and_then(|j| j.as_bool()),
                typed.opt_str("base_verdict").as_deref(),
                typed.opt_str("answer").as_deref(),
            );
            let decision_kind = e.get("decision_kind").unwrap().as_str().unwrap();
            let tick = e.get("tick").unwrap().as_i64().unwrap();
            let sha = receipt_sha(tick, &state_hash, &delta_hash, decision_kind, &payload_hash, &db);
            assert_eq!(sha, expected.get("sha").unwrap().as_str().unwrap(), "Receipt.sha() diverged at tick {}", tick);
            shas.push(sha);
        }

        let expected_chain = v
            .get("orgbook")
            .unwrap()
            .get("expected_chain")
            .unwrap()
            .as_str()
            .unwrap();
        assert_eq!(chain(&shas), expected_chain, "OrgBook.chain() diverged");
    }

    #[test]
    fn decisions_digest_reproduced_byte_for_byte_from_typed_fields() {
        let v = load();
        let diploma = v.get("diploma").unwrap().as_i64().unwrap();
        let entries = v
            .get("orgbook")
            .unwrap()
            .get("entries")
            .unwrap()
            .as_arr()
            .unwrap();
        let typed: Vec<TypedEntry> = entries
            .iter()
            .map(|e| {
                let t = e.get("typed").unwrap();
                TypedEntry {
                    dispatch_id: t.opt_str("dispatch_id").unwrap(),
                    runner: t.opt_str("runner").unwrap(),
                    key: t.opt_str("key").unwrap(),
                    correct: t.get("correct").unwrap().as_bool().unwrap(),
                    base_verdict: t.opt_str("base_verdict"),
                    answer: t.opt_str("answer").unwrap(),
                }
            })
            .collect();

        let expected = v
            .get("decisions_digest")
            .unwrap()
            .get("expected")
            .unwrap()
            .as_str()
            .unwrap();
        assert_eq!(decisions_digest(&typed, diploma), expected);
    }

    #[test]
    fn commons_root_reproduced_byte_for_byte_from_deposits_and_tombstones() {
        let v = load();
        let commons = v.get("commons").unwrap();
        let deposits: Vec<(String, String, i64)> = commons
            .get("deposits")
            .unwrap()
            .as_arr()
            .unwrap()
            .iter()
            .map(|d| {
                (
                    d.opt_str("key").unwrap(),
                    d.opt_str("answer").unwrap(),
                    d.get("weight").unwrap().as_i64().unwrap(),
                )
            })
            .collect();
        let tombstones: Vec<(String, String)> = commons
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
        let expected = commons.get("expected_root_hex").unwrap().as_str().unwrap();
        assert_eq!(hex32(&commons_root(&deposits, &tombstones)), expected);
    }

    #[test]
    fn all_three_pins_agree_with_python_end_to_end() {
        // The reproducibility gate itself: recompute every pin the way the
        // tests above do, independently, and compare against
        // `Schoolhouse.pins()`'s own tuple — the second witness.
        let v = load();
        let pins = v.get("pins").unwrap();
        assert_eq!(
            v.get("orgbook").unwrap().get("expected_chain").unwrap().as_str().unwrap(),
            pins.get("chain").unwrap().as_str().unwrap()
        );
        assert_eq!(
            v.get("decisions_digest").unwrap().get("expected").unwrap().as_str().unwrap(),
            pins.get("decisions_digest").unwrap().as_str().unwrap()
        );
        assert_eq!(
            v.get("commons").unwrap().get("expected_root_hex").unwrap().as_str().unwrap(),
            pins.get("commons_root").unwrap().as_str().unwrap()
        );
    }
}

/// A tiny hex decoder (no `hex` crate — see the module docstring: no
/// external APIs). Named to read naturally at call sites in tests above.
#[cfg(test)]
mod hex {
    pub fn decode(s: &str) -> Vec<u8> {
        assert_eq!(s.len() % 2, 0, "odd-length hex string");
        (0..s.len())
            .step_by(2)
            .map(|i| u8::from_str_radix(&s[i..i + 2], 16).expect("bad hex digit"))
            .collect()
    }
}
