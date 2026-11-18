from typing import FrozenSet, Iterable
from engine.models import DFAState, State, Symbol, NFA


def move(nfa: NFA, current_subset: Iterable[State], symbol: Symbol) -> DFAState:
    """
    Computes move(T, a) = ⋃ { nfa.transitions[s][a] for s in T }.
    Returns a frozenset representing the target DFA state.
    If no transitions exist on symbol, returns frozenset() (the empty set / trap state).
    """
    reachable = set()
    for s in current_subset:
        targets = nfa.get_transitions(s, symbol)
        reachable.update(targets)
    return frozenset(reachable)
