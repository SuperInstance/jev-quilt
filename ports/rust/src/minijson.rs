//! A tiny, dependency-free JSON reader — just enough to load the G20b
//! cross-language vectors fixture (`vectors/g20b_second_reader_vectors.json`)
//! without pulling in `serde_json` (G20b's whole point is bytes-law
//! independence: no external crate stands between this reader and the
//! fixture bytes). Not a general-purpose JSON library: no streaming, no
//! error recovery beyond `Result`, integers only (no floats — the fixture
//! never has one).

use std::fmt;

#[derive(Debug, Clone, PartialEq)]
pub enum Json {
    Null,
    Bool(bool),
    Num(i64),
    Str(String),
    Arr(Vec<Json>),
    Obj(Vec<(String, Json)>),
}

#[derive(Debug)]
pub struct ParseError(pub String);
impl fmt::Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "JSON parse error: {}", self.0)
    }
}

pub fn parse(input: &str) -> Result<Json, ParseError> {
    let chars: Vec<char> = input.chars().collect();
    let mut pos = 0usize;
    let v = parse_value(&chars, &mut pos)?;
    skip_ws(&chars, &mut pos);
    Ok(v)
}

fn skip_ws(c: &[char], pos: &mut usize) {
    while *pos < c.len() && c[*pos].is_whitespace() {
        *pos += 1;
    }
}

fn peek(c: &[char], pos: usize) -> Option<char> {
    c.get(pos).copied()
}

fn parse_value(c: &[char], pos: &mut usize) -> Result<Json, ParseError> {
    skip_ws(c, pos);
    match peek(c, *pos) {
        Some('{') => parse_obj(c, pos),
        Some('[') => parse_arr(c, pos),
        Some('"') => Ok(Json::Str(parse_string(c, pos)?)),
        Some('t') => {
            expect_lit(c, pos, "true")?;
            Ok(Json::Bool(true))
        }
        Some('f') => {
            expect_lit(c, pos, "false")?;
            Ok(Json::Bool(false))
        }
        Some('n') => {
            expect_lit(c, pos, "null")?;
            Ok(Json::Null)
        }
        Some(ch) if ch == '-' || ch.is_ascii_digit() => parse_num(c, pos),
        other => Err(ParseError(format!("unexpected {:?} at {}", other, pos))),
    }
}

fn expect_lit(c: &[char], pos: &mut usize, lit: &str) -> Result<(), ParseError> {
    for ch in lit.chars() {
        if peek(c, *pos) != Some(ch) {
            return Err(ParseError(format!("expected literal {}", lit)));
        }
        *pos += 1;
    }
    Ok(())
}

fn parse_num(c: &[char], pos: &mut usize) -> Result<Json, ParseError> {
    let start = *pos;
    if peek(c, *pos) == Some('-') {
        *pos += 1;
    }
    while matches!(peek(c, *pos), Some(ch) if ch.is_ascii_digit()) {
        *pos += 1;
    }
    let s: String = c[start..*pos].iter().collect();
    s.parse::<i64>()
        .map(Json::Num)
        .map_err(|e| ParseError(format!("bad number {:?}: {}", s, e)))
}

fn parse_string(c: &[char], pos: &mut usize) -> Result<String, ParseError> {
    if peek(c, *pos) != Some('"') {
        return Err(ParseError("expected opening quote".into()));
    }
    *pos += 1;
    let mut out = String::new();
    loop {
        match peek(c, *pos) {
            None => return Err(ParseError("unterminated string".into())),
            Some('"') => {
                *pos += 1;
                return Ok(out);
            }
            Some('\\') => {
                *pos += 1;
                match peek(c, *pos) {
                    Some('"') => out.push('"'),
                    Some('\\') => out.push('\\'),
                    Some('/') => out.push('/'),
                    Some('n') => out.push('\n'),
                    Some('t') => out.push('\t'),
                    Some('r') => out.push('\r'),
                    Some('b') => out.push('\u{0008}'),
                    Some('f') => out.push('\u{000C}'),
                    Some('u') => {
                        let hex: String = c[*pos + 1..*pos + 5].iter().collect();
                        let code = u32::from_str_radix(&hex, 16)
                            .map_err(|e| ParseError(format!("bad \\u escape: {}", e)))?;
                        out.push(char::from_u32(code).unwrap_or('\u{FFFD}'));
                        *pos += 4;
                    }
                    other => return Err(ParseError(format!("bad escape {:?}", other))),
                }
                *pos += 1;
            }
            Some(ch) => {
                out.push(ch);
                *pos += 1;
            }
        }
    }
}

fn parse_arr(c: &[char], pos: &mut usize) -> Result<Json, ParseError> {
    *pos += 1; // '['
    let mut items = Vec::new();
    skip_ws(c, pos);
    if peek(c, *pos) == Some(']') {
        *pos += 1;
        return Ok(Json::Arr(items));
    }
    loop {
        let v = parse_value(c, pos)?;
        items.push(v);
        skip_ws(c, pos);
        match peek(c, *pos) {
            Some(',') => {
                *pos += 1;
            }
            Some(']') => {
                *pos += 1;
                break;
            }
            other => return Err(ParseError(format!("expected , or ] got {:?}", other))),
        }
    }
    Ok(Json::Arr(items))
}

fn parse_obj(c: &[char], pos: &mut usize) -> Result<Json, ParseError> {
    *pos += 1; // '{'
    let mut items = Vec::new();
    skip_ws(c, pos);
    if peek(c, *pos) == Some('}') {
        *pos += 1;
        return Ok(Json::Obj(items));
    }
    loop {
        skip_ws(c, pos);
        let key = parse_string(c, pos)?;
        skip_ws(c, pos);
        if peek(c, *pos) != Some(':') {
            return Err(ParseError("expected ':'".into()));
        }
        *pos += 1;
        let val = parse_value(c, pos)?;
        items.push((key, val));
        skip_ws(c, pos);
        match peek(c, *pos) {
            Some(',') => {
                *pos += 1;
            }
            Some('}') => {
                *pos += 1;
                break;
            }
            other => return Err(ParseError(format!("expected , or {{}} got {:?}", other))),
        }
    }
    Ok(Json::Obj(items))
}

impl Json {
    pub fn get(&self, key: &str) -> Option<&Json> {
        match self {
            Json::Obj(fields) => fields.iter().find(|(k, _)| k == key).map(|(_, v)| v),
            _ => None,
        }
    }
    pub fn as_str(&self) -> Option<&str> {
        match self {
            Json::Str(s) => Some(s.as_str()),
            _ => None,
        }
    }
    pub fn as_bool(&self) -> Option<bool> {
        match self {
            Json::Bool(b) => Some(*b),
            _ => None,
        }
    }
    pub fn as_i64(&self) -> Option<i64> {
        match self {
            Json::Num(n) => Some(*n),
            _ => None,
        }
    }
    pub fn as_arr(&self) -> Option<&Vec<Json>> {
        match self {
            Json::Arr(v) => Some(v),
            _ => None,
        }
    }
    pub fn as_obj(&self) -> Option<&Vec<(String, Json)>> {
        match self {
            Json::Obj(v) => Some(v),
            _ => None,
        }
    }
    /// str field, or None if absent/JSON null (mirrors the fixture's use of
    /// `null` for an unset Optional[str] typed field).
    pub fn opt_str(&self, key: &str) -> Option<String> {
        match self.get(key) {
            Some(Json::Str(s)) => Some(s.clone()),
            _ => None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn round_trip_shapes() {
        let v = parse(r#"{"a": 1, "b": [true, false, null, "x\"y"], "c": {"d": -3}}"#).unwrap();
        assert_eq!(v.get("a").unwrap().as_i64(), Some(1));
        let arr = v.get("b").unwrap().as_arr().unwrap();
        assert_eq!(arr[0].as_bool(), Some(true));
        assert_eq!(arr[3].as_str(), Some("x\"y"));
        assert_eq!(v.get("c").unwrap().get("d").unwrap().as_i64(), Some(-3));
    }
}
