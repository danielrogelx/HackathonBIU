import json
import re
from datetime import datetime, timezone
from pydantic import BaseModel, field_validator
from core.openrouter import chat as call_openrouter


def _strip_html(text: str) -> str:
    """Remove any HTML tags the LLM may have included in text fields."""
    return re.sub(r"<[^>]+>", "", text or "").strip()


class DebriefReport(BaseModel):
    score_persuasion: int  # שכנוע          1–10
    score_law: int  # שליטה בחוק     1–10
    score_evidence: int  # ניהול ראיות     1–10
    score_pressure: int  # תגובה לאתגרים   1–10
    score_procedure: int  # סדרה ונוהל      1–10
    overall: int  # ממוצע מעוגל     1–10
    strong_points: str  # ✅ טענות חזקות
    weaknesses: str  # ⚠️ חולשות
    procedural_errors: str  # ❌ טעויות סדריות
    reality_check: str  # 🎭 מה היו עושים בפועל
    recommendations: str  # 💡 המלצות
    case_type: str  # "פלילי" or "אזרחי"
    timestamp: str  # ISO 8601

    @field_validator(
        "score_persuasion",
        "score_law",
        "score_evidence",
        "score_pressure",
        "score_procedure",
        "overall",
    )
    @classmethod
    def score_in_range(cls, v: int) -> int:
        if not 1 <= v <= 10:
            raise ValueError(f"Score must be between 1 and 10, got {v}")
        return v

    @field_validator(
        "strong_points",
        "weaknesses",
        "procedural_errors",
        "reality_check",
        "recommendations",
    )
    @classmethod
    def strip_html_from_text(cls, v: str) -> str:
        """LLMs occasionally wrap text in HTML tags — strip them."""
        return _strip_html(v)


COACH_SYSTEM_PROMPT = """אתה מאמן משפטי מנוסה המנתח ביצועי עורך דין ישראלי בסימולציה של דיון בבית משפט.

כללים מחייבים:
- השב אך ורק בעברית
- ציטוט חוקים: אך ורק חוקים ישראליים אמיתיים
- אם אינך בטוח בפרט משפטי ספציפי, כתוב "על פי הכללים הכלליים של הדין הישראלי"
- אל תמציא שמות פסקי דין, מספרי תיקים, או מספרי סעיפים

קבל תמליל דיון והחזר תשובה בפורמט JSON בדיוק בסכמה הבאה, ללא טקסט נוסף לפני או אחרי:
{
  "score_persuasion": <מספר שלם 1-10>,
  "score_law": <מספר שלם 1-10>,
  "score_evidence": <מספר שלם 1-10>,
  "score_pressure": <מספר שלם 1-10>,
  "score_procedure": <מספר שלם 1-10>,
  "overall": <ממוצע מעוגל של חמשת הציונים, מספר שלם>,
  "strong_points": "<פסקת טקסט בעברית: מה עבד טוב>",
  "weaknesses": "<פסקת טקסט בעברית: חולשות ונקודות לשיפור>",
  "procedural_errors": "<פסקת טקסט בעברית: טעויות סדריות לפי הדין הישראלי>",
  "reality_check": "<פסקת טקסט בעברית: מה השופט ועו\"ד הצד שכנגד היו עושים בפועל>",
  "recommendations": "<פסקת טקסט בעברית: המלצות קונקרטיות לדיון האמיתי>"
}

חמשת ממדי הניקוד:
1. שכנוע — עד כמה הטיעונים שכנעו את בית המשפט?
2. שליטה בחוק — האם הוצגו החוקים הנכונים בדייקנות?
3. ניהול ראיות — האם הראיות הוצגו כהלכה ובאופן קביל?
4. תגובה לאתגרים — עד כמה טוב עורך הדין התמודד עם התנגדויות ושאלות?
5. סדרה ונוהל — האם נשמר סדר הדיון הנכון לפי הדין הישראלי?"""


def _transcript_to_text(transcript: list[dict]) -> str:
    role_map = {
        "lawyer": "עורך דין",
        "judge": "שופט",
        "attorney": 'עו"ד שכנגד',
    }
    lines = []
    for msg in transcript:
        role = role_map.get(msg["role"], msg["role"])
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)


def _parse_json_response(raw: str) -> dict:
    """Strip markdown code fences and parse JSON; fall back to regex extraction on truncation."""
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = (
            "\n".join(lines[1:-1])
            if lines[-1].strip() == "```"
            else "\n".join(lines[1:])
        )
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return _extract_partial_json(cleaned)


def _extract_partial_json(text: str) -> dict:
    """
    Recover what we can from a truncated JSON response using regex.
    Integer fields default to 5 and text fields to a Hebrew fallback string.
    """
    result: dict = {}
    int_fields = (
        "score_persuasion",
        "score_law",
        "score_evidence",
        "score_pressure",
        "score_procedure",
        "overall",
    )
    str_fields = (
        "strong_points",
        "weaknesses",
        "procedural_errors",
        "reality_check",
        "recommendations",
    )
    for field in int_fields:
        m = re.search(rf'"{field}"\s*:\s*(\d+)', text)
        result[field] = int(m.group(1)) if m else 5

    for field in str_fields:
        # First try a complete quoted value
        m = re.search(rf'"{field}"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
        if m:
            result[field] = m.group(1)
        else:
            # Response was truncated mid-string — take what was generated
            m = re.search(rf'"{field}"\s*:\s*"(.*)', text, re.DOTALL)
            result[field] = m.group(1).strip() if m else "(לא ניתן לנתח — הדוח נקטע)"
    return result


def analyze_session(transcript: list[dict], case_type: str) -> DebriefReport:
    """
    Analyze a completed court session and return a structured debrief.

    transcript: list of {"role": "lawyer"|"judge"|"attorney", "content": str}
    case_type:  "פלילי" or "אזרחי"
    """
    # Limit transcript length — very long sessions overflow the coach context window
    # and cause the JSON response to be truncated.
    trimmed = transcript[-40:] if len(transcript) > 40 else transcript
    transcript_text = _transcript_to_text(trimmed)
    messages = [{"role": "user", "content": f"תמליל הדיון:\n\n{transcript_text}"}]

    # Use a generous token budget so the full JSON response is never cut off.
    raw = call_openrouter(messages, COACH_SYSTEM_PROMPT, max_tokens=4096)
    data = _parse_json_response(raw)
    data["case_type"] = case_type
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    return DebriefReport(**data)
