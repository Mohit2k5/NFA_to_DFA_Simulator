from typing import Optional, Tuple
import streamlit as st
from engine.models import DFA, DFAState, FrozenSet, NFA, State, format_state_set
from engine.simulate import simulate_dfa, simulate_nfa


def render_string_tester(
    nfa: NFA, dfa: DFA
) -> Tuple[Optional[FrozenSet[State]], Optional[DFAState]]:
    """
    Renders the interactive String Tester component.
    Returns (active_nfa_states_for_graph, active_dfa_state_for_graph).
    """
    st.subheader("🧪 Interactive String Tester")
    st.caption("Test any string over the alphabet on both the NFA and DFA simultaneously.")

    alphabet_hint = ", ".join(f"'{a}'" for a in nfa.alphabet)

    col_in, col_btn = st.columns([3, 1])
    with col_in:
        test_input = st.text_input(
            "Input string (empty string ε allowed):",
            value=st.session_state.get("current_test_string", ""),
            placeholder=f"Enter string over {alphabet_hint}...",
            key="string_tester_input",
        )
    with col_btn:
        st.write("")  # alignment
        st.write("")
        run_clicked = st.button("Run Test", type="primary", use_container_width=True)

    if run_clicked or test_input != st.session_state.get("last_tested_string", None):
        st.session_state["last_tested_string"] = test_input
        st.session_state["string_step_index"] = len(test_input)

    # Run simulations
    nfa_acc, nfa_path, nfa_err = simulate_nfa(nfa, test_input)
    dfa_acc, dfa_path, dfa_err = simulate_dfa(dfa, test_input)

    if nfa_err or dfa_err:
        st.error(nfa_err or dfa_err)
        return None, None

    # Step slider for string character traversal
    if len(test_input) > 0:
        str_step = st.slider(
            "Character-by-character trace position:",
            min_value=0,
            max_value=len(test_input),
            value=st.session_state.get("string_step_index", len(test_input)),
            help="Step through the string character by character to observe active state transitions.",
            key="string_slider",
        )
        st.session_state["string_step_index"] = str_step
    else:
        str_step = 0

    active_nfa_states = nfa_path[str_step] if str_step < len(nfa_path) else nfa_path[-1]
    active_dfa_state = dfa_path[str_step] if str_step < len(dfa_path) else dfa_path[-1]

    # Verdict display
    v_col1, v_col2, v_col3 = st.columns(3)

    with v_col1:
        if nfa_acc:
            st.success("##### NFA Verdict: ✅ ACCEPT")
        else:
            st.error("##### NFA Verdict: ❌ REJECT")
        st.caption(f"Final active subset: `{format_state_set(nfa_path[-1])}`")

    with v_col2:
        if dfa_acc:
            st.success("##### DFA Verdict: ✅ ACCEPT")
        else:
            st.error("##### DFA Verdict: ❌ REJECT")
        st.caption(f"Final DFA state: `{format_state_set(dfa_path[-1])}`")

    with v_col3:
        if nfa_acc == dfa_acc:
            st.info("##### Agreement: 🎯 MATCH")
            st.caption("Both automata produce identical acceptance verdicts.")
        else:
            st.warning("##### Agreement: ⚠️ MISMATCH")
            st.caption("Discrepancy detected between NFA and DFA results!")

    # Path breakdown
    with st.expander("🔍 View Detailed Step-by-Step Execution Paths", expanded=False):
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            st.markdown("**NFA Active States Path:**")
            path_strs = []
            for i, st_set in enumerate(nfa_path):
                char_label = f" --('{test_input[i-1]}')--> " if i > 0 else "Start: "
                curr_mark = " 📍" if i == str_step else ""
                path_strs.append(f"{char_label}`{format_state_set(st_set)}`{curr_mark}")
            st.markdown("\n\n".join(path_strs))

        with p_col2:
            st.markdown("**DFA Active State Path:**")
            path_strs_dfa = []
            for i, st_state in enumerate(dfa_path):
                char_label = f" --('{test_input[i-1]}')--> " if i > 0 else "Start: "
                curr_mark = " 📍" if i == str_step else ""
                path_strs_dfa.append(f"{char_label}`{format_state_set(st_state)}`{curr_mark}")
            st.markdown("\n\n".join(path_strs_dfa))

    return active_nfa_states, active_dfa_state
