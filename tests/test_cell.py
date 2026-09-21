import sys
sys.path.insert(0, "/workspace/repos/jev-quilt")



from jev_quilt.cell import Cell, Hook, Projection, DEADBAND


def test_coord_must_be_integer():
    c = Cell(name="ok", coord=(3, 7))
    assert c.coord == (3, 7)
    with pytest.raises(TypeError):
        Cell(name="bad", coord=(3.0, 7))
    with pytest.raises(TypeError):
        Cell(name="bad2", coord=(3,))


def test_hook_defaults_to_delta():
    h = Hook(source="sibling")
    assert h.on == "delta"
    assert h.floor == DEADBAND


def test_projection_declares_type():
    p = Projection(to="voice.tone", as_type="coefficient")
    assert p.as_type == "coefficient"


def test_backend_whitelist():
    with pytest.raises(ValueError):
        Cell(name="x", coord=(0, 0), backend="chatgpt")


def test_viability_floor_binary():
    c = Cell(name="x", coord=(0, 0))
    class D: confidence = 0.0
    assert c.viability_floor(D()) is False
    class D2: confidence = 0.4
    assert c.viability_floor(D2()) is True
    # no confidence attr → viable (floor applies only where confidence exists)
    assert c.viability_floor(object()) is True
