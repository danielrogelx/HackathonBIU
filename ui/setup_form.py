import streamlit as st
from core.orchestrator import start_session
from core.document_parser import extract_text

_DOC_TYPES = ["txt", "pdf", "docx"]


def render():
    st.markdown(
        '<div style="color:#A0714F;font-size:16px;font-weight:bold;margin-bottom:2px;">הגדרת תיק</div>'
        '<div class="gold-rule"></div>',
        unsafe_allow_html=True,
    )

    case_type = st.radio("סוג תיק", ["פלילי", "אזרחי"], horizontal=True)
    side = st.radio("איזה צד אני מייצג", ["הגנה", "תביעה"], horizontal=True)

    st.markdown("---")

    st.markdown(
        '<div style="color:#A0714F;font-size:14px;font-weight:bold;margin-bottom:8px;">מסמכים משפטיים (חובה)</div>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        claim_file = st.file_uploader("כתב תביעה / כתב אישום *", type=_DOC_TYPES, key="claim_file")
        st.caption(".txt · .pdf · .docx")
    with col2:
        defense_file = st.file_uploader("כתב הגנה *", type=_DOC_TYPES, key="defense_file")
        st.caption(".txt · .pdf · .docx")

    if st.button("בחן אותי! ⚖️", type="primary"):
        errors = []
        if not claim_file:
            errors.append("יש להעלות כתב תביעה / כתב אישום")
        if not defense_file:
            errors.append("יש להעלות כתב הגנה")
        if errors:
            for e in errors:
                st.error(e)
            return

        plaintiff_text = ""
        defense_text = ""
        try:
            plaintiff_text = extract_text(claim_file)
        except Exception as e:
            st.warning(f"לא ניתן לקרוא את כתב התביעה: {e}")
        try:
            defense_text = extract_text(defense_file)
        except Exception as e:
            st.warning(f"לא ניתן לקרוא את כתב ההגנה: {e}")

        case = {
            "type": "criminal" if case_type == "פלילי" else "civil",
            "side": "defense" if side == "הגנה" else "prosecution",
            "parties": "",
            "charges": "",
            "evidence": "",
            "plaintiff_text": plaintiff_text,
            "defense_text": defense_text,
        }

        with st.spinner("מנתח מסמכים ומכין את הסימולציה..."):
            result = start_session(case)

        st.session_state["case"] = case
        st.session_state["personas"] = result["personas"]
        st.session_state["phase"] = result["phase"]
        st.session_state["messages"] = [result["opening_message"]]
        st.session_state["screen"] = "chat"
        st.rerun()
