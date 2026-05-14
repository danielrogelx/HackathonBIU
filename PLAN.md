# מתמחה בבית המשפט — Implementation Plan
## HackAgents BIU Hackathon 2026 | ~12 Hours Remaining

---

## 1. Project Summary

**Name:** מתמחה בבית המשפט (Court Practice Simulator)

**What it does:**  
A Hebrew-language AI system that lets lawyers rehearse court sessions. The lawyer fills in case details, then engages in a live simulated hearing with two AI agents — a Judge and an Opposing Attorney — that behave as realistically as possible. If the lawyer provides real names, a Research Agent finds verified information about those individuals and uses it to shape the agents' behavior. After the session, a Coach Agent delivers a structured debrief with strengths, weaknesses, procedural errors, and recommendations.

**Evaluation alignment:**
| Criterion | How we score |
|---|---|
| Technical Execution (20%) | Multi-agent orchestration, tool use (Firecrawl), phase state machine |
| Innovation & Novelty (20%) | First Hebrew courtroom AI simulator with real-person persona research |
| Impact & Utility (25%) | Direct real-world use for Israeli lawyers doing trial prep |
| User Experience (20%) | Streamlit RTL Hebrew UI, structured phases, full debrief report |
| Evaluation (15%) | Built-in benchmark: coach agent scores the session on 5 dimensions |

---

## 2. Architecture

```
┌──────────────────────────────────────────────────────┐
│                  Streamlit Frontend (RTL Hebrew)      │
│  [Setup Form] → [Chat Interface] → [Debrief Report]  │
└─────────────────────────┬────────────────────────────┘
                          │ session state
┌─────────────────────────▼────────────────────────────┐
│              Session Orchestrator                     │
│  • Manages hearing phases                            │
│  • Routes lawyer messages to correct agent           │
│  • Tracks objections, rulings, procedure             │
└──────┬──────────┬──────────┬────────────────┬────────┘
       │          │          │                │
┌──────▼──┐  ┌───▼────┐  ┌──▼────────┐  ┌───▼──────┐
│  Judge  │  │Opposing│  │ Research  │  │  Coach   │
│  Agent  │  │Attorney│  │  Agent    │  │  Agent   │
│ (שופט)  │  │(עו"ד)  │  │(Firecrawl)│  │ (מאמן)   │
└──────┬──┘  └───┬────┘  └──────────-┘  └──────────┘
       │          │
┌──────▼──────────▼─────────────────────────────────┐
│        OpenRouter API → Claude Sonnet 4.5          │
│        (anthropic/claude-sonnet-4-5)               │
└────────────────────────────────────────────────────┘
```

---

## 3. Legal Framework (embedded in agent prompts)

### Criminal Track (פלילי)
- **Primary law:** חוק סדר הדין הפלילי [נוסח משולב], תשמ"ב-1982
- **Penal code:** חוק העונשין, תשל"ז-1977
- **Evidence:** פקודת הראיות [נוסח חדש], תשל"א-1971
- **Phases:** כתב אישום → פתיחה → הצגת הוכחות → חקירת עדים → סיכומים → גזר דין

### Civil Track (אזרחי)
- **Primary law:** תקנות סדר הדין האזרחי, תשע"ט-2018
- **Contract law:** חוק החוזים (חלק כללי), תשל"ג-1973
- **Torts:** פקודת הנזיקין [נוסח חדש]
- **Phases:** כתב תביעה → פתיחה → טיעונים → חקירה נגדית → סיכומים → פסק דין

### Anti-hallucination rules (enforced in all prompts)
- Agents may ONLY cite real Israeli statutes and Supreme Court precedents
- When uncertain about a specific ruling, agents use: "בהתאם לעקרונות הכלליים של הדין הישראלי"
- Agents never invent case names, docket numbers, or statute sections
- Research agent flags low-confidence information rather than presenting it as fact

### Default Personas (when no name is provided or no info found)
- **Judge:** Supreme Court level judge — modeled on general characteristics of Israeli Supreme Court justices (active, questioning, strict on procedure, references Barak-era precedents)
- **Opposing Attorney:** Senior litigator — aggressive on cross-examination, expert at raising procedural objections, challenges evidence admissibility

---

## 4. File Structure

```
Hackathon/
├── app.py                    # Streamlit entry point
├── agents/
│   ├── __init__.py
│   ├── judge.py              # Judge agent
│   ├── attorney.py           # Opposing attorney agent
│   ├── research.py           # Research agent (Firecrawl)
│   └── coach.py              # Post-session debrief agent
├── core/
│   ├── __init__.py
│   ├── orchestrator.py       # Session phase state machine
│   ├── openrouter.py         # OpenRouter API client
│   └── prompts.py            # All system prompt templates
├── ui/
│   ├── setup_form.py         # Case setup UI component
│   ├── chat_view.py          # Simulation chat UI
│   └── debrief_view.py       # Coach report UI
├── config.py                 # Model names, API settings, phase definitions
├── requirements.txt
├── .env.example              # OPENROUTER_API_KEY=...
├── README.md
└── PLAN.md                   # This file
```

---

## 5. Session Phase State Machine

```python
# Criminal phases
CRIMINAL_PHASES = [
    "setup",          # Case details form
    "opening",        # פתיחה — lawyer presents case summary to judge
    "evidence",       # הצגת הוכחות — lawyer argues, attorney objects
    "examination",    # חקירת עדים — optional, lawyer examines witnesses
    "closing",        # סיכומים — final arguments from both sides
    "ruling",         # גזר דין — judge delivers ruling
    "debrief",        # דוח מאמן — coach analysis
]

# Civil phases
CIVIL_PHASES = [
    "setup",
    "opening",        # פתיחה
    "arguments",      # הצגת טענות
    "cross",          # חקירה נגדית
    "closing",        # סיכומים
    "judgment",       # פסק דין
    "debrief",        # דוח מאמן
]
```

Each phase has:
- A Hebrew phase header displayed in the UI
- A phase-specific instruction injected into the agent system prompts
- A trigger condition to advance to the next phase (judge says so, or lawyer requests)

---

## 6. Agent System Prompts (structure)

### Judge Agent Prompt Template
```
אתה שופט ישראלי בכיר המנהל דיון בבית משפט.
[PERSONA_BLOCK]  ← injected from research or default
[CASE_TYPE_BLOCK] ← criminal or civil procedure rules
[CURRENT_PHASE_BLOCK] ← current phase instructions
[CASE_FACTS_BLOCK] ← structured form data

כללים מחייבים:
- אתה מדבר אך ורק בעברית
- אתה מצטט אך ורק חוקים וחוקות ישראליים אמיתיים
- אם אינך בטוח בפרט משפטי ספציפי, אמור "בהתאם לעקרונות הכלליים של הדין הישראלי"
- אתה שולט בקצב הדיון ומחליט מתי עו"ד הצד שכנגד רשאי לדבר
- אתה מציג שאלות קשות לעורך הדין שמתאמן
```

### Opposing Attorney Prompt Template
```
אתה עורך דין מנוסה המייצג את הצד שכנגד בדיון.
[PERSONA_BLOCK]
[CASE_TYPE_BLOCK]
[CURRENT_PHASE_BLOCK]
[CASE_FACTS_BLOCK]

כללים מחייבים:
- אתה מדבר אך ורק בעברית
- אתה מגיש התנגדויות על בסיס חוק ישראלי בלבד
- אתה מנסה לפרוק את הטיעונים של עורך הדין שמתאמן
- אתה תוקפני אך מקצועי
- אתה לא ממציא עובדות — אתה מגיב רק למה שנאמר
```

### Coach Agent Prompt Template
```
אתה מאמן משפטי מנוסה המנתח ביצועי עורך דין בסימולציה.
להלן תמליל הדיון המלא: [TRANSCRIPT]

הפק דוח מובנה הכולל:
1. טענות חזקות (✅)
2. חולשות ונקודות לשיפור (⚠️)
3. טעויות סדריות לפי הדין הישראלי (❌)
4. מה השופט/עו"ד הצד שכנגד היו עושים בפועל (🎭)
5. המלצות קונקרטיות לדיון האמיתי (💡)
6. ציון כולל 1-10 עם הסבר

ציון לפי 5 ממדים:
- שכנוע (1-10)
- שליטה בחוק (1-10)
- ניהול ראיות (1-10)
- תגובה לאתגרים (1-10)
- סדרה ונוהל (1-10)
```

---

## 7. Research Agent Logic

```python
def research_persona(name: str, role: str) -> dict:
    """
    1. Search for name on: nevo.co.il, court.gov.il, Israeli news, bar association
    2. Scrape top 3 most relevant results
    3. Extract: position, notable rulings, known style/tendencies, court level
    4. If confidence < threshold → return default_persona(role)
    5. Return persona dict for injection into agent prompt
    """
    
    # Search queries (Hebrew + English)
    queries = [
        f"{name} שופט ישראל פסקי דין",
        f"{name} עורך דין ישראל",
        f"{name} judge Israel court ruling",
    ]
    
    # Firecrawl search → scrape top results
    # Validate: must find actual court/legal context
    # If found: build verified persona
    # If not found: use elite default persona
```

**Default elite personas:**
- **Judge:** Characteristics of a Supreme Court President — strict proceduralist, asks pointed questions about evidence admissibility, frequently references constitutional principles (חוק יסוד: כבוד האדם וחירותו), known for demanding precise legal citations
- **Attorney:** Characteristics of a top Israeli litigator — aggressive cross-examination, expert in raising hearsay objections (עדות שמיעה), challenges chain of custody on physical evidence, forces procedural errors

---

## 8. OpenRouter API Client

```python
# core/openrouter.py
import httpx

MODEL = "anthropic/claude-sonnet-4-5"
BASE_URL = "https://openrouter.ai/api/v1"

def chat(messages: list[dict], system: str) -> str:
    """Single call to OpenRouter, returns assistant message text."""
    response = httpx.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/hackagents-biu",
            "X-Title": "Court Practice Simulator",
        },
        json={
            "model": MODEL,
            "messages": [{"role": "system", "content": system}] + messages,
            "stream": True,
        },
        timeout=60,
    )
    # Stream and return full content
```

---

## 9. Evaluation Benchmark (15% of score)

The Coach Agent scores every session on 5 dimensions (1–10 each), producing an overall score. This is the built-in evaluation benchmark.

**Benchmark dimensions:**
1. **שכנוע** — persuasiveness of arguments
2. **שליטה בחוק** — accuracy and depth of legal knowledge
3. **ניהול ראיות** — evidence handling and admissibility awareness
4. **תגובה לאתגרים** — response quality under pressure from judge/attorney
5. **סדרה ונוהל** — procedural correctness under Israeli law

Scores are stored per session and can be compared across sessions (same lawyer improving over time).

---

## 10. Team Task Split (12 hours)

### Person 1 — CS Masters → **Architect + Core Agents**
**Hours 1–3:** Project skeleton, `config.py`, `core/openrouter.py`, `core/orchestrator.py` (phase state machine), `core/prompts.py` (all system prompt templates with full Israeli legal content)  
**Hours 3–7:** `agents/judge.py`, `agents/attorney.py` — implement agent call logic, conversation history management, phase-aware system prompt injection  
**Hours 7–10:** Integration with Streamlit session state, end-to-end flow testing  
**Hours 10–12:** Bug fixing, prompt refinement, help with demo

### Person 2 — Comp Engineering → **Research Agent + DevOps**
**Hours 1–2:** Set up Python environment, `requirements.txt`, `.env`, GitHub remote, README skeleton  
**Hours 2–6:** `agents/research.py` — Firecrawl search + scrape, persona extraction, confidence scoring, fallback logic  
**Hours 6–9:** Connect research output to judge/attorney agent prompts; test with real Israeli judge/attorney names  
**Hours 9–12:** Integration testing, help with demo, push to GitHub

### Person 3 — Data Engineering Student 1 → **Streamlit Frontend**
**Hours 1–3:** `app.py` skeleton, Hebrew RTL CSS config, case type selector (פלילי/אזרחי)  
**Hours 3–6:** `ui/setup_form.py` — structured input form (case type, parties, charges, evidence, optional judge/attorney names)  
**Hours 6–9:** `ui/chat_view.py` — chat interface with distinct styling for Judge (blue), Attorney (red), Lawyer (white); phase header display; streaming text output  
**Hours 9–12:** Polish, RTL fixes, session reset button, connect all UI to orchestrator

### Person 4 — Data Engineering Student 2 → **Coach Agent + Benchmark + Docs**
**Hours 1–3:** `agents/coach.py` — post-session transcript analysis, structured debrief generation  
**Hours 3–6:** `ui/debrief_view.py` — formatted report display (scores, checkmarks, recommendations)  
**Hours 6–8:** Evaluation benchmark — session scoring, score persistence, comparison view  
**Hours 8–10:** README.md (English + Hebrew), test the full end-to-end flow with a real sample case  
**Hours 10–12:** Demo script preparation, final testing, GitHub push

---

## 11. Streamlit UI Flow

```
1. Landing page
   ├── Title: "מתמחה בבית המשפט 🏛️"
   ├── Subtitle: "סימולטור דיון משפטי לעורכי דין"
   └── [התחל סשן חדש] button

2. Setup Form
   ├── סוג תיק: [פלילי 🔴] [אזרחי 🔵]
   ├── שם השופט (אופציונלי): ____________
   ├── שם עו"ד הצד שכנגד (אופציונלי): ____________
   ├── פרטי התיק:
   │   ├── הצדדים: ____________
   │   ├── האישום/התביעה: ____________
   │   └── ראיות מרכזיות: ____________
   └── [בחן אותי!] button → triggers research agent

3. Research loading screen (if names provided)
   └── "מחפש מידע על השופט X..."

4. Simulation Chat
   ├── Phase header: "שלב: פתיחה | שופט: [name]"
   ├── Chat messages:
   │   ├── 🔵 [שופט]: ...
   │   ├── 🔴 [עו"ד]: ...
   │   └── ⚪ [אתה]: ____________
   └── [סיים דיון] button

5. Debrief Report
   ├── Scores: שכנוע 7/10 | שליטה בחוק 6/10 | ...
   ├── ✅ טענות חזקות
   ├── ⚠️ חולשות
   ├── ❌ טעויות סדריות
   ├── 🎭 מה היו עושים בפועל
   └── 💡 המלצות
```

---

## 12. Requirements

```
# requirements.txt
streamlit>=1.40.0
httpx>=0.27.0
python-dotenv>=1.0.0
firecrawl-py>=1.0.0
pydantic>=2.0.0
```

---

## 13. Demo Script (5-minute live demo)

**Minute 1:** Show the setup form. Enter a criminal case (e.g., theft / גניבה). Enter "אסתר חיות" as judge name. Watch the research agent find her profile.

**Minute 2:** Show the simulation starting. Judge opens the session formally in Hebrew. Lawyer makes their opening argument.

**Minute 3:** Lawyer presents evidence. Opposing attorney objects (raises hearsay objection per פקודת הראיות). Judge rules on the objection and asks the lawyer a hard question.

**Minute 4:** Closing arguments. Judge delivers ruling in Hebrew with legal reasoning.

**Minute 5:** Debrief report — show the 5 dimension scores, the procedural errors caught, and the concrete recommendations. This is the money shot for judges.

---

## 14. Risk Mitigations

| Risk | Mitigation |
|---|---|
| Firecrawl finds no useful info | Fallback to elite default personas (pre-written, validated) |
| Hebrew RTL broken in Streamlit | Add `st.markdown('<style>body{direction:rtl}</style>', unsafe_allow_html=True)` |
| Model hallucinating case law | System prompt explicitly forbids invented citations; agents say "עקרונות כלליים" when uncertain |
| $50 budget runs out | Claude Sonnet 4.5 at ~$3/1M tokens; a full session is ~10K tokens → ~$0.03/session; budget covers 1,600+ sessions |
| Phase transitions unclear | Orchestrator has explicit triggers; lawyer can also manually advance phase |
| Agents break character | Each call re-injects full system prompt; no shared conversation history between Judge and Attorney |
