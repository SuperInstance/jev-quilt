import unittest
from jev_quilt.cell import Cell, Hook, Projection
from jev_quilt.engine import Engine
from jev_quilt.q16 import Q16


def _cell(name, **kw):
    return Cell(name=name, coord=(0, 0), **kw)




class TestConverted(unittest.TestCase):

    def test_hook_when_gate_limits_touch(self):
        eng = Engine()
        eng.register(_cell("src"))
        eng.register(_cell("dst.a", input_hooks=[Hook("src", when=lambda s: "a" in s["touched"])],
                           decision={"rule": "threshold", "value": (7, 10), "threshold": (1, 2)}))
        eng.register(_cell("dst.b", input_hooks=[Hook("src", when=lambda s: "b" in s["touched"])],
                           decision={"rule": "threshold", "value": (7, 10), "threshold": (1, 2)}))
        res = eng.emit("src", {"mag": Q16(1)}, state={"touched": {"a"}})
        by = {r.cell: r.reason for r in res}
        assert by["dst.a"] == "decided"
        assert by["dst.b"] == "silent_deadband"




def test_hook_when_broken_predicate_does_not_silence():
    eng = Engine()
    eng.register(_cell("src"))
    eng.register(_cell("dst", input_hooks=[Hook("src", when=lambda s: 1 / 0)],
                       decision={"rule": "threshold", "value": (7, 10), "threshold": (1, 2)}))
    res = eng.emit("src", {"mag": Q16(1)}, state={})
    assert res[0].reason == "decided"


def test_hook_when_none_means_always_cares():
    eng = Engine()
    eng.register(_cell("src"))
    eng.register(_cell("dst", input_hooks=[Hook("src")],
                       decision={"rule": "threshold", "value": (7, 10), "threshold": (1, 2)}))
    res = eng.emit("src", {"mag": Q16(1)}, state={"irrelevant": True})
    assert res[0].reason == "decided"
