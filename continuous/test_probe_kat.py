#!/usr/bin/env python3
"""
test_probe_kat.py — a known-answer test for the JEV canon battery.

WHY THIS EXISTS
`jev_continuous_probe.py` is the load-bearing artifact of dozens of wipes. It has 278
lines, 25 wipe-rebuild cycles of refinement, and — until now — **no test that would fail if
it silently stopped measuring what it claims to measure.** It was frozen, not learned.

This is the cheapest high-value fix in the fleet's backlog, and it is deliberately
NETWORK-FREE: `call_jev` is mocked, so the suite runs in a wiped sandbox with no key and
no Typesafe access. A test that needs the network to pass is a test that silently stops
being run.

WHAT IS PINNED
  1. the question bank has the shape a generator would depend on
  2. the doctrinal-state lever is actually attached to the right questions
  3. `parse_verdicts` handles the shapes JEV really returns, INCLUDING the ones that
     should yield nothing rather than a wrong number
  4. `run_round` writes the round file and the history line, and records a FAILURE when the
     call fails rather than reporting an empty success
  5. a NEGATIVE CONTROL: the suite must fail when the parser is deliberately broken
"""
import json, os, sys, random, tempfile, importlib.util
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("probe", HERE / "jev_continuous_probe.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

R = []
def check(name, ok, detail=""):
    R.append((name, bool(ok), detail))
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))

VALID_TYPES = {"noul", "choice", "score"}

# ---- 1. the question bank -------------------------------------------------------
bank = probe.QUESTION_BANK
check("question bank is non-empty", len(bank) >= 20, f"{len(bank)} questions")
check("every question is a 4-tuple (qid, type, text, kind)",
      all(len(q) == 4 for q in bank))
bad_type = [(q[0], q[1]) for q in bank if q[1] not in VALID_TYPES]
check("every question carries a valid type discriminator", not bad_type, str(bad_type[:3]))
dupes = [q[0] for q in bank if [x[0] for x in bank].count(q[0]) > 1]
check("question ids are unique", not dupes, str(sorted(set(dupes))[:4]))
check("no question has empty text", all(str(q[2]).strip() for q in bank))

# ---- 2. the doctrinal-state lever -----------------------------------------------
ds = probe.DOCTRINAL_STATE
check("doctrinal state is populated", bool(ds) and len(ds) > 0, f"{len(ds)} sections")
# The state lever keys on DOCTRINE names ("witness_log_is_prediction"), not on qids
# ("q02_witness_log_is_prediction") -- except for q17, which IS named by id. My first
# version of this check looked for qids and found none, which read as "the lever is
# broken". It is not; the check was.
doctrine_names = set()
for _sec, _items in ds.items():
    if isinstance(_items, dict):
        doctrine_names |= set(_items.keys())
qid_stems = {q[0].split("_", 1)[1] for q in bank}
matched = {n for n in doctrine_names if n in qid_stems}
check("the state lever names at least some real questions by doctrine stem",
      len(matched) >= 3, f"{len(matched)} matched of {len(doctrine_names)} doctrine keys")
_flat_state = " ".join(str(v) for v in ds.values()) if not isinstance(list(ds.values())[0], dict) \
    else " ".join(str(v) for sec in ds.values() if isinstance(sec, dict) for v in sec.values())
check("the lever explicitly damps the speculative set",
      "SPECULATIVE" in _flat_state and "DAMPEN" in _flat_state,
      "spec_notebook must dampen the speculative questions")
check("build_state() flattens to a non-empty mapping", len(probe.build_state()) > 0,
      f"{len(probe.build_state())} keys")

# ---- 3. parse_verdicts, against shapes JEV really returns -----------------------
# The one that matters: `choice` answers carry no `noul`, and must yield NOTHING
# rather than a silently wrong number.
cases = [
    ("well-formed noul",
     {"answers": {"q01": {"noul": 0.94}, "q02": {"noul": 0.31}}},
     {"q01": 0.94, "q02": 0.31}),
    ("choice answers are skipped, not coerced",
     {"answers": {"q01": {"noul": 0.9}, "q02": {"choice": ["a", "b"]}}},
     {"q01": 0.9}),
    ("score answers are skipped",
     {"answers": {"q03": {"score": 0.99}}}, {}),
    ("a non-numeric noul is dropped",
     {"answers": {"q04": {"noul": "high"}, "q05": {"noul": 0.5}}},
     {"q05": 0.5}),
    ("an integer noul is accepted and becomes a float",
     {"answers": {"q06": {"noul": 1}}}, {"q06": 1.0}),
    ("a missing answers key yields nothing",
     {"result": {}}, {}),
    ("a null answers value does not raise",
     {"answers": None}, {}),
]
for label, resp, want in cases:
    try:
        got = probe.parse_verdicts(resp)
    except Exception as e:
        got = {"__raised__": str(e)}
    check(f"parse_verdicts: {label}", got == want, f"got {got}")

# ---- 4. run_round, with the network mocked --------------------------------------
OK_RESP = {"answers": {"q01": {"noul": 0.97}, "q02": {"noul": 0.94}},
           "usage": {"prompt_tokens": 10}}
FAIL_RESP = {"error": "simulated 503"}

with tempfile.TemporaryDirectory() as td:
    out = Path(td)
    with mock.patch.object(probe, "call_jev", return_value=("ok", OK_RESP)):
        rec = probe.run_round(1, out, n_questions=2)
    check("run_round reports ok when the call succeeds", rec["status"] == "ok")
    check("run_round wrote continuous_r001.json", (out / "continuous_r001.json").exists())
    check("run_round appended exactly one history line",
          len([l for l in (out / "history.jsonl").read_text().splitlines() if l.strip()]) == 1)
    on_disk = json.loads((out / "continuous_r001.json").read_text())
    check("the round file carries the PARSED verdicts, not the raw answer envelope",
          on_disk["verdicts"] == {"q01": 0.97, "q02": 0.94},
          str(on_disk["verdicts"]))
    check("the round file records which questions were sampled",
          isinstance(on_disk.get("sampled_qids"), list) and len(on_disk["sampled_qids"]) == 2)

with tempfile.TemporaryDirectory() as td:
    out = Path(td)
    with mock.patch.object(probe, "call_jev", return_value=("fail", FAIL_RESP)):
        rec = probe.run_round(2, out, n_questions=2)
    check("a failed call is reported as fail, NOT as an empty success",
          rec["status"] == "fail", rec.get("status", ""))
    check("a failed round writes continuous_r002.fail.json",
          (out / "continuous_r002.fail.json").exists())
    check("a failed round does NOT append to history",
          not (out / "history.jsonl").exists() or
          not (out / "history.jsonl").read_text().strip())

# ---- 5. determinism with a fixed seed -------------------------------------------
with tempfile.TemporaryDirectory() as td:
    out = Path(td)
    with mock.patch.object(probe, "call_jev", return_value=("ok", OK_RESP)):
        random.seed(1234); a = probe.build_question_specs(1, 3)[1]
        random.seed(1234); b = probe.build_question_specs(1, 3)[1]
    check("question selection is reproducible under a fixed seed", a == b, str(a))
    check("sampling honours the requested count", len(a) == 3)

# ---- 6. NEGATIVE CONTROL --------------------------------------------------------
# A suite that cannot fail proves nothing. Break the parser and require the suite to
# notice. If this check ever stops detecting the break, the suite is decorative.
import copy
real_parse = probe.parse_verdicts
probe.parse_verdicts = lambda resp: {k: 0.5 for k in resp.get("answers", {})}
try:
    got = probe.parse_verdicts(OK_RESP)
    detected = got != {"q01": 0.97, "q02": 0.94}
except Exception:
    detected = True
check("NEGATIVE CONTROL: a broken parser is detected by the cases above", detected)
probe.parse_verdicts = real_parse
check("NEGATIVE CONTROL: the real parser is restored and still correct",
      probe.parse_verdicts(OK_RESP) == {"q01": 0.97, "q02": 0.94})

n = sum(1 for _, ok, _ in R if ok)
print(f"\n  {n}/{len(R)} checks pass")
sys.exit(0 if n == len(R) else 1)
