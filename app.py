import streamlit as st

_CSS = """
<style>
body, .stApp, .stMarkdown { direction: rtl; text-align: right; }

textarea, .stTextInput input {
    background: #111122 !important;
    color: #e8e0cc !important;
    border-color: #2a2a4a !important;
}

.msg-judge {
    background: #1e2550;
    border-right: 3px solid #c9a84c;
    padding: 10px 14px;
    margin: 3px 0 12px 0;
    font-size: 13px;
    line-height: 1.6;
    border-radius: 1px;
}
.msg-attorney {
    background: #231520;
    border-right: 3px solid #cc4444;
    padding: 10px 14px;
    margin: 3px 0 12px 0;
    font-size: 13px;
    line-height: 1.6;
    border-radius: 1px;
}
.msg-user {
    background: #1e2535;
    border-right: 3px solid #88aabb;
    padding: 10px 14px;
    margin: 3px 0 12px 0;
    font-size: 13px;
    line-height: 1.6;
    border-radius: 1px;
}
.speaker-label {
    font-size: 10px;
    letter-spacing: 1px;
    font-weight: bold;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.gold-rule {
    background: #c9a84c;
    height: 1px;
    width: 40px;
    margin: 4px 0 18px auto;
}
[data-testid="stMetric"] {
    border-top: 2px solid #c9a84c !important;
    background: #111122 !important;
    padding: 12px 8px !important;
    border-radius: 2px !important;
}
</style>
"""

_HEADER_HTML = """
<div style="text-align:center;padding-bottom:24px;margin-bottom:24px;border-bottom:1px solid #c9a84c44;">
  <div style="display:inline-flex;align-items:center;justify-content:center;
    width:56px;height:56px;border:2px solid #c9a84c;border-radius:50%;
    font-size:28px;color:#c9a84c;margin-bottom:10px;">⚖</div>
  <div style="color:#c9a84c;font-size:14px;letter-spacing:4px;text-transform:uppercase;margin-bottom:4px;">מתמחה בבית המשפט</div>
  <div style="color:#3a3a5c;font-size:10px;letter-spacing:2px;font-style:italic;">Court Practice Simulator</div>
</div>
"""

st.markdown(_CSS, unsafe_allow_html=True)
st.markdown(_HEADER_HTML, unsafe_allow_html=True)

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
