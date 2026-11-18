from engine.examples import EXAMPLES
from engine.equivalence import check_equivalence_exhaustive
from engine.subset import subset_construction


def test_all_examples_exhaustive_equivalence():
    for ex_id, example in EXAMPLES.items():
        dfa, _ = subset_construction(example.nfa)
        is_equiv, counter, nfa_v, dfa_v, total = check_equivalence_exhaustive(
            example.nfa, dfa, max_length=5
        )
        assert is_equiv is True, f"Failed equivalence for example {ex_id} on string {counter}"
        assert counter is None
        assert total > 0


def test_equivalence_detects_corrupted_dfa():
    ex = EXAMPLES["ends_with_01"]
    dfa, _ = subset_construction(ex.nfa)

    # Artificially corrupt the DFA by removing its accept state
    dfa.accepts = []
    is_equiv, counter, nfa_v, dfa_v, total = check_equivalence_exhaustive(
        ex.nfa, dfa, max_length=4
    )

    assert is_equiv is False
    assert counter is not None
    assert nfa_v is True
    assert dfa_v is False
