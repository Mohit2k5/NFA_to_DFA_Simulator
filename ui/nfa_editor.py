import json
from typing import List, Optional, Tuple
import pandas as pd
import streamlit as st
from engine.examples import EXAMPLES
from engine.models import NFA
from engine.validate import validate_nfa
from parsers.from_json import nfa_from_json, nfa_to_json
from parsers.from_table import nfa_to_table_rows, table_rows_to_nfa
from validation.test_cases import TestCase


def render_nfa_editor() -> Tuple[NFA, Optional[str], List[TestCase]]:
    """
    Renders the dynamic NFA editor panel with:
    - Preloaded examples selector
    - Transition-table editor (st.data_editor)
    - JSON import/export
    - Instant validation error feedback
    Returns (nfa, example_id_or_none, test_cases_list).
    """
    st.sidebar.header("⚙️ NFA Input & Configuration")

    # 1. Preset Examples Selector
    example_options = ["Custom NFA"] + [ex.name for ex in EXAMPLES.values()]
    example_map = {ex.name: ex.id for ex in EXAMPLES.values()}

    selected_example_name = st.sidebar.selectbox(
        "Choose an example or create custom:",
        options=example_options,
        index=1 if "ends_with_01" in EXAMPLES else 0,
        key="selected_example_dropdown",
    )

    # Track example changes
    if "last_selected_example" not in st.session_state:
        st.session_state["last_selected_example"] = selected_example_name

    if st.session_state["last_selected_example"] != selected_example_name:
        st.session_state["last_selected_example"] = selected_example_name
        st.session_state["step_index"] = 0
        st.session_state["is_playing"] = False
        st.session_state["custom_test_cases"] = []

        if selected_example_name != "Custom NFA":
            ex_id = example_map[selected_example_name]
            ex = EXAMPLES[ex_id]
            st.session_state["current_nfa"] = ex.nfa
            st.session_state["current_example_id"] = ex_id
            st.session_state["current_test_cases"] = list(ex.test_cases)
        st.rerun()

    # Load initial NFA if not set
    if "current_nfa" not in st.session_state:
        default_ex = EXAMPLES["ends_with_01"]
        st.session_state["current_nfa"] = default_ex.nfa
        st.session_state["current_example_id"] = "ends_with_01"
        st.session_state["current_test_cases"] = list(default_ex.test_cases)

    current_nfa: NFA = st.session_state["current_nfa"]
    example_id: Optional[str] = st.session_state.get("current_example_id")
    test_cases: List[TestCase] = st.session_state.get(
        "current_test_cases", []
    ) + st.session_state.get("custom_test_cases", [])

    # Sidebar JSON Import
    with st.sidebar.expander("📥 Import NFA from JSON", expanded=False):
        uploaded_file = st.file_uploader("Upload JSON file", type=["json"], key="nfa_json_upload")
        pasted_json = st.text_area("Or paste JSON:", height=120, key="nfa_json_paste")
        if st.button("Load JSON"):
            raw_text = ""
            if uploaded_file is not None:
                raw_text = uploaded_file.read().decode("utf-8")
            elif pasted_json.strip():
                raw_text = pasted_json.strip()

            if raw_text:
                try:
                    imported_nfa = nfa_from_json(raw_text)
                    is_valid, val_errs = validate_nfa(imported_nfa)
                    if not is_valid:
                        st.sidebar.error("Validation failed:\n" + "\n".join(val_errs))
                    else:
                        st.session_state["current_nfa"] = imported_nfa
                        st.session_state["current_example_id"] = None
                        st.session_state["current_test_cases"] = []
                        st.session_state["step_index"] = 0
                        st.session_state["is_playing"] = False
                        st.sidebar.success("NFA successfully imported!")
                        st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Failed to parse JSON: {e}")

    # Description of built-in example if active
    if example_id and example_id in EXAMPLES:
        st.sidebar.info(f"**About this example:**\n{EXAMPLES[example_id].description}")

    # Editable transition table in an expander or tab
    with st.sidebar.expander("✏️ Transition Table & State Editor", expanded=False):
        st.markdown("**Alphabet (comma-separated):**")
        alphabet_input = st.text_input(
            "Alphabet symbols",
            value=", ".join(current_nfa.alphabet),
            key="alphabet_str_input",
            label_visibility="collapsed",
        )
        new_alphabet = [s.strip() for s in alphabet_input.split(",") if s.strip()]

        table_rows = nfa_to_table_rows(current_nfa)
        df_table = pd.DataFrame(table_rows)

        st.markdown(
            "**Transitions:** Mark Start/Accept, specify comma-separated target states for each symbol (e.g. `q0, q1` or leave empty)."
        )
        edited_df = st.data_editor(
            df_table,
            num_rows="dynamic",
            use_container_width=True,
            key="nfa_data_editor",
        )

        if st.button("Apply Table Changes", type="primary"):
            new_rows = edited_df.to_dict(orient="records")
            parsed_nfa, tbl_errs = table_rows_to_nfa(new_rows, new_alphabet)
            is_val, val_errs = validate_nfa(parsed_nfa)
            all_errs = tbl_errs + val_errs

            if all_errs:
                st.sidebar.error("Errors found:\n" + "\n".join(f"• {err}" for err in all_errs))
            else:
                st.session_state["current_nfa"] = parsed_nfa
                st.session_state["current_example_id"] = None
                st.session_state["step_index"] = 0
                st.session_state["is_playing"] = False
                st.sidebar.success("Applied new NFA configuration!")
                st.rerun()

    return current_nfa, example_id, test_cases
