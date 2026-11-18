from typing import Any, Dict, List, Tuple
from engine.models import NFA


def nfa_to_table_rows(nfa: NFA) -> List[Dict[str, Any]]:
    """
    Converts an NFA into row dictionaries suitable for st.data_editor / DataFrame.
    Columns: State, Is Start, Is Accept, followed by a column for each alphabet symbol.
    """
    rows = []
    accept_set = set(nfa.accepts)
    for state in nfa.states:
        row: Dict[str, Any] = {
            "State": state,
            "Is Start": (state == nfa.start),
            "Is Accept": (state in accept_set),
        }
        for sym in nfa.alphabet:
            targets = nfa.get_transitions(state, sym)
            row[sym] = ", ".join(sorted(targets)) if targets else ""
        rows.append(row)
    return rows


def table_rows_to_nfa(
    rows: List[Dict[str, Any]], alphabet: List[str]
) -> Tuple[NFA, List[str]]:
    """
    Converts edited table rows into an NFA object, returning (NFA, errors).
    """
    errors: List[str] = []
    states: List[str] = []
    accepts: List[str] = []
    start_candidates: List[str] = []
    transitions: Dict[str, Dict[str, List[str]]] = {}

    for row in rows:
        state = str(row.get("State", "")).strip()
        if not state:
            continue
        if state in states:
            errors.append(f"Duplicate state name '{state}' found in table.")
        states.append(state)

        if row.get("Is Start"):
            start_candidates.append(state)
        if row.get("Is Accept"):
            accepts.append(state)

        transitions[state] = {}
        for sym in alphabet:
            raw_val = str(row.get(sym, "")).strip()
            if raw_val and raw_val != "-" and raw_val != "∅":
                targets = [t.strip() for t in raw_val.split(",") if t.strip()]
                transitions[state][sym] = targets
            else:
                transitions[state][sym] = []

    if not states:
        errors.append("At least one state must be defined in the transition table.")

    if len(start_candidates) == 0:
        start_state = states[0] if states else ""
        errors.append("No start state was selected. Please mark one state as 'Is Start'.")
    elif len(start_candidates) > 1:
        start_state = start_candidates[0]
        errors.append(
            f"Multiple start states selected: {start_candidates}. An NFA must have exactly one start state."
        )
    else:
        start_state = start_candidates[0]

    nfa = NFA(
        states=states,
        alphabet=alphabet,
        transitions=transitions,
        start=start_state,
        accepts=accepts,
    )
    return nfa, errors
