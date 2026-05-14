# Coach Agent + Benchmark + Docs — Execution Plan
## Branch: `coach-benchmark-docs` | Data Engineering Student 2

---

## Decisions locked in

- **No Streamlit** — pure Python only. Person 3 owns all UI including debrief view.
- **No API calls yet** — stub exists in code but is not invoked until team testing phase.
- **OpenRouter stub** — write your own minimal stub; replace with Person 1's when ready.
- **API key** — in `.env` (gitignored). Never commit.
- **Score storage** — JSON file (`sessions.json`, gitignored).
- **README** — one bilingual file, Hebrew + English stacked.

---

## Your Deliverables

| File | What it is |
|---|---|
| `core/openrouter_stub.py` | Real API client (not called until testing) |
| `agents/coach.py` | Coach logic — takes transcript, returns `DebriefReport` |
| `data/session_store.py` | Save/load session scores to `sessions.json` |
| `README.md` | Bilingual English + Hebrew |
| `.env.example` | API key template for teammates |

**Hand off to Person 3:** the `DebriefReport` Pydantic model — they render it in Streamlit.
**Hand off to Person 1:** agree on transcript format (see bottom of this file).

---

## Hours 1–3: `core/openrouter_stub.py` + `agents/coach.py`

### Step 1 — Create the folder skeleton

Run once to set up your part of the project:

```bash
mkdir -p agents core data
touch agents/__init__.py core/__init__.py data/__init__.py
```

### Step 2 — `core/openrouter_stub.py`

Real OpenRouter client. Do NOT call it yet — just write it and test that it imports cleanly.

```python
# core/openrouter_stub.py
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

MODEL = "anthropic/claude-sonnet-4-5"
BASE_URL = "https://openrouter.ai/api/v1"


def call_openrouter(messages: list[dict], system: str) -> str:
    """Call OpenRouter and return the assistant message text."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    resp = httpx.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/danielrogelx/HackathonBIU",
            "X-Title": "Court Practice Simulator",
        },
        json={
            "model": MODEL,
            "messages": [{"role": "system", "content": system}] + messages,
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
```

### Step 3 — `agents/coach.py`

The full coach agent. Returns a structured `DebriefReport` Pydantic model.
Person 3 imports `DebriefReport` from here to build the UI.

```python
# agents/coach.py
import json
from datetime import datetime, timezone
from pydantic import BaseModel
from core.openrouter_stub import call_openrouter


class DebriefReport(BaseModel):
    score_persuasion: int   # שכנוע         1-10
    score_law: int          # שליטה בחוק    1-10
    score_evidence: int     # ניהול ראיות    1-10
    score_pressure: int     # תגובה לאתגרים  1-10
    score_procedure: int    # סדרה ונוהל     1-10
    overall: int            # ממוצע מעוגל    1-10
    strong_points: str      # ✅ טענות חזקות
    weaknesses: str         # ⚠️ חולשות
    procedural_errors: str  # ❌ טעויות סדריות
    reality_check: str      # 🎭 מה היו עושים בפועל
    recommendations: str    # 💡 המלצות
    case_type: str          # "פלילי" or "אזרחי"
    timestamp: str          # ISO 8601


COACH_SYSTEM_PROMPT = """אתה מאמן משפטי מנוסה המנתח ביצועי עורך דין ישראלי בסימולציה של דיון בבית משפט.

כללים מחייבים:
- השב אך ורק בעברית
- ציטוט חוקים: אך ורק חוקים ישראליים אמיתיים
- אם אינך בטוח בפרט משפטי ספציפי, כתוב "על פי הכללים הכלליים של הדין הישראלי"
- אל תמציא שמות פסקי דין, מספרי תיקים, או מספרי סעיפים

קבל תמליל דיון והחזר תשובה בפורמט JSON בדיוק בסכמה הבאה (ללא טקסט נוסף):
{
  "score_persuasion": <מספר שלם 1-10>,
  "score_law": <מספר שלם 1-10>,
  "score_evidence": <מספר שלם 1-10>,
  "score_pressure": <מספר שלם 1-10>,
  "score_procedure": <מספר שלם 1-10>,
  "overall": <ממוצע מעוגל של חמשת הציונים, מספר שלם>,
  "strong_points": "<טקסט: מה עבד טוב>",
  "weaknesses": "<טקסט: חולשות ונקודות לשיפור>",
  "procedural_errors": "<טקסט: טעויות סדריות לפי הדין הישראלי>",
  "reality_check": "<טקסט: מה השופט/עו\"ד הצד שכנגד היו עושים בפועל>",
  "recommendations": "<טקסט: המלצות קונקרטיות לדיון האמיתי>"
}

חמשת ממדי הניקוד:
1. שכנוע — עד כמה הטיעונים שכנעו את בית המשפט?
2. שליטה בחוק — האם הוצגו החוקים והפסיקות הנכונות?
3. ניהול ראיות — האם הראיות הוצגו כהלכה ובאופן קביל?
4. תגובה לאתגרים — עד כמה טוב עורך הדין התמודד עם התנגדויות ושאלות?
5. סדרה ונוהל — האם נשמר סדר הדיון הנכון לפי החוק הישראלי?"""


def _transcript_to_text(transcript: list[dict]) -> str:
    role_map = {"lawyer": "עורך דין", "judge": "שופט", "attorney": "עו\"ד שכנגד"}
    lines = []
    for msg in transcript:
        role = role_map.get(msg["role"], msg["role"])
        lines.append(f"{role}: {msg['content']}")
    return "\n".join(lines)


def analyze_session(transcript: list[dict], case_type: str) -> DebriefReport:
    """
    Takes the full session transcript and returns a structured debrief.

    transcript: list of {"role": "lawyer"|"judge"|"attorney", "content": str}
    case_type: "פלילי" or "אזרחי"
    """
    transcript_text = _transcript_to_text(transcript)
    messages = [{"role": "user", "content": f"תמליל הדיון:\n\n{transcript_text}"}]

    raw = call_openrouter(messages, COACH_SYSTEM_PROMPT)

    # Strip markdown code fences if model wraps response
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[1:])
    if cleaned.endswith("```"):
        cleaned = "\n".join(cleaned.split("\n")[:-1])

    data = json.loads(cleaned)
    data["case_type"] = case_type
    data["timestamp"] = datetime.now(timezone.utc).isoformat()
    return DebriefReport(**data)
```

---

## Hours 3–6: `data/session_store.py`

Saves each completed session's scores to `sessions.json` so a lawyer can track progress over time.
Person 3 calls `load_sessions()` to render the history table in Streamlit.

```python
# data/session_store.py
import json
import os
from agents.coach import DebriefReport

SESSIONS_FILE = os.path.join(os.path.dirname(__file__), "sessions.json")


def save_session(report: DebriefReport, lawyer_name: str = "לא צוין") -> None:
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
    if not os.path.exists(SESSIONS_FILE):
        return []
    with open(SESSIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_latest_session() -> dict | None:
    sessions = load_sessions()
    return sessions[-1] if sessions else None
```

---

## Hours 6–8: Testing (with real API)

By this point the team should have the core flow working. Run your standalone test:

```python
# test_coach.py — run with: python test_coach.py
from agents.coach import analyze_session

fake_transcript = [
    {"role": "lawyer",   "content": "כבוד השופט, הנאשם גנב את הרכב ביום 3.1.2024. יש לנו ראיות ממצלמות האבטחה."},
    {"role": "judge",    "content": "האם הראיות הוגשו כחוק? מה לגבי שרשרת השמירה?"},
    {"role": "lawyer",   "content": "כן כבוד השופט, הראיות נשמרו כחוק."},
    {"role": "attorney", "content": "אני מתנגד — לא הוכחה שרשרת שמירה תקינה על הראיות."},
    {"role": "lawyer",   "content": "אני מסכים לבחון שוב את שרשרת השמירה."},
]

report = analyze_session(fake_transcript, "פלילי")
print(report.model_dump_json(indent=2))

# Also test save
from data.session_store import save_session, load_sessions
save_session(report, "ישראל ישראלי")
print(f"\nSessions saved: {len(load_sessions())}")
```

What to verify:
- [ ] All 5 scores are integers between 1–10
- [ ] `overall` is the rounded average
- [ ] All text fields are in Hebrew
- [ ] `sessions.json` is created with one entry
- [ ] Running the test a second time appends a second entry

---

## Hours 8–10: README.md + `.env.example`

### `.env.example`

```
OPENROUTER_API_KEY=your_key_here
```

### README.md structure

```markdown
# מתמחה בבית המשפט — Court Practice Simulator

> סימולטור דיון משפטי לעורכי דין ישראלים  
> AI-powered Hebrew courtroom simulator for Israeli lawyers

---

## על הפרויקט | About

[Hebrew paragraph describing what it does]

[English paragraph]

## התקנה | Installation

...

## הרצה | Running

...

## ארכיטקטורה | Architecture

...

## הצוות | Team

...
```

---

## Hours 10–12: Demo Prep + Push

### Your 90 seconds in the demo (Minute 5)
1. "עכשיו נראה את דוח המאמן..."
2. Show the 5 score cards — point to color coding
3. Open "טעויות סדריות" — show a real procedural error the AI caught
4. Show "המלצות" — one concrete actionable tip
5. Show the history table — "ככה עורך הדין יכול לעקוב אחרי ההתקדמות שלו לאורך זמן"

### Push to GitHub
```bash
git add agents/coach.py core/openrouter_stub.py data/session_store.py README.md .env.example .gitignore
git commit -m "Add coach agent, score persistence, and README"
git push origin coach-benchmark-docs
# Open PR on GitHub to merge into main
```

---

## Interface Contract with Teammates

### With Person 1 (Architect)
Agree on transcript format — every message is:
```python
{"role": "lawyer" | "judge" | "attorney", "content": "Hebrew text"}
```
When Person 1's `core/openrouter.py` is ready, change the import in `core/openrouter_stub.py` or just point `agents/coach.py` to their version.

### With Person 3 (Frontend)
Give them `DebriefReport` and `load_sessions()`:
```python
from agents.coach import DebriefReport
from data.session_store import load_sessions
```
They handle all rendering — you just produce the data.
