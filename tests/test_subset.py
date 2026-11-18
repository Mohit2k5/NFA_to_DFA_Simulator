import pytest
from engine.examples import EXAMPLES
from engine.models import DFAState, NFA
from engine.subset import subset_construction


def test_subset_construction_ends_with_01():
    ex = EXAMPLES["ends_with_01"]
    dfa, trace = subset_construction(ex.nfa)

    assert dfa.start == frozenset(["q0"])
    assert len(dfa.states) == 3
    assert len(dfa.accepts) == 1
    assert frozenset(["q0", "q2"]) in dfa.accepts
    assert len(trace) > 0
    assert trace[0].type == "START"
    assert trace[-1].type == "DONE"


def test_subset_construction_trap_state():
    ex = EXAMPLES["starts_0_ends_1"]
    dfa, trace = subset_construction(ex.nfa)

    # Empty set ∅ must be present as a DFA state
    assert frozenset() in dfa.states
    # Trap state transitions to itself on all symbols
    for sym in dfa.alphabet:
        assert dfa.transitions[frozenset()][sym] == frozenset()


def test_state_limit_blowup():
    # NFA with exponential blow-up
    # NFA for: symbol k from end is '1'
    n = 8
    states = [f"q{i}" for i in range(n + 1)]
    transitions = {"q0": {"0": ["q0"], "1": ["q0", "q1"]}}
    for i in range(1, n):
        transitions[f"q{i}"] = {"0": [f"q{i+1}"], "1": [f"q{i+1}"]}
    transitions[f"q{n}"] = {}

    nfa = NFA(
        states=states,
        alphabet=["0", "1"],
        transitions=transitions,
        start="q0",
        accepts=[f"q{n}"],
    )

    with pytest.raises(ValueError, match="limit"):
        subset_construction(nfa, max_states=16)
