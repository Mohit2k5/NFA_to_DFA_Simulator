import streamlit as st
from engine.models import TraceStep, format_state_set


def render_step_explanation(step: TraceStep, step_index: int, total_steps: int):
    """Renders a styled explanation card for the current step in the subset construction trace."""
    badge_colors = {
        "START": ("#0D6EFD", "🚀 Initial Start State"),
        "PICK_STATE": ("#6F42C1", "🔍 State Expansion"),
        "MOVE": ("#0DCAF0", "⚡ Computing Move"),
        "NEW_STATE": ("#198754", "✨ New DFA State Discovered"),
        "EXISTING_STATE": ("#6C757D", "🔗 Existing State Linked"),
        "MARK_ACCEPT": ("#FFC107", "★ Accept States Marking"),
        "DONE": ("#20C997", "🎉 Construction Complete"),
    }

    color, title = badge_colors.get(step.type, ("#6C757D", f"Step: {step.type}"))

    st.markdown(
        f"""
        <div style="border-left: 5px solid {color}; padding: 10px 16px; background-color: rgba(240, 242, 246, 0.5); border-radius: 4px; margin-bottom: 12px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="font-weight: 700; color: {color}; font-size: 1.05rem;">{title}</span>
                <span style="font-size: 0.85rem; color: #6C757D; font-weight: 600;">Step {step_index + 1} of {total_steps}</span>
            </div>
            <div style="font-size: 0.95rem; line-height: 1.5; color: #212529;">
                {step.explanation}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
