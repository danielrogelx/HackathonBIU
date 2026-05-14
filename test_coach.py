"""
Standalone test for the coach agent and session store.

Usage (no API call — safe to run anytime):
    python test_coach.py --dry-run

Usage (calls real API — only when team is ready to test):
    python test_coach.py

The SAMPLE_TRANSCRIPT constant can also be imported by app.py
for demo/development purposes.
"""

import sys
import json
from agents.coach import DebriefReport

# ── Sample data ───────────────────────────────────────────────────────────────
# A short criminal-track transcript: theft case, evidence objection raised.
SAMPLE_TRANSCRIPT = [
    {
        "role": "judge",
        "content": "בית המשפט נפתח. עורך הדין מטעם התביעה, אנא פתח את הדיון.",
    },
    {
        "role": "lawyer",
        "content": (
            "כבוד השופט, הנאשם גנב רכב ביום ה-3 בינואר 2024. "
            "ברשותנו צילומי מצלמות אבטחה המזהים את הנאשם בזירה."
        ),
    },
    {
        "role": "attorney",
        "content": (
            "אני מתנגד. לא הוכחה שרשרת שמירה תקינה על צילומי המצלמה. "
            "בהתאם לפקודת הראיות, ראיה שמקורה לא הוכח אינה קבילה."
        ),
    },
    {
        "role": "judge",
        "content": "עורך הדין, כיצד תגיב על ההתנגדות בנוגע לשרשרת השמירה?",
    },
    {
        "role": "lawyer",
        "content": "אני מסכים לבחון שוב את שרשרת השמירה ואגיש תצהיר מתאים.",
    },
    {
        "role": "judge",
        "content": "בית המשפט ייתן לתביעה שבועיים להגשת התצהיר. ניגש לשלב הבא.",
    },
]

SAMPLE_CASE_TYPE = "פלילי"


# ── Dry-run (no API) ──────────────────────────────────────────────────────────
def dry_run() -> None:
    """Verify imports and data structures without touching the API."""
    print("=== Dry run — no API calls ===\n")

    # Verify DebriefReport model accepts valid data
    dummy = DebriefReport(
        score_persuasion=7,
        score_law=6,
        score_evidence=8,
        score_pressure=5,
        score_procedure=7,
        overall=7,
        strong_points="הוצגו ראיות פיזיות בצורה ברורה.",
        weaknesses="התגובה לשרשרת השמירה הייתה חלשה.",
        procedural_errors="לא הוגש תצהיר שרשרת שמירה מראש.",
        reality_check="שופט מנוסה היה עשוי להוציא את הראיה.",
        recommendations="הכן תצהיר שרשרת שמירה לפני הדיון.",
        case_type=SAMPLE_CASE_TYPE,
        timestamp="2026-05-14T10:00:00+00:00",
    )

    print("DebriefReport created successfully:")
    print(dummy.model_dump_json(indent=2, ensure_ascii=False))

    # Verify session store save/load cycle (uses a temp file)
    import os, tempfile, json
    from data import session_store as ss

    original = ss.SESSIONS_FILE
    tmp = tempfile.mktemp(suffix=".json")
    ss.SESSIONS_FILE = tmp  # redirect to temp file for the test

    try:
        ss.save_session(dummy, lawyer_name="ישראל ישראלי")
        loaded = ss.load_sessions()
        assert len(loaded) == 1, "Expected 1 session after save"
        assert loaded[0]["overall"] == 7
        print("\nSession store: save/load OK ✅")
        latest = ss.get_latest_session()
        assert latest is not None
        print("Session store: get_latest_session OK ✅")
    finally:
        ss.SESSIONS_FILE = original
        if os.path.exists(tmp):
            os.remove(tmp)

    print("\n✅ All dry-run checks passed. Ready for API testing.")


# ── Full run (calls API) ──────────────────────────────────────────────────────
def full_run() -> None:
    """Call the real API and print the debrief report. Only use when testing."""
    print("=== Full run — calling OpenRouter API ===\n")
    from agents.coach import analyze_session
    from data.session_store import save_session, load_sessions

    report = analyze_session(SAMPLE_TRANSCRIPT, SAMPLE_CASE_TYPE)
    print("DebriefReport received:")
    print(report.model_dump_json(indent=2, ensure_ascii=False))

    save_session(report, lawyer_name="ישראל ישראלי")
    print(f"\nSessions in store: {len(load_sessions())}")
    print("\n✅ Full run complete.")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if "--dry-run" in sys.argv:
        dry_run()
    else:
        full_run()
