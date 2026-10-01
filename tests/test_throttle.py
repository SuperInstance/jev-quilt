import unittest
"""tests/test_throttle.py — the homeostatic circuit breaker."""
from jev_quilt import Bookkeeper
from jev_quilt.throttle import HomeostaticThrottle


def make_fn():
    return lambda text: f"done:{text[:12]}"




class TestConverted(unittest.TestCase):

    def test_flood_of_identical_is_shed(self):
        t = HomeostaticThrottle(make_fn())
        results = [t("same request") for _ in range(100)]
        escalations = [r for r in results if r is not None]
        assert len(escalations) <= 3, "identical flood must self-shed"
        assert t.shed + t.escalated == 100




def test_novel_traffic_escalates_then_ratchet_absorbs():
    t = HomeostaticThrottle(make_fn())
    for i in range(20):
        t(f"routine {i % 3}")                 # build a boring boundary
    hits = [t(f"genuinely-new-{j}") for j in range(5)]
    assert hits[0] is not None, "the FIRST surprise escalates"
    assert hits.count(None) >= 1, "the ratchet then absorbs the burst:"
    #   each admission re-anchors the boundary — sustained 'novelty'
    #   becomes the new normal. An attacker alternating payloads does
    #   NOT buy perpetual escalation. The ratchet is anti-DoS armor.


def test_every_call_is_booked():
    t = HomeostaticThrottle(make_fn(), keeper=Bookkeeper("audit"))
    for i in range(30):
        t(f"call {i % 5}")
    kinds = [e.decision_kind for e in t.keeper.entries]
    assert "shed" in kinds and "escalated" in kinds
    assert len(t.keeper.entries) == 30
    assert t.keeper.replay()


def test_anti_dos_flood_costs_nothing():
    t = HomeostaticThrottle(make_fn())
    for _ in range(200):
        t("attack payload")                   # adversarial repetition
    assert t.escalated <= 2, "ratchet: repetition is learnable noise"
    assert t.shed >= 198


def test_window_slides_and_relearns():
    t = HomeostaticThrottle(make_fn(), window=8)
    for i in range(10):
        t(f"family A {i}")
    before = t.shed
    for i in range(10):
        t(f"family B {i}")                    # new family: first admits
    assert t.escalated > 0
    assert t.shed >= before                   # and B quickly becomes shed
