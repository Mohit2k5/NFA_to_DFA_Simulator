from typing import Optional
import streamlit as st
from engine.minimize import minimize_dfa
from engine.models import DFA, NFA, format_state_set
from parsers.from_json import dfa_to_json, nfa_to_json
from ui.graph_view import dfa_to_dot
from ui.tables import build_dfa_table_df


def dfa_to_tikz(dfa: DFA) -> str:
    """Generates LaTeX TikZ automata code for the DFA."""
    lines = [
        r"\begin{tikzpicture}[shorten >=1pt, node distance=2.5cm, on grid, auto]",
        r"  \tikzstyle{every state}=[fill=white,draw=black,text=black]",
    ]

    accept_set = set(dfa.accepts)
    state_names = {s: f"q_{i}" for i, s in enumerate(dfa.states)}

    for s, name in state_names.items():
        is_acc = s in accept_set
        is_start = s == dfa.start
        styles = []
        if is_acc:
            styles.append("accepting")
        if is_start:
            styles.append("initial")
        style_str = f"state,{','.join(styles)}" if styles else "state"
        clean_label = format_state_set(s).replace("{", r"\{").replace("}", r"\}")
        lines.append(f"  \\node[{style_str}] ({name}) {{{clean_label}}};")

    lines.append(r"  \path[->]")
    for src, sym_map in dfa.transitions.items():
        src_name = state_names[src]
        for sym, tgt in sym_map.items():
            tgt_name = state_names[tgt]
            if src_name == tgt_name:
                lines.append(f"    ({src_name}) edge [loop above] node {{{sym}}} ({tgt_name})")
            else:
                lines.append(f"    ({src_name}) edge node {{{sym}}} ({tgt_name})")
    lines.append(r"  ;")
    lines.append(r"\end{tikzpicture}")
    return "\n".join(lines)


def render_result_panel(nfa: NFA, dfa: DFA):
    """Renders the comprehensive Result and Summary panel."""
    st.subheader("📊 Conversion Result & Summary")

    nfa_count = len(nfa.states)
    dfa_count = len(dfa.states)
    has_trap = any(len(s) == 0 for s in dfa.states)
    acc_count = len(dfa.accepts)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("NFA States", nfa_count)
    c2.metric("DFA States", dfa_count, delta=f"{dfa_count - nfa_count} change")
    c3.metric("DFA Accept States", acc_count)
    c4.metric("Trap State (∅)", "Generated" if has_trap else "None")

    st.markdown("#### Generated DFA Transition Table")
    dfa_df = build_dfa_table_df(dfa)
    st.dataframe(dfa_df, use_container_width=True, hide_index=True)

    # DFA Minimization (Stretch goal)
    with st.expander("✂️ DFA Minimization (Hopcroft / Partition Refinement)", expanded=False):
        st.markdown(
            "Check if any generated DFA states are equivalent and can be merged into a minimal DFA."
        )
        min_dfa, log = minimize_dfa(dfa)

        m_col1, m_col2 = st.columns([1, 2])
        with m_col1:
            st.metric("Original DFA States", len(dfa.states))
            st.metric("Minimized DFA States", len(min_dfa.states))
            if len(min_dfa.states) < len(dfa.states):
                st.success(f"Reduced by {len(dfa.states) - len(min_dfa.states)} redundant states!")
            else:
                st.info("The generated DFA is already in its minimal canonical form.")

        with m_col2:
            st.markdown("**Minimization Refinement Log:**")
            for entry in log:
                st.caption(f"• {entry}")

        st.markdown("**Minimized DFA Transition Table:**")
        st.dataframe(build_dfa_table_df(min_dfa), use_container_width=True, hide_index=True)
        st.markdown("**Minimized DFA Graph:**")
        st.graphviz_chart(dfa_to_dot(min_dfa), use_container_width=True)

    # Exports
    with st.expander("💾 Export Options (JSON, Graphviz DOT, LaTeX/TikZ)", expanded=False):
        e_col1, e_col2, e_col3 = st.columns(3)

        with e_col1:
            dfa_json_data = dfa_to_json(dfa)
            st.download_button(
                label="📥 Download DFA JSON",
                data=dfa_json_data,
                file_name="generated_dfa.json",
                mime="application/json",
                use_container_width=True,
            )

        with e_col2:
            nfa_json_data = nfa_to_json(nfa)
            st.download_button(
                label="📥 Download NFA JSON",
                data=nfa_json_data,
                file_name="nfa.json",
                mime="application/json",
                use_container_width=True,
            )

        with e_col3:
            dot_str = dfa_to_dot(dfa)
            st.download_button(
                label="📥 Download DOT Script",
                data=dot_str,
                file_name="dfa_graph.dot",
                mime="text/vnd.graphviz",
                use_container_width=True,
            )

        st.markdown("**LaTeX / TikZ Code snippet:**")
        tikz_code = dfa_to_tikz(dfa)
        st.code(tikz_code, language="latex")
