from typing import Dict, FrozenSet, Iterable, List, Optional, Set, Tuple
from engine.models import DFA, DFAState, NFA, State, Symbol, format_state_set


def escape_label(s: str) -> str:
    """Escapes quotes and backslashes for Graphviz DOT labels."""
    return s.replace('\\', '\\\\').replace('"', '\\"')


def nfa_to_dot(
    nfa: NFA,
    active_states: Optional[Iterable[State]] = None,
    active_transition: Optional[Tuple[State, State, Symbol]] = None,
) -> str:
    """
    Generates a Graphviz DOT script for an NFA.
    Renders start indicator, double circle for accept states, merged parallel edges,
    and highlights active states / transitions.
    """
    lines = [
        "digraph NFA {",
        '  rankdir=LR;',
        '  fontname="Helvetica,Arial,sans-serif";',
        '  node [fontname="Helvetica,Arial,sans-serif", fontsize=12, style="filled", fillcolor="#F8F9FA", color="#495057"];',
        '  edge [fontname="Helvetica,Arial,sans-serif", fontsize=11, color="#6C757D"];',
        "",
        '  // Start state indicator',
        '  __start__ [shape=none, label="", width=0, height=0];',
        f'  __start__ -> "{escape_label(nfa.start)}";',
        "",
    ]

    active_set = set(active_states) if active_states else set()
    accept_set = set(nfa.accepts)

    # Nodes
    for state in nfa.states:
        is_acc = state in accept_set
        shape = "doublecircle" if is_acc else "circle"
        if state in active_set:
            attrs = f'shape={shape}, label="{escape_label(state)}", fillcolor="#FFF3CD", color="#FFC107", penwidth=2.5'
        else:
            attrs = f'shape={shape}, label="{escape_label(state)}", fillcolor="#FFFFFF", color="#343A40", penwidth=1.5'
        lines.append(f'  "{escape_label(state)}" [{attrs}];')

    lines.append("")

    # Merge parallel transitions between src and tgt
    edge_map: Dict[Tuple[State, State], List[Symbol]] = {}
    for src, sym_map in nfa.transitions.items():
        for sym, targets in sym_map.items():
            for tgt in targets:
                edge_map.setdefault((src, tgt), []).append(sym)

    for (src, tgt), symbols in edge_map.items():
        label_text = ", ".join(sorted(symbols))
        is_active_edge = False
        if active_transition and active_transition[0] == src and active_transition[1] == tgt:
            if active_transition[2] in symbols:
                is_active_edge = True

        if is_active_edge:
            edge_attrs = f'label="{escape_label(label_text)}", color="#DC3545", fontcolor="#DC3545", penwidth=2.5'
        else:
            edge_attrs = f'label="{escape_label(label_text)}", color="#495057", fontcolor="#212529"'
        lines.append(f'  "{escape_label(src)}" -> "{escape_label(tgt)}" [{edge_attrs}];')

    lines.append("}")
    return "\n".join(lines)


def dfa_to_dot(
    dfa: DFA,
    active_state: Optional[DFAState] = None,
    active_edge: Optional[Tuple[DFAState, DFAState, Symbol]] = None,
    visible_states: Optional[Iterable[DFAState]] = None,
    visible_transitions: Optional[Dict[DFAState, Dict[Symbol, DFAState]]] = None,
    hide_trap: bool = False,
) -> str:
    """
    Generates a Graphviz DOT script for a DFA.
    Labels states with their NFA subset representation (e.g. {q0,q1} or ∅).
    Supports progressive visibility during step-by-step playback and state/edge highlighting.
    """
    lines = [
        "digraph DFA {",
        '  rankdir=LR;',
        '  fontname="Helvetica,Arial,sans-serif";',
        '  node [fontname="Helvetica,Arial,sans-serif", fontsize=11, style="filled", fillcolor="#F8F9FA", color="#495057"];',
        '  edge [fontname="Helvetica,Arial,sans-serif", fontsize=11, color="#6C757D"];',
        "",
    ]

    states_to_show = list(visible_states) if visible_states is not None else list(dfa.states)
    if hide_trap:
        states_to_show = [s for s in states_to_show if len(s) > 0]

    # Deterministic node ids to avoid DOT syntax issues with braces and commas
    state_id_map: Dict[DFAState, str] = {s: f"node_{i}" for i, s in enumerate(dfa.states)}
    # Handle any temporary states in visible_states that might not be in dfa.states
    for s in states_to_show:
        if s not in state_id_map:
            state_id_map[s] = f"node_{len(state_id_map)}"

    # Start arrow if start state is visible
    if dfa.start in states_to_show:
        lines.append('  // Start state indicator')
        lines.append('  __dfa_start__ [shape=none, label="", width=0, height=0];')
        lines.append(f'  __dfa_start__ -> {state_id_map[dfa.start]};')
        lines.append("")

    accept_set = set(dfa.accepts)

    for s in states_to_show:
        node_id = state_id_map[s]
        label = format_state_set(s)
        is_acc = s in accept_set
        shape = "doublecircle" if is_acc else "circle"

        if active_state is not None and s == active_state:
            attrs = f'shape={shape}, label="{escape_label(label)}", fillcolor="#D1E7DD", color="#198754", penwidth=3.0, fontcolor="#0F5132"'
        else:
            if not s:  # Trap state ∅
                attrs = f'shape={shape}, label="{escape_label(label)}", fillcolor="#F8D7DA", color="#DC3545", penwidth=1.5, fontcolor="#842029"'
            else:
                attrs = f'shape={shape}, label="{escape_label(label)}", fillcolor="#FFFFFF", color="#343A40", penwidth=1.5'
        lines.append(f'  {node_id} [{attrs}];')

    lines.append("")

    # Collect transitions
    transitions_source = visible_transitions if visible_transitions is not None else dfa.transitions
    edge_map: Dict[Tuple[DFAState, DFAState], List[Symbol]] = {}

    for src, sym_map in transitions_source.items():
        if src not in states_to_show:
            continue
        for sym, tgt in sym_map.items():
            if tgt not in states_to_show:
                continue
            edge_map.setdefault((src, tgt), []).append(sym)

    for (src, tgt), symbols in edge_map.items():
        src_id = state_id_map[src]
        tgt_id = state_id_map[tgt]
        label_text = ", ".join(sorted(symbols))

        is_active = False
        if active_edge and active_edge[0] == src and active_edge[1] == tgt:
            if active_edge[2] in symbols:
                is_active = True

        if is_active:
            edge_attrs = f'label="{escape_label(label_text)}", color="#0D6EFD", fontcolor="#0D6EFD", penwidth=2.5'
        else:
            edge_attrs = f'label="{escape_label(label_text)}", color="#495057", fontcolor="#212529"'
        lines.append(f'  {src_id} -> {tgt_id} [{edge_attrs}];')

    lines.append("}")
    return "\n".join(lines)
