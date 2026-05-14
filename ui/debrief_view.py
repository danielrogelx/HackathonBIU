import html
import streamlit as st
from agents.coach import DebriefReport
from data.session_store import load_sessions

# ── Palette ──────────────────────────────────────────────────────────────────
COLOR_HIGH   = "#2ecc71"   # 8–10
COLOR_MID    = "#f39c12"   # 5–7
COLOR_LOW    = "#e74c3c"   # 1–4
COLOR_GOLD   = "#c9a84c"
COLOR_BG     = "#0d1117"
COLOR_CARD   = "#161b22"
COLOR_BORDER = "#30363d"


def _score_color(score: int) -> str:
    if score >= 8:
        return COLOR_HIGH
    if score >= 5:
        return COLOR_MID
    return COLOR_LOW


def _inject_styles() -> None:
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@400;700;900&display=swap');

    html, body, [class*="css"] {{
        direction: rtl;
        text-align: right;
        font-family: 'Frank Ruhl Libre', serif;
        background-color: {COLOR_BG};
        color: #e6edf3;
    }}

    /* Score card grid */
    .score-grid {{
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 12px;
        margin: 20px 0 28px 0;
    }}

    .score-card {{
        background: {COLOR_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 10px;
        padding: 16px 10px 14px 10px;
        text-align: center;
    }}

    .score-label {{
        font-size: 0.78rem;
        color: #8b949e;
        margin-bottom: 8px;
        font-weight: 400;
    }}

    .score-number {{
        font-size: 2.4rem;
        font-weight: 900;
        line-height: 1;
        margin-bottom: 10px;
    }}

    .score-bar-bg {{
        background: #21262d;
        border-radius: 4px;
        height: 6px;
        width: 100%;
    }}

    .score-bar-fill {{
        height: 6px;
        border-radius: 4px;
    }}

    /* Overall score banner */
    .overall-banner {{
        background: linear-gradient(135deg, #1a2332 0%, #0d1117 100%);
        border: 1px solid {COLOR_GOLD};
        border-radius: 12px;
        padding: 20px 28px;
        margin-bottom: 28px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .overall-label {{
        font-size: 1.1rem;
        color: {COLOR_GOLD};
        font-weight: 700;
    }}

    .overall-number {{
        font-size: 3rem;
        font-weight: 900;
        color: {COLOR_GOLD};
    }}

    /* Section cards */
    .section-card {{
        background: {COLOR_CARD};
        border: 1px solid {COLOR_BORDER};
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 14px;
        line-height: 1.8;
    }}

    .section-title {{
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 10px;
        color: #e6edf3;
    }}

    .section-body {{
        color: #c9d1d9;
        font-size: 0.95rem;
    }}

    /* History table header */
    .history-header {{
        font-size: 1.1rem;
        font-weight: 700;
        color: {COLOR_GOLD};
        border-bottom: 1px solid {COLOR_BORDER};
        padding-bottom: 8px;
        margin: 32px 0 16px 0;
    }}

    /* Override Streamlit's default divider colour */
    hr {{
        border-color: {COLOR_BORDER} !important;
    }}
    </style>
    """, unsafe_allow_html=True)


def _score_card_html(label: str, score: int) -> str:
    color = _score_color(score)
    pct = score * 10
    return f"""
    <div class="score-card">
        <div class="score-label">{label}</div>
        <div class="score-number" style="color:{color}">{score}</div>
        <div class="score-bar-bg">
            <div class="score-bar-fill" style="width:{pct}%; background:{color};"></div>
        </div>
    </div>
    """


def render_debrief(report: DebriefReport) -> None:
    """
    Render the full post-session debrief report.
    Called by app.py after analyze_session() returns a DebriefReport.
    """
    _inject_styles()

    st.markdown("## 📋 דוח מאמן — ניתוח ביצועים")
    st.markdown(f"**סוג תיק:** {report.case_type} &nbsp;|&nbsp; **תאריך:** {report.timestamp[:10]}")
    st.markdown("---")

    # ── Overall score banner ──────────────────────────────────────────────────
    overall_color = _score_color(report.overall)
    st.markdown(f"""
    <div class="overall-banner">
        <div class="overall-label">⭐ ציון כולל</div>
        <div class="overall-number" style="color:{overall_color}">{report.overall}<span style="font-size:1.4rem; color:#8b949e">/10</span></div>
    </div>
    """, unsafe_allow_html=True)

    # ── Five score cards ──────────────────────────────────────────────────────
    dims = [
        ("שכנוע",          report.score_persuasion),
        ("שליטה בחוק",     report.score_law),
        ("ניהול ראיות",    report.score_evidence),
        ("תגובה לאתגרים",  report.score_pressure),
        ("סדרה ונוהל",     report.score_procedure),
    ]
    cards_html = '<div class="score-grid">'
    for label, score in dims:
        cards_html += _score_card_html(label, score)
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)

    # ── Debrief sections ──────────────────────────────────────────────────────
    sections = [
        ("✅ טענות חזקות",                     report.strong_points),
        ("⚠️ חולשות ונקודות לשיפור",            report.weaknesses),
        ("❌ טעויות סדריות לפי הדין הישראלי",   report.procedural_errors),
        ('🎭 מה היו עושים בפועל',               report.reality_check),
        ("💡 המלצות קונקרטיות",                  report.recommendations),
    ]
    for title, body in sections:
        st.markdown(f"""
        <div class="section-card">
            <div class="section-title">{title}</div>
            <div class="section-body">{html.escape(body)}</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Session history table ─────────────────────────────────────────────────
    render_history()


def render_history() -> None:
    """Render the score history table (last 10 sessions)."""
    sessions = load_sessions()
    if not sessions:
        return

    st.markdown('<div class="history-header">📊 היסטוריית ציונים</div>', unsafe_allow_html=True)

    rows = []
    for s in reversed(sessions[-10:]):
        rows.append({
            "תאריך":       s["timestamp"][:10],
            "עורך דין":    s.get("lawyer", "לא צוין"),
            "סוג תיק":     s["case_type"],
            "ציון כולל":   f"{s['overall']}/10",
            "שכנוע":       s["score_persuasion"],
            "שליטה בחוק":  s["score_law"],
            "ניהול ראיות": s["score_evidence"],
            "תגובה":       s["score_pressure"],
            "נוהל":        s["score_procedure"],
        })

    st.dataframe(rows, use_container_width=True, hide_index=True)


def render() -> None:
    """Entry point called by app.py with no arguments."""
    report = st.session_state.get("debrief")
    if report is None:
        st.error("לא נמצא דוח מאמן. אנא סיים דיון תחילה.")
        return
    render_debrief(report)
