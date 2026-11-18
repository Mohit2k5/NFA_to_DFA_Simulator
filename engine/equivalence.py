import itertools
from typing import Optional, Tuple
from engine.models import DFA, NFA
from engine.simulate import simulate_dfa, simulate_nfa


def check_equivalence_exhaustive(
    nfa: NFA, dfa: DFA, max_length: int = 6
) -> Tuple[bool, Optional[str], Optional[bool], Optional[bool], int]:
    """
    Exhaustively tests all strings over alphabet up to max_length on both NFA and DFA.
    Returns (is_equivalent, counterexample_str, nfa_verdict, dfa_verdict, total_tested).
    """
    alphabet = sorted(list(nfa.alphabet))
    total_tested = 0

    for length in range(max_length + 1):
        if length == 0:
            candidates = [""]
        else:
            candidates = ("".join(p) for p in itertools.product(alphabet, repeat=length))

        for candidate in candidates:
            total_tested += 1
            nfa_acc, _, err_nfa = simulate_nfa(nfa, candidate)
            dfa_acc, _, err_dfa = simulate_dfa(dfa, candidate)

            if nfa_acc != dfa_acc:
                return False, candidate, nfa_acc, dfa_acc, total_tested

    return True, None, None, None, total_tested
