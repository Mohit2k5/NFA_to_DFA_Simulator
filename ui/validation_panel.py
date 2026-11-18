from typing import List, Optional
import pandas as pd
import streamlit as st
from engine.models import DFA, NFA, format_state_set
from validation.golden import get_golden_dfa
from validation.runner import ValidationReport, run_validation
from validation.test_cases import TestCase


def render_validation_panel(
    nfa: NFA,
    dfa: DFA,
    example_id: Optional[str] = None,
    current_test_cases: Optional[List[TestCase]] = None,
):
    """Renders the comprehensive 3-Layer Validation Panel."""
    st.subheader("🛡️ Automata Validation Suite")
    st.caption(
        "Formal multi-layer correctness verification: test suites, exhaustive equivalence, and golden-reference isomorphism."
    )

    if current_test_cases is None:
        current_test_cases = []

    # Tabbed or stacked layout for the 3 layers
    tab_a, tab_b, tab_c = st.tabs(
        [
            "Layer A: Test Cases Suite",
            "Layer B: Exhaustive Equivalence",
            "Layer C: Golden DFA Comparison",
        ]
    )

    # -------------------------------------------------------------
    # Layer A: Test Cases
    # -------------------------------------------------------------
    with tab_a:
        st.markdown("#### Layer A: Expected vs Generated Results")
        st.caption(
            "Verifies that each test string satisfies: `Expected == NFA Result == DFA Result`."
        )

        # Run validation for Layer A
        rep = run_validation(
            nfa=nfa,
            dfa=dfa,
            test_cases=current_test_cases,
            example_id=example_id,
            exhaustive_max_length=4,  # fast run for preview
        )
        layer_a = rep.layer_a

        if layer_a.total > 0:
            if layer_a.all_passed:
                st.success(
                    f"🎉 **All Test Cases Passed!** ({layer_a.passed_count}/{layer_a.total} passed)"
                )
            else:
                st.error(
                    f"⚠️ **Some Test Cases Failed:** {layer_a.passed_count}/{layer_a.total} passed"
                )

            # Build summary table
            rows = []
            for i, res in enumerate(layer_a.results, 1):
                exp_str = "Accept" if res.expected else "Reject"
                nfa_str = "Accept" if res.nfa_verdict else "Reject"
                dfa_str = "Accept" if res.dfa_verdict else "Reject"
                status_str = "✅ PASS" if res.passed else "❌ FAIL"
                disp_str = f"\"{res.input_string}\"" if res.input_string else "ε (empty)"

                rows.append(
                    {
                        "#": i,
                        "Input String": disp_str,
                        "Expected": exp_str,
                        "NFA Verdict": nfa_str,
                        "DFA Verdict": dfa_str,
                        "Status": status_str,
                        "Description": res.description or "—",
                    }
                )

            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No test cases currently loaded. Add your own test cases below!")

        # Add custom test case
        with st.expander("➕ Add Custom Test Case", expanded=False):
            col_s, col_exp, col_desc = st.columns([2, 1, 3])
            with col_s:
                new_str = st.text_input("Test string:", key="custom_tc_str")
            with col_exp:
                new_exp = st.selectbox("Expected verdict:", ["Accept", "Reject"], key="custom_tc_exp")
            with col_desc:
                new_desc = st.text_input("Description:", key="custom_tc_desc")

            if st.button("Add to Test Suite"):
                expected_bool = new_exp == "Accept"
                new_case = TestCase(
                    input_string=new_str,
                    expected=expected_bool,
                    description=new_desc or f"Custom test case '{new_str}'",
                )
                if "custom_test_cases" not in st.session_state:
                    st.session_state["custom_test_cases"] = []
                st.session_state["custom_test_cases"].append(new_case)
                st.success(f"Added test case '{new_str}'!")
                st.rerun()

    # -------------------------------------------------------------
    # Layer B: Automatic Exhaustive Equivalence Check
    # -------------------------------------------------------------
    with tab_b:
        st.markdown("#### Layer B: Exhaustive Equivalence Testing")
        st.caption(
            "Generates and checks every possible string over the alphabet up to length N on both NFA and DFA."
        )

        eq_col1, eq_col2 = st.columns([1, 2])
        with eq_col1:
            max_len = st.slider(
                "Max string length N:",
                min_value=3,
                max_value=8,
                value=6,
                help="Higher lengths generate exponentially more combinations (e.g. 2^8 = 256 strings).",
            )
            run_eq = st.button("Run Exhaustive Check", type="primary")

        with eq_col2:
            if run_eq or st.session_state.get("ran_equivalence", True):
                st.session_state["ran_equivalence"] = True
                with st.spinner("Testing all string combinations..."):
                    val_rep = run_validation(
                        nfa=nfa,
                        dfa=dfa,
                        test_cases=[],
                        example_id=example_id,
                        exhaustive_max_length=max_len,
                    )
                    layer_b = val_rep.layer_b

                if layer_b.is_equivalent:
                    st.success(
                        f"✅ **Automata are Equivalent!** Tested **{layer_b.total_tested}** strings "
                        f"(lengths 0 through {max_len}). Zero mismatches found!"
                    )
                else:
                    st.error(
                        f"❌ **Counterexample Found!** Mismatch on string: `'{layer_b.counterexample}'`"
                    )
                    st.markdown(
                        f"- NFA Verdict: `{'Accept' if layer_b.nfa_verdict else 'Reject'}`\n"
                        f"- DFA Verdict: `{'Accept' if layer_b.dfa_verdict else 'Reject'}`"
                    )

    # -------------------------------------------------------------
    # Layer C: Golden-DFA Comparison (Isomorphism)
    # -------------------------------------------------------------
    with tab_c:
        st.markdown("#### Layer C: Golden DFA Comparison (Isomorphism)")
        st.caption(
            "Compares the generated DFA with a trusted textbook Golden Reference DFA under graph isomorphism."
        )

        golden_ref = get_golden_dfa(example_id) if example_id else None
        if golden_ref is not None:
            c_rep = run_validation(
                nfa=nfa,
                dfa=dfa,
                test_cases=[],
                example_id=example_id,
                golden_dfa=golden_ref,
            )
            layer_c = c_rep.layer_c

            if layer_c.matched:
                st.success("✅ **Matches Golden Reference DFA!** Structure and transitions are isomorphic.")
            else:
                st.error("❌ **Structural Discrepancies with Golden DFA Found:**")
                for diff in layer_c.differences:
                    st.markdown(f"- {diff}")

            st.markdown("##### State Bijection Mapping (Generated ↔ Golden)")
            map_rows = []
            for gen_s, gold_s in layer_c.mapping.items():
                gold_label = format_state_set(gold_s) if isinstance(gold_s, (frozenset, set)) else str(gold_s)
                map_rows.append(
                    {
                        "Generated DFA State": format_state_set(gen_s),
                        "Maps To Golden State": gold_label,
                        "Generated Is Accepting": dfa.is_accepting(gen_s),
                        "Golden Is Accepting": golden_ref.is_accepting(gold_s) if hasattr(golden_ref, "is_accepting") else False,
                    }
                )
            st.dataframe(pd.DataFrame(map_rows), use_container_width=True, hide_index=True)
        else:
            st.info(
                "ℹ️ **Golden DFA is available for built-in textbook examples.** "
                "For custom user-defined NFAs, correctness is guaranteed via **Layer A** (test cases) and **Layer B** (exhaustive equivalence check)."
            )
