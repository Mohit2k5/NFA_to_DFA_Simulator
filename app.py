import streamlit as st
from engine.models import DFAState, format_state_set
from engine.subset import subset_construction
from engine.validate import validate_nfa
from ui.explanation import render_step_explanation
from ui.graph_view import dfa_to_dot, nfa_to_dot
from ui.nfa_editor import render_nfa_editor
from ui.result_panel import render_result_panel
from ui.step_controls import render_step_controls
from ui.string_tester import render_string_tester
from ui.tables import build_dfa_table_df, build_nfa_table_df
from ui.validation_panel import render_validation_panel


def main():
    st.set_page_config(
        page_title="NFA → DFA Simulator | CSET302",
        page_icon="🔄",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Header
    st.title("🔄 NFA → DFA Conversion Simulator")
    st.markdown(
        "**Course:** CSET302 – Automata Theory and Computability &nbsp;|&nbsp; "
        "**Algorithm:** Subset Construction (Plain NFAs without ε-transitions)"
    )
    st.markdown("---")

    # Sidebar: Input Panel
    nfa, example_id, test_cases = render_nfa_editor()

    # Validate input NFA
    is_valid, errors = validate_nfa(nfa)
    if not is_valid:
        st.error("### ⚠️ Invalid NFA Configuration")
        for err in errors:
            st.markdown(f"- {err}")
        return

    # Run Algorithm Engine
    try:
        dfa, trace = subset_construction(nfa)
    except ValueError as val_err:
        st.error(f"⚠️ Subset Construction Aborted: {val_err}")
        return

    # Clamp step_index
    if "step_index" not in st.session_state:
        st.session_state["step_index"] = 0
    st.session_state["step_index"] = max(
        0, min(st.session_state["step_index"], len(trace) - 1)
    )
    curr_step_idx = st.session_state["step_index"]
    current_step = trace[curr_step_idx]

    # Section 1: Step Controls & Explanation
    st.markdown("### ⏯️ Step-by-Step Conversion Walkthrough")
    render_step_explanation(current_step, curr_step_idx, len(trace))
    render_step_controls(len(trace))

    st.markdown("---")

    # Section 2: Side-by-Side Visualization
    st.markdown("### 🗺️ Automata Visualizations")
    col_nfa, col_dfa = st.columns(2)

    # Progressive snapshots from current trace step
    active_nfa = current_step.active_nfa_states or []
    visible_dfa_states = current_step.discovered_states
    visible_dfa_trans = current_step.discovered_transitions
    active_dfa_state = current_step.dfa_state

    # Compute active edge if current step is MOVE
    active_dfa_edge = None
    if current_step.type in ("MOVE", "NEW_STATE", "EXISTING_STATE"):
        if current_step.dfa_state is not None and current_step.moved is not None and current_step.symbol:
            active_dfa_edge = (current_step.dfa_state, current_step.moved, current_step.symbol)

    with col_nfa:
        st.markdown("#### Input NFA")
        nfa_dot = nfa_to_dot(nfa, active_states=active_nfa)
        st.graphviz_chart(nfa_dot, use_container_width=True)

        with st.expander("📋 View NFA Transition Table", expanded=False):
            st.dataframe(build_nfa_table_df(nfa), use_container_width=True, hide_index=True)

    with col_dfa:
        st.markdown("#### Generated DFA (Subset Construction)")
        hide_trap = st.checkbox("Hide dead/trap state (∅)", value=False, key="hide_trap_toggle")

        dfa_dot = dfa_to_dot(
            dfa,
            active_state=active_dfa_state,
            active_edge=active_dfa_edge,
            visible_states=visible_dfa_states,
            visible_transitions=visible_dfa_trans,
            hide_trap=hide_trap,
        )
        st.graphviz_chart(dfa_dot, use_container_width=True)

        with st.expander("📋 View Progressive DFA Transition Table", expanded=False):
            st.dataframe(
                build_dfa_table_df(dfa, visible_states=visible_dfa_states, visible_transitions=visible_dfa_trans),
                use_container_width=True,
                hide_index=True,
            )

    st.markdown("---")

    # Section 3: Interactive String Tester
    render_string_tester(nfa, dfa)

    st.markdown("---")

    # Section 4: Result Summary & Multi-Layer Validation
    render_result_panel(nfa, dfa)

    st.markdown("---")

    render_validation_panel(
        nfa=nfa,
        dfa=dfa,
        example_id=example_id,
        current_test_cases=test_cases,
    )


if __name__ == "__main__":
    main()
