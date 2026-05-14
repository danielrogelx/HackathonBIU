import streamlit as st
from core.orchestrator import send_message, end_session

PHASE_LABELS = {
    "opening":   "פתיחה",
    "evidence":  "הצגת הוכחות",
    "examination": "חקירת עדים",
    "arguments": "הצגת טענות",
    "cross":     "חקירה נגדית",
    "closing":   "סיכומים",
    "ruling":    "גזר דין",
    "judgment":  "פסק דין",
}

SPEAKER_STYLE = {
    "judge":    ("🔵", "#c9a84c",  "msg-judge",    "כב׳ השופט"),
    "attorney": ("🔴", "#cc4444",  "msg-attorney", "עו״ד הצד שכנגד"),
    "user":     ("⚪", "#88aabb",  "msg-user",     "אתה"),
}


def _render_message(msg: dict):
    role = msg.get("role", "user")
    emoji, color, css_class, default_label = SPEAKER_STYLE.get(role, SPEAKER_STYLE["user"])
    label = msg.get("speaker", default_label)
    st.markdown(
        f'<div class="speaker-label" style="color:{color};">{emoji} {label}:</div>'
        f'<div class="{css_class}">{msg["content"]}</div>',
        unsafe_allow_html=True,
    )


def render():
    phase = st.session_state.get("phase", "opening")
    case = st.session_state.get("case", {})
    personas = st.session_state.get("personas", {})
    messages = st.session_state.get("messages", [])

    judge_display = case.get("judge_name") or "שופט"
    case_type = "פלילי" if case.get("type") == "criminal" else "אזרחי"
    phase_label = PHASE_LABELS.get(phase, phase)

    st.markdown(
        f'<div style="margin-bottom:6px;">'
        f'<span style="color:#c9a84c;font-size:13px;font-weight:bold;letter-spacing:1px;">⚖ שלב: {phase_label}</span>'
        f'&nbsp;&nbsp;<span style="color:#8a8a9a;font-size:11px;">{judge_display} · {case_type}</span>'
        f'</div><div class="gold-rule"></div>',
        unsafe_allow_html=True,
    )

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
