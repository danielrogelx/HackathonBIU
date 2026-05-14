import streamlit as st

_CSS = """
<style>
body, .stApp, .stMarkdown { direction: rtl; text-align: right; }

textarea, .stTextInput input {
    background: #F0E8D8 !important;
    color: #3D2B1F !important;
    border-color: #C4A882 !important;
}

.msg-judge {
    background: #EDE3D3;
    border-right: 3px solid #A0714F;
    padding: 10px 14px;
    margin: 3px 0 12px 0;
    font-size: 13px;
    line-height: 1.6;
    border-radius: 1px;
    color: #3D2B1F;
}
.msg-attorney {
    background: #EDD8D8;
    border-right: 3px solid #A05050;
    padding: 10px 14px;
    margin: 3px 0 12px 0;
    font-size: 13px;
    line-height: 1.6;
    border-radius: 1px;
    color: #3D2B1F;
}
.msg-user {
    background: #E8EDE3;
    border-right: 3px solid #6B8E6B;
    padding: 10px 14px;
    margin: 3px 0 12px 0;
    font-size: 13px;
    line-height: 1.6;
    border-radius: 1px;
    color: #3D2B1F;
}
.speaker-label {
    font-size: 10px;
    letter-spacing: 1px;
    font-weight: bold;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.gold-rule {
    background: #A0714F;
    height: 1px;
    width: 40px;
    margin: 4px 0 18px auto;
}
[data-testid="stMetric"] {
    border-top: 2px solid #A0714F !important;
    background: #F0E8D8 !important;
    padding: 12px 8px !important;
    border-radius: 2px !important;
}
[data-testid="InputInstructions"] { display: none; }

/* Hide file uploader size limit text */
[data-testid="stFileUploaderDropzoneInstructions"] { display: none !important; }
</style>
"""

_HEADER_HTML = """
<div style="text-align:center;padding-bottom:32px;margin-bottom:32px;border-bottom:1px solid #C4A88266;">
  <div style="display:inline-flex;align-items:center;justify-content:center;
    width:88px;height:88px;border:3px solid #A0714F;border-radius:50%;
    font-size:44px;color:#A0714F;margin-bottom:14px;">⚖</div>
  <div style="color:#A0714F;font-size:22px;letter-spacing:4px;text-transform:uppercase;margin-bottom:6px;">מתמחה בבית המשפט</div>
  <div style="color:#C4A882;font-size:13px;letter-spacing:3px;font-style:italic;">Court Practice Simulator</div>
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
