from collections import deque
from typing import Dict, List, Set, Tuple
from engine.models import DFA, DFAState, Symbol, format_state_set


def minimize_dfa(dfa: DFA) -> Tuple[DFA, List[str]]:
    """
    Minimizes a DFA using the table-filling / equivalence partition refinement algorithm.
    Returns (minimized_dfa, partition_log).
    """
    log: List[str] = []

    # 1. Reachable states
    reachable: Set[DFAState] = set()
    queue = deque([dfa.start])
    reachable.add(dfa.start)

    while queue:
        curr = queue.popleft()
        for sym in dfa.alphabet:
            nxt = dfa.get_transition(curr, sym)
            if nxt is not None and nxt not in reachable:
                reachable.add(nxt)
                queue.append(nxt)

    log.append(f"Reachable states ({len(reachable)}): {[format_state_set(s) for s in reachable]}")

    # 2. Initial partitions: accepting (F) vs non-accepting (Q \ F)
    f_states = frozenset(s for s in reachable if dfa.is_accepting(s))
    non_f_states = frozenset(s for s in reachable if not dfa.is_accepting(s))

    partitions: List[FrozenSet[DFAState]] = []
    if non_f_states:
        partitions.append(non_f_states)
    if f_states:
        partitions.append(f_states)

    log.append(
        f"Initial partition P0: "
        f"[Non-accepting: {len(non_f_states)} states, Accepting: {len(f_states)} states]"
    )

    # 3. Iterative refinement
    changed = True
    iteration = 1
    while changed:
        changed = False
        new_partitions: List[FrozenSet[DFAState]] = []

        # Map state to its current partition index
        state_to_part = {}
        for idx, part in enumerate(partitions):
            for s in part:
                state_to_part[s] = idx

        for part in partitions:
            if len(part) <= 1:
                new_partitions.append(part)
                continue

            # Group states in part by their transition partition signatures
            subgroups: Dict[Tuple[int, ...], List[DFAState]] = {}
            for s in part:
                sig = []
                for sym in dfa.alphabet:
                    nxt = dfa.get_transition(s, sym)
                    nxt_idx = state_to_part.get(nxt, -1)
                    sig.append(nxt_idx)
                sig_tuple = tuple(sig)
                subgroups.setdefault(sig_tuple, []).append(s)

            if len(subgroups) > 1:
                changed = True
                for grp in subgroups.values():
                    new_partitions.append(frozenset(grp))
            else:
                new_partitions.append(part)

        partitions = new_partitions
        log.append(f"Iteration {iteration}: {len(partitions)} partition groups")
        iteration += 1

    # 4. Construct minimized DFA
    # Each partition becomes a new DFAState (union of NFA states across the partition)
    # Map old DFAState to representative merged state
    part_to_merged: Dict[FrozenSet[DFAState], DFAState] = {}
    old_to_merged: Dict[DFAState, DFAState] = {}

    merged_states: List[DFAState] = []
    for part in partitions:
        # Union all NFA states contained within the grouped DFA states
        combined_nfa_states = set()
        for d_state in part:
            combined_nfa_states.update(d_state)
        merged_state = frozenset(combined_nfa_states)
        part_to_merged[part] = merged_state
        merged_states.append(merged_state)
        for d_state in part:
            old_to_merged[d_state] = merged_state

    min_start = old_to_merged[dfa.start]
    min_accepts: List[DFAState] = []
    min_transitions: Dict[DFAState, Dict[Symbol, DFAState]] = {}

    for part in partitions:
        rep = next(iter(part))
        m_state = part_to_merged[part]

        if dfa.is_accepting(rep) and m_state not in min_accepts:
            min_accepts.append(m_state)

        min_transitions[m_state] = {}
        for sym in dfa.alphabet:
            nxt = dfa.get_transition(rep, sym)
            if nxt in old_to_merged:
                min_transitions[m_state][sym] = old_to_merged[nxt]

    min_dfa = DFA(
        states=merged_states,
        alphabet=list(dfa.alphabet),
        transitions=min_transitions,
        start=min_start,
        accepts=min_accepts,
    )

    log.append(
        f"Minimization complete: {len(dfa.states)} states reduced to {len(min_dfa.states)} states."
    )
    return min_dfa, log
