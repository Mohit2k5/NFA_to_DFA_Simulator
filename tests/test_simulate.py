from engine.examples import EXAMPLES
from engine.simulate import simulate_dfa, simulate_nfa
from engine.subset import subset_construction


def test_simulate_nfa_and_dfa_matches_ends_with_01():
    ex = EXAMPLES["ends_with_01"]
    dfa, _ = subset_construction(ex.nfa)

    test_strings = ["", "0", "1", "01", "101", "00001", "0101", "010"]
    for s in test_strings:
        nfa_acc, nfa_path, nfa_err = simulate_nfa(ex.nfa, s)
        dfa_acc, dfa_path, dfa_err = simulate_dfa(dfa, s)

        assert nfa_err is None
        assert dfa_err is None
        assert nfa_acc == dfa_acc
        assert len(nfa_path) == len(s) + 1
        assert len(dfa_path) == len(s) + 1


def test_simulate_empty_string():
    ex = EXAMPLES["mod_3_zeros"]
    dfa, _ = subset_construction(ex.nfa)

    nfa_acc, _, _ = simulate_nfa(ex.nfa, "")
    dfa_acc, _, _ = simulate_dfa(dfa, "")

    assert nfa_acc is True
    assert dfa_acc is True


def test_invalid_symbol_rejected():
    ex = EXAMPLES["ends_with_01"]
    dfa, _ = subset_construction(ex.nfa)

    nfa_acc, _, nfa_err = simulate_nfa(ex.nfa, "012")
    dfa_acc, _, dfa_err = simulate_dfa(dfa, "012")

    assert nfa_err is not None
    assert dfa_err is not None
    assert "not in the alphabet" in nfa_err
