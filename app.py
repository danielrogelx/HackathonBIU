import streamlit as st

st.markdown(
    "<style>body, .stApp, .stMarkdown { direction: rtl; text-align: right; }</style>",
    unsafe_allow_html=True,
)

screen = st.session_state.get("screen", "setup")

if screen == "setup":
    from ui.setup_form import render
    render()
elif screen == "chat":
    from ui.chat_view import render
    render()
elif screen == "debrief":
    from ui.debrief_view import render
    render()
