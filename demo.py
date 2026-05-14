"""
Quick demo to test the coach agent + debrief view locally.
Run with:  streamlit run demo.py
"""
import streamlit as st
from test_coach import SAMPLE_TRANSCRIPT, SAMPLE_CASE_TYPE

st.set_page_config(page_title="מתמחה בבית המשפט — Demo", layout="wide", page_icon="⚖️")

st.title("⚖️ מתמחה בבית המשפט")
st.markdown("**דמו — דוח מאמן**")
st.divider()

st.markdown("### התמליל שנשלח לניתוח")
role_map = {"lawyer": "🧑‍💼 עורך דין", "judge": "👨‍⚖️ שופט", "attorney": "⚔️ עו״ד שכנגד"}
for msg in SAMPLE_TRANSCRIPT:
    label = role_map.get(msg["role"], msg["role"])
    st.markdown(f"**{label}:** {msg['content']}")

st.divider()

if st.button("🔍 נתח את הדיון וקבל דוח מאמן", type="primary"):
    with st.spinner("שולח לניתוח... (עשוי לקחת כ-10 שניות)"):
        from agents.coach import analyze_session
        from data.session_store import save_session
        report = analyze_session(SAMPLE_TRANSCRIPT, SAMPLE_CASE_TYPE)
        save_session(report, lawyer_name="דמו")

    st.success("הניתוח הושלם!")
    st.divider()

    from ui.debrief_view import render_debrief
    render_debrief(report)
