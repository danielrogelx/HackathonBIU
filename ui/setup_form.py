import streamlit as st
from core.orchestrator import start_session


def render():
    st.markdown(
        '<div style="color:#c9a84c;font-size:16px;font-weight:bold;margin-bottom:2px;">הגדרת תיק</div>'
        '<div class="gold-rule"></div>',
        unsafe_allow_html=True,
    )

    case_type = st.radio("סוג תיק", ["פלילי", "אזרחי"], horizontal=True)

    parties = st.text_input("הצדדים *", placeholder="לדוגמה: מדינת ישראל נ' ראובן שמעון")
    charges = st.text_area("האישום / התביעה *", placeholder="תאר את האישום הפלילי או עילת התביעה")
    evidence = st.text_area("ראיות מרכזיות *", placeholder="פרט את הראיות המרכזיות שברשותך")

    st.markdown("---")
    st.caption("אופציונלי — ניתן להשאיר ריק לקבל פרסונות ברירת מחדל")
    judge_name = st.text_input("שם השופט", placeholder="לדוגמה: אסתר חיות")
    attorney_name = st.text_input("שם עו\"ד הצד שכנגד", placeholder="לדוגמה: דן מרידור")

    if st.button("בחן אותי! ⚖️", type="primary"):
        if not parties or not charges or not evidence:
            st.error("יש למלא את כל השדות המסומנים ב-*")
            return

        case = {
            "type": "criminal" if case_type == "פלילי" else "civil",
            "parties": parties,
            "charges": charges,
            "evidence": evidence,
            "judge_name": judge_name,
            "attorney_name": attorney_name,
        }

        with st.spinner("מכין את הסימולציה..."):
            result = start_session(case)

        st.session_state["case"] = case
        st.session_state["personas"] = result["personas"]
        st.session_state["phase"] = result["phase"]
        st.session_state["messages"] = [result["opening_message"]]
        st.session_state["screen"] = "chat"
        st.rerun()
