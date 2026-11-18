from engine.examples import EXAMPLES
from engine.isomorphism import check_dfa_isomorphism
from engine.subset import subset_construction


def test_golden_dfa_isomorphism_all_examples():
    for ex_id, example in EXAMPLES.items():
        gen_dfa, _ = subset_construction(example.nfa)
        is_iso, mapping, diffs = check_dfa_isomorphism(gen_dfa, example.golden_dfa)

        assert is_iso is True, f"Example {ex_id} failed isomorphism: {diffs}"
        assert len(diffs) == 0
        assert len(mapping) == len(example.golden_dfa.states)


def test_isomorphism_detects_structure_differences():
    ex1 = EXAMPLES["ends_with_01"]
    ex2 = EXAMPLES["contains_aba"]

    dfa1, _ = subset_construction(ex1.nfa)
    dfa2, _ = subset_construction(ex2.nfa)

    is_iso, mapping, diffs = check_dfa_isomorphism(dfa1, dfa2)
    assert is_iso is False
    assert len(diffs) > 0
