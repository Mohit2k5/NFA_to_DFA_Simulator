from collections import deque
from typing import Dict, List, Tuple
from engine.models import DFA, DFAState, NFA, Symbol, TraceStep, format_state_set
from engine.move import move


def subset_construction(nfa: NFA, max_states: int = 64) -> Tuple[DFA, List[TraceStep]]:
    """
    Converts a plain NFA to an equivalent DFA using the subset construction algorithm.
    Returns (DFA, List[TraceStep]).
    Raises ValueError if state count exceeds max_states to protect against exponential blow-up.
    """
    start_state: DFAState = frozenset([nfa.start])
    dfa_states: List[DFAState] = [start_state]
    unmarked = deque([start_state])
    transitions: Dict[DFAState, Dict[Symbol, DFAState]] = {}

    trace: List[TraceStep] = []

    def make_snapshot() -> Dict[DFAState, Dict[Symbol, DFAState]]:
        return {s: dict(targets) for s, targets in transitions.items()}

    trace.append(
        TraceStep(
            type="START",
            dfa_state=start_state,
            explanation=f"Initial DFA start state created from NFA start state: {format_state_set(start_state)}.",
            active_nfa_states=[nfa.start],
            discovered_states=list(dfa_states),
            discovered_transitions=make_snapshot(),
        )
    )

    while unmarked:
        t_state: DFAState = unmarked.popleft()
        transitions[t_state] = {}

        trace.append(
            TraceStep(
                type="PICK_STATE",
                dfa_state=t_state,
                explanation=f"Expanding DFA state {format_state_set(t_state)}. Checking transitions on all alphabet symbols {nfa.alphabet}.",
                active_nfa_states=sorted(list(t_state)),
                discovered_states=list(dfa_states),
                discovered_transitions=make_snapshot(),
            )
        )

        for sym in nfa.alphabet:
            u_state: DFAState = move(nfa, t_state, sym)

            trace.append(
                TraceStep(
                    type="MOVE",
                    dfa_state=t_state,
                    symbol=sym,
                    moved=u_state,
                    explanation=(
                        f"move({format_state_set(t_state)}, '{sym}') = "
                        f"⋃ {{ transitions(q, '{sym}') for q in {format_state_set(t_state)} }} = "
                        f"{format_state_set(u_state)}."
                        + (" (Empty set / Trap state)" if not u_state else "")
                    ),
                    active_nfa_states=sorted(list(u_state)) if u_state else [],
                    discovered_states=list(dfa_states),
                    discovered_transitions=make_snapshot(),
                )
            )

            is_new = u_state not in dfa_states
            if is_new:
                if len(dfa_states) >= max_states:
                    raise ValueError(
                        f"State limit of {max_states} states reached during subset construction! "
                        "Aborting to avoid exponential state blow-up."
                    )
                dfa_states.append(u_state)
                unmarked.append(u_state)
                transitions[t_state][sym] = u_state

                trace.append(
                    TraceStep(
                        type="NEW_STATE",
                        dfa_state=u_state,
                        symbol=sym,
                        moved=u_state,
                        explanation=f"{format_state_set(u_state)} is a NEW DFA state! Added to the set of DFA states and queue.",
                        active_nfa_states=sorted(list(u_state)) if u_state else [],
                        discovered_states=list(dfa_states),
                        discovered_transitions=make_snapshot(),
                    )
                )
            else:
                transitions[t_state][sym] = u_state
                trace.append(
                    TraceStep(
                        type="EXISTING_STATE",
                        dfa_state=u_state,
                        symbol=sym,
                        moved=u_state,
                        explanation=f"{format_state_set(u_state)} already exists in the DFA. Linked transition ({format_state_set(t_state)}, '{sym}') -> {format_state_set(u_state)}.",
                        active_nfa_states=sorted(list(u_state)) if u_state else [],
                        discovered_states=list(dfa_states),
                        discovered_transitions=make_snapshot(),
                    )
                )

    accepts: List[DFAState] = [s for s in dfa_states if any(q in nfa.accepts for q in s)]

    trace.append(
        TraceStep(
            type="MARK_ACCEPT",
            explanation=(
                f"Marking accepting states: Any DFA subset containing at least one NFA accept state "
                f"{set(nfa.accepts)} is accepting. "
                f"Accepting DFA states ({len(accepts)}): {[format_state_set(s) for s in accepts]}."
            ),
            discovered_states=list(dfa_states),
            discovered_transitions=make_snapshot(),
        )
    )

    trace.append(
        TraceStep(
            type="DONE",
            explanation=f"Subset construction complete! Final DFA has {len(dfa_states)} state(s) and {len(accepts)} accepting state(s).",
            discovered_states=list(dfa_states),
            discovered_transitions=make_snapshot(),
        )
    )

    dfa = DFA(
        states=dfa_states,
        alphabet=list(nfa.alphabet),
        transitions=transitions,
        start=start_state,
        accepts=accepts,
    )
    return dfa, trace
