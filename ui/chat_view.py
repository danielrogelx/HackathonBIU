"""
Chat View Component
Renders the main simulation chat interface
"""

import streamlit as st
from core.orchestrator import Orchestrator
from agents.judge import JudgeAgent
from agents.attorney import AttorneyAgent

_ROLE_DISPLAY = {
    "judge": ("השופט", "⚖️", "assistant"),
    "attorney": ('עו"ד צד שכנגד', "🔴", "assistant"),
    "lawyer": ("אתה", "👤", "user"),
}


def render_chat_interface(
    orchestrator: Orchestrator,
    judge_agent: JudgeAgent,
    attorney_agent: AttorneyAgent,
):
    # Opening remarks (once at top)
    if st.session_state.get("opening_remarks"):
        with st.chat_message("assistant", avatar="⚖️"):
            st.markdown("**השופט (פתיחה):**\n\n" + st.session_state.opening_remarks)

    # Render all saved history messages
    for msg in orchestrator.get_state().conversation_history:
        role = msg.get("role", "lawyer")
        content = msg.get("content") or ""
        label, avatar, chat_role = _ROLE_DISPLAY.get(role, ("?", "❓", "user"))
        with st.chat_message(chat_role, avatar=avatar):
            st.markdown("**" + label + ":**\n\n" + content)

    # Mode selector
    mode = st.session_state.get("input_mode", "speak")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(
            "💬 טיעון",
            use_container_width=True,
            type="primary" if mode == "speak" else "secondary",
        ):
            st.session_state.input_mode = "speak"
            st.rerun()
    with col2:
        if st.button(
            "⚖️ התנגדות",
            use_container_width=True,
            type="primary" if mode == "object" else "secondary",
        ):
            st.session_state.input_mode = "object"
            st.rerun()
    with col3:
        if st.button(
            "🔍 חקירה",
            use_container_width=True,
            type="primary" if mode == "question" else "secondary",
        ):
            st.session_state.input_mode = "question"
            st.rerun()

    placeholders = {
        "speak": "כתוב את טיעונך ולחץ Enter...",
        "object": "נמק את ההתנגדות — עדות שמיעה, חוסר בסיס...",
        "question": 'כתוב שאלה לשופט או לעו"ד...',
    }

    # Chat input — st.chat_input triggers rerun on submit automatically
    user_input = st.chat_input(placeholders[mode])

    if not user_input or not user_input.strip():
        return

    # Show user message inline (same render pass — visible immediately)
    with st.chat_message("user", avatar="👤"):
        st.markdown("**אתה:**\n\n" + user_input)

    # Judge responds
    with st.chat_message("assistant", avatar="⚖️"):
        try:
            with st.spinner("השופט מחשב..."):
                # speak() adds lawyer msg + judge reply to orchestrator history internally
                judge_reply = judge_agent.speak(lawyer_message=user_input, stream=False)
            st.markdown("**השופט:**\n\n" + (judge_reply or ""))
        except Exception as e:
            st.error("שגיאה בחיבור לשופט: " + str(e))
            return

    # Attorney responds
    with st.chat_message("assistant", avatar="🔴"):
        try:
            if mode == "object":
                with st.spinner('עו"ד מגיש התנגדות...'):
                    atty_reply = attorney_agent.object_to_evidence(
                        user_input, stream=False
                    )
            elif mode == "question":
                with st.spinner('עו"ד מגיב לחקירה...'):
                    atty_reply = attorney_agent.cross_examine(user_input, stream=False)
            else:
                with st.spinner('עו"ד מגיב...'):
                    atty_reply = attorney_agent.speak(
                        lawyer_message=user_input, stream=False
                    )
            st.markdown('**עו"ד צד שכנגד:**\n\n' + (atty_reply or ""))
        except Exception as e:
            st.error('שגיאה בחיבור לעו"ד: ' + str(e))
