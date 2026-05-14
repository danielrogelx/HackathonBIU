"""
Debrief View Component
Renders the post-session coach analysis report
"""

import streamlit as st


def render_debrief_report(debrief_data: dict):
    """
    Render the structured debrief report.

    Args:
        debrief_data: Dict with analysis from coach agent
    """

    # Overall score
    overall_score = debrief_data.get("overall_score", 0)
    st.markdown(f"## ⭐ ציון כולל: **{overall_score}/10**")

    # 5-Dimension scores
    st.markdown("### 📈 ניתוח לפי ממדים (1-10)")

    dimensions = debrief_data.get("dimensions", {})
    cols = st.columns(5)

    metrics = [
        ("שכנוע", "persuasion"),
        ("שליטה בחוק", "legal_mastery"),
        ("ניהול ראיות", "evidence_management"),
        ("תגובה לאתגרים", "challenge_response"),
        ("סדרה ונוהל", "procedure"),
    ]

    for col, (label_he, key) in zip(cols, metrics):
        score = dimensions.get(key, 0)
        with col:
            st.metric(label=label_he, value=f"{score}/10")

    st.divider()

    # Strengths
    st.markdown("### ✅ טענות חזקות")
    strengths = debrief_data.get("strengths", [])
    if strengths:
        for strength in strengths:
            st.success(f"✓ {strength}")
    else:
        st.info("אין נתונים זמינים")

    # Weaknesses
    st.markdown("### ⚠️ חולשות ונקודות לשיפור")
    weaknesses = debrief_data.get("weaknesses", [])
    if weaknesses:
        for weakness in weaknesses:
            st.warning(f"⚠ {weakness}")
    else:
        st.info("אין נתונים זמינים")

    # Procedural errors
    st.markdown("### ❌ טעויות סדריות")
    errors = debrief_data.get("procedural_errors", [])
    if errors:
        for error in errors:
            st.error(f"✗ {error}")
    else:
        st.success("לא היו טעויות סדריות קריטיות")

    # What experts do
    st.markdown("### 🎭 איך היו עושים זאת בפועל")
    what_experts = debrief_data.get("what_experts_do", "")
    if what_experts:
        st.info(what_experts)
    else:
        st.info("אין נתונים זמינים")

    # Recommendations
    st.markdown("### 💡 המלצות קונקרטיות")
    recommendations = debrief_data.get("recommendations", [])
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"**{i}.** {rec}")
    else:
        st.info("אין המלצות זמינות")

    # Full analysis
    st.markdown("### 📋 ניתוח מלא")
    full_analysis = debrief_data.get("full_analysis", "")
    if full_analysis:
        st.text(full_analysis)
    else:
        st.info("אין ניתוח מלא זמין")

    # Export options
    st.divider()
    st.markdown("### 📥 אפשרויות ייצוא")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 הורד דוח PDF", use_container_width=True):
            st.info("🔄 תכונה בפיתוח")

    with col2:
        if st.button("📊 הורד דוח Excel", use_container_width=True):
            st.info("🔄 תכונה בפיתוח")
