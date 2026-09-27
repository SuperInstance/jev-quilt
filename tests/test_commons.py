"""The deposit commons (FRONTIER R2, other half): shared, content-addressed,
confluent memory over fold.mmr_root. Pooled evidence lets a route no single cell
earned become fleet-earned; the root proves two nodes agree; merges are order-free.
"""
from jev_quilt.bookkeeper import Bookkeeper
from jev_quilt.standing import Standing
from jev_quilt.commons import Commons, Deposit


def _book(rows):
    bk = Bookkeeper("cell")
    for key, correct, answer in rows:
        bk.book({}, {}, answer, {"key": key, "correct": correct, "answer": answer})
    return bk


def test_pooled_evidence_makes_a_route_fleet_earned():
    # three cells, each only ONE correct on open→warm (none earns it alone at diploma 3)
    books = {f"c{i}": _book([("open", True, "warm")]) for i in range(3)}
    c = Commons.from_books(books, diploma=3, quorum=3)
    assert c.weight("open", "warm") == 3        # evidence pools
    assert c.earned("open")                     # fleet-earned though no cell was
    assert c.recall("open") == "warm"


def test_recall_picks_the_best_answer_ties_broken_deterministically():
    c = Commons(quorum=1)
    c.deposit("route", "left", 5)
    c.deposit("route", "right", 2)
    assert c.recall("route") == "left"          # higher pooled weight wins
    c.deposit("route", "right", 3)              # now tied at 5
    assert c.recall("route") == "left"          # tie → lexicographic, stable
    assert c.recall("never-seen") is None       # honest absence


def test_confluent_merge_order_never_changes_the_root():
    a = Commons(); a.deposit("k", "v", 2); a.deposit("m", "w", 1)
    b = Commons(); b.deposit("k", "v", 3); b.deposit("n", "x", 4)
    import copy
    ab = copy.deepcopy(a).merge(copy.deepcopy(b))
    ba = copy.deepcopy(b).merge(copy.deepcopy(a))
    assert ab.root() == ba.root()               # A∪B == B∪A
    assert ab.agrees_with(ba)
    assert ab.weight("k", "v") == 5             # weights added


def test_content_addressed_same_deposits_same_root_built_any_order():
    a = Commons(); a.deposit("b", "2", 1); a.deposit("a", "1", 2)
    b = Commons(); b.deposit("a", "1", 2); b.deposit("b", "2", 1)   # reverse insert
    assert a.root() == b.root()
    b.deposit("a", "1", 1)                        # change one weight
    assert a.root() != b.root()                   # root is sensitive to content


def test_agreement_is_one_root_comparison():
    a = Commons(); b = Commons()
    for c in (a, b):
        c.deposit("x", "y", 4)
    assert a.agrees_with(b)
    b.deposit("x", "z", 1)
    assert not a.agrees_with(b)                   # divergence shows in the root


def test_from_books_reads_real_standing():
    # one cell truly earns open→warm (3 in a row); another has a stale, revoked one
    books = {
        "veteran": _book([("open", True, "warm")] * 3),
        "drifted": _book([("open", True, "cold")] * 3 + [("open", False, "cold")]),
    }
    c = Commons.from_books(books, diploma=3, quorum=3)
    assert c.recall("open") == "warm"             # the revoked 'cold' contributes nothing
    assert c.weight("open", "cold") == 0
    assert isinstance(c.deposits()[0], Deposit)


# ── G11: trust-weighted cross-fleet gluing (defeats weight-inflation) ──────────

def test_g11_trust_weighted_gluing_defeats_a_strangers_inflated_lie():
    honest = Commons(quorum=1); honest.deposit("k", "safe_a", 5, source="honest")
    stranger = Commons(quorum=1); stranger.deposit("k", "lie", 1000, source="stranger")
    # stranger is unknown → default trust 0: its lie is scaled to nothing
    glued = honest.provenance_merge(stranger, trust={"honest": 100})
    assert glued.recall("k") == "safe_a"
    assert glued.weight("k", "lie") == 0
    assert glued.weight("k", "safe_a") == 500


def test_g11_confluent_and_agrees_regardless_of_glue_order():
    import copy
    a = Commons(quorum=1); a.deposit("k", "x", 3, source="A")
    b = Commons(quorum=1); b.deposit("k", "x", 2, source="B")
    trust = {"A": 10, "B": 10}
    ab = copy.deepcopy(a).provenance_merge(copy.deepcopy(b), trust=trust)
    ba = copy.deepcopy(b).provenance_merge(copy.deepcopy(a), trust=trust)
    assert ab.root() == ba.root()          # A∪B == B∪A under trust
    assert ab.agrees_with(ba)
    assert ab.weight("k", "x") == 50       # (3+2)·10


def test_g11_trust_is_the_lever_an_earned_stranger_contributes():
    honest = Commons(quorum=1); honest.deposit("k", "safe_a", 5, source="honest")
    stranger = Commons(quorum=1); stranger.deposit("k", "new_b", 5, source="stranger")
    # once the stranger has EARNED trust, its evidence counts (500 > 50)
    glued = honest.provenance_merge(stranger, trust={"honest": 10, "stranger": 100})
    assert glued.recall("k") == "new_b"


def test_g11_from_books_carries_provenance():
    from jev_quilt.bookkeeper import Bookkeeper
    def bk(name, rows):
        b = Bookkeeper(name)
        for key, correct, answer in rows:
            b.book({}, {}, answer, {"key": key, "correct": correct, "answer": answer})
        return b
    books = {"veteran": bk("veteran", [("open", True, "warm")] * 3),
             "newcomer": bk("newcomer", [("open", True, "cold")] * 3)}
    c = Commons.from_books(books, diploma=3, quorum=1)
    assert c.sources() == {"veteran", "newcomer"}
    # trust only the veteran → its answer wins despite equal raw streaks
    glued = c.trust_weighted({"veteran": 100})
    assert glued.recall("open") == "warm"
