import time
import streamlit as st


def render_step_controls(total_steps: int):
    """
    Renders step navigation controls: First, Prev, Play/Pause, Next, End, Reset,
    and a step slider for direct seeking.
    """
    if "step_index" not in st.session_state:
        st.session_state["step_index"] = 0
    if "is_playing" not in st.session_state:
        st.session_state["is_playing"] = False

    curr_step = st.session_state["step_index"]

    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1.2, 1, 1, 1.2])

    with col1:
        if st.button("⏮ First", disabled=(curr_step == 0), use_container_width=True):
            st.session_state["step_index"] = 0
            st.session_state["is_playing"] = False
            st.rerun()

    with col2:
        if st.button("◀ Prev", disabled=(curr_step == 0), use_container_width=True):
            st.session_state["step_index"] = max(0, curr_step - 1)
            st.session_state["is_playing"] = False
            st.rerun()

    with col3:
        play_label = "⏸ Pause" if st.session_state["is_playing"] else "▶ Play"
        if st.button(play_label, disabled=(curr_step >= total_steps - 1 and not st.session_state["is_playing"]), use_container_width=True):
            st.session_state["is_playing"] = not st.session_state["is_playing"]
            st.rerun()

    with col4:
        if st.button("Next ▶", disabled=(curr_step >= total_steps - 1), use_container_width=True):
            st.session_state["step_index"] = min(total_steps - 1, curr_step + 1)
            st.session_state["is_playing"] = False
            st.rerun()

    with col5:
        if st.button("⏭ End", disabled=(curr_step >= total_steps - 1), use_container_width=True):
            st.session_state["step_index"] = total_steps - 1
            st.session_state["is_playing"] = False
            st.rerun()

    with col6:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state["step_index"] = 0
            st.session_state["is_playing"] = False
            st.rerun()

    speed_col, slider_col = st.columns([1.2, 2.8])
    with speed_col:
        play_speed = st.slider(
            "Auto-play delay (sec)",
            min_value=0.2,
            max_value=2.0,
            value=0.7,
            step=0.1,
            label_visibility="collapsed",
            help="Playback speed in seconds per step",
        )
    with slider_col:
        new_step = st.slider(
            "Jump to step",
            min_value=0,
            max_value=total_steps - 1,
            value=curr_step,
            label_visibility="collapsed",
            help="Drag to jump to any step in the subset construction trace",
        )
        if new_step != curr_step:
            st.session_state["step_index"] = new_step
            st.session_state["is_playing"] = False
            st.rerun()

    # Handle auto-play cycle
    if st.session_state["is_playing"]:
        if curr_step < total_steps - 1:
            time.sleep(play_speed)
            st.session_state["step_index"] = curr_step + 1
            st.rerun()
        else:
            st.session_state["is_playing"] = False
            st.rerun()
