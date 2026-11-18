from typing import Any, Dict, List, Optional
import pandas as pd
from engine.models import DFA, DFAState, NFA, format_state_set


def build_nfa_table_df(nfa: NFA) -> pd.DataFrame:
    """Builds a Pandas DataFrame representing the NFA transition table."""
    rows = []
    accept_set = set(nfa.accepts)
    for state in nfa.states:
        badges = []
        if state == nfa.start:
            badges.append("→ Start")
        if state in accept_set:
            badges.append("★ Accept")
        status_str = " & ".join(badges) if badges else "Normal"

        row: Dict[str, Any] = {
            "State": state,
            "Type": status_str,
        }
        for sym in nfa.alphabet:
            targets = nfa.get_transitions(state, sym)
            row[sym] = ", ".join(sorted(targets)) if targets else "∅"
        rows.append(row)

    return pd.DataFrame(rows)


def build_dfa_table_df(
    dfa: DFA,
    visible_states: Optional[List[DFAState]] = None,
    visible_transitions: Optional[Dict[DFAState, Dict[str, DFAState]]] = None,
) -> pd.DataFrame:
    """
    Builds a Pandas DataFrame representing the generated DFA transition table,
    including the NFA subset behind each state and its accepting/start status.
    """
    states_list = visible_states if visible_states is not None else dfa.states
    transitions_map = visible_transitions if visible_transitions is not None else dfa.transitions
    accept_set = set(dfa.accepts)

    rows = []
    for s in states_list:
        label = format_state_set(s)
        subset_str = ", ".join(sorted(list(s))) if s else "(empty set)"

        badges = []
        if s == dfa.start:
            badges.append("→ Start")
        if s in accept_set:
            badges.append("★ Accept")
        if not s:
            badges.append("Trap (∅)")
        status_str = " & ".join(badges) if badges else "Normal"

        row: Dict[str, Any] = {
            "DFA State": label,
            "NFA Subset": subset_str,
            "Status": status_str,
        }

        s_trans = transitions_map.get(s, {})
        for sym in dfa.alphabet:
            tgt = s_trans.get(sym)
            row[sym] = format_state_set(tgt) if tgt is not None else "—"

        rows.append(row)

    return pd.DataFrame(rows)
