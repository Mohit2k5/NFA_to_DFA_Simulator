import json
from typing import Any, Dict
from engine.models import DFA, DFAState, NFA, format_state_set


def nfa_to_json(nfa: NFA, indent: int = 2) -> str:
    """Serializes an NFA object to formatted JSON."""
    data = {
        "states": nfa.states,
        "alphabet": nfa.alphabet,
        "transitions": nfa.transitions,
        "start": nfa.start,
        "accepts": nfa.accepts,
    }
    return json.dumps(data, indent=indent)


def nfa_from_json(json_str: str) -> NFA:
    """Parses JSON string into an NFA object."""
    data = json.loads(json_str)
    # Ensure transitions format is Dict[str, Dict[str, List[str]]]
    raw_trans = data.get("transitions", {})
    cleaned_trans = {}
    for state, sym_map in raw_trans.items():
        cleaned_trans[str(state)] = {}
        for sym, targets in sym_map.items():
            if isinstance(targets, list):
                cleaned_trans[str(state)][str(sym)] = [str(t) for t in targets]
            elif isinstance(targets, str):
                cleaned_trans[str(state)][str(sym)] = [
                    t.strip() for t in targets.split(",") if t.strip()
                ]
            else:
                cleaned_trans[str(state)][str(sym)] = []

    return NFA(
        states=[str(s) for s in data["states"]],
        alphabet=[str(a) for a in data["alphabet"]],
        transitions=cleaned_trans,
        start=str(data["start"]),
        accepts=[str(a) for a in data.get("accepts", [])],
    )


def dfa_to_json(dfa: DFA, indent: int = 2) -> str:
    """Serializes a DFA object to JSON, formatting frozenset state labels."""
    state_names = {s: format_state_set(s) for s in dfa.states}
    serialized_transitions = {}
    for s, sym_map in dfa.transitions.items():
        s_name = state_names[s]
        serialized_transitions[s_name] = {
            sym: state_names[tgt] for sym, tgt in sym_map.items()
        }

    data = {
        "states": [state_names[s] for s in dfa.states],
        "state_subsets": {state_names[s]: sorted(list(s)) for s in dfa.states},
        "alphabet": dfa.alphabet,
        "start": state_names[dfa.start],
        "accepts": [state_names[s] for s in dfa.accepts],
        "transitions": serialized_transitions,
    }
    return json.dumps(data, indent=indent)
