from typing import List, Tuple
from engine.models import NFA

EPSILON_SYMBOLS = {"ε", "e", "epsilon", "λ", "", "eps"}


def validate_nfa(nfa: NFA) -> Tuple[bool, List[str]]:
    """
    Validates an NFA definition against course constraints.
    Returns (is_valid, list_of_error_messages).
    """
    errors: List[str] = []

    if not nfa.states:
        errors.append("States list cannot be empty.")

    if not nfa.alphabet:
        errors.append("Alphabet cannot be empty.")

    # Check for epsilon in alphabet
    for sym in nfa.alphabet:
        if sym.strip() in EPSILON_SYMBOLS:
            errors.append(
                f"Epsilon transition symbol '{sym}' is not supported. "
                "This simulator handles plain NFAs only (no ε-transitions)."
            )
        if not sym.strip():
            errors.append("Empty or whitespace symbol is not allowed in alphabet.")

    # Check start state
    if not nfa.start:
        errors.append("Start state must be specified.")
    elif nfa.start not in nfa.states:
        errors.append(f"Start state '{nfa.start}' is not in the states list {nfa.states}.")

    # Check accept states
    states_set = set(nfa.states)
    for acc in nfa.accepts:
        if acc not in states_set:
            errors.append(f"Accept state '{acc}' is not in the states list {nfa.states}.")

    # Check transitions
    alphabet_set = set(nfa.alphabet)
    for src, sym_map in nfa.transitions.items():
        if src not in states_set:
            errors.append(f"Transition source state '{src}' is not in states list.")
        for sym, targets in sym_map.items():
            if sym.strip() in EPSILON_SYMBOLS:
                errors.append(
                    f"Transition from state '{src}' on '{sym}' contains an epsilon transition. "
                    "Plain NFAs only."
                )
            elif sym not in alphabet_set:
                errors.append(f"Transition symbol '{sym}' from state '{src}' is not in the alphabet {nfa.alphabet}.")

            if not isinstance(targets, list):
                errors.append(f"Targets for state '{src}' on symbol '{sym}' must be a list.")
            else:
                for tgt in targets:
                    if tgt not in states_set:
                        errors.append(
                            f"Target state '{tgt}' in transition from '{src}' on '{sym}' is not in states list."
                        )

    return len(errors) == 0, errors
