"""
Configuration for Court Practice Simulator
מתמחה בבית המשפט — Hackathon BIU 2026
"""

import os
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

# API Configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
print(
    f"Loaded OpenRouter API Key: {OPENROUTER_API_KEY if OPENROUTER_API_KEY else 'No'}"
)
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL = "anthropic/claude-sonnet-4-5"

# Model parameters
MAX_TOKENS = 1024
TEMPERATURE = 0.7

# HTTP Configuration
HTTP_TIMEOUT = 60
HTTP_REFERER = "https://github.com/hackagents-biu"
HTTP_TITLE = "Court Practice Simulator"


# Phase Definitions
class CaseType(str, Enum):
    CRIMINAL = "criminal"  # פלילי
    CIVIL = "civil"  # אזרחי


CRIMINAL_PHASES = [
    "setup",  # Case details form
    "opening",  # פתיחה — lawyer presents case summary to judge
    "evidence",  # הצגת הוכחות — lawyer argues, attorney objects
    "examination",  # חקירת עדים — optional, lawyer examines witnesses
    "closing",  # סיכומים — final arguments from both sides
    "ruling",  # גזר דין — judge delivers ruling
    "debrief",  # דוח מאמן — coach analysis
]

CIVIL_PHASES = [
    "setup",
    "opening",  # פתיחה
    "arguments",  # הצגת טענות
    "cross",  # חקירה נגדית
    "closing",  # סיכומים
    "judgment",  # פסק דין
    "debrief",  # דוח מאמן
]

# Phase display names (Hebrew)
PHASE_NAMES_HE = {
    "setup": "הגדרת התיק",
    "opening": "פתיחה",
    "evidence": "הצגת הוכחות",
    "arguments": "הצגת טענות",
    "examination": "חקירת עדים",
    "cross": "חקירה נגדית",
    "closing": "סיכומים",
    "ruling": "גזר דין",
    "judgment": "פסק דין",
    "debrief": "דוח מאמן",
}

# UI Configuration
UI_TITLE = "מתמחה בבית המשפט 🏛️"
UI_SUBTITLE = "סימולטור דיון משפטי לעורכי דין"

# Agent roles
AGENT_JUDGE = "judge"
AGENT_ATTORNEY = "attorney"
AGENT_COACH = "coach"
AGENT_RESEARCH = "research"

# Hebrew legal references
CRIMINAL_LAW_STATUTES = {
    "ccp": 'חוק סדר הדין הפלילי [נוסח משולב], תשמ"ב-1982',
    "penal": 'חוק העונשין, תשל"ז-1977',
    "evidence": 'פקודת הראיות [נוסח חדש], תשל"א-1971',
}

CIVIL_LAW_STATUTES = {
    "ccp": 'תקנות סדר הדין האזרחי, תשע"ט-2018',
    "contracts": 'חוק החוזים (חלק כללי), תשל"ג-1973',
    "torts": "פקודת הנזיקין [נוסח חדש]",
}

# Default persona characteristics (used when research finds no info)
DEFAULT_JUDGE_STYLE = {
    "level": "עליון",
    "characteristic": "שופט עליון מנוסה, קפדן בנוהל, שואל שאלות חדות על קבילות ראיות",
    "known_references": ["חוק יסוד: כבוד האדם וחירותו", "עקרונות הערך העליון של הצדק"],
}

DEFAULT_ATTORNEY_STYLE = {
    "experience": "עורך דין בכיר",
    "characteristic": "תוקפני בחקירה נגדית, מומחה בהתנגדויות על בסיס חוק, מתמחה בהעלאת ממצאי הליך",
    "tactics": ["התנגדות לעדות שמיעה", "אתגר בשרשרת שמירה", "כשלים סדריים"],
}

# Research confidence thresholds
RESEARCH_CONFIDENCE_THRESHOLD = 0.6  # 60% confidence to use found persona

# Budget tracking (optional)
BUDGET_LIMIT_DOLLARS = 50
COST_PER_TOKEN = 0.003 / 1_000_000  # $3 per 1M tokens (approximate)
