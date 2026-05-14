import streamlit as st
from core.orchestrator import send_message, end_session

PHASE_LABELS = {
    "opening": "פתיחה",
    "evidence": "הצגת הוכחות",
    "examination": "חקירת עדים",
    "arguments": "הצגת טענות",
    "cross": "חקירה נגדית",
    "closing": "סיכומים",
    "ruling": "גזר דין",
    "judgment": "פסק דין",
}

SPEAKER_STYLE = {
    "judge":    ("🔵", "#1a3a6b", "שופט"),
    "attorney": ("🔴", "#6b1a1a", "עו\"ד"),
    "user":     ("⚪", "#3a3a3a", "אתה"),
}


def _render_message(msg: dict):
    role = msg.get("role", "user")
    emoji, color, label = SPEAKER_STYLE.get(role, SPEAKER_STYLE["user"])
    st.markdown(
        f"""<div style="background:{color}22; border-right:4px solid {color};
        padding:10px 14px; margin:6px 0; border-radius:6px; direction:rtl;">
        <strong>{emoji} {label}:</strong> {msg["content"]}</div>""",
        unsafe_allow_html=True,
    )


def render():
    phase = st.session_state.get("phase", "opening")
    case = st.session_state.get("case", {})
    personas = st.session_state.get("personas", {})
    messages = st.session_state.get("messages", [])

    judge_display = case.get("judge_name") or "שופט"
    phase_label = PHASE_LABELS.get(phase, phase)
    st.subheader(f"שלב: {phase_label} | שופט: {judge_display}")
    st.markdown("---")

    for msg in messages:
        _render_message(msg)

    st.markdown("---")
    user_input = st.text_area("הטענה שלך:", key="user_input_area", height=100)

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        if st.button("שלח ▶", type="primary"):
            if user_input.strip():
                messages.append({"role": "user", "content": user_input.strip()})
                result = send_message(
                    user_input=user_input.strip(),
                    messages=messages,
                    phase=phase,
                    case=case,
                    personas=personas,
                )
                messages.append(result["judge_response"])
                messages.append(result["attorney_response"])
                st.session_state["messages"] = messages
                st.session_state["phase"] = result["new_phase"]
                st.rerun()

    with col2:
        if st.button("סיים דיון 🔚"):
            debrief = end_session(messages)
            st.session_state["debrief"] = debrief
            st.session_state["screen"] = "debrief"
            st.rerun()

    with col3:
        if st.button("התחל מחדש 🔄"):
            for key in ["case", "personas", "phase", "messages", "debrief"]:
                st.session_state.pop(key, None)
            st.session_state["screen"] = "setup"
            st.rerun()
