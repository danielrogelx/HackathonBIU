import streamlit as st
from core.orchestrator import start_session
from core.document_parser import extract_text


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

    st.markdown("---")
    st.caption("העלאת מסמכי תיק — אופציונלי אך מומלץ (תומך ב-.txt, .docx, .pdf)")
    plaintiff_file = st.file_uploader("כתב תביעה / כתב אישום", type=["txt", "docx", "pdf"], key="plaintiff_upload")
    defense_file = st.file_uploader("כתב הגנה", type=["txt", "docx", "pdf"], key="defense_upload")

    if st.button("בחן אותי! ⚖️", type="primary"):
        if not parties or not charges or not evidence:
            st.error("יש למלא את כל השדות המסומנים ב-*")
            return

        # Parse uploaded documents if provided
        plaintiff_text = ""
        defense_text = ""
        if plaintiff_file:
            try:
                plaintiff_text = extract_text(plaintiff_file)
            except Exception as e:
                st.warning(f"לא ניתן לקרוא את כתב התביעה: {e}")
        if defense_file:
            try:
                defense_text = extract_text(defense_file)
            except Exception as e:
                st.warning(f"לא ניתן לקרוא את כתב ההגנה: {e}")

        case = {
            "type": "criminal" if case_type == "פלילי" else "civil",
            "parties": parties,
            "charges": charges,
            "evidence": evidence,
            "judge_name": judge_name,
            "attorney_name": attorney_name,
            "plaintiff_text": plaintiff_text,
            "defense_text": defense_text,
        }

        doc_status = ""
        if plaintiff_text and defense_text:
            doc_status = " ומנתח מסמכים..."
        elif plaintiff_text or defense_text:
            doc_status = " ומנתח מסמך..."

        with st.spinner(f"מכין את הסימולציה{doc_status}"):
            result = start_session(case)

        st.session_state["case"] = case
        st.session_state["personas"] = result["personas"]
        st.session_state["phase"] = result["phase"]
        st.session_state["messages"] = [result["opening_message"]]
        st.session_state["screen"] = "chat"
        st.rerun()
