"""
Document Analyzer — runs a one-time legal analysis of the uploaded case documents
(כתב תביעה / כתב הגנה) at session start.

The structured findings are stored in session state and injected into the
judge's system prompt throughout the entire session.
"""

from core.openrouter import chat

_ANALYSIS_PROMPT = """אתה עורך דין בכיר ומנוסה בדין הישראלי. ניתח את המסמכים המשפטיים הבאים וזהה:

1. **הטענות המרכזיות** בכל מסמך (כתב תביעה / כתב אישום וכתב הגנה)
2. **הראיות שמוצגות** — ומה חסר
3. **חולשות משפטיות** בכל אחד מהמסמכים לפי הדין הישראלי
4. **סתירות** בין שני המסמכים
5. **בעיות סדריות ופרוצדורליות** — כגון אי-עמידה בכללי הגשה, היעדר פרטים נדרשים, או ניסוחים בעייתיים

חשוב:
- ציין אך ורק עובדות שמוצגות במסמכים עצמם
- אל תמציא פרטים שלא מופיעים
- השתמש בעברית בלבד
- ענה בצורה מובנית עם כותרות ברורות
"""


def analyze_case_documents(plaintiff_text: str, defense_text: str) -> str:
    """
    Analyze plaintiff and defense documents once at session start.

    Args:
        plaintiff_text: Extracted text from כתב תביעה / כתב אישום
        defense_text:   Extracted text from כתב הגנה

    Returns:
        Structured Hebrew analysis string stored in session state
    """
    # Trim to avoid exceeding context — 8K chars each is ~2K tokens each
    p_excerpt = plaintiff_text[:8000].strip()
    d_excerpt = defense_text[:8000].strip()

    combined = f"""כתב תביעה / כתב אישום:
{p_excerpt}

---

כתב הגנה:
{d_excerpt}"""

    messages = [{"role": "user", "content": combined}]
    return chat(messages=messages, system=_ANALYSIS_PROMPT, max_tokens=2048)
