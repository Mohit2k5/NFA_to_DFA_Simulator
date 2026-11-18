from collections import deque
from typing import Any, Dict, List, Set, Tuple
from engine.models import DFA, DFAState, format_state_set


def check_dfa_isomorphism(
    gen_dfa: DFA, golden_dfa: DFA
) -> Tuple[bool, Dict[DFAState, Any], List[str]]:
    """
    Checks if gen_dfa and golden_dfa are isomorphic under reachable state bijection.
    Returns (is_isomorphic, state_mapping, list_of_differences).
    """
    differences: List[str] = []

    # Check alphabet consistency
    if set(gen_dfa.alphabet) != set(golden_dfa.alphabet):
        differences.append(
            f"Alphabets differ: Generated {set(gen_dfa.alphabet)} vs Golden {set(golden_dfa.alphabet)}"
        )
        return False, {}, differences

    # Mapping: gen_state -> golden_state
    gen_to_golden: Dict[DFAState, Any] = {}
    golden_to_gen: Dict[Any, DFAState] = {}

    queue = deque([(gen_dfa.start, golden_dfa.start)])
    gen_to_golden[gen_dfa.start] = golden_dfa.start
    golden_to_gen[golden_dfa.start] = gen_dfa.start

    visited_pairs: Set[Tuple[DFAState, Any]] = set()

    alphabet = sorted(list(gen_dfa.alphabet))

    while queue:
        curr_gen, curr_golden = queue.popleft()
        pair = (curr_gen, curr_golden)
        if pair in visited_pairs:
            continue
        visited_pairs.add(pair)

        # Check accepting status
        gen_acc = gen_dfa.is_accepting(curr_gen)
        golden_acc = golden_dfa.is_accepting(curr_golden)
        if gen_acc != golden_acc:
            differences.append(
                f"Accepting mismatch: Generated state '{format_state_set(curr_gen)}' "
                f"(accepting={gen_acc}) maps to Golden state '{curr_golden}' "
                f"(accepting={golden_acc})."
            )

        # Explore transitions for all symbols
        for sym in alphabet:
            tgt_gen = gen_dfa.get_transition(curr_gen, sym)
            tgt_golden = golden_dfa.get_transition(curr_golden, sym)

            # In DFA, missing transition is equivalent to empty set trap state
            if tgt_gen is None:
                tgt_gen = frozenset()
            if tgt_golden is None:
                tgt_golden = frozenset() if isinstance(golden_dfa.start, frozenset) else "TRAP"

            # Check mapping consistency
            if tgt_gen in gen_to_golden:
                if gen_to_golden[tgt_gen] != tgt_golden:
                    differences.append(
                        f"Non-deterministic mapping conflict on symbol '{sym}': "
                        f"Generated state '{format_state_set(tgt_gen)}' already mapped to "
                        f"'{gen_to_golden[tgt_gen]}', but Golden reached '{tgt_golden}'."
                    )
            elif tgt_golden in golden_to_gen:
                if golden_to_gen[tgt_golden] != tgt_gen:
                    differences.append(
                        f"Injective mapping conflict on symbol '{sym}': "
                        f"Golden state '{tgt_golden}' already mapped to "
                        f"'{format_state_set(golden_to_gen[tgt_golden])}', but Generated reached '{format_state_set(tgt_gen)}'."
                    )
            else:
                gen_to_golden[tgt_gen] = tgt_golden
                golden_to_gen[tgt_golden] = tgt_gen
                queue.append((tgt_gen, tgt_golden))

    # Check total state counts
    if len(gen_to_golden) != len(golden_dfa.states):
        differences.append(
            f"State count mismatch: Mapped {len(gen_to_golden)} reachable states, "
            f"while Golden DFA has {len(golden_dfa.states)} states."
        )

    is_isomorphic = len(differences) == 0
    return is_isomorphic, gen_to_golden, differences
