"""
Setup Form Component
Renders the case details input form
"""

import streamlit as st
from config import CaseType


def render_setup_form(case_type: CaseType) -> tuple:
    """
    Render the case setup form.

    Args:
        case_type: Criminal or Civil

    Returns:
        Tuple of (case_facts, judge_name, attorney_name)
    """

    st.markdown(f"### פרטי התיק")

    # Basic case info
    col1, col2 = st.columns(2)

    with col1:
        parties = st.text_input(
            "👥 הצדדים בתיק (שם מתלונן / תובע כנגד)",
            placeholder="למשל: מדינת ישראל כנגד ראובן כהן",
        )

    with col2:
        judge_name = st.text_input(
            "🔵 שם השופט (אופציונלי)",
            placeholder="אם יש לך בחירה מסוימת",
        )

    attorney_name = st.text_input(
        '🔴 שם עו"ד הצד שכנגד (אופציונלי)',
        placeholder="שם המשיב / הנתבע",
    )

    # Charge or claim
    if case_type == CaseType.CRIMINAL:
        charges = st.text_area(
            "📋 האישום / הטענה",
            placeholder="למשל: גניבה בתחזוקה, שודדות מלווה בדם...",
            height=80,
        )
        claim = ""
    else:
        claim = st.text_area(
            "📋 תביעה",
            placeholder="למשל: פיצוי על נזקי גוף, חוזה שלא בוצע...",
            height=80,
        )
        charges = ""

    # Evidence
    evidence = st.text_area(
        "🔍 ראיות עיקריות / טיעונים",
        placeholder="פרט את הראיות או טיעוניך המרכזיים",
        height=100,
    )

    # Defense story (lawyer's main argument)
    defendant_story = st.text_area(
        "🗣️ הגרסה / הטיעון שלך (מה תגיד בדיון)",
        placeholder="מה הסיפור שלך? מה תטען?",
        height=100,
    )

    # Compile case facts
    case_facts = {
        "parties": parties,
        "charges": charges,
        "claim": claim,
        "evidence": evidence,
        "defendant_story": defendant_story,
        "case_type": case_type.value,
    }

    return case_facts, judge_name, attorney_name
