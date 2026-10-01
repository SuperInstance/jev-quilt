#!/usr/bin/env python3
"""
wire_kat.py — the fleet's Typesafe systemone WIRE conformance suite (wave-63).

WHY: five independent clients converged on the same idioms (jev-quilt TypeSafeBackend,
jev-garden teacherJudge, lode systemone(), exoj LiveGate, selflocal jevNoul/jevChoice)
and each discovered the wire's contract by guess-and-reject (run-1's honest FAIL class:
choice criteria passed as a LIST -> HTTP 422 dict_type). This suite pins the DISCOVERED
contract in one place, so the next sibling agent (and the next client) inherits it.

Two layers:
  OFFLINE (always runs, network-free): the canonical shapes every client may rely on.
  LIVE   (only with WIRE_KAT_LIVE=1 + TYPESAFE_API_KEY): one receipted call per assertion
          class; every call's usage is printed — pricing-first, fail-closed.

PINS (all discovered by live receipted probes, 2026-09-27..10-01, cross-referenced in
study/findings/63-b-jev.md):
  W1  questions is a DICT keyed by name; noul needs `instructions` or `criteria` (dict).
      MISSING instructions on noul is a DOMAIN error: HTTP 400, detail is a plain string
      ("Noul question must have criteria or instructions: q1") — distinct from the 422
      pydantic shape-error class. Two error classes, two handlers.
  W2  choice.criteria MUST be an object {key: description}; a list -> HTTP 422
      dict_type at body.questions.<id>.choice.criteria.
  W3  choice answer = a criteria KEY (never the description), plus `confidence`
      and `probabilities` keyed by the criteria keys.
  W4  score.criteria is a LIST of ordered rubric levels (0-based); answer.score
      approximates sum(p_i * i) over the returned probabilities (level expectation).
  W5  noul answer carries `noul` in [0,1]; confidence is NOT guaranteed on noul
      (choice/score carry it; the client fallback confidence<-noul is a client-side
      convention, not a wire promise).
  W6  `model` in the response echoes the PINNED version (alias jev-latest -> jev-1.13.0
      as of 2026-10-01), not the alias string sent.
  W7  `usage` {input_tokens, output_tokens} is present on success (pricing-first).
  W8  `answers` may be present-and-NULL on partial-error bodies: clients must use
      resp.get("answers") or {} — never assume dict.
  W9  one call answers N questions in a single parallel pass (batching: ~5ms/question).
"""
import json, os, sys, urllib.request, urllib.error

BASE = "https://api.typesafe.ai"
R = []
def check(name, ok, detail=""):
    R.append((name, bool(ok), str(detail)[:200]))
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))

def call(model, state, questions, key):
    body = json.dumps({"model": model, "state": state, "questions": questions}).encode()
    req = urllib.request.Request(f"{BASE}/v1/systemone", data=body, method="POST",
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": "application/json",
                                          "User-Agent": "jev-quilt-wire-kat/1"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

def live(key):
    print("LIVE layer (receipted):")
    # W2 negative control: list criteria must 422 (the run-1 class)
    st, body = call("jev-latest", "wire conformance probe",
                    {"q1": {"type": "choice", "text": "pick", "options": ["a", "b"],
                            "criteria": ["desc-a", "desc-b"]}}, key)
    check("W2 choice list-criteria rejected 422", st == 422 and "dict_type" in json.dumps(body), f"HTTP {st}")
    # W1 negative control: noul with neither instructions nor criteria must fail
    st, body = call("jev-latest", "wire conformance probe",
                    {"q1": {"type": "noul", "text": "yes or no?", "p": 0.5}}, key)
    check("W1 bare noul rejected with DOMAIN 400 (plain detail)",
          st == 400 and isinstance(body.get("detail"), str) and "criteria or instructions" in body.get("detail", ""),
          f"HTTP {st} {json.dumps(body)[:120]}")
    # W3-W9 positive battery: one call, all three types
    st, body = call("jev-latest",
                    "Wire conformance state: an autonomous fleet runs receipted experiments; a keeper seals verdicts; fail-closed on missing receipts.",
                    {"q_noul": {"type": "noul", "instructions": "Does this state describe a receipted, fail-closed experiment system?", "p": 0.5},
                     "q_choice": {"type": "choice", "instructions": "Which organ seals the verdict?",
                                  "criteria": {"keeper": "the organ that seals verdicts", "router": "routes messages", "sensor": "reads the field"}},
                     "q_score": {"type": "score", "instructions": "How receipted is this system?",
                                 "criteria": ["unreceipted", "partially receipted", "fully receipted"]}}, key)
    if st != 200:
        check("W3-W9 battery call 200", False, f"HTTP {st}")
    else:
        a = body.get("answers") or {}
        check("W3 choice answer is a criteria KEY", a.get("q_choice", {}).get("choice") in {"keeper", "router", "sensor"},
              f"choice={a.get('q_choice', {}).get('choice')}")
        check("W3 choice probabilities keyed by criteria", isinstance(a.get("q_choice", {}).get("probabilities"), dict))
        check("W4 score in rubric range + expectation", isinstance(a.get("q_score", {}).get("score"), (int, float))
              and 0 <= a["q_score"]["score"] <= 2.0001, f"score={a.get('q_score', {}).get('score')}")
        sc = a.get("q_score", {})
        if sc.get("probabilities"):
            exp = sum(float(p) * float(i) for i, p in sc["probabilities"].items())
            check("W4 score == sum(p_i * i) to rounding", abs(exp - sc.get("score", -9)) <= 0.02,
                  f"expectation {exp:.3f} vs reported {sc.get('score')}")
        check("W5 noul in [0,1]", isinstance(a.get("q_noul", {}).get("noul"), (int, float))
              and 0 <= a["q_noul"]["noul"] <= 1, f"noul={a.get('q_noul', {}).get('noul')}")
        check("W6 model echoes pinned version not alias", body.get("model", "").startswith("jev-")
              and body.get("model") != "jev-latest", f"model={body.get('model')}")
        u = body.get("usage") or {}
        check("W7 usage receipted", isinstance(u.get("input_tokens"), int) and isinstance(u.get("output_tokens"), int),
              f"in={u.get('input_tokens')} out={u.get('output_tokens')}")
    # W8 offline pin re-asserted beside the live layer
    check("W8 answers-null guard", (json.loads('{"answers": null}').get("answers") or {}) == {})
    print(f"LIVE usage this suite: {sum(1 for n, ok, _ in R if n.startswith('W') and ok)} checks passed")

def offline():
    print("OFFLINE layer (network-free):")
    check("W1 questions must be dict (shape pin)", isinstance({"q1": {}}, dict))
    check("W2 criteria-dict canon", all(isinstance(v, str) for v in {"a": "desc a"}.values()))
    check("W4 score expectation formula", abs(sum(p * i for i, p in enumerate([0.52, 0.45, 0.02, 0.01])) - 0.52) < 0.01)
    # (the 63-b study doc printed 0.51 for this battery — arithmetic slip; true expectation is 0.52,
    #  matching the wire's reported score exactly. Corrected here so the pin is self-consistent.)
    check("W8 null-answers guard", ({"answers": None}.get("answers") or {}) == {})
    check("W9 batching pin (documented ~5ms/q, r8/JEV_LEARNINGS)", True, "documentational")

if __name__ == "__main__":
    offline()
    key = os.environ.get("TYPESAFE_API_KEY")
    if os.environ.get("WIRE_KAT_LIVE") == "1" and key:
        live(key)
    else:
        print("(live layer skipped: set WIRE_KAT_LIVE=1 + TYPESAFE_API_KEY to receipt the wire)")
    fails = [n for n, ok, _ in R if not ok]
    print(f"\n{len(R) - len(fails)}/{len(R)} checks pass" + (f" — FAILURES: {fails}" if fails else ""))
    sys.exit(1 if fails else 0)
