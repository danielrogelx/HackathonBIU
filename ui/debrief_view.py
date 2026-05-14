import streamlit as st

SCORE_LABELS = {
    "persuasion": "שכנוע",
    "law_knowledge": "שליטה בחוק",
    "evidence": "ניהול ראיות",
    "pressure_response": "תגובה לאתגרים",
    "procedure": "סדרה ונוהל",
}


def render():
    st.title("דוח מאמן 📋")
    st.subheader("ניתוח ביצועים — סיום הדיון")
    st.markdown("---")

    debrief = st.session_state.get("debrief", {})
    scores = debrief.get("scores", {})

    if scores:
        st.markdown("### ציונים")
        cols = st.columns(len(SCORE_LABELS))
        for col, (key, label) in zip(cols, SCORE_LABELS.items()):
            score = scores.get(key, 0)
            col.metric(label, f"{score}/10")
        st.markdown("---")

    sections = [
        ("strengths",       "✅ טענות חזקות"),
        ("weaknesses",      "⚠️ חולשות ונקודות לשיפור"),
        ("errors",          "❌ טעויות סדריות"),
        ("recommendations", "💡 המלצות"),
    ]

    for key, title in sections:
        items = debrief.get(key, [])
        st.markdown(f"### {title}")
        if items:
            for item in items:
                st.markdown(f"- {item}")
        else:
            st.caption("(יופיע לאחר חיבור ה-AI)")
        st.markdown("")

    st.markdown("---")
    if st.button("התחל סשן חדש 🔄", type="primary"):
        for key in ["case", "personas", "phase", "messages", "debrief"]:
            st.session_state.pop(key, None)
        st.session_state["screen"] = "setup"
        st.rerun()
