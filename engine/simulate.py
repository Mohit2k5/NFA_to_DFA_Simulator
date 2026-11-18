from typing import List, Optional, Tuple
from engine.models import DFA, DFAState, FrozenSet, NFA, State, Symbol
from engine.move import move


def simulate_nfa(
    nfa: NFA, input_string: str
) -> Tuple[bool, List[FrozenSet[State]], Optional[str]]:
    """
    Simulates execution of an input string on an NFA.
    Returns (accepted: bool, path: List[FrozenSet[State]], error: Optional[str]).
    path[0] is the start state set {nfa.start}, path[i] is the active state set after reading character i.
    """
    current_set: FrozenSet[State] = frozenset([nfa.start])
    path: List[FrozenSet[State]] = [current_set]

    alphabet_set = set(nfa.alphabet)
    for idx, char in enumerate(input_string):
        if char not in alphabet_set:
            return (
                False,
                path,
                f"Symbol '{char}' at index {idx} is not in the alphabet {nfa.alphabet}."
            )
        current_set = move(nfa, current_set, char)
        path.append(current_set)

    is_accepted = any(q in nfa.accepts for q in current_set)
    return is_accepted, path, None


def simulate_dfa(
    dfa: DFA, input_string: str
) -> Tuple[bool, List[DFAState], Optional[str]]:
    """
    Simulates execution of an input string on a DFA.
    Returns (accepted: bool, path: List[DFAState], error: Optional[str]).
    path[0] is dfa.start, path[i] is active DFAState after reading character i.
    """
    current: DFAState = dfa.start
    path: List[DFAState] = [current]

    alphabet_set = set(dfa.alphabet)
    for idx, char in enumerate(input_string):
        if char not in alphabet_set:
            return (
                False,
                path,
                f"Symbol '{char}' at index {idx} is not in the alphabet {dfa.alphabet}."
            )
        next_state = dfa.get_transition(current, char)
        if next_state is None:
            # Trap state / undefined transition goes to empty set
            next_state = frozenset()
        current = next_state
        path.append(current)

    is_accepted = dfa.is_accepting(current)
    return is_accepted, path, None
