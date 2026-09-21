import json

from jev_quilt import Cell, Hook, Q16, Engine, MeanPredictor, Bookkeeper
from jev_quilt.inquire import next_questions


def _fabric():
    eng = Engine()
    eng.register(Cell("src", (0, 0)))
    eng.register(Cell(
        "sense.a", (1, 0), input_hooks=[Hook("src")],
        decision={"rule": "identity", "value": Q16(1, 10)},
        predictor=MeanPredictor(k=4), surprise_floor=Q16(15, 100)))
    return eng


def test_prediction_precommitted_in_receipt():
    eng = _fabric()
    eng.cells["sense.a"].decision = {"rule": "identity", "value": Q16(8, 10)}
    eng.emit("src", {"mag": Q16(1)}, state={"t": 1})
    for _ in range(4):  # warm the window
        eng.emit("src", {"mag": Q16(1)}, state={"t": 2})
    eng.cells["sense.a"].decision = {"rule": "identity", "value": Q16(9, 10)}
    eng.emit("src", {"mag": Q16(1)}, state={"t": 9})
    r = json.loads(eng.books["sense.a"].entries[-1].payload)
    assert "predicted" in r and "surprise" in r
    assert r["surprise"] == "1/10"  # 0.9 - 0.8, exact


def test_alarm_flagged_when_surprise_above_floor():
    eng = _fabric()
    for v in (1, 1, 1, 1):  # constant regime warms predictor at 0.1
        eng.cells["sense.a"].decision = {"rule": "identity", "value": Q16(v, 10)}
        eng.emit("src", {"mag": Q16(1)}, state={})
    eng.cells["sense.a"].decision = {"rule": "identity", "value": Q16(8, 10)}
    eng.emit("src", {"mag": Q16(1)}, state={})
    r = json.loads(eng.books["sense.a"].entries[-1].payload)
    assert r.get("alarmed") == "true"


def test_inquiry_emits_questions_from_books():
    eng = _fabric()
    for i in range(10):
        eng.cells["sense.a"].decision = {"rule": "identity",
                                         "value": Q16(8 if i == 9 else 1, 10)}
        eng.emit("src", {"mag": Q16(1)}, state={"t": i})
    qs = next_questions(eng.books)
    assert any("surprise series" in q["question"] for q in qs)


def test_inquiry_alarms_branch_after_repeated_surprise():
    eng = _fabric()
    for i in range(10):
        eng.cells["sense.a"].decision = {
            "rule": "identity",
            "value": Q16(1 if i % 2 == 0 else 9, 10),  # alternating = perpetual alarm
        }
        eng.emit("src", {"mag": Q16(1)}, state={"t": i})
    qs = next_questions(eng.books)
    assert any("non-stationary" in q["question"] for q in qs)
