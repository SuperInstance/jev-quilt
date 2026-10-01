import unittest
from jev_quilt.cell import Cell, Hook, Projection, DEADBAND
from jev_quilt.engine import Engine, WakeResult
from jev_quilt.q16 import Q16


def _cell(name, **kw):
    return Cell(name=name, coord=(0, 0), **kw)




class TestConverted(unittest.TestCase):


    def _monkeypatch(self):
        class _MP:
            def __init__(self, tc):
                self.tc = tc
                self._saved = {}
            def setattr(self, obj, name, value):
                import sys
                if hasattr(obj, name):
                    self._saved.setdefault(('attr', id(obj), name), getattr(obj, name))
                setattr(obj, name, value)
            def delenv(self, name, raising=True):
                import os
                self._saved.setdefault(('env', name), os.environ.get(name))
                if name in os.environ:
                    del os.environ[name]
            def setenv(self, name, value):
                import os
                self._saved.setdefault(('env', name), os.environ.get(name))
                os.environ[name] = value
            def undo(self):
                import os
                for (kind, *rest), value in self._saved.items():
                    if kind == 'env':
                        if value is None:
                            os.environ.pop(rest[0], None)
                        else:
                            os.environ[rest[0]] = value
                    elif kind == 'attr':
                        setattr(rest[0], rest[1], value)
        m = _MP(self)
        self.addCleanup(m.undo)
        return m
    def test_emit_wakes_hooked_cell(self):
        eng = Engine()
        eng.register(_cell("src"))
        eng.register(_cell("dst", input_hooks=[Hook("src")],
                           decision={"rule": "threshold", "value": (7, 10), "threshold": (1, 2)}))
        res = eng.emit("src", Q16(1, 10))
        woke = [r for r in res if r.cell == "dst"]
        assert len(woke) == 1 and woke[0].reason == "decided"
        assert woke[0].decision.value is True




def test_unhooked_cell_silent():
    eng = Engine()
    eng.register(_cell("src"))
    eng.register(_cell("bystander"))
    assert eng.emit("src", Q16(1)) == []


def test_deadband_silences_small_delta():
    eng = Engine()
    eng.register(_cell("src"))
    eng.register(_cell("dst", input_hooks=[Hook("src", floor=Q16(1, 100))],
                       decision={"rule": "threshold", "value": (7, 10), "threshold": (1, 2)}))
    res = eng.emit("src", {"mag": Q16(5, 1000)})  # 0.005 < 0.01
    assert res[0].reason == "silent_deadband"
    res2 = eng.emit("src", {"mag": Q16(3, 100)})  # 0.03 >= 0.01
    assert res2[0].reason == "decided"


def test_deadband_token_means_no_filtering():
    eng = Engine()
    eng.register(_cell("src"))
    eng.register(_cell("dst", input_hooks=[Hook("src", floor=DEADBAND)],
                       decision={"rule": "threshold", "value": (1,), "threshold": (2,)}))
    res = eng.emit("src", {"tiny": True})  # unmeasurable, DEADBAND token
    assert res[0].reason == "decided"


def test_viability_rejection_books_but_never_projects():
    eng = Engine()
    eng.register(_cell("src"))
    eng.register(_cell("dst", input_hooks=[Hook("src")],
                       decision={"rule": "threshold", "value": (9, 10), "threshold": (1, 2)},
                       outputs=[Projection("out", "json")]))
    # force zero-confidence refusal: q16 always 1.0, so monkeypatch floor
    eng.cells["dst"].viability_floor = lambda d: False
    res = eng.emit("src", Q16(1))
    assert res[0].reason == "rejected"
    assert res[0].projections_fired == []
    # book recorded the rejection: 2 entries (decision + rejected)
    assert len(eng.books["dst"].entries) == 2
    assert eng.books["dst"].entries[-1].decision_kind == "rejected"


def test_wake_catches_up_book_first():
    eng = Engine()
    eng.register(_cell("src"))
    eng.register(_cell("dst", input_hooks=[Hook("src")],
                       decision={"rule": "threshold", "value": (7, 10), "threshold": (1, 2)}))
    eng.emit("src", Q16(1))
    eng.emit("src", Q16(2))
    bk = eng.books["dst"]
    assert bk.verify() and bk._tick == 2  # every wake booked before deciding


def test_backend_refusal_books_miss_no_projection():
    eng = Engine()
    eng.register(_cell("src"))
    eng.register(_cell("dst", input_hooks=[Hook("src")], backend="openjev-local",
                       decision={"question": {"type": "noul"}},
                       outputs=[Projection("out", "json")]))
    res = eng.emit("src", Q16(1))
    assert res[0].reason == "refused"
    assert res[0].projections_fired == []
    assert eng.books["dst"].entries[-1].decision_kind == "refused"


def test_unknown_source_emits_nothing():
    eng = Engine()
    eng.register(_cell("dst", input_hooks=[Hook("ghost")]))
    assert eng.emit("nobody", Q16(1)) == []
