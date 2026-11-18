from engine.examples import EXAMPLES
from engine.minimize import minimize_dfa
from engine.models import DFAState
from engine.subset import subset_construction
from engine.equivalence import check_equivalence_exhaustive


def test_minimize_dfa_preserves_language():
    for ex_id, example in EXAMPLES.items():
        dfa, _ = subset_construction(example.nfa)
        min_dfa, log = minimize_dfa(dfa)

        # Minimized DFA must accept the exact same language
        is_equiv, counter, _, _, _ = check_equivalence_exhaustive(
            example.nfa, min_dfa, max_length=5
        )
        assert is_equiv is True, f"Minimized DFA diverged for {ex_id} on string {counter}"
        assert len(min_dfa.states) <= len(dfa.states)
