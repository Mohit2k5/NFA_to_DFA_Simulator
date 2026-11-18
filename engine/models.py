from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional, Set, Union

State = str
Symbol = str
DFAState = FrozenSet[State]


def format_state_set(s: Union[FrozenSet[State], Set[State], List[State]], empty_symbol: str = "∅") -> str:
    """Formats a set of states deterministically, e.g. {q0, q1} or ∅ for empty set."""
    if not s:
        return empty_symbol
    sorted_states = sorted(list(s))
    return "{" + ", ".join(sorted_states) + "}"


@dataclass
class NFA:
    states: List[State]
    alphabet: List[Symbol]
    transitions: Dict[State, Dict[Symbol, List[State]]]
    start: State
    accepts: List[State]

    def get_transitions(self, state: State, symbol: Symbol) -> List[State]:
        return self.transitions.get(state, {}).get(symbol, [])


@dataclass
class DFA:
    states: List[DFAState]
    alphabet: List[Symbol]
    transitions: Dict[DFAState, Dict[Symbol, DFAState]]
    start: DFAState
    accepts: List[DFAState]

    def is_accepting(self, state: DFAState) -> bool:
        return state in self.accepts

    def get_transition(self, state: DFAState, symbol: Symbol) -> Optional[DFAState]:
        return self.transitions.get(state, {}).get(symbol)


@dataclass
class TraceStep:
    type: str  # "START" | "PICK_STATE" | "MOVE" | "NEW_STATE" | "EXISTING_STATE" | "MARK_ACCEPT" | "DONE"
    dfa_state: Optional[DFAState] = None
    symbol: Optional[Symbol] = None
    moved: Optional[DFAState] = None
    explanation: str = ""
    active_nfa_states: Optional[List[State]] = None
    discovered_states: Optional[List[DFAState]] = None
    discovered_transitions: Optional[Dict[DFAState, Dict[Symbol, DFAState]]] = None
