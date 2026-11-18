import pytest
from engine.models import NFA
from engine.validate import validate_nfa


def test_valid_nfa():
    nfa = NFA(
        states=["q0", "q1"],
        alphabet=["0", "1"],
        transitions={"q0": {"0": ["q1"], "1": ["q0"]}, "q1": {}},
        start="q0",
        accepts=["q1"],
    )
    is_valid, errors = validate_nfa(nfa)
    assert is_valid is True
    assert len(errors) == 0


def test_epsilon_in_alphabet_rejected():
    for eps in ["ε", "e", "epsilon", "λ"]:
        nfa = NFA(
            states=["q0", "q1"],
            alphabet=["0", eps],
            transitions={"q0": {"0": ["q1"]}, "q1": {}},
            start="q0",
            accepts=["q1"],
        )
        is_valid, errors = validate_nfa(nfa)
        assert is_valid is False
        assert any("not supported" in err.lower() or "epsilon" in err.lower() for err in errors)


def test_epsilon_in_transitions_rejected():
    nfa = NFA(
        states=["q0", "q1"],
        alphabet=["0", "1"],
        transitions={"q0": {"ε": ["q1"], "0": ["q0"]}, "q1": {}},
        start="q0",
        accepts=["q1"],
    )
    is_valid, errors = validate_nfa(nfa)
    assert is_valid is False
    assert any("epsilon" in err.lower() for err in errors)


def test_invalid_start_and_accept_states():
    nfa = NFA(
        states=["q0"],
        alphabet=["0"],
        transitions={"q0": {}},
        start="q99",  # not in states
        accepts=["q88"],  # not in states
    )
    is_valid, errors = validate_nfa(nfa)
    assert is_valid is False
    assert any("q99" in err for err in errors)
    assert any("q88" in err for err in errors)


def test_invalid_transition_target():
    nfa = NFA(
        states=["q0"],
        alphabet=["0"],
        transitions={"q0": {"0": ["q_unknown"]}},
        start="q0",
        accepts=[],
    )
    is_valid, errors = validate_nfa(nfa)
    assert is_valid is False
    assert any("q_unknown" in err for err in errors)
