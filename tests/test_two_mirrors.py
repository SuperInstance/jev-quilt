from jev_quilt import (Q16, WorldModel, imagine_choice, imagine_score)
from jev_quilt.readings import (ConstReading, NgramReading, DriftReading,
                                ReadingEnsemble)


import unittest


class TestConverted(unittest.TestCase):
    def test_ngram_locks_exactly_on_periodic_signal(self):
        r = NgramReading(k=2)
        r.update(Q16(1, 10)); r.update(Q16(9, 10))
        # period-2 world: after seeing [a, b], the next value is a — exact lock
        assert r.predict() == Q16(1, 10)
        r.update(Q16(1, 10))
        assert r.predict() == Q16(9, 10)


    def test_drift_tracks_a_ramp_exactly(self):
        r = DriftReading(k=4)
        for v in (1, 2, 3, 4, 5):           # ramp of +1/10 each beat
            r.update(Q16(v, 10))
        pred = r.predict()
        assert pred is not None
        # last=0.5, mean increment over [0.1,0.1,0.1,0.1] window = 0.1 -> 0.6
        assert pred == Q16(6, 10)


    def test_ensemble_prefers_periodic_reader_over_mean(self):
        ens = ReadingEnsemble({"mean": __import__("jev_quilt").MeanPredictor(k=4),
                               "period": NgramReading(k=3)})
        floor = Q16(15, 100)
        sig = [Q16(1, 10), Q16(5, 10), Q16(9, 10)] * 6   # period-3 world
        for v in sig:
            pred = ens.predict()
            # surprise vs committed prediction, exact
            if pred is not None:
                from jev_quilt import surprise
                s = surprise(v, pred)
                if s > floor:
                    pass  # engine does the booking; here we drive updates
            ens.update(v)
        assert ens.alarms["period"] == 0      # period reader never surprised
        assert ens.alarms["mean"] >= 3        # mean reader lost on periodic world
        # weights now favor period; next prediction comes from it
        ens.predict()
        assert ens.last_choice == "period"


    def test_ensemble_names_mean_when_world_is_constant(self):
        ens = ReadingEnsemble({"mean": __import__("jev_quilt").MeanPredictor(k=4),
                               "period": NgramReading(k=2)})
        for _ in range(8):
            ens.update(Q16(3, 10))
        ens.predict()
        # both would do fine; tie breaks alphabetically -> 'mean'
        assert ens.last_choice == "mean"



# ---- imagination: JEPA rolling futures, JEV signing the surface ----

def _gridworld():
    # positions 0..3 on a line, food (energy 0) at 3, each step costs
    # distance-to-food. 'stay' is its own action (explicit, not a footgun
    # where unknown names silently act as 'left').
    def transition(s: Q16, a: str) -> Q16:
        pos = s.num // s.den
        if a == "right":
            pos = min(3, pos + 1)
        elif a == "left":
            pos = max(0, pos - 1)
        elif a == "stay":
            pass
        else:
            raise ValueError(f"gridworld: unknown action {a!r}")
        return Q16(pos, 1)

    def energy(s: Q16) -> Q16:
        return Q16(3, 1) - s   # distance-to-food cost, exact

    return WorldModel(transition, energy)


def test_imagine_choice_prefers_the_foodward_action():
    w = _gridworld()
    d = imagine_choice(w, Q16(1, 1), ["left", "right"], horizon=2)
    assert d.kind == "choice"
    assert d.value == "right"     # rolled futures: right lands on food
    assert "probs=" in d.receipt_note
    assert "left:1/5" in d.receipt_note
    assert "right:4/5" in d.receipt_note  # 0-gap vs 3-gap: weights 1 vs 4


def test_imagine_choice_probabilities_exact():
    w = _gridworld()
    d = imagine_choice(w, Q16(0, 1), ["right", "stay"], horizon=1)
    # right -> pos1 (gap 2), stay -> pos0 (gap 3): weights 1+2 vs 1+3... gap
    # measured from worst = 3: right weight 1+(3-2)=2, stay 1+0=1 -> 2/3,1/3
    assert "right:2/3" in d.receipt_note
    assert "stay:1/3" in d.receipt_note


def test_imagine_score_and_noul_honesty():
    w = _gridworld()
    near = imagine_score(w, Q16(2, 1), [Q16(1, 10), Q16(3, 10)], horizon=1,
                         action="right")   # pos3, energy 0, nearest 0.1
    assert near.kind == "score"
    far = imagine_score(w, Q16(0, 1), [Q16(9, 1)], horizon=1, action="left")
    assert far.kind == "noul"     # honest refusal, not a confident guess


def test_imagine_budget_refuses():
    w = _gridworld()
    with self.assertRaises(ValueError) as _cm:
        self.assertIn("budget", str(_cm.exception))
        imagine_choice(w, Q16(0, 1), ["right"] * 5000, horizon=1)
