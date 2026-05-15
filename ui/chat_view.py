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
    "judge": ("🔵", "#A0714F", "msg-judge", "כב׳ השופט"),
    "attorney": ("🔴", "#A05050", "msg-attorney", "עו״ד הצד שכנגד"),
    "user": ("⚪", "#6B8E6B", "msg-user", "אתה"),
}


def _render_message(msg: dict):
    role = msg.get("role", "user")
    emoji, color, css_class, default_label = SPEAKER_STYLE.get(
        role, SPEAKER_STYLE["user"]
    )
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

    # ── Step 2: pending LLM call ──────────────────────────────────────────
    # The user message was already appended and shown above.  Now call the
    # LLM under a spinner and add the responses, then rerun to render them.
    pending = st.session_state.pop("_pending_input", None)
    if pending:
        with st.spinner("השופט מעיין..."):
            result = send_message(
                user_input=pending,
                messages=messages,
                phase=phase,
                case=case,
                personas=personas,
            )
        messages.append(result["judge_response"])
        if result.get("attorney_response"):
            messages.append(result["attorney_response"])
        if result.get("judge_followup"):
            messages.append(result["judge_followup"])
        st.session_state["messages"] = messages
        st.session_state["phase"] = result["new_phase"]
        st.rerun()

    st.markdown("---")
    # ── Step 1: submit ────────────────────────────────────────────────────
    # Add the user message to session state immediately and rerun so it
    # appears before the LLM is even called.  The actual LLM call happens
    # on the next render (Step 2 above) under a spinner.
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area("הטענה שלך:", height=100)
        submitted = st.form_submit_button("שלח ▶", type="primary")

    if submitted and user_input.strip():
        messages.append({"role": "user", "content": user_input.strip()})
        st.session_state["messages"] = messages
        st.session_state["_pending_input"] = user_input.strip()
        st.rerun()

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("סיים דיון 🔚"):
            debrief = end_session(messages)
            st.session_state["debrief"] = debrief
            from data.session_store import save_session

            save_session(debrief, lawyer_name=case.get("attorney_name") or "לא צוין")
            st.session_state["screen"] = "debrief"
            st.rerun()

    with col2:
        if st.button("התחל מחדש 🔄"):
            for key in ["case", "personas", "phase", "messages", "debrief"]:
                st.session_state.pop(key, None)
            st.session_state["screen"] = "setup"
            st.rerun()
