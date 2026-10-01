import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))



from jev_quilt.cell import Cell, Hook, Projection, DEADBAND


import unittest


class TestConverted(unittest.TestCase):
    def test_coord_must_be_integer(self):
        c = Cell(name="ok", coord=(3, 7))
        assert c.coord == (3, 7)
        with self.assertRaises(TypeError):
            Cell(name="bad", coord=(3.0, 7))
        with self.assertRaises(TypeError):
            Cell(name="bad2", coord=(3,))


    def test_hook_defaults_to_delta(self):
        h = Hook(source="sibling")
        assert h.on == "delta"
        assert h.floor == DEADBAND


    def test_projection_declares_type(self):
        p = Projection(to="voice.tone", as_type="coefficient")
        assert p.as_type == "coefficient"


    def test_backend_whitelist(self):
        with self.assertRaises(ValueError):
            Cell(name="x", coord=(0, 0), backend="chatgpt")


    def test_viability_floor_binary(self):
        c = Cell(name="x", coord=(0, 0))
        class D: confidence = 0.0
        assert c.viability_floor(D()) is False
        class D2: confidence = 0.4
        assert c.viability_floor(D2()) is True
        # no confidence attr → viable (floor applies only where confidence exists)
        assert c.viability_floor(object()) is True
