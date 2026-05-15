import html
import streamlit as st
from agents.coach import DebriefReport
from data.session_store import load_sessions

# ── Palette (Navy & Gold) ─────────────────────────────────────────────────────
COLOR_HIGH   = "#4A8C5C"   # 8–10
COLOR_MID    = "#C4884A"   # 5–7
COLOR_LOW    = "#B05040"   # 1–4
COLOR_GOLD   = "#A0714F"
COLOR_CARD   = "#F0E8D8"
COLOR_BORDER = "#C4A882"


def _score_color(score: int) -> str:
    if score >= 8:
        return COLOR_HIGH
    if score >= 5:
        return COLOR_MID
    return COLOR_LOW


def _inject_styles() -> None:
    st.markdown(f"""
    <style>
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
        border-top: 2px solid {COLOR_GOLD};
        border-radius: 4px;
        padding: 16px 10px 14px 10px;
        text-align: center;
    }}

    .score-label {{
        font-size: 0.78rem;
        color: #8a8a9a;
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
        background: #DDD0BC;
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
        background: linear-gradient(135deg, #EDE3D3 0%, #F0E8D8 100%);
        border: 1px solid {COLOR_GOLD};
        border-radius: 4px;
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
        border-right: 3px solid {COLOR_GOLD};
        border-radius: 2px;
        padding: 18px 22px;
        margin-bottom: 14px;
        line-height: 1.8;
    }}

    .section-title {{
        font-size: 1rem;
        font-weight: 700;
        margin-bottom: 10px;
        color: #3D2B1F;
    }}

    .section-body {{
        color: #5C3D2A;
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
    _inject_styles()

    st.markdown(
        '<div style="color:#c9a84c;font-size:16px;font-weight:bold;margin-bottom:2px;">דוח מאמן</div>'
        '<div class="gold-rule"></div>',
        unsafe_allow_html=True,
    )
    st.caption(f"סוג תיק: {report.case_type} · תאריך: {report.timestamp[:10]}")
    st.markdown("---")

    # ── Overall score banner ──────────────────────────────────────────────────
    overall_color = _score_color(report.overall)
    st.markdown(f"""
    <div class="overall-banner">
        <div class="overall-label">⭐ ציון כולל</div>
        <div class="overall-number" style="color:{overall_color}">{report.overall}<span style="font-size:1.4rem; color:#8a8a9a">/10</span></div>
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
        ("🎭 מה היו עושים בפועל",               report.reality_check),
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

    st.markdown("---")
    if st.button("התחל סשן חדש 🔄", type="primary"):
        for key in ["case", "personas", "phase", "messages", "debrief",
                    "_orchestrator", "_judge", "_attorney", "_msg_count"]:
            st.session_state.pop(key, None)
        st.session_state["screen"] = "setup"
        st.rerun()


def render_history() -> None:
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
            "ציון כולל":   s["overall"],
            "שכנוע":       s["score_persuasion"],
            "שליטה בחוק":  s["score_law"],
            "ניהול ראיות": s["score_evidence"],
            "תגובה":       s["score_pressure"],
            "נוהל":        s["score_procedure"],
        })

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "תאריך":       st.column_config.TextColumn("תאריך", width="small"),
            "עורך דין":    st.column_config.TextColumn("עורך דין"),
            "סוג תיק":     st.column_config.TextColumn("סוג תיק", width="small"),
            "ציון כולל":   st.column_config.NumberColumn("ציון כולל", format="%d/10", width="small"),
            "שכנוע":       st.column_config.NumberColumn("שכנוע", format="%d", width="small"),
            "שליטה בחוק":  st.column_config.NumberColumn("שליטה בחוק", format="%d", width="small"),
            "ניהול ראיות": st.column_config.NumberColumn("ניהול ראיות", format="%d", width="small"),
            "תגובה":       st.column_config.NumberColumn("תגובה", format="%d", width="small"),
            "נוהל":        st.column_config.NumberColumn("נוהל", format="%d", width="small"),
        },
    )


def render() -> None:
    report = st.session_state.get("debrief")
    if report is None:
        st.error("לא נמצא דוח מאמן. אנא סיים דיון תחילה.")
        return
    render_debrief(report)
