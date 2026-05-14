import streamlit as st
from core.orchestrator import start_session

_DOC_TYPES = ["txt", "pdf", "docx"]
_ALL_TYPES = ["txt", "pdf", "docx", "jpg", "jpeg", "png"]


def _extract_text(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    if name.endswith(".txt"):
        return uploaded_file.read().decode("utf-8", errors="ignore")
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(uploaded_file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if name.endswith(".docx"):
        from docx import Document
        doc = Document(uploaded_file)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    if name.endswith((".jpg", ".jpeg", ".png")):
        return f"[תמונה: {uploaded_file.name}]"
    return ""


def render():
    st.markdown(
        '<div style="color:#A0714F;font-size:16px;font-weight:bold;margin-bottom:2px;">הגדרת תיק</div>'
        '<div class="gold-rule"></div>',
        unsafe_allow_html=True,
    )

    case_type = st.radio("סוג תיק", ["פלילי", "אזרחי"], horizontal=True)
    side = st.radio("איזה צד אני מייצג", ["הגנה", "תביעה"], horizontal=True)

    parties = st.text_input("הצדדים *", placeholder="לדוגמה: מדינת ישראל נ' ראובן שמעון")
    charges = st.text_area("האישום / התביעה *", placeholder="תאר את האישום הפלילי או עילת התביעה")
    evidence = st.text_area("ראיות מרכזיות *", placeholder="פרט את הראיות המרכזיות שברשותך")

    st.markdown("---")

    # ── Mandatory legal documents ─────────────────────────────────────────────
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

    st.markdown("---")

    # ── Optional supporting files ─────────────────────────────────────────────
    uploaded_files = st.file_uploader(
        "מסמכים וצילומי מסך לגיבוי הטענות (אופציונלי)",
        type=_ALL_TYPES,
        accept_multiple_files=True,
    )
    st.caption("קבצים נתמכים: .txt · .pdf · .docx · .jpg · .png")

    if uploaded_files:
        images = [f for f in uploaded_files if f.name.lower().endswith((".jpg", ".jpeg", ".png"))]
        if images:
            cols = st.columns(min(len(images), 4))
            for col, img in zip(cols, images):
                col.image(img, use_container_width=True, caption=img.name)

    st.markdown("---")
    st.caption("אופציונלי — ניתן להשאיר ריק לקבל פרסונות ברירת מחדל")
    judge_name = st.text_input("שם השופט", placeholder="לדוגמה: אסתר חיות")
    attorney_name = st.text_input("שם עו\"ד הצד שכנגד", placeholder="לדוגמה: דן מרידור")

    if st.button("בחן אותי! ⚖️", type="primary"):
        errors = []
        if not parties or not charges or not evidence:
            errors.append("יש למלא את כל שדות הטקסט המסומנים ב-*")
        if not claim_file:
            errors.append("יש להעלות כתב תביעה / כתב אישום")
        if not defense_file:
            errors.append("יש להעלות כתב הגנה")
        if errors:
            for e in errors:
                st.error(e)
            return

        # Build documents context: mandatory first, then optional
        parts = [
            f"=== כתב תביעה ({claim_file.name}) ===\n{_extract_text(claim_file).strip()}",
            f"=== כתב הגנה ({defense_file.name}) ===\n{_extract_text(defense_file).strip()}",
        ]
        if uploaded_files:
            for f in uploaded_files:
                text = _extract_text(f)
                if text.strip():
                    parts.append(f"=== {f.name} ===\n{text.strip()}")
        documents = "\n\n".join(parts)

        case = {
            "type": "criminal" if case_type == "פלילי" else "civil",
            "side": "defense" if side == "הגנה" else "prosecution",
            "parties": parties,
            "charges": charges,
            "evidence": evidence,
            "documents": documents,
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
