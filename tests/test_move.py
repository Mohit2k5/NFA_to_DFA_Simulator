from engine.models import NFA
from engine.move import move


def test_move_basic():
    nfa = NFA(
        states=["q0", "q1", "q2"],
        alphabet=["0", "1"],
        transitions={
            "q0": {"0": ["q0", "q1"], "1": ["q0"]},
            "q1": {"1": ["q2"]},
            "q2": {},
        },
        start="q0",
        accepts=["q2"],
    )

    # move({q0}, '0') = {q0, q1}
    assert move(nfa, ["q0"], "0") == frozenset(["q0", "q1"])

    # move({q0}, '1') = {q0}
    assert move(nfa, ["q0"], "1") == frozenset(["q0"])

    # move({q0, q1}, '1') = {q0, q2}
    assert move(nfa, ["q0", "q1"], "1") == frozenset(["q0", "q2"])

    # move({q2}, '0') = ∅ (trap state)
    assert move(nfa, ["q2"], "0") == frozenset()

    # move on empty set = ∅
    assert move(nfa, [], "0") == frozenset()
