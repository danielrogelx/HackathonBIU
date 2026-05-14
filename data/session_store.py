import json
import os
from agents.coach import DebriefReport

SESSIONS_FILE = os.path.join(os.path.dirname(__file__), "sessions.json")


def save_session(report: DebriefReport, lawyer_name: str = "לא צוין") -> None:
    """Append a completed session's scores to sessions.json."""
    sessions = load_sessions()
    sessions.append({
        "timestamp": report.timestamp,
        "lawyer": lawyer_name,
        "case_type": report.case_type,
        "overall": report.overall,
        "score_persuasion": report.score_persuasion,
        "score_law": report.score_law,
        "score_evidence": report.score_evidence,
        "score_pressure": report.score_pressure,
        "score_procedure": report.score_procedure,
        "strong_points": report.strong_points,
        "recommendations": report.recommendations,
    })
    with open(SESSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)


def load_sessions() -> list[dict]:
    """Return all saved sessions, oldest first."""
    if not os.path.exists(SESSIONS_FILE):
        return []
    with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_latest_session() -> dict | None:
    """Return the most recent session, or None if none exist."""
    sessions = load_sessions()
    return sessions[-1] if sessions else None
