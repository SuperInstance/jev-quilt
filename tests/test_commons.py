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
