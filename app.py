"""
Court Practice Simulator - Main Streamlit App
מתמחה בבית המשפט

A Hebrew-language AI system for lawyers to rehearse court sessions
"""

import streamlit as st
from streamlit_option_menu import option_menu
import uuid
from config import UI_TITLE, UI_SUBTITLE, CaseType, PHASE_NAMES_HE
from core.orchestrator import Orchestrator
from agents.judge import JudgeAgent
from agents.attorney import AttorneyAgent
from agents.coach import CoachAgent
from ui.setup_form import render_setup_form
from ui.chat_view import render_chat_interface
from ui.debrief_view import render_debrief_report

# ============================================================================
# PAGE CONFIG & STATE INITIALIZATION
# ============================================================================

st.set_page_config(
    page_title=UI_TITLE,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Hebrew RTL support
st.markdown(
    """
    <style>
    body { direction: rtl; }
    .stMarkdown, .stText { direction: rtl; text-align: right; }
    </style>
    """,
    unsafe_allow_html=True,
)


def init_session_state():
    """Initialize Streamlit session state variables."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"

    if "orchestrator" not in st.session_state:
        st.session_state.orchestrator = None

    if "judge_agent" not in st.session_state:
        st.session_state.judge_agent = None

    if "attorney_agent" not in st.session_state:
        st.session_state.attorney_agent = None

    if "coach_agent" not in st.session_state:
        st.session_state.coach_agent = None

    if "session_complete" not in st.session_state:
        st.session_state.session_complete = False


# ============================================================================
# HEADER & NAVIGATION
# ============================================================================


def render_header():
    """Render the main header."""
    col1, col2 = st.columns([1, 3])
    with col1:
        st.markdown("🏛️")
    with col2:
        st.markdown(f"# {UI_TITLE}")
        st.markdown(f"__{UI_SUBTITLE}__")


# ============================================================================
# HOME PAGE
# ============================================================================


def render_home():
    """Render the home page with welcome and quick start."""
    st.markdown("""
    ## ברוכים הבאים לסימולטור דיון משפטי

    מערכת זו מאפשרת לעורכי דין להתרגל בדיונים משפטיים עם שני סוכנים בינה מלאכותית:
    - 🔵 **שופט** — מנהל את הדיון בקפדנות וקצב
    - 🔴 **עו"ד צד שכנגד** — תוקפני וממוקד על הפרות בטיעונים

    ### איך זה עובד:

    1. **הגדרה** — תספק פרטי תיק (סוג תיק, צדדים, הוכחות)
    2. **סימולציה** — תתחיל דיון עם השופט, ההתנגדויות של עו"ד, וקבלת הכללים
    3. **דוח** — בסוף, מאמן משפטי יגיד לך מה עשית טוב ומה לשפר

    ### התחלה

    בחר סוג תיק:
    """)

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🔴 **תיק פלילי (Criminal)** - אישום, ראיות, זיכוי",
            use_container_width=True,
        ):
            st.session_state.current_page = "setup"
            st.session_state.case_type = CaseType.CRIMINAL
            st.rerun()

    with col2:
        if st.button(
            "🔵 **תיק אזרחי (Civil)** - תביעה, טיעונים, פסק דין",
            use_container_width=True,
        ):
            st.session_state.current_page = "setup"
            st.session_state.case_type = CaseType.CIVIL
            st.rerun()


# ============================================================================
# SETUP PAGE
# ============================================================================


def render_setup():
    """Render the case setup form."""
    st.markdown(f"## הגדרת התיק")

    case_type = st.session_state.get("case_type", CaseType.CRIMINAL)

    # Render form
    case_facts, judge_name, attorney_name = render_setup_form(case_type)

    # Start simulation
    if st.button("▶️ **התחל דיון**", use_container_width=True, type="primary"):
        # Create orchestrator
        orchestrator = Orchestrator(
            session_id=st.session_state.session_id,
            case_type=case_type,
        )

        # TODO: Call research agent for personas (Person 2 to implement)
        judge_persona = {"description": "", "style": ""}
        attorney_persona = {"description": "", "tactics": []}

        orchestrator.set_judge(judge_name or "שופט בכיר", judge_persona)
        orchestrator.set_attorney(attorney_name or "עורך דין בכיר", attorney_persona)
        orchestrator.set_case_facts(case_facts)

        judge_agent = JudgeAgent(orchestrator)
        attorney_agent = AttorneyAgent(orchestrator)

        st.session_state.orchestrator = orchestrator
        st.session_state.judge_agent = judge_agent
        st.session_state.attorney_agent = attorney_agent
        st.session_state.current_page = "simulation"

        # Judge opens the hearing
        with st.spinner("שופט מוציא את הדיון לדרך..."):
            opening = judge_agent.opening_remarks(stream=False)
            st.session_state.opening_remarks = opening

        st.rerun()


# ============================================================================
# SIMULATION PAGE
# ============================================================================


def render_simulation():
    """Render the main simulation chat interface."""
    orchestrator = st.session_state.orchestrator
    judge_agent = st.session_state.judge_agent
    attorney_agent = st.session_state.attorney_agent

    if not orchestrator:
        st.error("שגיאה: אין סשן פעיל. חזרו לעמוד הבית.")
        return

    # Display phase header
    phase_he = PHASE_NAMES_HE.get(
        orchestrator.state.current_phase, orchestrator.state.current_phase
    )
    st.markdown(f"### שלב: __{phase_he}__")
    st.markdown(
        f'שופט: **{orchestrator.state.judge_name}** | עו"ד צד שכנגד: **{orchestrator.state.attorney_name}**'
    )
    st.divider()

    # Render chat interface
    render_chat_interface(orchestrator, judge_agent, attorney_agent)

    # Session control buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⏭️ דלג לשלב הבא", use_container_width=True):
            if orchestrator.can_advance_phase():
                with st.spinner("השופט פותח את השלב הבא..."):
                    judge_agent.advance_phase()
                st.rerun()

    with col2:
        if st.button("🏁 סיים דיון", use_container_width=True):
            orchestrator.mark_complete()
            coach_agent = CoachAgent(orchestrator)
            st.session_state.coach_agent = coach_agent
            st.session_state.current_page = "debrief"
            st.rerun()

    with col3:
        if st.button("🏠 חזרה לעמוד הבית", use_container_width=True):
            # Reset session
            st.session_state.clear()
            init_session_state()
            st.session_state.current_page = "home"
            st.rerun()


# ============================================================================
# DEBRIEF PAGE
# ============================================================================


def render_debrief():
    """Render the post-session debrief report."""
    coach_agent = st.session_state.coach_agent

    if not coach_agent:
        st.error("שגיאה: אין דוח זמין.")
        return

    st.markdown("## 📊 דוח ניתוח הביצוע")

    # Generate and display debrief
    debrief_data = coach_agent.generate_debrief()
    render_debrief_report(debrief_data)

    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 התחל סשן חדש", use_container_width=True):
            st.session_state.clear()
            init_session_state()
            st.session_state.current_page = "home"
            st.rerun()

    with col2:
        if st.button("💾 שמור דוח", use_container_width=True):
            st.info("💾 פונקציונליות שמירה תיושם בגרסה הבאה")


# ============================================================================
# MAIN APP
# ============================================================================


def main():
    """Main app entry point."""
    init_session_state()
    render_header()

    # Page routing
    current_page = st.session_state.current_page

    if current_page == "home":
        render_home()
    elif current_page == "setup":
        render_setup()
    elif current_page == "simulation":
        render_simulation()
    elif current_page == "debrief":
        render_debrief()
    else:
        render_home()

    # Footer
    st.divider()
    st.markdown(
        """
        <div style="text-align: center; color: gray; font-size: 0.8em;">
        מתמחה בבית המשפט — BIU Hackathon 2026 | סימולטור דיון משפטי עם בינה מלאכותית
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
